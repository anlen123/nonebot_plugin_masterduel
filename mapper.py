from typing import List, Any

from .model.Card import YgoCard
from .model.Datas import Datas
from .model.Texts import Texts
from .model.Card import buildYgoCard
import sqlite3


def get_card_info_by_id(cardId: int) -> YgoCard:
    """

    :param cardId:
    :return:
    """
    try:
        datas = get_datas(f'SELECT * FROM datas WHERE id = {cardId}')[0]
        texts = get_texts(f'SELECT * FROM texts WHERE id = {cardId}')[0]
    except IndexError:
        print(f"No card found with id {cardId}")
        return None

    ygoCard = buildYgoCard(datas, texts)
    print(ygoCard)
    return ygoCard


def get_card_info_by_name(name: str) -> YgoCard:
    try:
        texts = get_texts(f'SELECT * FROM texts WHERE name = "{name}"')[0]
    except IndexError:
        print(f"No card found with id {name}")
        return None

    return get_card_info_by_id(int(texts.id))


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
