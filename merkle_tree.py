# Adi Peled, 318814308, Itamar Fisch, 312502602
from MerkleNode import MerkleBinaryNode, hash_function
import RSAsignature
from SparseMerkleTree import SparseMerkleTree


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

    def proof_of_inclusion(self, node_number):
        proof = str(self.root.data)
        node = self.leaves[node_number]
        while node.data != self.root.data:
            proof += " " + node.get_prefix_of_brother() + node.get_brother_data()
            node = node.parent
        return proof

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


def case1(m_tree, u_input):
    data = u_input[2:]
    node = MerkleBinaryNode(None, None, data)
    m_tree.add_leaf(node)


def case2(m_tree):
    print(m_tree.get_root_key())


def case3(m_tree, node_number):
    print(m_tree.proof_of_inclusion(node_number))


def case4(user_input):
    arg = user_input.split(' ')
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


sparse_merkle_tree = SparseMerkleTree(256)
merkle_tree = BinaryMerkleTree()
sign_algo = RSAsignature.RSAsignature
while True:
    user_input = input()
# for i in range(20):
#     user_input = '1 ' + chr(ord('a') + i)
    option_len = user_input.find(' ')
    if option_len == -1:
        option_len = len(user_input)
    option = user_input[:option_len]
    if option == '1':
        case1(merkle_tree, user_input)
    elif option == '2':
        case2(merkle_tree)
    elif option == '3':
        leaf_num = int(user_input[2:])
        case3(merkle_tree, leaf_num)
    elif option == '4':
        case4(user_input)
    elif option == '5':
        sk, vk = sign_algo.generate()
        print(sk)
        print(vk)
    elif option == '6':
        private_key = user_input[2:]
        private_key = read_key_from_user(private_key)
        sign_root(merkle_tree, sign_algo, private_key)
    elif option == '7':
        pub_key = user_input[2:]
        pub_key = read_key_from_user(pub_key)
        verify_sign(sign_algo, pub_key)
    elif option == '8':
        digest = user_input[2:]
        sparse_merkle_tree.mark_leaf(digest)
    elif option == '9':
        print(sparse_merkle_tree.get_root_key())
    elif option == '10':
        digest = user_input[3:]
        root_key, proof = sparse_merkle_tree.generate_proof_of_inclusion(digest)
        print(root_key, end=' ')
        for key in proof:
            print(key, end=' ')
        print()
    elif option == '11':
        arg1_end = user_input.find(' ', option_len + 1)
        arg2_end = arg1_end + 2  # +1 to skip space and another +1 for the len of the classification bit
        digest = user_input[option_len + 1:arg1_end]
        classification_bit = user_input[arg1_end + 1: arg2_end]
        proof = user_input[arg2_end + 1:].split(' ')
        sparse_merkle_tree.check_proof_of_inclusion(digest, classification_bit, proof)





