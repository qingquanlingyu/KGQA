from queue import Empty
from typing import Set
from urllib import response
from fastapi import FastAPI
from data import loadData
from neo4jDriver import Neo4j
from AC import Ahocorasick
import json
from intent.predict import predict
from rwkv import rwkv, rwkvreset

app = FastAPI()
URI = "neo4j://localhost:7687"
USER = "neo4j"
PASSWORD = "asantuSB"

Neo = Neo4j(URI, USER, PASSWORD)
entity = loadData()

important = ["商店", "景点", "博物馆", "餐厅"]


def build_actree(wordlist):
    ac = Ahocorasick()
    for word in wordlist:
        print(word)
        ac.addWord(word)
    ac.make()
    return ac


ac = build_actree(entity)


def replace_entity(question, re):
    recog_entities = ac.find(question)
    re += recog_entities
    for e in recog_entities:
        question = question.replace(e, entity[e], 1)
    return question


@ app.get("/")
async def root():
    return "Hello, World!"


@ app.get("/base/{question}")
async def base(question: str):
    ques_entities = []  # 问题中出现的实体，字符串格式
    question.strip()
    question = replace_entity(question, ques_entities)

    with open('./dic.json') as _dic:
        dic = json.load(_dic)
        for d in dic:
            question = question.replace(d, dic[d])
        _dic.close()

    question = replace_entity(question, ques_entities)

    yuqi = ["?", "？", "吗", "啊", "呀"]
    for yuqici in yuqi:
        if (question.endswith(yuqici)):
            question = question[:len(question)-len(yuqici)]

    cnt = len(ques_entities)

    base_rep: str = "抱歉，我无法理解你的问题"
    print("处理后问题: " + question)

    if cnt == 0 or cnt > 2:
        return base_rep
    else:
        inte, reco = predict(question)
        print(["识别意图: ", inte])

        if (reco is False):
            return rwkv(question)
        elif cnt == 1:
            if inte == 1 or inte == 11:  # 问双实体关系，不应该出现
                return base_rep
            elif inte == 0:  # 问地址
                if (entity[ques_entities[0]] == "locale" and "国" not in question and "州" not in question and "市" not in question and "区" not in question):
                    tmpp = Neo.findName_retAttr(ques_entities[0], "address")
                    if (len(tmpp) == 1):
                        return f"{ques_entities[0]}地址是{tmpp[0]}"
                res = []
                tmp = ques_entities[0]
                while True:
                    tmp = Neo.findARelB_retB(tmp, "belong")
                    if (len(tmp) != 1):
                        break
                    tmp = tmp[0]
                    if (entity[tmp] == "country" and "国" in question):
                        return f"{ques_entities[0]}位于{tmp}"
                    if (entity[tmp] == "state" and "州" in question):
                        return f"{ques_entities[0]}位于{tmp}"
                    if (entity[tmp] == "city" and "市" in question):
                        return f"{ques_entities[0]}位于{tmp}"
                    if (entity[tmp] == "region" and "区" in question):
                        return f"{ques_entities[0]}位于{tmp}"
                    if (entity[tmp] == "locale" and "国" not in question and "州" not in question and "市" not in question and "区" not in question):
                        tmpp = Neo.findName_retAttr(ques_entities[0], "attr")
                        if (len(res) == 1):
                            return f"{ques_entities[0]}属于{tmp}，地址是{tmpp[0]}"
                    res.insert(0, tmp)
                if (len(res) == 0):
                    return f"抱歉，无法找到{ques_entities[0]}的位置信息"
                return f"{ques_entities[0]}位于"+"，".join(res)

            elif inte == 2:  # 问如何到达
                if (entity[ques_entities[0]] == "locale"):
                    res = Neo.findARelB_WithAAttr_retA(
                        ques_entities[0], "belong", "class", "出入口")
                    if (len(res) == 0):
                        return f"抱歉，未查询到如何到达{ques_entities[0]}"
                    else:
                        return f"可以通过"+"、".join(res)+f"到达{ques_entities[0]}"
                elif (entity[ques_entities[0]] == "site"):
                    locale = Neo.findARelB_retB(ques_entities[0], "belong")
                    if (len(locale) != 1):
                        return f"抱歉，未查询到如何到达{ques_entities[0]}"
                    res = Neo.findARelB_WithAAttr_retA(
                        locale[0], "belong", "class", "出入口")
                    if (len(res) == 0):
                        return f"抱歉，未查询到如何到达{ques_entities[0]}"
                    else:
                        return f"可以通过"+"、".join(res)+f"到达{ques_entities[0]}"
                else:
                    return f"抱歉，“{ques_entities[0]}”不合法，请检查地名"
            elif inte == 3:  # 问联系方式
                rep = ""
                res = Neo.findName_retAttr(ques_entities[0], "phone")
                if (len(res) > 0):
                    rep += (f"{ques_entities[0]}的电话为："+"，".join(res) + "\n")
                res = Neo.findName_retAttr(ques_entities[0], "website")
                if (len(res) > 0):
                    rep += (f"{ques_entities[0]}的网址为："+"，".join(res))
                if (rep == ""):
                    rep = f"抱歉，未找到{ques_entities[0]}的联系方式"
                return rep
            elif inte == 4:  # 问电话
                res = Neo.findName_retAttr(ques_entities[0], "phone")
                if (len(res) == 0):
                    return f"抱歉，未找到{ques_entities[0]}的电话联系方式"
                else:
                    return f"{ques_entities[0]}的电话为："+"，".join(res)
            elif inte == 5:  # 问网站
                res = Neo.findName_retAttr(ques_entities[0], "website")
                if (len(res) == 0):
                    return f"抱歉，未找到{ques_entities[0]}的网址"
                else:
                    return f"{ques_entities[0]}的网址为："+"，".join(res)
            elif inte == 6:  # 问介绍
                res = Neo.findName_retAttr(ques_entities[0], "intro")
                if (len(res) == 0):
                    return f"抱歉，未找到{ques_entities[0]}的介绍信息"
                else:
                    return f"{ques_entities[0]}"+"，".join(res)
            elif inte == 7:  # 问附属吃
                if (entity[ques_entities[0]] == "locale"):
                    res = Neo.findARelB_WithAAttr_retA(
                        ques_entities[0], "belong", "class", "餐厅")
                    if (len(res) == 0):
                        return f"抱歉，未找到{ques_entities[0]}处餐厅"
                    else:
                        return f"{ques_entities[0]}处的餐厅有："+"，".join(res)
                elif (entity[ques_entities[0]] == "site"):
                    locale = Neo.findARelB_retB(ques_entities[0], "belong")
                    if (len(locale) != 1):
                        return f"抱歉，未找到{ques_entities[0]}附近餐厅"
                    res = Neo.findARelB_WithAAttr_retA(
                        locale[0], "belong", "class", "餐厅")
                    if (len(res) == 0):
                        return f"抱歉，未找到{ques_entities[0]}附近餐厅"
                    else:
                        return f"{ques_entities[0]}附近的餐厅有："+"，".join(res)
                else:
                    return f"抱歉，“{ques_entities[0]}”不合法，请检查地名"
            elif inte == 8:  # 问附属买
                if (entity[ques_entities[0]] == "locale"):
                    res = Neo.findARelB_WithAAttr_retA(
                        ques_entities[0], "belong", "class", "商店")
                    if (len(res) == 0):
                        return f"抱歉，未找到{ques_entities[0]}处商店"
                    else:
                        return f"{ques_entities[0]}处的商店有："+"，".join(res)
                elif (entity[ques_entities[0]] == "site"):
                    locale = Neo.findARelB_retB(ques_entities[0], "belong")
                    if (len(locale) != 1):
                        return f"抱歉，未找到{ques_entities[0]}附近商店"
                    res = Neo.findARelB_WithAAttr_retA(
                        locale[0], "belong", "class", "商店")
                    if (len(res) == 0):
                        return f"抱歉，未找到{ques_entities[0]}附近商店"
                    else:
                        return f"{ques_entities[0]}附近的商店有："+"，".join(res)
                else:
                    return f"抱歉，“{ques_entities[0]}”不合法，请检查地名"
            elif inte == 9:  # 问下属
                res = Neo.findARelB_retA(
                    ques_entities[0], "belong")
                if (len(res) == 0):
                    return f"抱歉，未找到{ques_entities[0]}有下属区域"
                else:
                    return f"，".join(res)
            elif inte == 10:  # 问同级
                locale = Neo.findARelB_retB(ques_entities[0], "belong")
                if (len(locale) != 1):
                    return f"抱歉，未找到{ques_entities[0]}附近的重要同级地点"
                res = []
                for imp in important:
                    res += Neo.findARelB_WithAAttr_retA(
                        locale[0], "belong", "class", imp)
                res = [s for s in res if s != ques_entities[0]]
                if (len(res) == 0):
                    return f"抱歉，未找到{ques_entities[0]}附近的重要同级地点"
                else:
                    return "你可以去：""，".join(res)

        elif cnt == 2:
            if inte != 1 and inte != 11:  # 不是问关系和除同级，不应该出现
                return base_rep
            elif inte == 1:
                res = Neo.find2Name_retRel(ques_entities[0], ques_entities[1])
                if (len(res) == 0):
                    return f"抱歉，{ques_entities[0]}和{ques_entities[1]}间不存在任何关系"
                else:
                    return "，".join(res)
            elif inte == 11:
                locale = Neo.findARelB_retB(ques_entities[0], "belong")
                if (len(locale) != 1 or locale[0] != ques_entities[1]):
                    return f"抱歉，{ques_entities[0]}的上级不是{ques_entities[1]}，请检查地名"
                res = Neo.findARelB_retA(
                    locale[0], "belong")
                res = [s for s in res if s != ques_entities[0]]
                if (len(res) == 0):
                    return f"抱歉，未找到除{ques_entities[0]}外的同级地点"
                else:
                    return "还有"+"，".join(res)

        else:
            return base_rep

    return base_rep


