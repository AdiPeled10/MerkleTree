# Adi Peled, 318814308, Itamar Fisch, 312502602
import math
import base64
from hashlib import sha256


class Node :
    def __init__(self, data) :
        self.left = None
        self.right = None
        self.parent = None
        self.data = hash_function(data)

    def inorder_print(self):
        if self is not None:
            print(self.data)
            if self.left is not None:
                self.left.inorder_print()
                self.right.inorder_print()

def left_binding(parent, child):
    parent.left = child
    child.parent = parent


class BinaryMerkleTree :
    def __init__(self) :
        self.root = None
        self.leaves = []

    def add_leaf(self, node):
        self.leaves.append(node)
        if len(self.leaves) == 1:
            self.root = node
            return 1

        temp = Node(0)
        right = self.leaves[len(self.leaves) - 1]

        # replace root
        if math.log(len(self.leaves) - 1, 2).is_integer():
            self.triangle_binding(temp, self.root, right)
            self.root = temp
        elif len(self.leaves) % 2 == 0:
            left = self.leaves[len(self.leaves) - 2]
            grandpa = left.parent
            self.triangle_binding(temp, left, right)
            self.right_binding(grandpa, temp)
        else:
            left = self.root.right
            self.triangle_binding(temp, left, right)
            self.right_binding(self.root, temp)
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


def proof_of_inclusion(m_tree, node_number):
    proof = str(m_tree.root.data)
    node = m_tree.leaves[node_number]
    while node.data != m_tree.root.data:
        proof += " " + get_prefix(node) + get_brother(node)
        node = node.parent
    return proof


def get_brother(node):
    left_data = node.parent.left.data
    right_data = node.parent.right.data
    if left_data == node.data:
        return str(right_data)
    return str(left_data)


def get_prefix(node):
    if node.parent.left.data == node.data:
        return "0"
    return "1"


def case1(m_tree, user_input):
    data = user_input[2:]
    node = Node(data)
    m_tree.add_leaf(node)


def case2(m_tree):
    print(m_tree.root.data)


def case3(m_tree, node_number):
    print(proof_of_inclusion(m_tree, node_number))


def case4(m_tree, arg):
    temp = arg[1]
    root = arg[2]
    for index in range(3, len(arg)-1):
        if arg[index][0] == '0':
            temp = hash_function(arg[index][1:]+temp)
            print("-0-")
        else:
            temp = hash_function(temp+arg[index][1:])
            print("-1-")
    print(temp)
    print(root)
    if temp == root:
        print("True")
        return
    print("False")


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

node = Node("a")
merkle_tree.add_leaf(node)
node = Node("b")
merkle_tree.add_leaf(node)
node = Node("c")
merkle_tree.add_leaf(node)
node = Node("d")
merkle_tree.add_leaf(node)

case2(merkle_tree)

while True:
    user_input = input()
    args = user_input.split()
    if args[0] == '1':
        case1(merkle_tree, user_input)
    elif args[0] == '2':
        case2(merkle_tree)
    elif args[0] == '3':
        case3(merkle_tree, int(args[1]))
    elif args[0] == '4':
        case4(merkle_tree, args)