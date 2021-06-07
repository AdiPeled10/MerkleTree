from hashlib import sha256
from BinaryTree import BinaryNode
from copy import deepcopy


def print_error(msg):
    # TODO before submit make sure to replace the code with "print('')"
    # This function will help us make all the prints disappear before submit
    print(msg)


class MerkleNode(BinaryNode):
    def get_route_to_leaf(self, leaf_num):
        route = []
        next_node = self
        while next_node is not None:
            route.append(next_node)

            next_node = next_node.get_son()


class SparseMerkleTree:
    def __init__(self, depth: int):
        # for 2**256 leaves we need depth of 256
        self.depth = depth
        curr = MerkleNode(0)
        while depth > 0:
            depth -= 1
            curr_parent = MerkleNode(0, curr, curr)
            curr = curr_parent
        self.root = curr

    def _get_route_to_leaf(self, digest):
        route = []
        mask = 1 << (self.depth - 1)
        path_int = int(digest, 8)
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
        if len(digest) != self.depth:
            print_error("digest isn't in the correct length!")

        # create the path to the digest leaf
        current = self.root
        stack = [self.root]
        for bit in digest:
            bit = ord(bit) - SparseMerkleTree.mark_leaf.bit_to_int_offset
            if bit == BinaryNode.LEFT_DIRECTION:
                current.left_son = deepcopy(current.left_son)
                current = current.left_son
            else:  # bit == BinaryNode.Right_DIRECTION:
                current.right_son = deepcopy(current.right_son)
                current = current.right_son
            stack.insert(0, current)

        # update the digest leaf
        stack[0].key = '1'
        stack.pop(0)

        # update the path to the digest leaf and try to segment
        for node in stack:
            node.key = sha256(node.left_son.key + node.right_son.key)
            # The subtrees are the same, save only one copy of it
            if node.left_son.key == node.right_son.key:
                node.left_son = node.right_son

    def get_root_key(self):
        return self.root.get_key()

    def generate_proof_of_inclusion(self, digest):
        # initialize
        root_sign = self.root.compute_key()
        proof = []
        route_to_digest = self._get_route_to_leaf(digest)

        # skip nodes that can be computed using only the digest value
        while len(route_to_digest) > 1 and route_to_digest[-2].left_son.key == route_to_digest[-2].right_son.key:
            route_to_digest.pop(-1)
        # if at least one node was removed, append the last hash of digest that is the same as the hash of its sibling
        if len(route_to_digest) < self.depth:
            proof.append(route_to_digest[-1].key)

        # create the rest of the proof
        for i in range(len(route_to_digest) - 2, -1, -1):
            # if the left son is on the path to digest, add the other sibling to the proof
            if route_to_digest[i].left_son is route_to_digest[i + 1]:
                proof.append(route_to_digest[i].right_son.key)
            else:
                proof.append(route_to_digest[i].left_son.key)

        # return proof
        return root_sign, proof

    def check_proof_of_inclusion(self, digest, classification_bit, proof):
        # adding the direction bit to each key
        first_key = proof.pop(0)
        regular_proof = [bit + key for bit, key in zip(digest, proof)]
        regular_proof.insert(0, first_key)
        return self.root.check_proof_of_inclusion(classification_bit, regular_proof)
