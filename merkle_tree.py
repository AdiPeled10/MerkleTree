# Adi Peled, 318814308, Itamar Fisch, 312502602
import math
import base64
from MekleNode import MerkleBinaryNode


class BinaryMerkleTree:
    def __init__(self):
        self.root = None
        self.leaves = []

    def get_root_key(self):
        if self.root is None:
            return ''
        return self.root.data

    def add_leaf(self, node: MerkleBinaryNode):
        self.leaves.append(node)
        if len(self.leaves) == 1:
            self.root = node
            return 1
        inserted_node_parent = MerkleBinaryNode(None, None, 0)

        # check if current tree is complete
        if is_power_of_2(len(self.leaves) - 1):
            inserted_node_parent.triangle_binding(self.root, node)
            self.root = inserted_node_parent
        else:
            # find first node with incomplete right subtree
            curr_node = self.leaves[-2]  # the previous last leaf
            while curr_node.parent.height == curr_node.height + 1:
                curr_node = curr_node.parent

            # Add the node to the tree
            curr_node.parent.right_binding(inserted_node_parent)
            inserted_node_parent.triangle_binding(curr_node, node)

        # updating all keys in the path to the new node
        inserted_node_parent.node_diffusion()

    def inorder_traversal(self):
        self.root.inorder_print()


def print_error(msg) :
    # TODO before submit make sure to replace the code with "print('')"
    # This function will help us make all the prints disappear before submit
    print(msg)


def is_power_of_2(n: int):
    if n == 0:
        return False
    n_minus_one = n - 1
    return (n & n_minus_one) == 0


def case1(merkle_tree, user_input):
    data = user_input[2:]
    node = MerkleBinaryNode(None, None, data)
    merkle_tree.add_leaf(node)


def case2(merkle_tree):
    print(merkle_tree.get_root_key())


merkle_tree = BinaryMerkleTree()
while True:
    user_input = input()
# for i in range(20):
#     user_input = '1 ' + chr(ord('a') + i)
    args = user_input.split()
    if args[0] == '1':
        case1(merkle_tree, user_input)
    elif args[0] == '2':
        case2(merkle_tree)
# merkle_tree.inorder_traversal()

