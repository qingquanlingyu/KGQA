__all__ = ['Ahocorasick']


class Node(object):
    def __init__(self):
        self.next = {}
        self.fail = None
        self.isWord = False
        self.fullword = ""


class Ahocorasick(object):
    def __init__(self):
        self.__root = Node()

    def addWord(self, word: str):
        '''
            添加关键词到Tire树中
        '''
        tmp = self.__root
        for i in range(0, len(word)):
            if not tmp.next.__contains__(word[i]):
                tmp.next[word[i]] = Node()
            tmp = tmp.next[word[i]]
        tmp.isWord = True
        tmp.fullword = word

    def make(self):
        '''
            构建自动机，失效函数
        '''
        tmpQueue = []
        tmpQueue.append(self.__root)
        while (len(tmpQueue) > 0):
            temp = tmpQueue.pop()
            p = None
            for k, v in temp.next.items():
                if temp == self.__root:
                    temp.next[k].fail = self.__root
                else:
                    p = temp.fail
                    while p is not None:
                        if p.next.__contains__(k):
                            temp.next[k].fail = p.next[k]
                            break
                        p = p.fail
                    if p is None:
                        temp.next[k].fail = self.__root
                tmpQueue.append(temp.next[k])

    def find(self, content):
        '''
            返回句子中搜索到的实体
        '''
        p = self.__root
        currentPosition = 0
        res = []

        while currentPosition < len(content):
            word = content[currentPosition]
            # 检索状态机，直到匹配
            while p.next.__contains__(word) == False and p != self.__root:
                p = p.fail

            if p.next.__contains__(word):
                # 转移状态机的状态
                p = p.next[word]
            else:
                p = self.__root

            if p.isWord:
                # 若状态为词的结尾，找到，加入
                res.append(p.fullword)

            currentPosition += 1
        return res
