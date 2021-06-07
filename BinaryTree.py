class BinaryNode:
    LEFT_DIRECTION = 0
    RIGHT_DIRECTION = 1

    def __init__(self, value):
        self.key = value
        self.left_son = None
        self.right_son = None

    def make_son(self, node, direction):
        if direction == BinaryNode.LEFT_DIRECTION:
            self.left_son = node
        elif direction == BinaryNode.RIGHT_DIRECTION:
            self.right_son = node

    def _make_sons(self, lnode, rnode):
        self.left_son = lnode
        self.right_son = rnode

    def get_son(self, direction):
        node = None
        if direction == BinaryNode.LEFT_DIRECTION:
            node = self.left_son
        elif direction == BinaryNode.RIGHT_DIRECTION:
            node = self.right_son
        return node

