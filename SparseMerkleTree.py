from hashlib import sha256
from BinaryTree import BinaryNode
from MerkleNode import hash_function, MerkleBinaryNode


def print_error(msg):
    # TODO before submit make sure to replace the code with "print('')"
    # This function will help us make all the prints disappear before submit
    print(msg)


class SparseMerkleTree:
    """
    This class emulates a complete merkle tre with 2**depth indicator leaves (0 or 1).
    The class make a smart use of the fact bit-patterns reoccur and each hash is unique. It is done by the following
    logic:
        1. The tree is initialize as linked list -
                Because all leaves are the same, all the hashes in the same height have the same value, this allows me
                to save just 1 node per height (depth+1 nodes).
        2. Segmentation -
                When a node is updated, it will check if its two sons have the same hash, if so, it will free the right
                son and make the left son as both left & right sons. This gives a very strong space saving property - if
                there is 2 adjacent strips of l leaves that are the same, their mutual ancestor will have 2 sons with
                the same hashes and the same subtree, so only 1 subtree will be saved in memory.
                One will suggest to use a dictionary of values for each level (level=all nodes with the same height) to
                reuse subtree even more, but I claim that for levels (except the leaves level) it will not profit us
                with more segments because of the initial state, the fact you can't "unmark" leaves, and the fact that
                if there are bits between 2 equal patterns, the .
        3. When marking a leaf, recreate a copy of the route from the root to the leaf because nodes are immutable -
                This promise us that if some other node points to a node in the original route (possible due to
                segmentation), the update will not corrupt its data.
                When a route is no longer needed by any node, the garbage collector will notice no active member is
                pointing to the route and it will release its memory.
    """
    def __init__(self, depth: int):
        """
        Creates a full sparse tree with given depth (which means, 2**depth leaves), each leaf is initial with '0'.
        :param depth: The wanted size of the sparse merkle tree.
        """
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

            # if the subtrees are the same, save only one copy of it
            node = path_to_digest[i]
            if node.left.data == node.right.data:
                node.right_binding(node.left)

        # update the root
        self.root = path_to_digest[0]

    def get_root_key(self):
        return self.root.data

    def generate_proof_of_inclusion(self, digest):
        # initialize
        proof = [self.root.data]
        route_to_digest = self._get_route_to_leaf(digest)

        # skip nodes that can be computed using only the digest value
        while len(route_to_digest) > 1 and route_to_digest[-2].left is route_to_digest[-2].right:
            route_to_digest.pop(-1)
        # if at least two nodes were removed, append the last hash of node that its subtree is actually a linked list
        if len(route_to_digest) < self.depth:
            proof.append(route_to_digest[-1].data)
        # if only one node was removed, return it to the route - it's smaller than a hash
        elif len(route_to_digest) == self.depth:
            proof.append(route_to_digest[-1].left.data)

        # create the rest of the proof
        for i in range(len(route_to_digest) - 2, -1, -1):
            # if the left son is on the path to digest, add the other sibling to the proof
            if route_to_digest[i].left is route_to_digest[i + 1]:
                proof.append(route_to_digest[i].right.data)
            else:
                proof.append(route_to_digest[i].left.data)

        # return proof
        return proof

    def check_proof_of_inclusion(self, digest, classification_bit, proof):
        # parse digest and proof
        path_int = int(digest, 16)
        correct_final_result = proof.pop(0)

        # Compute self-hash-shortcut
        current_hash_val = classification_bit
        # there are depth+1 nodes in the route from root to leaf. We poped the root, so a full proof is depth long.
        if len(proof) < self.depth:
            correct_last_self_hash_val = proof.pop(0)
            self_hashes_count = self.depth - len(proof)  # num of missing hashes from the proof
            while self_hashes_count > 0:
                self_hashes_count -= 1
                path_int = path_int >> 1
                current_hash_val = hash_function(current_hash_val + current_hash_val)
            # check we reached to the correct last self hash result
            if current_hash_val != correct_last_self_hash_val:
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

