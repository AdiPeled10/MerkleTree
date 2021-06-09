# Adi Peled, 318814308, Itamar Fisch, 312502602
import math
import base64
from MerkleNode import MerkleBinaryNode
import RSAsignature


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


def read_key_from_user(prefix=''):
    line = input()
    key = [prefix]
    while line != '':
        key.append(line)
        line = input()
    return '\n'.join(key)


def sign_root(merkle_tree, sign_algo, private_key):
    sk_bytes = private_key.encode('ASCII')
    data = merkle_tree.get_root_key().encode('ASCII')
    sign = sign_algo.sign(data, sk_bytes)
    print(sign)


def verify_sign(sign_algo, pub_key):
    user_input = input()
    sign_len = user_input.find(' ')
    sign = user_input[:sign_len]
    signed_text = user_input[sign_len + 1:].encode('ASCII')
    print(sign_algo.verify(signed_text, pub_key, sign))


merkle_tree = BinaryMerkleTree()
sign_algo = RSAsignature.RSAsignature
while True:
    user_input = input()
# for i in range(20):
#     user_input = '1 ' + chr(ord('a') + i)
    option = user_input[0]
    if option == '1':
        case1(merkle_tree, user_input)
    elif option == '2':
        case2(merkle_tree)
    elif option == '5':
        sk, vk = sign_algo.generate()
        print(sk)
        print(vk)
    elif option == '6':
        private_key = user_input[2:]
        private_key = read_key_from_user(private_key)
        sign_root(merkle_tree, sign_algo, private_key)
    elif user_input[0] == '7':
        pub_key = user_input[2:]
        pub_key = read_key_from_user(pub_key)
        verify_sign(sign_algo, pub_key)

# merkle_tree.inorder_traversal()

