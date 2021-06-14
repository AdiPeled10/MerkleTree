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
    :param s: string to be hashed
    :return: hash value
    """
    s = str(s)
    hash_string = sha256(s.encode()).hexdigest()
    return hash_string


class MerkleBinaryNode(BinaryNode):
    def __init__(self, left_son, right_son, value=None):
        """
        initiate a merkle binary node.
        value can be given or be calculated by both sons but not both.
        both sons need to be not-None or None.

        :param left_son: a MerkleBinaryNode or None
        :param right_son: a MerkleBinaryNode or None
        :param value: None or string.
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
        :param value: the value to be saved at the leaf.
        :return: a MerkleBinaryNode. binary merkle leaf with non hashed value
        """
        leaf = MerkleBinaryNode(None, None, '')
        leaf.data = value
        return leaf

    def node_diffusion(self):
        """
        Adding/updating a leaf requires updating the values up the tree
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
        :return: data of the node brother (another node with same parent)
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
        Adds a leaf to the tree.
        :param node: a MerkleBinaryNode.
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
        Generate a proof that the i-th leaf is in the tree.
        :param node_number: the i from the above sentence.
        :return: a string that is proof of correctness of information.
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
    calculate if n is a power of 2 with O(1) complexity.
    :param n: an integer.
    :return: true if n is a power of 2, false otherwise
    """
    if n == 0:
        return False
    n_minus_one = n - 1
    # only for a power of 2 all the bits will change.
    return (n & n_minus_one) == 0


class SparseBinaryNode:
    """
    A binary tree node that also holds the number of nodes "self" is one of its son and holds
    a flag that says whether or not "self" represent a whole binary tree.
    """
    LEFT_DIRECTION = 0
    RIGHT_DIRECTION = 1

    def __init__(self, left_son, right_son, value):
        self.count_single_refs = 0
        self.is_sub_segment = False
        if left_son is not None:
            if left_son is right_son:
                # if I'm both of the sons of my parent, than I mask a whole tree.
                left_son.is_sub_segment = True
            else:
                left_son.count_single_refs += 1
                right_son.count_single_refs += 1
        self.data = value
        self.left = left_son
        self.right = right_son

    def get_son(self, direction):
        """
        :param direction:
        :return: letf/right son, according to direction
        """
        node = None
        if direction == SparseBinaryNode.LEFT_DIRECTION:
            node = self.left
        elif direction == SparseBinaryNode.RIGHT_DIRECTION:
            node = self.right
        return node


class SparseMerkleDB:
    """
    This class is responsible for space-efficient managing of the used SparseBinaryNode.
    """
    def __init__(self, depth):
        """
        Creates a new DB of SparseBinaryNode. Initialized only with leaf '0' and leaf '1'.
        :param depth:
        """
        # create level dictionaries - used in every level except root level
        usage_dicts = []
        while depth >= 0:
            depth -= 1
            usage_dicts.append({})
        self.usage_dicts = usage_dicts

        # create basic leaves
        self.usage_dicts[0]['0'] = SparseBinaryNode(None, None, '0')
        self.usage_dicts[0]['1'] = SparseBinaryNode(None, None, '1')

    def create_node(self, height, left_son, right_son):
        """
        Creates a new node SparseBinaryNode with its value as the hash of left_son.data + right_son.data,
        Or gives you a created SparseBinaryNode with the same hash.
        :param height: the height of the created node.
        :param left_son: the left son for the node.
        :param right_son: the right son for the node.
        :return: The created/cached node.
        """
        hash_table = self.usage_dicts[height]
        value = hash_function(left_son.data + right_son.data)
        if value in hash_table:
            response = hash_table[value]
        else:
            response = SparseBinaryNode(left_son, right_son, value)
            hash_table[value] = response
        return response

    def delete_node(self, height, node: SparseBinaryNode):
        """
        Checks if the given node is still in use by other node, if so it just updates the node ref counts.
        If not, it deleted it from the cache and the garbage collector can free its memory.
        :param height: the height of the to be deleted node.
        :param node: the node to be deleted.
        :return: False/True - whether or not the node was deleted.
        """
        if not node.is_sub_segment and node.count_single_refs <= 0:
            if node.left is node.right:
                node.left.is_sub_segment = False
            else:
                node.left.count_single_refs -= 1
                node.right.count_single_refs -= 1
            self.usage_dicts[height].pop(node.data)
            return True
        return False

    def get_leaf(self, value):
        """
        :param value: the leaf value.
        :return: A cached leaf with the gives value.
        """
        return self.usage_dicts[0][value]


class SparseMerkleTree:
    """
    This class emulates a complete merkle tre with 2**depth indicator leaves (0 or 1).
    The class make a smart use of the fact bit-patterns reoccur and each hash is unique. It is done by the following
    logic:
        1. The tree is initialize as linked list -
                Because all leaves are the same, all the hashes in the same height have the same value, this allows me
                to save just 1 node per height (depth+1 nodes).
        2. level-hash-tables -
                A level k in a tree is all the nodes of the tree with height k.
                For each level there is a hash table from data to the first node that needed it and still in the tree.
                This allows a great reuse of subtrees (very effective for at least heights 0 to 7 even with random
                inputs), and because the leaves can only change from 0 to 1, it will start shrinking the memory usage
                after enough leaves were marked.
        3. When marking a leaf, recreate a copy of the route from the root to the leaf because nodes are immutable -
                This promise us that if some other node points to a node in the original route (possible due to
                segmentation), the update will not corrupt its data.
                When a route is no longer needed by any node, the garbage collector will notice no active member is
                pointing to the route and it will release its memory.
    """
    def __init__(self, depth: int):
        """
        Creates a full sparse tree with given depth (which means, 2**depth leaves), each leaf is initial with '0'.
        :param depth: The wanted size of the sparse merkle tree.
        """
        # for 2**256 leaves we need depth of 256
        self.depth = depth
        # create level dictionaries - used in every level except root level
        self.db = SparseMerkleDB(depth)
        # create tree
        curr = self.db.get_leaf('0')
        curr_height = 1
        while depth > 0:
            depth -= 1
            curr_parent = self.db.create_node(curr_height, curr, curr)
            curr_height += 1
            curr = curr_parent
        self.root = curr

    def _get_route_to_leaf(self, digest):
        """
        :param digest: a hex string representing the leaf number.
        :return: a list with all the nodes visited on the way from the root to the leaf.
        """
        route = []
        mask = 1 << (self.depth - 1)
        # the digest bits represents the left & right turns to be done on the way from the root to the leaf.
        path_int = int(digest, 16)
        next_node = self.root
        while next_node is not None:
            route.append(next_node)
            # direction is 1 if and only if the next direction bit is 1
            direction = (path_int & mask) != 0
            mask = mask >> 1
            next_node = next_node.get_son(direction)
        return route

    def mark_leaf(self, digest):
        """
        Changes the value of the leaf represented by digest to "1".
        :param digest: a hex string representing the leaf number.
        """
        SparseMerkleTree.mark_leaf.bit_to_int_offset = ord('0')

        # create the path to the digest leaf
        path_to_digest = self._get_route_to_leaf(digest)

        # update the digest leaf
        old_path_to_digest = path_to_digest[:]
        path_to_digest[-1] = self.db.get_leaf('1')

        # update the path to the digest leaf
        # this also update the keys from the marked node towards the root
        path_int = int(digest, 16)
        curr_height = 1
        for i in range(len(path_to_digest) - 2, -1, -1):  # go through the path in reverse order (including the root)
            # create a new copy of the current node with updated son
            if path_int & 1 == SparseBinaryNode.RIGHT_DIRECTION:
                path_to_digest[i] = self.db.create_node(curr_height, path_to_digest[i].left, path_to_digest[i + 1])
            else:
                path_to_digest[i] = self.db.create_node(curr_height, path_to_digest[i + 1], path_to_digest[i].right)
            path_int = path_int >> 1
            curr_height += 1

        # delete nodes
        curr_height = self.depth
        while self.db.delete_node(curr_height, old_path_to_digest.pop(0)):
            curr_height -= 1

        # update the root
        self.root = path_to_digest[0]

    def get_root_key(self):
        """
        :return: the value of the root.
        """
        return self.root.data

    def generate_proof_of_inclusion(self, digest):
        """
        Generate a proof that the i-th leaf is in the tree.
        If the k first hashes of the proof can be computed be doing k+1 times the following:
            value = hash_function(value + value)         stating with value equal to the leaf value.
        Then the first k hashes will not be in the proof, instead the proof will began with the k-th hash.

        exception:
        if k=1 (only the hash of 2 leaves can be self-calculated) then it will still use a full proof. That is
        because the leaf value is shorter than the parent value and using the above "shortcut" will actually
        make the proof longer.

        :param digest: a hex string representing the leaf number.
        :return: a list that proves the correctness of information.
        """
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
        """
        Checks if the proof of inclusion is true for a sparse tree with "classification_bit" value at the digest
        leaf.
        :param digest: a hex string representing the leaf number.
        :param classification_bit: "0" or "1" the claim on the leaf value.
        :param proof: a list that proves the correctness of information. this must be created using a
                        SparseMerkleTree object.
        :return: True/False - did the proof holds for te claim.
        """
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
            if path_int & 1 == SparseBinaryNode.RIGHT_DIRECTION:
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
        generates a new public and private RSA keys with key_size bits per key.
        :param key_size: the bits in the key.
        :return: private and public keys at PEM format.
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
        :param data: data to be signed.
        :param pem_private_key: PEM of an RSA private key to be used for the signature.
        :return: the signature of the data as a base64 string.
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
        :param pem_public_key: a RSA public key in a PEM format.
        :param signature: The RSA signutre of the data as a base64 string.
        :return: True/False - whether or not the signature of the data is correct.
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
    """
    Checks proof of correctness for a regular BinaryMerkleTree
    :param user_input: the proof given by the user with the option prefix.
    :return: prints True/False - whether or not the proof is correct.
    """
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
    """
    Reads a PEM RSA key from the user.
    :param prefix: string to be concat in-front of the key.
    :return: the key as PEM string.
    """
    line = input()
    key = [prefix]
    while line != '':
        key.append(line)
        line = input()
    return '\n'.join(key)


def sign_root(merkle_tree, sign_algo, private_key):
    """
    prints a signature of the merkle root value.
    :param merkle_tree:
    :param sign_algo: an object with a "sign" method that gets bytes to sign and bytes for key.
    :param private_key: ASCII string of the key.
    """
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
# loop for parsing the input and calling the right procedure.
while True:
    user_input = input()
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