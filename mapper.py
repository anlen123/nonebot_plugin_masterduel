from typing import List, Any

from .model.Card import YgoCard
from .model.Datas import Datas
from .model.Texts import Texts
from .model.Rarity import Rarity
from .model.Card import buildYgoCard
import sqlite3
from .model.Alias import Alias


def get_card_info_by_id(cardId: int) -> YgoCard:
    try:
        datas = get_datas(f'SELECT * FROM datas WHERE id = {cardId}')[0]
        texts = get_texts(f'SELECT * FROM texts WHERE id = {cardId}')[0]
    except IndexError:
        print(f"No card found with id {cardId}")
        return None

    ygoCard = buildYgoCard(datas, texts)
    return ygoCard


def get_card_info_like_name(name: str) -> YgoCard:
    try:
        texts = get_texts(f'SELECT * FROM texts WHERE name like "%{name}%"')[0]
    except IndexError:
        print(f"No card found with id {name}")
        return None

    return get_card_info_by_id(int(texts.id))


def get_card_info_like_names(name: str) -> List[YgoCard]:
    try:
        textsList = get_texts(f'SELECT * FROM texts WHERE name like "%{name}%"')
    except IndexError:
        print(f"No card found with id {name}")
        return None

    return [get_card_info_by_id(int(texts.id)) for texts in textsList]

def get_card_info_by_name(name: str) -> YgoCard:
    try:
        texts = get_texts(f'SELECT * FROM texts WHERE name = "{name}"')[0]
    except IndexError:
        print(f"No card found with id {name}")
        return None

    return get_card_info_by_id(int(texts.id))


def get_card_info_by_alias(name: str) -> YgoCard:
    try:
        aliasList = get_nonebot_plugin_masterduel_alias(f'SELECT * FROM alias WHERE name = "{name}"')
    except IndexError:
        print(f"No card found with id {name}")
        return None

    if aliasList:
        return get_card_info_by_id(int(aliasList[0].card_id))
    return None


def set_card_alias_by_id(cardId: int, name: str):
    try:
        aliasList = get_nonebot_plugin_masterduel_alias(f'SELECT * FROM alias WHERE name = "{name}"')
    except IndexError:
        print(f"No card found with id {name}")
        return None

    if aliasList:
        alias = aliasList[0]  # 更新
        set_nonebot_plugin_masterduel_alias(f'update from alias set card_id = {cardId} where name = "{alias.name}"')
    else:
        # 插入
        set_nonebot_plugin_masterduel_alias(f'insert into alias (name, card_id) VALUES ("{name}",{cardId})')




def get_nonebot_plugin_masterduel_rarity(sql: str) -> list[Rarity]:
    # 连接到 SQLite 数据库

    conn = sqlite3.connect('nonebot_plugin_masterduel.cdb')

    # 创建一个 Cursor 对象，用于执行 SQL 命令
    cursor = conn.cursor()

    # 执行 SQL 命令，获取 datas 表的所有行
    cursor.execute(sql)

    # 获取查询结果
    rows = cursor.fetchall()

    # 创建一个空列表，用于存储 Ygo_Card 对象
    rarityList = []

    # 对于每一行，创建一个 Ygo_Card 对象，并添加到列表中
    for row in rows:
        # print(row)
        rarity = Rarity(*row)
        rarityList.append(rarity)

    # 关闭连接
    conn.close()

    return rarityList

def get_datas(sql: str) -> list[Datas]:
    print(sql)
    # 连接到 SQLite 数据库
    conn = sqlite3.connect('cards.cdb')

    # 创建一个 Cursor 对象，用于执行 SQL 命令
    cursor = conn.cursor()

    # 执行 SQL 命令，获取 datas 表的所有行
    cursor.execute(sql)

    # 获取查询结果
    rows = cursor.fetchall()

    # 创建一个空列表，用于存储 Ygo_Card 对象
    datasList = []

    # 对于每一行，创建一个 Ygo_Card 对象，并添加到列表中
    for row in rows:
        # print(row)
        datas = Datas(*row)
        datasList.append(datas)

    # 关闭连接
    conn.close()

    return datasList


def set_nonebot_plugin_masterduel_alias(sql: str):
    # 连接到 SQLite 数据库
    print(sql)
    conn = sqlite3.connect('nonebot_plugin_masterduel.cdb')

    # 创建一个 Cursor 对象，用于执行 SQL 命令
    cursor = conn.cursor()

    # 执行 SQL 命令，获取 datas 表的所有行
    cursor.execute(sql)

    conn.commit()

    # 关闭连接
    conn.close()


def get_nonebot_plugin_masterduel_alias(sql: str) -> list[Alias]:
    # 连接到 SQLite 数据库
    print(sql)
    conn = sqlite3.connect('nonebot_plugin_masterduel.cdb')

    # 创建一个 Cursor 对象，用于执行 SQL 命令
    cursor = conn.cursor()

    # 执行 SQL 命令，获取 datas 表的所有行
    cursor.execute(sql)

    # 获取查询结果
    rows = cursor.fetchall()

    # 创建一个空列表，用于存储 Ygo_Card 对象
    aliasList = []

    # 对于每一行，创建一个 Ygo_Card 对象，并添加到列表中
    for row in rows:
        # print(row)
        alias = Alias(*row)
        aliasList.append(alias)

    # 关闭连接
    conn.close()

    return aliasList


def get_texts(sql: str) -> list[Texts]:
    # 连接到 SQLite 数据库
    print(sql)
    conn = sqlite3.connect('cards.cdb')

    # 创建一个 Cursor 对象，用于执行 SQL 命令
    cursor = conn.cursor()

    # 执行 SQL 命令，获取 datas 表的所有行
    cursor.execute(sql)

    # 获取查询结果
    rows = cursor.fetchall()

    # 创建一个空列表，用于存储 Ygo_Card 对象
    textsList = []

    # 对于每一行，创建一个 Ygo_Card 对象，并添加到列表中
    for row in rows:
        # print(row)
        texts = Texts(*row)
        textsList.append(texts)

    # 关闭连接
    conn.close()

    return textsList
