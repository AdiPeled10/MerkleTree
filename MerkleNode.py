from BinaryTree import BinaryNode
from hashlib import sha256


def hash_function(s):
    s = str(s)
    hash_string = sha256(s.encode()).hexdigest()
    return hash_string


class MerkleBinaryNode(BinaryNode):
    def __init__(self, left_son, right_son, value=None):
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
        leaf = MerkleBinaryNode(None, None, '')
        leaf.data = value
        return leaf

    def node_diffusion(self):
        if self.left is not None:  # possible only if both sons are not None
            self.data = hash_function(self.left.data + self.right.data)
        if self.parent is not None:
            self.parent.node_diffusion()

    def get_prefix_of_brother(self):
        if self.parent.left is self:
            return "1"
        return "0"

    def get_brother_data(self):
        brother = self.parent.left
        if brother is self:
            brother = self.parent.right
        return str(brother.data)

