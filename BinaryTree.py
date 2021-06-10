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
        if self.left is not None and self.left.parent is self:  # if I'm the main father of the current left son
            self.left.parent = None  # delete pointer
        self.left = child
        if self.left is not None:
            self.height = self.left.height + 1
        else:
            self.height = 0
        child.parent = self

    def right_binding(self, child):
        if self.right is not None and self.right.parent is self:  # if I'm the main father of the current right son
            self.right.parent = None  # delete pointer
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