@ app.get("/llm/{question}")
async def llm(question: str):
    pre_question = question
    ques_entities = []  # 问题中出现的实体，字符串格式
    question.strip()
    question = replace_entity(question, ques_entities)

    with open('./dic.json') as _dic:
        dic = json.load(_dic)
        for d in dic:
            question = question.replace(d, dic[d])
        _dic.close()

    question = replace_entity(question, ques_entities)

    knowledge = ""  # 查询到的全部相关知识

    for onee in ques_entities:
        attrs = Neo.findName_retAllAttr(onee)  # 本身参数
        for attr in attrs:
            for key in attr:
                if (key == "address"):
                    knowledge += f"{onee}的精确地址是:{attr[key]}。\n"
                elif (key == "intro"):
                    knowledge += f"{onee}的介绍是:{attr[key]}。\n"
                elif (key == "class"):
                    knowledge += f"{onee}的类型是:{attr[key]}。\n"
                elif (key == "phone"):
                    knowledge += f"{onee}的电话号码联系方式是:{attr[key]}。\n"
                elif (key == "website"):
                    knowledge += f"{onee}的网址联系方式是:{attr[key]}。\n"

        tmp = onee  # 所有上级，仅限本知识图谱父子关系明确，复杂关系建议只提供邻居信息
        while True:
            tmp2 = Neo.findARelB_retB(tmp, "belong")
            if (len(tmp2) != 1):
                break
            tmp2 = tmp2[0]
            knowledge += f"{tmp}在地理上从属于{tmp2}，"
            tmp = tmp2
        if (knowledge.endswith('，')):
            knowledge = knowledge[:-len('，')]
            knowledge += "。\n"

        if (entity[onee] == "site"):
            upper = Neo.findARelB_retB(onee, "belong")
            if (len(upper) == 1):
                for imp in important:
                    res = Neo.findARelB_WithAAttr_retA(
                        upper[0], "belong", "class", imp)
                    res = [s for s in res if s != onee]
                    if (len(res) != 0):
                        res = "、".join(res)
                        knowledge += f"{onee}附近的{imp}有:{res}。\n"
                res = Neo.findARelB_WithAAttr_retA(
                    upper[0], "belong", "class", "出入口")
                res = [s for s in res if s != onee]
                if (len(res) != 0):
                    res = "、".join(res)
                    knowledge += f"可以通过{res}到达{onee}。\n"
        if (entity[onee] == "locale"):
            for imp in important:
                res = Neo.findARelB_WithAAttr_retA(
                    onee, "belong", "class", imp)
                if (len(res) != 0):
                    res = "、".join(res)
                    knowledge += f"{onee}附近的{imp}有:{res}。\n"
            res = Neo.findARelB_WithAAttr_retA(
                onee, "belong", "class", "出入口")
            if (len(res) != 0):
                res = "、".join(res)
                knowledge += f"可以通过{res}到达{onee}。\n"
    rep = rwkv(
        f"学习以下文段,用中文回答问题。如果无法从中得到答案，忽略文段内容并用中文回答问题。\n{knowledge}问题：{pre_question}")

    return rep


@ app.get("/reset")
async def reset():
    return rwkvreset()
