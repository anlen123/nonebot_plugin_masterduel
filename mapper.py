from .model.Datas import Datas
from .model.Texts import Texts
from .model.Rarity import Rarity
from .model.Card import buildYgoCard
import sqlite3
from .model.Alias import Alias
import difflib, pypinyin
from typing import List, Any
import nonebot, requests, json

from .model.Card import YgoCard

global_config = nonebot.get_driver().config
config = global_config.dict()
nonebot_plugin_masterduel_img_dir = config.get('nonebot_plugin_masterduel_img_dir')
nonebot_plugin_masterduel_root_dir = config.get('nonebot_plugin_masterduel_root_dir')


def get_card_info_by_id(cardId: int) -> YgoCard:
    try:
        datas = get_datas(f'SELECT * FROM datas WHERE id = {cardId}')[0]
        texts = get_texts(f'SELECT * FROM texts WHERE id = {cardId}')[0]
        ygoCard = buildYgoCard(datas, texts)
        return ygoCard
    except IndexError:
        print(f"No card found with id {cardId}")


def get_card_info_like_name(name: str) -> YgoCard:
    try:
        texts = get_texts(f'SELECT * FROM texts WHERE name like "%{name}%"')[0]
        return get_card_info_by_id(int(texts.id))
    except IndexError:
        print(f"No card found with id {name}")


def get_card_info_like_names(name: str) -> List[YgoCard]:
    try:
        textsList = get_texts(f'SELECT * FROM texts WHERE name like "%{name}%"')
        return [get_card_info_by_id(int(texts.id)) for texts in textsList]
    except IndexError:
        print(f"No card found with id {name}")


def get_card_info_by_name(name: str) -> YgoCard:
    try:
        texts = get_texts(f'SELECT * FROM texts WHERE name = "{name}"')[0]
        return get_card_info_by_id(int(texts.id))
    except IndexError:
        print(f"No card found with id {name}")


def get_card_info_by_alias(name: str) -> YgoCard:
    try:
        aliasList = get_nonebot_plugin_masterduel_alias(f'SELECT * FROM alias WHERE name = "{name}"')
        if aliasList:
            return get_card_info_by_id(int(aliasList[0].card_id))
    except IndexError:
        print(f"No card found with id {name}")


def set_card_alias_by_id(cardId: int, name: str):
    try:
        aliasList = get_nonebot_plugin_masterduel_alias(f'SELECT * FROM alias WHERE name = "{name}"')
    except IndexError:
        print(f"No card found with id {name}")
        return None

    if aliasList:
        alias = aliasList[0]  # 更新
        set_nonebot_plugin_masterduel(f'update alias set card_id = {cardId} where name = "{alias.name}"')
    else:
        # 插入
        set_nonebot_plugin_masterduel(f'insert into alias (name, card_id) VALUES ("{name}",{cardId})')


def get_nonebot_plugin_masterduel_rarity(sql: str) -> list[Rarity]:
    rows = get_nonebot_plugin_masterduel(sql)
    rarityList = []
    # 对于每一行，创建一个 Ygo_Card 对象，并添加到列表中
    for row in rows:
        # print(row)
        rarity = Rarity(*row)
        rarityList.append(rarity)
    return rarityList


def get_datas(sql: str) -> list[Datas]:
    rows = get_cards(sql)
    datasList = []
    for row in rows:
        # print(row)
        datas = Datas(*row)
        datasList.append(datas)
    return datasList


def set_nonebot_plugin_masterduel(sql: str):
    conn = sqlite3.connect(f'{nonebot_plugin_masterduel_root_dir}\\nonebot_plugin_masterduel.cdb')
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


def get_nonebot_plugin_masterduel_alias(sql: str) -> list[Alias]:
    rows = get_nonebot_plugin_masterduel(sql)
    aliasList = []
    for row in rows:
        alias = Alias(*row)
        aliasList.append(alias)
    return aliasList


def get_texts(sql: str) -> list[Texts]:
    rows = get_cards(sql)
    textsList = []
    for row in rows:
        texts = Texts(*row)
        textsList.append(texts)
    return textsList


