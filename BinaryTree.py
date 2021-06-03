class BinaryTree:
    LEFT_DIRECTION = 0
    RIGHT_DIRECTION = 1

    def __init__(self, value):
        self._key = value
        self._left_son = None
        self._right_son = None

    def make_son(self, node, direction):
        if direction == BinaryTree.LEFT_DIRECTION:
            self._left_son = node
        elif direction == BinaryTree.RIGHT_DIRECTION:
            self._right_son = node

    def get_son(self, direction):
        node = None
        if direction == BinaryTree.LEFT_DIRECTION:
            node = self._left_son
        elif direction == BinaryTree.RIGHT_DIRECTION:
            node = self._right_son
        return node

