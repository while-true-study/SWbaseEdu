class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
            return

        current = self.root

        while True:
            if value < current.value:
                if current.left is None:
                    current.left = Node(value)
                    return
                current = current.left
            elif value > current.value:
                if current.right is None:
                    current.right = Node(value)
                    return
                current = current.right
            else:
                return

    def find(self, value):
        current = self.root

        while current is not None:
            if value == current.value:
                return True

            if value < current.value:
                current = current.left
            else:
                current = current.right

        return False

    def delete(self, value):
        self.root = self._delete_node(self.root, value)

    def _delete_node(self, node, value):
        if node is None:
            return None

        if value < node.value:
            node.left = self._delete_node(node.left, value)
        elif value > node.value:
            node.right = self._delete_node(node.right, value)
        else:
            if node.left is None:
                return node.right

            if node.right is None:
                return node.left

            min_node = self._find_min_node(node.right)
            node.value = min_node.value
            node.right = self._delete_node(node.right, min_node.value)

        return node

    def _find_min_node(self, node):
        current = node

        while current.left is not None:
            current = current.left

        return current

    def inorder(self):
        result = []
        self._inorder_traversal(self.root, result)
        return result

    def _inorder_traversal(self, node, result):
        if node is None:
            return

        self._inorder_traversal(node.left, result)
        result.append(node.value)
        self._inorder_traversal(node.right, result)


binarytree = BinarySearchTree()

binarytree.insert(50)
binarytree.insert(30)
binarytree.insert(70)
binarytree.insert(20)
binarytree.insert(40)
binarytree.insert(60)
binarytree.insert(80)

print(binarytree.inorder())

print(binarytree.find(40))
print(binarytree.find(100))

binarytree.delete(20)
print(binarytree.inorder())

binarytree.delete(30)
print(binarytree.inorder())

binarytree.delete(50)
print(binarytree.inorder())