def get_nonebot_plugin_masterduel(sql: str):
    conn = sqlite3.connect(f'{nonebot_plugin_masterduel_root_dir}\\nonebot_plugin_masterduel.cdb')
    cursor = conn.cursor()
    cursor.execute(sql)
    # 获取查询结果
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_cards(sql: str):
    conn = sqlite3.connect(f'{nonebot_plugin_masterduel_root_dir}\\cards.cdb')
    cursor = conn.cursor()
    cursor.execute(sql)
    # 获取查询结果
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_id_and_name_all():
    return get_cards("select id,name from texts")


def get_max_like_id(name: str):
    name = pypinyin.pinyin(name, pypinyin.NORMAL)
    name = [x[0] for x in name]
    print(name)

    rows = get_id_and_name_all()
    ret = None
    max_number = 0

    for row in rows:
        c_name = pypinyin.pinyin(row[1], pypinyin.NORMAL)
        c_name = [x[0] for x in c_name]
        # print(c_name)
        dis = difflib.SequenceMatcher(None, c_name, name).ratio()
        if dis > max_number:
            max_number = dis
            ret = row
    if not ret:
        return ""
    return ret[0]


def get_nonebot_plugin_masterduel_id_by_cid(cid: int):
    ret = get_nonebot_plugin_masterduel(f"select id from cid where cid = '{cid}'")

    url = f'https://ygocdb.com/api/v0/?search={cid}'

    if ret:
        return ret[0][0]
    else:
        url = f'https://ygocdb.com/api/v0/?search={cid}'
        resp = requests.get(url, headers={"qq": "1761512493"})
        resp_json = json.loads(resp.text)
        flag = False
        for x in resp_json['result']:
            r_cid = (x['cid'])
            card_id = (x['id'])
            if str(cid).strip() == str(r_cid).strip():
                set_nonebot_plugin_masterduel(f"insert into cid (id,cid) values ('{card_id}','{cid}')")
                return card_id


def get_card_by_md_shard_deck_code(deckCode: str) -> tuple:
    search_url = "https://ayk-deck.mo.konami.net/ayk/yocgapi/search"
    detail_url = "https://ayk-deck.mo.konami.net/ayk/yocgapi/detail"

    headers = {"User-Agent": "UnityPlayer/2020.3.46f1 (UnityWebRequest/1.0, libcurl/7.84.0-DEV)",
               "Host": "ayk-deck.mo.konami.net"}

    post_data = {"commandName": "data.ycdb.searchDeckForMd",
                 "params": {"typeCode": 0, "categoryList": [], "tagList": [], "cardIdList": [], "keyword": "",
                            "deckCode": f"{deckCode}", "sortCode": 2, "sizePerPage": 100, "requestPageNo": 0,
                            "deckTypeList": [1, 2]}}

    resp = requests.post(url=search_url, data=json.dumps(post_data), headers=headers, verify=False)
    deck_resp = json.loads(resp.text)
    # print(f"{deck_resp=}")
    if not deck_resp['result']['deckList']:
        return ()
    post_data = {"commandName": "data.ycdb.searchDeckForMd",
                 "params": {"targetId": f"{deck_resp['result']['deckList'][0]['cardgameId']}",
                            "deckNo": f"{deck_resp['result']['deckList'][0]['deckNo']}", }}

    resp = requests.post(url=detail_url, data=json.dumps(post_data), headers=headers, verify=False)

    # print(resp.text)

    card_resp = json.loads(resp.text)
    mainCardListCid = []
    extraCardListCid = []
    for cid in card_resp['result']['mainCardList']:
        cardId = [cid['cardId']]
        count = int(cid['count'])
        if cardId:
            mainCardListCid += cardId * count

    for cid in card_resp['result']['extraCardList']:
        cardId = [cid['cardId']]
        count = int(cid['count'])
        if cardId:
            extraCardListCid += cardId * count

    mainCardList = [y for y in [get_nonebot_plugin_masterduel_id_by_cid(int(x)) for x in mainCardListCid] if y]
    exCardList = [y for y in [get_nonebot_plugin_masterduel_id_by_cid(int(x)) for x in extraCardListCid] if y]

    return mainCardList, exCardList
