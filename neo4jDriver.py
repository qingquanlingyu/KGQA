from neo4j import GraphDatabase

__all__ = ['Neo4j']


class Neo4j:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run(self, cmd):
        with self.driver.session() as session:
            res = session.run(cmd)
            return res

    def run_retValue(self, cmd):
        with self.driver.session() as session:
            res = session.run(cmd).value()
            return res

    def findLabel_retAttr(self, label, attr):
        with self.driver.session() as session:
            return session.execute_read(self._findLabel_retAttr, label, attr)

    def findName_retAttr(self, name, attr):
        with self.driver.session() as session:
            return session.execute_read(self._findName_retAttr, name, attr)

    def find2Name_retRel(self, val1, val2):
        with self.driver.session() as session:
            res = []
            sres = session.execute_read(
                self._find2Attr_retRel, "name", val1, "name", val2)
            for i in range(len(sres)):
                res.append(sres[i].replace(
                    r"%from", val1).replace(r"%to", val2))
            sres = session.execute_read(
                self._find2Attr_retRel, "name", val2, "name", val1)
            for i in range(len(sres)):
                res.append(sres[i].replace(
                    r"%from", val2).replace(r"%to", val1))
            return res

    def find2Attr_retRel(self, attr1, val1, attr2, val2):
        with self.driver.session() as session:
            res = session.execute_read(
                self._find2Attr_retRel, attr1, val1, attr2, val2)
            return res

    def findARelB_WithBAttr_retB(self, aname, rel, battr, bval):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findARelB_WithBAttr_retB, aname, rel, battr, bval)
            return res

    def findARelB_WithAAttr_retA(self, bname, rel, aattr, aval):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findARelB_WithAAttr_retA, bname, rel, aattr, aval)
            return res

    def findARelB_retA(self, fname, rel):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findARelB_retA, fname, rel)
            return res

    def findARelB_retB(self, fname, rel):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findARelB_retB, fname, rel)
            return res

    def findName_retAllAttr(self, name):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findName_retAllAttr, name)
            return res

    @staticmethod
    def _findLabel_retAttr(tx, label, attr):
        # 通过label查找一个实体并返回其特定属性
        res = []
        search = f'MATCH (a:{label}) RETURN a.{attr}'
        result = tx.run(search)
        for record in result:
            if record["a."+attr] is not None:
                res.append(record["a."+attr])
        return res

    @staticmethod
    def _findName_retAttr(tx, name, attr):
        # 通过name查找一个实体并返回其特定属性值
        res = []
        search = f'MATCH (a) WHERE a.name="{name}" RETURN a.{attr}'
        result = tx.run(search)
        for record in result:
            if record["a."+attr] is not None:
                res.append(record["a."+attr])
        return res

    @staticmethod
    def _find2Attr_retRel(tx, attr1, val1, attr2, val2):
        # 通过两个实体的属性查找其关系
        res = []
        search = f'MATCH (a)-[r]->(b) WHERE a.{attr1}="{val1}" AND b.{attr2}="{val2}" RETURN r.note'
        result = tx.run(search)
        for record in result:
            if record["r.note"] is not None:
                res.append(record["r.note"])
        return res

    @staticmethod
    def _findARelB_retB(tx, fname, rel):
        # 在特定关系类型下，返回某个结点子结点的结点名
        res = []
        search = f'MATCH (a)-[r:{rel}]->(b) WHERE a.name="{fname}" RETURN b.name'
        result = tx.run(search)
        for record in result:
            if record["b.name"] is not None:
                res.append(record["b.name"])
        return res

    @staticmethod
    def _findARelB_retA(tx, fname, rel):
        # 在特定关系类型下，返回某个结点父结点的结点名
        res = []
        search = f'MATCH (a)-[r:{rel}]->(b) WHERE b.name="{fname}" RETURN a.name'
        result = tx.run(search)
        for record in result:
            if record["a.name"] is not None:
                res.append(record["a.name"])
        return res

    @staticmethod
    def _findARelB_WithBAttr_retB(tx, aname, rel, battr, bval):
        # 在特定关系类型下，返回某个结点子结点中属性符合要求的结点名
        res = []
        search = f'MATCH (a)-[r:{rel}]->(b) WHERE a.name="{aname}" AND b.{battr}="{bval}" RETURN b.name'
        result = tx.run(search)
        for record in result:
            if record["b.name"] is not None:
                res.append(record["b.name"])
        return res

    @staticmethod
    def _findARelB_WithAAttr_retA(tx, bname, rel, aattr, aval):
        # 在特定关系类型下，返回某个结点子结点中属性符合要求的结点名
        res = []
        search = f'MATCH (a)-[r:{rel}]->(b) WHERE b.name="{bname}" AND a.{aattr}="{aval}" RETURN a.name'
        result = tx.run(search)
        for record in result:
            if record["a.name"] is not None:
                res.append(record["a.name"])
        return res

    @staticmethod
    def _findName_retAllAttr(tx, name):
        # 根据结点名，返回所有属性名
        res = []
        search = f'MATCH (n) WHERE n.name="{name}" RETURN properties(n) AS properties'
        result = tx.run(search)
        for record in result:
            if record["properties"] is not None:
                res.append(record["properties"])
        return res
