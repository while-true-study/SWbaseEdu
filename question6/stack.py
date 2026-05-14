class Stack:
    def __init__(self, max_size=10):
        self.items = []
        self.max_size = max_size

    def push(self, value):
        if len(self.items) >= self.max_size:
            print('경고: 스택이 가득 차서 더 이상 추가할 수 없습니다.')
            return

        self.items.append(value)
        print(value, '추가 완료')

    def pop(self):
        if self.empty():
            print('경고: 스택이 비어 있어서 가져올 내용이 없습니다.')
            return None

        value = self.items.pop()
        print(value, '가져오기 완료')
        return value

    def empty(self):
        return len(self.items) == 0

    def peek(self):
        if self.empty():
            print('경고: 스택이 비어 있어서 확인할 내용이 없습니다.')
            return None

        return self.items[-1]

    def show(self):
        print('현재 스택 상태')

        if self.empty():
            print('[비어 있음]')
            return

        for index in range(len(self.items) - 1, -1, -1):
            if index == len(self.items) - 1:
                print('|', self.items[index], '| <- top')
            else:
                print('|', self.items[index], '|')

        print('--------')


stack = Stack()

stack.push('item_01')
stack.push('item_02')
stack.push('item_03')
stack.push('item_04')
stack.push('item_05')
stack.push('item_06')
stack.push('item_07')
stack.push('item_08')
stack.push('item_09')
stack.push('item_10')

stack.show()

stack.push('item_11')

print('peek 결과:', stack.peek())

stack.pop()
stack.pop()
stack.pop()

stack.show()

print('스택이 비어 있나요?', stack.empty())

stack.pop()
stack.pop()
stack.pop()
stack.pop()
stack.pop()
stack.pop()
stack.pop()
stack.pop()

print('스택이 비어 있나요?', stack.empty())

stack.pop()
stack.peek()

stack.show()