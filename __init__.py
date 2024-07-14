from typing import List, Any
from .config import Config
from nonebot.plugin import on_notice, on_regex, on_message
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message, GroupMessageEvent, MessageEvent, \
    PrivateMessageEvent
import nonebot, os, random, re
from nonebot.typing import T_State

from .model.Card import YgoCard
from nonebot.rule import Rule
from .mapper import *
from .utils import imgUtils
from .utils import rarityUtils
from urllib import parse

global_config = nonebot.get_driver().config
config = global_config.dict()

nonebot_plugin_masterduel_img_dir = config.get('nonebot_plugin_masterduel_img_dir')
nonebot_plugin_masterduel_root_dir = config.get('nonebot_plugin_masterduel_root_dir')

master_duel = on_regex(pattern="^ck")
master_duel_CK = on_regex(pattern="^CK")


@master_duel.handle()
@master_duel_CK.handle()
async def master_duel_rev(bot: Bot, event: Event):
    cmd = event.get_plaintext()[2:]
    cmd = cmd.strip()
    if not cmd:
        return
    ygoCard = None
    if cmd.isdigit():
        ygoCard = mapper.get_card_info_by_id(int(cmd))

    if not ygoCard:
        ygoCard = mapper.get_card_info_by_alias(cmd)
        if not ygoCard:
            cardId = get_max_like_id(cmd)
            ygoCard = get_card_info_by_id(cardId)
    if ygoCard:
        messageSegment = await get_send_msg(ygoCard)
        await bot.send(event, messageSegment)
        directory = f"{nonebot_plugin_masterduel_img_dir}\\{ygoCard.id}"
        if os.path.exists(directory):
            files = os.listdir(directory)
            print(directory)
            print(random.choice(files))
            file = directory + "\\" + random.choice(files)
            print(file)
            await bot.send(event, MessageSegment.image(file))
    else:
        await bot.send(event, MessageSegment.text("未查询到卡片"))


async def get_send_msg(card: YgoCard) -> Message:
    rarity = rarityUtils.get_rarity(card.id)
    urlBase64 = imgUtils.pin_quality(int(card.id), rarity)
    return MessageSegment.text(f"卡号：{card.id}\n{card.name}\n") + MessageSegment.text(
        "暂未登录MD" if not rarity else "") + MessageSegment.image(urlBase64) + MessageSegment.text(f"{card.desc}")


alias_card = on_regex(pattern="^别名")
alias_card2 = on_regex(pattern="^外号")


@alias_card.handle()
@alias_card2.handle()
async def alias_card_rev(bot: Bot, event: Event):
    cmd = event.get_plaintext()[2:]
    cmd = cmd.strip()
    ags = cmd.split(" ")
    if len(ags) != 2 and is_int(ags[0]):
        await bot.send(event, "例子：别名 30459350 王宫壁")
    cardId = ags[0]
    aliasName = ags[1]
    mapper.set_card_alias_by_id(int(cardId), aliasName)
    await bot.send(event, "别名设置成功！")


def is_int(n: str):
    try:
        float_n = float(n)
        int_n = int(float_n)
    except ValueError as e:
        return False
    else:
        return float_n == int_n


master_like_duel = on_regex(pattern="^lck")


@master_like_duel.handle()
async def master_like_duel_rev(bot: Bot, event: Event):
    cmd = event.get_plaintext()[3:]
    cmd = cmd.strip()

    ygoCardList = mapper.get_card_info_like_names(cmd)
    if not ygoCardList:
        await bot.send(event, MessageSegment.text("未查询到卡片"))
        return
    ygoCardList = ygoCardList[:20]
    msgs = ""
    for card in ygoCardList:
        msgs += MessageSegment.text(f"卡号：{card.id}      {card.name}\n\n")
    await bot.send(event=event, message=msgs)


def push_ygo_card() -> Rule:
    async def push_ygo_card_(bot: "Bot", event: "Event") -> bool:
        if event.get_type() != "message":
            return False
        msg = str(event.get_plaintext())
        if re.findall("^上传游戏王卡图\ \d+$", msg):
            return True
        return False

    return Rule(push_ygo_card_)


master_duel_push_img = on_message(rule=push_ygo_card())


@master_duel_push_img.handle()
async def master_duel_push_img_rev(bot: Bot, event: MessageEvent, state: T_State):
    card_id = event.get_plaintext().strip().split(" ")[-1].strip()
    if card_id:
        state['card_id'] = card_id
        ygoCard = mapper.get_card_info_by_id(int(card_id))
        if not ygoCard:
            await bot.send(event=event, message="没有找到这张卡")
            state['img'] = "None"
            return


@master_duel_push_img.got("img", prompt="图呢？")
async def get_setu(bot: Bot, event: MessageEvent, state: T_State):
    if state['img'] == "None":
        return
    msg = event.get_message()
    card_id = state['card_id']
    try:
        if msg[0].type == "image":
            url = msg[0].data["url"]  # 图片链接
            imgUtils.down_img(f"{nonebot_plugin_masterduel_img_dir}\\{card_id}\\", url,
                              f"{random.randint(1, 10000000)}.jpg")
            await bot.send(event=event, message="上传成功！")
    except Exception as e:
        await bot.send(event=event, message="错误的上传图片")


my_deck = on_regex(pattern="^卡组码 ")


@my_deck.handle()
async def master_duel_rev(bot: Bot, event: Event):
    cmd = event.get_plaintext()[3:]
    cmd = cmd.strip()
    zipCard = mapper.get_card_by_md_shard_deck_code(cmd)

    if not zipCard:
        await bot.send(event=event, message="未找到卡组")
        return
    mainCardList, exCardList = zipCard
    sss = imgUtils.get_all_temp(mainCardList, exCardList)
    pngName = f"{os.getcwd()}\\{random.randint(1, 99999999999)}.png"
    imgUtils.screenshot(sss, pngName)
    print(pngName)
    await bot.send(event=event, message=MessageSegment.image(pngName))
    os.remove(pngName)


cai_ding = on_regex(pattern="^裁定")


@cai_ding.handle()
async def cai_ding_rev(bot: Bot, event: Event):
    cmd = event.get_plaintext()[2:]
    cmd = cmd.strip()
    ygoCard = mapper.get_card_info_by_id(int(cmd))
    if ygoCard:
        messageSegment = await get_send_msg(ygoCard)
        # await bot.send(event, messageSegment)
        htmlStr = get_cai_ding_html(ygoCard.id)
        pngName = f"{os.getcwd()}\\{random.randint(1, 99999999999)}.png"
        imgUtils.screenshot(htmlStr, pngName)
        print(pngName)
        await bot.send(event=event, message=messageSegment + MessageSegment.image(pngName))
        os.remove(pngName)
    else:
        await bot.send(event=event, message="请输入正确的卡密")


def chunk_string(s, chunk_size):
    return [s[i:i + chunk_size] for i in range(0, len(s), chunk_size)]


# 合并消息
# 合并消息
async def send_forward_msg_group(bot: Bot, event: GroupMessageEvent, name: str, msgs: list):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": bot.self_id, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=messages)
