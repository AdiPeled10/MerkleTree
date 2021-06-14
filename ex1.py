# Adi Peled, 318814308, Itamar Fisch, 312502602
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64



class BinaryNode:
    LEFT_DIRECTION = 0
    RIGHT_DIRECTION = 1

    def __init__(self, data):
        self.left = None
        self.right = None
        self.parent = None
        self.height = 0
        self.data = data

    def get_son(self, direction):
        """
        :param direction:
        :return: letf/right son, according to direction
        """
        node = None
        if direction == BinaryNode.LEFT_DIRECTION:
            node = self.left
        elif direction == BinaryNode.RIGHT_DIRECTION:
            node = self.right
        return node

    def left_binding(self, child):
        """
        bind left child and parent
        :param child:
        :return:
        """
        if self.left is not None and self.left.parent is self:  # if I'm the main father of the current left son
            self.left.parent = None  # delete pointer
        self.left = child
        if self.left is not None:
            self.height = self.left.height + 1
        else:
            self.height = 0
        child.parent = self

    def right_binding(self, child):
        """
        bind right child and parent
        :param child:
        :return:
        """
        if self.right is not None and self.right.parent is self:  # if I'm the main father of the current right son
            self.right.parent = None  # delete pointer
        self.right = child
        child.parent = self

    def triangle_binding(self, left, right):
        """
        bind parent with two sons
        :param left:
        :param right:
        :return:
        """
        self.left_binding(left)
        self.right_binding(right)

    def inorder_print(self):
        """
        help method.
        :return:
        """
        if self is not None:
            print(self.height * ' ' + self.data)
            if self.left is not None:
                self.left.inorder_print()
                self.right.inorder_print()


def hash_function(s):
    """

    :param s:
    :return: hash value
    """
    s = str(s)
    hash_string = sha256(s.encode()).hexdigest()
    return hash_string


class MerkleBinaryNode(BinaryNode):
    def __init__(self, left_son, right_son, value=None):
        """
        initiate a merkle binary node
        :param left_son:
        :param right_son:
        :param value:
        """
        if ((left_son is None or right_son is None) and value is None) or \
             (left_son is not None and right_son is not None and value is not None):
            raise ValueError("Bad parameters! parameters should be 2 MerkleNodes or a non-None value, but never both.")
        if value is None:
            data = left_son.data + right_son.data
            super().__init__(hash_function(data))
            self.triangle_binding(left_son, right_son)
        else:
            super().__init__(hash_function(value))

    @staticmethod
    def create_non_hash_leaf(value):
        """

        :param value:
        :return: binary merkle leaf with non hashed value
        """
        leaf = MerkleBinaryNode(None, None, '')
        leaf.data = value
        return leaf

    def node_diffusion(self):
        """
        Adding a leaf requires updating the values up the tree
        :return:
        """
        if self.left is not None:  # possible only if both sons are not None
            self.data = hash_function(self.left.data + self.right.data)
        if self.parent is not None:
            self.parent.node_diffusion()

    def get_prefix_of_brother(self):
        if self.parent.left is self:
            return "1"
        return "0"

    def get_brother_data(self):
        """

        :return: date of the node brother (another node with same parent)
        """
        brother = self.parent.left
        if brother is self:
            brother = self.parent.right
        return str(brother.data)


class BinaryMerkleTree:
    def __init__(self):
        self.root = None
        self.leaves = []

    def get_root_key(self):
        """
        :return: value of the tree's root
        """
        if self.root is None:
            return ''
        return self.root.data

    def add_leaf(self, node: MerkleBinaryNode):
        """

        :param node:
        :return:
        """
        # add to the leaves array
        self.leaves.append(node)
        # first node check:
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
        """

        :param node_number:
        :return: a string that is proof of correctness of information
        """
        proof = str(self.root.data)
        node = self.leaves[node_number]
        while node.data != self.root.data:
            proof += " " + node.get_prefix_of_brother() + node.get_brother_data()
            node = node.parent
        return proof

    def inorder_traversal(self):
        self.root.inorder_print()


def is_power_of_2(n: int):
    """
    calculate if n is a power of 2 with O(1) complexity
    :param n:
    :return: true if n is a power of 2, false otherwise
    """
    if n == 0:
        return False
    n_minus_one = n - 1
    return (n & n_minus_one) == 0


class SparseMerkleTree:
    def __init__(self, depth: int):
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


class RSAsignature:
    _PUBLIC_KEY = 65537

    @staticmethod
    def generate(key_size=2048):
        """

        :param key_size:
        :return: private and public keys
        """
        private_key = rsa.generate_private_key(public_exponent=RSAsignature._PUBLIC_KEY,
                                               key_size=key_size, backend=default_backend())
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem.decode('utf-8'), public_pem.decode('utf-8')

    @staticmethod
    def sign(data: bytes, pem_private_key):
        """

        :param data:
        :param pem_private_key:
        :return: sing of the key over the data
        """
        private_key = serialization.load_pem_private_key(pem_private_key, None, default_backend())

        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('ASCII')

    @staticmethod
    def verify(data: bytes, pem_public_key, signature):
        """

        :param data:
        :param pem_public_key:
        :param signature:
        :return: verify the sign is correct
        """
        # encoding params
        pem_public_key = pem_public_key.encode('utf-8')
        signature = base64.b64decode(signature)

        # reading public key
        public_key = serialization.load_pem_public_key(pem_public_key, default_backend())

        # verifying
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            sign_matched = True
        except InvalidSignature:
            sign_matched = False
        return sign_matched


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
    curr_hash = hash_function(arg[1])
    root = arg[2]
    # loop over the chunks of the string, verify the last hash value identify to the root
    for index in range(3, len(arg)):
        if arg[index][0] == '0':
            curr_hash = hash_function(arg[index][1:] + curr_hash)
        else:
            curr_hash = hash_function(curr_hash + arg[index][1:])
    if curr_hash == root:
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
sign_algo = RSAsignature
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
        proof = sparse_merkle_tree.generate_proof_of_inclusion(digest)
        last = proof.pop()
        for key in proof:
            print(key, end=' ')
        print(last)
    elif option == '11':
        arg1_end = user_input.find(' ', option_len + 1)
        arg2_end = arg1_end + 2  # +1 to skip space and another +1 for the len of the classification bit
        digest = user_input[option_len + 1:arg1_end]
        classification_bit = user_input[arg1_end + 1: arg2_end]
        proof = user_input[arg2_end + 1:].split(' ')
        result = sparse_merkle_tree.check_proof_of_inclusion(digest, classification_bit, proof)
        print(result)



