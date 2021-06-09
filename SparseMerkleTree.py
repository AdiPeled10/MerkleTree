from hashlib import sha256
from BinaryTree import BinaryNode
from MerkleNode import hash_function, MerkleBinaryNode


def print_error(msg):
    # TODO before submit make sure to replace the code with "print('')"
    # This function will help us make all the prints disappear before submit
    print(msg)


class SparseMerkleTree:
    def __init__(self, depth: int):
        # for 2**256 leaves we need depth of 256
        self.depth = depth
        curr = MerkleBinaryNode.create_non_hash_leaf('0')
        while depth > 0:
            depth -= 1
            curr_parent = MerkleBinaryNode(curr, curr)
            curr = curr_parent
        self.root = curr

    def _get_route_to_leaf(self, digest):
        route = []
        mask = 1 << (self.depth - 1)
        path_int = int(digest, 16)
        next_node = self.root
        while next_node is not None:
            route.append(next_node)
            direction = (path_int & mask) != 0  # direction is 1 iff the next direction bit is 1
            mask = mask >> 1
            next_node = next_node.get_son(direction)
        return route

    def mark_leaf(self, digest):
        SparseMerkleTree.mark_leaf.bit_to_int_offset = ord('0')

        # check input is valid
        if 4 * len(digest) != self.depth:
            print_error("digest isn't in the correct length!")

        # create the path to the digest leaf
        path_to_digest = self._get_route_to_leaf(digest)

        # update the digest leaf
        path_to_digest[-1] = MerkleBinaryNode.create_non_hash_leaf('1')

        # update the path to the digest leaf and try to segment
        # this also update the keys from the marked node towards the root
        path_int = int(digest, 16)
        for i in range(len(path_to_digest) - 2, -1, -1):  # go through the path in reverse order (including the root)
            # create a new copy of the current node with updated son
            replaced_node = path_to_digest[i]
            if path_int & 1 == BinaryNode.RIGHT_DIRECTION:
                path_to_digest[i] = MerkleBinaryNode(path_to_digest[i].left, path_to_digest[i + 1])
            else:
                path_to_digest[i] = MerkleBinaryNode(path_to_digest[i + 1], path_to_digest[i].right)
            path_int = path_int >> 1

            # remove references from old node to current tree - to help clean out memory
            replaced_node.one_way_detach_node()

            # if the subtrees are the same, save only one copy of it
            node = path_to_digest[i]
            if node.left.data == node.right.data:
                node.right.parent = None
                node.right_binding(node.left)

        # update the root
        self.root = path_to_digest[0]

    def get_root_key(self):
        return self.root.data

    def generate_proof_of_inclusion(self, digest):
        # initialize
        root_sign = self.root.data
        proof = []
        route_to_digest = self._get_route_to_leaf(digest)

        # skip nodes that can be computed using only the digest value
        while len(route_to_digest) > 1 and route_to_digest[-2].left.data == route_to_digest[-2].right.data:
            route_to_digest.pop(-1)
        # if at least one node was removed, append the last hash of digest that is the same as the hash of its sibling
        if len(route_to_digest) < self.depth:
            proof.append(route_to_digest[-1].data)

        # create the rest of the proof
        for i in range(len(route_to_digest) - 2, -1, -1):
            # if the left son is on the path to digest, add the other sibling to the proof
            if route_to_digest[i].left is route_to_digest[i + 1]:
                proof.append(route_to_digest[i].right.data)
            else:
                proof.append(route_to_digest[i].left.data)

        # return proof
        return root_sign, proof

    def check_proof_of_inclusion(self, digest, classification_bit, proof):
        # parse digest and proof
        path_int = int(digest, 16)
        correct_final_result = proof[0]
        proof = proof[1]

        # compute self-hash-shortcut
        current_hash_val = classification_bit
        self_hashes_count = self.depth - 1 - len(proof)
        while self_hashes_count > 0:
            self_hashes_count -= 1
            path_int = path_int >> 1
            current_hash_val = hash_function(current_hash_val + current_hash_val)
        if self.depth - 1 > len(proof):  # if at least one iteration was preformed
            correct_current_hash_val = proof.pop(0)
            if current_hash_val != correct_current_hash_val:
                return False

        # compute rest of the hashes using the proof
        for sibling_hash in proof:
            if path_int & 1 == BinaryNode.RIGHT_DIRECTION:
                current_hash_val = hash_function(sibling_hash + current_hash_val)
            else:
                current_hash_val = hash_function(current_hash_val + sibling_hash)
            path_int = path_int >> 1

        # return validation result
        return current_hash_val == correct_final_result

