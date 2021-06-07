# Adi Peled, 318814308, Itamar Fisch, 312502602
import math
import base64
from hashlib import sha256


class Node:
    def __init__(self, data):
        self.left = None
        self.right = None
        self.parent = None
        self.height = 0
        self.data = data

    def left_binding(self, child):
        self.left = child
        self.height = self.left.height + 1
        child.parent = self

    def right_binding(self, child):
        self.right = child
        child.parent = self

    def triangle_binding(self, left, right):
        self.left_binding(left)
        self.right_binding(right)

    def inorder_print(self):
        if self is not None:
            print(self.data)
            if self.left is not None:
                self.left.inorder_print()
                self.right.inorder_print()


class MerkleNode(Node):
    def __init__(self, left_son, right_son):
        data = left_son.data + right_son.data
        super().__init__(hash_function(data))
        self.triangle_binding(left_son, right_son)

    @staticmethod
    def create_leaf(value, to_hash=True):
        leaf = MerkleNode(None, None)
        if to_hash:
            leaf.data = hash_function(value)
        else:
            leaf.data = value
        return leaf

    def node_diffusion(self):
        if self.left is not None:  # possible only if both sons are not None
            self.data = hash_function(self.left.data + self.right.data)
        if self.parent is not None:
            self.parent.node_diffusion()


class BinaryMerkleTree:
    def __init__(self) :
        self.root = None
        self.leaves = []

    def add_leaf(self, node: MerkleNode):
        self.leaves.append(node)
        if len(self.leaves) == 1:
            self.root = node
            return 1
        inserted_node_parent = MerkleNode.create_leaf(0, False)

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


def hash_function(s):
    s = str(s)
    hash_string = sha256(s.encode()).hexdigest()
    return hash_string


def case1(merkle_tree, user_input):
    data = user_input[2:]
    node = MerkleNode.create_leaf(data)
    merkle_tree.add_leaf(node)


def case2(merkle_tree):
    print(merkle_tree.root.data)


merkle_tree = BinaryMerkleTree()
while(True):
    user_input = input()
    args = user_input.split()
    if args[0] == '1':
        case1(merkle_tree, user_input)
    elif args[0] == '2':
        case2(merkle_tree)
