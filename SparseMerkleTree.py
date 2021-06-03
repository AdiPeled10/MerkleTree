from hashlib import sha256
from BinaryTree import BinaryNode
from copy import deepcopy


def print_error(msg):
    # TODO before submit make sure to replace the code with "print('')"
    # This function will help us make all the prints disappear before submit
    print(msg)


class MerkleNode(BinaryNode):
    def __init__(self, value, lson=None, rson=None):
        pass
    def compute_key(self):
        pass


class SparseMerkleTree:
    def __init__(self, depth: int):
        # for 2**256 leaves we need depth of 256
        self.depth = depth
        curr = MerkleNode(0)
        while depth > 0:
            depth -= 1
            curr_parent = BinaryNode(0, curr, curr)
            curr = curr_parent
        self.root = curr

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
        leaf_number = int(digest, 2)
        regular_proof = self.root.generate_proof_of_inclusion(leaf_number)
        # removing the direction bit
        first_key = regular_proof.pop(0)
        proof = [key[1:] for key in regular_proof]
        proof.insert(0, first_key)
        return proof

    def check_proof_of_inclusion(self, digest, classification_bit, proof):
        # adding the direction bit to each key
        first_key = proof.pop(0)
        regular_proof = [bit + key for bit, key in zip(digest, proof)]
        regular_proof.insert(0, first_key)
        return self.root.check_proof_of_inclusion(classification_bit, regular_proof)
