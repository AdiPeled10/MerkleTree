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
        node = None
        if direction == BinaryNode.LEFT_DIRECTION:
            node = self.left
        elif direction == BinaryNode.RIGHT_DIRECTION:
            node = self.right
        return node

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
            print(self.height * ' ' + self.data)
            if self.left is not None:
                self.left.inorder_print()
                self.right.inorder_print()