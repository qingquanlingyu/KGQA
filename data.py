import json
import pandas as pd
import shutil
from neo4jDriver import Neo4j


def loadData():
    entity = dict()
    with open('./config.json') as _config:
        URI = "neo4j://localhost:7687"
        USER = "neo4j"
        PASSWORD = "密码"
        Neo = Neo4j(URI, USER, PASSWORD)
        Neo.run("MATCH (n) DETACH DELETE n")

        cfg = json.load(_config)
        for label in cfg.get('entity'):
            shutil.copy("./{0}.csv".format(label),
                        cfg.get('neo4j_addr')+'bishe\\')
            data = pd.read_csv("./{0}.csv".format(label))
            cmd = "LOAD CSV WITH HEADERS FROM 'file:///bishe//{0}.csv' AS line CREATE (:{0} {{".format(
                label)
            for attr in data:
                cmd += "{0}:line.{0},".format(attr)
            cmd = cmd.strip(',')
            for en in data['name']:
                entity[en] = label
            cmd += "})"
            Neo.run(cmd)

        for label in cfg.get('relation'):
            shutil.copy("./{0}.csv".format(label),
                        cfg.get('neo4j_addr')+'bishe\\')
            data = pd.read_csv("./{0}.csv".format(label))
            cmd = "LOAD CSV WITH HEADERS FROM 'file:///bishe//{0}.csv' AS line MATCH (a),(b) WHERE line.from=a.name AND line.to=b.name AND line.a in labels(a) AND line.b in labels(b) CREATE (a)-[r:{0} {{".format(
                label)
            for attr in data:
                if (attr != 'a' and attr != 'b'):
                    cmd += "{0}:line.{0},".format(attr)
            cmd = cmd.strip(',')
            cmd += "}]->(b)"
            Neo.run(cmd)

        print(entity)
        
        Neo.close()
        _config.close()

    return entity


loadData()
