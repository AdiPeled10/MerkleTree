from hashlib import sha256
from BinaryTree import BinaryNode
from MerkleNode import hash_function, MerkleBinaryNode


def print_error(msg):
    # TODO before submit make sure to replace the code with "print('')"
    # This function will help us make all the prints disappear before submit
    print(msg)


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

