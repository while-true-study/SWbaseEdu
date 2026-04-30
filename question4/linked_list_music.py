class Node:
    '''연결 리스트의 기본 노드 클래스.'''

    def __init__(self, data):
        self.data = data
        self.next = None


class SinglyLinkedList:
    '''단순 연결 리스트 클래스.'''

    def __init__(self):
        self.head = None
        self.size = 0

    def __len__(self):
        return self.size

    def is_empty(self):
        return self.head is None

    def insert(self, data, position = None):
        '''노드를 삽입한다.

        position이 None이거나 현재 길이보다 크면 마지막에 추가한다.
        position이 0 이하이면 첫 번째에 추가한다.
        그 외에는 지정 위치에 삽입한다.
        '''
        new_node = Node(data)

        if self.head is None:
            self.head = new_node
            self.size += 1
            return

        if position is None or position >= self.size:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node
            self.size += 1
            return

        if position <= 0:
            new_node.next = self.head
            self.head = new_node
            self.size += 1
            return

        current = self.head
        index = 0
        while index < position - 1 and current.next is not None:
            current = current.next
            index += 1

        new_node.next = current.next
        current.next = new_node
        self.size += 1

    def delete(self, target = None, position = None):
        '''노드를 삭제한다.

        position이 주어지면 해당 위치의 노드를 삭제한다.
        position이 없으면 target 값과 일치하는 첫 번째 노드를 삭제한다.
        삭제 성공 시 True, 실패 시 False를 반환한다.
        '''
        if self.head is None:
            return False

        if position is not None:
            if position < 0 or position >= self.size:
                return False

            if position == 0:
                self.head = self.head.next
                self.size -= 1
                return True

            current = self.head
            index = 0
            while index < position - 1:
                current = current.next
                index += 1

            current.next = current.next.next
            self.size -= 1
            return True

        if target is None:
            return False

        if self.head.data == target:
            self.head = self.head.next
            self.size -= 1
            return True

        previous = self.head
        current = self.head.next

        while current is not None:
            if current.data == target:
                previous.next = current.next
                self.size -= 1
                return True
            previous = current
            current = current.next

        return False

    def get_list(self):
        '''처음부터 끝까지 모든 데이터를 리스트로 반환한다.'''
        items = []
        current = self.head

        while current is not None:
            items.append(current.data)
            current = current.next

        return items

    def display(self):
        '''연결 리스트를 사람이 보기 좋은 문자열로 출력한다.'''
        items = self.get_list()
        if not items:
            print('비어 있음')
            return
        print(' -> '.join(items))


class CircularLinkedList:
    '''원형 연결 리스트 클래스.'''

    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

    def __len__(self):
        return self.size

    def is_empty(self):
        return self.head is None

    def insert(self, data):
        '''원형 연결 리스트의 마지막에 노드를 추가한다.'''
        new_node = Node(data)

        if self.head is None:
            self.head = new_node
            self.tail = new_node
            new_node.next = new_node
            self.current = self.head
            self.size += 1
            return

        new_node.next = self.head
        self.tail.next = new_node
        self.tail = new_node
        self.size += 1

    def delete(self, target):
        '''값이 일치하는 첫 번째 노드를 삭제한다.'''
        if self.head is None:
            return False

        current = self.head
        previous = self.tail

        for _ in range(self.size):
            if current.data == target:
                if self.size == 1:
                    self.head = None
                    self.tail = None
                    self.current = None
                    self.size = 0
                    return True

                previous.next = current.next

                if current == self.head:
                    self.head = current.next
                if current == self.tail:
                    self.tail = previous
                if current == self.current:
                    self.current = current.next

                self.size -= 1
                return True

            previous = current
            current = current.next

        return False

    def get_next(self):
        '''현재 위치의 데이터를 반환하고 다음 노드로 이동한다.'''
        if self.current is None:
            return None

        data = self.current.data
        self.current = self.current.next
        return data

    def search(self, target):
        '''값을 검색해 위치를 반환한다. 없으면 -1을 반환한다.'''
        if self.head is None:
            return -1

        current = self.head
        index = 0

        for _ in range(self.size):
            if current.data == target:
                return index
            current = current.next
            index += 1

        return -1

    def get_list(self):
        '''원형 연결 리스트의 전체 데이터를 한 바퀴만 순회해 반환한다.'''
        items = []

        if self.head is None:
            return items

        current = self.head
        for _ in range(self.size):
            items.append(current.data)
            current = current.next

        return items

    def display(self):
        '''원형 연결 리스트를 사람이 보기 좋은 문자열로 출력한다.'''
        items = self.get_list()
        if not items:
            print('비어 있음')
            return
        print(' -> '.join(items) + ' -> ... (원형)')



def demo_singly_linked_list():
    '''단순 연결 리스트 예제 실행.'''
    print('1. 단순 연결 리스트 구현')
    linkedlist = SinglyLinkedList()

    linkedlist.insert('봄날')
    linkedlist.insert('Hype Boy')
    linkedlist.insert('Supernova')
    print('초기 목록')
    linkedlist.display()

    linkedlist.insert('Ditto', position = 0)
    print('맨 앞에 Ditto 삽입')
    linkedlist.display()

    linkedlist.insert('Love Dive', position = 2)
    print('중간에 Love Dive 삽입')
    linkedlist.display()

    linkedlist.insert('Attention', position = 999)
    print('맨 뒤에 Attention 삽입')
    linkedlist.display()

    linkedlist.delete(target = 'Hype Boy')
    print('Hype Boy 삭제')
    linkedlist.display()

    linkedlist.delete(position = 0)
    print('첫 번째 노드 삭제')
    linkedlist.display()

    print('get_list() 결과')
    print(linkedlist.get_list())
    print()



def demo_circular_linked_list():
    '''원형 연결 리스트 예제 실행.'''
    print('2. 원형 연결 리스트 구현')
    circularlist = CircularLinkedList()

    circularlist.insert('사건의 지평선')
    circularlist.insert('밤양갱')
    circularlist.insert('한 페이지가 될 수 있게')
    circularlist.insert('나는 아픈 건 딱 질색이니까')
    print('초기 목록')
    circularlist.display()

    keyword = '밤양갱'
    found_index = circularlist.search(keyword)
    print(f'\'{keyword}\' 검색 결과 위치: {found_index}')

    print('get_next()로 6번 순차 재생')
    for order in range(6):
        title = circularlist.get_next()
        print(f'{order + 1}번째 재생: {title}')

    circularlist.delete('밤양갱')
    print('\'밤양갱\' 삭제 후 목록')
    circularlist.display()

    print('삭제 후 get_next()로 5번 순차 재생')
    for order in range(5):
        title = circularlist.get_next()
        print(f'{order + 1}번째 재생: {title}')

    print('전체 목록')
    print(circularlist.get_list())
    print()



def main():
    demo_singly_linked_list()
    demo_circular_linked_list()


if __name__ == '__main__':
    main()
