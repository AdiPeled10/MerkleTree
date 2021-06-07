# Adi Peled, 318814308, Itamar Fisch, 312502602
import math
import base64
from hashlib import sha256


class Node :
    def __init__(self, data) :
        self.left = None
        self.right = None
        self.parent = None
        self.height = 0
        self.data = hash_function(data)

    def inorder_print(self):
        if self is not None:
            print(self.data)
            if self.left is not None:
                self.left.inorder_print()
                self.right.inorder_print()

class MerkleNode(Node):
    def __init__(self, left_son, right_son):
        pass
    @staticmethod
    def create_leaf(value):
        pass


def left_binding(parent, child):
    parent.left = child
    parent.height = parent.left.height + 1
    child.parent = parent


def is_power_of_2(n: int):
    if n == 0:
        return False
    n_minus_one = n - 1
    return (n & n_minus_one) == 0


class BinaryMerkleTree :
    def __init__(self) :
        self.root = None
        self.leaves = []

    def add_leaf(self, node):
        self.leaves.append(node)
        if len(self.leaves) == 1:
            self.root = node
            return 1
        inserted_node_parent = Node(0)

        # check if current tree is complete
        if is_power_of_2(len(self.leaves) - 1):
            self.triangle_binding(inserted_node_parent, self.root, node)
            self.root = inserted_node_parent
        else:
            # find first node with incomplete right subtree
            curr_node = self.leaves[-2]  # the previous last leaf
            while curr_node.parent.height == curr_node.height + 1:
                curr_node = curr_node.parent

            # Add the node to the tree
            self.right_binding(curr_node.parent, inserted_node_parent)
            self.triangle_binding(inserted_node_parent, curr_node, node)

        # updating all keys in the path to the new node
        self.node_diffusion(node.parent)

    def node_diffusion(self, node):
        if node is not None:
            self.node_hash_calculator(node)
            self.node_diffusion(node.parent)

    def right_binding(self, parent, child):
        parent.right = child
        child.parent = parent

    def triangle_binding(self, parent, left, right):
        left_binding(parent, left)
        self.right_binding(parent, right)

    def node_hash_calculator(self, parent):
        data1 = parent.left.data
        data2 = parent.right.data
        parent.data = hash_function(data1+data2)

    def inorder_traversal(self):
        self.root.inorder_print()


def print_error(msg) :
    # TODO before submit make sure to replace the code with "print('')"
    # This function will help us make all the prints disappear before submit
    print(msg)


def hash_function(s):
    s = str(s)
    hash_string = sha256(s.encode()).hexdigest()
    return hash_string


def case1(merkle_tree, user_input):
    data = user_input[2:]
    node = Node(data)
    merkle_tree.add_leaf(node)


def case2(merkle_tree):
    print(merkle_tree.root.data)


# This function is wrong! Listen to your recording with the improvements
# def calculate_max_needed_values_for_sparse_tree():
#     num_hashes_in_tree_level = [0] * 257
#     nodes_in_level = 2 ** 256
#     num_possible_values_in_level = 2
#     for i in range(-1, -len(num_hashes_in_tree_level) - 1, -1):
#         if num_possible_values_in_level < nodes_in_level:
#             num_hashes_in_tree_level[i] = num_possible_values_in_level
#             num_possible_values_in_level *= num_possible_values_in_level
#         else:
#             num_hashes_in_tree_level[i] = nodes_in_level
#         nodes_in_level >>= 1
#     return num_hashes_in_tree_level


# for x in range(8):
#     node = Node(x)
#     merkle_tree.add_leaf(node)
#
# merkle_tree.inorder_traversal()


merkle_tree = BinaryMerkleTree()
while(True):
    user_input = input()
    args = user_input.split()
    if args[0] == '1':
        case1(merkle_tree, user_input)
    elif args[0] == '2':
        case2(merkle_tree)
