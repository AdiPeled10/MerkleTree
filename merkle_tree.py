# Adi Peled, 318814308, Itamar Fisch, 312502602
import math
import base64

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from MerkleNode import MerkleBinaryNode, hash_function
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509


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


def proof_of_inclusion(m_tree, node_number):
    proof = str(m_tree.root.data)
    node = m_tree.leaves[node_number]
    while node.data != m_tree.root.data:
        proof += " " + get_prefix_of_brother(node) + get_brother(node)
        node = node.parent
    return proof


def get_prefix_of_brother(node):
    if node.parent.left.data == node.data:
        return "1"
    return "0"


def get_brother(node):
    if node.parent.left.data == node.data:
        return str(node.parent.right.data)
    return str(node.parent.left.data)


def is_power_of_2(n: int):
    if n == 0:
        return False
    n_minus_one = n - 1
    return (n & n_minus_one) == 0


def case1(m_tree, u_input):
    data = u_input[2:]
    node = MerkleBinaryNode(None, None, data)
    m_tree.add_leaf(node)


def case2(m_tree):
    print(m_tree.get_root_key())


def case3(m_tree, node_number):
    print(proof_of_inclusion(m_tree, node_number))


def case4(arg):
    temp = arg[1]
    root = arg[2]
    for index in range(3, len(arg)):
        if arg[index][0] == '0':
            temp = hash_function(arg[index][1:]+temp)
        else:
            temp = hash_function(temp+arg[index][1:])
    if temp == root:
        print("True")
        return
    print("False")


def case5():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()

    pem_private_key = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                encryption_algorithm=serialization.NoEncryption())\
        .decode("utf-8")
    pem_public_key = private_key.public_key().public_bytes(serialization.Encoding.PEM,
                                                           serialization.PublicFormat.SubjectPublicKeyInfo)\
        .decode("utf-8")
    print(pem_private_key)
    print(pem_public_key)


def case6(message, key):
    private_key_bytes = key.encode("ascii")
    private_key = load_pem_public_key(private_key_bytes)
    signature = private_key.sign(message,
                                 padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                             salt_length=padding.PSS.MAX_LENGTH),
                                 hashes.SHA256())
    print(signature)
    return signature


def case7():
    pass


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
    elif args[0] == '3':
        case3(merkle_tree, int(args[1]))
    elif args[0] == '4':
        case4(args)
    elif args[0] == '5':
        case5()
    elif args[0] == '6':
        case6(merkle_tree.root.data, user_input[2:])
    elif args[0] == '7':
        case7(args)

# merkle_tree.inorder_traversal()