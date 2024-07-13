from typing import List, Any
from .config import Config
from nonebot.plugin import on_notice, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message, GroupMessageEvent
import nonebot, os, random

from .model.Card import YgoCard
from .mapper import *
from .utils import imgUtils
from .utils import rarityUtils

global_config = nonebot.get_driver().config
config = global_config.dict()

master_duel = on_regex(pattern="^ck")
master_duel_CK = on_regex(pattern="^CK")


@master_duel.handle()
@master_duel_CK.handle()
async def master_duel_rev(bot: Bot, event: Event):
    cmd = event.get_plaintext()[2:]
    cmd = cmd.strip()
    if not cmd:
        return

    ygoCard = mapper.get_card_info_by_alias(cmd)

    if not ygoCard:
        cardId = get_max_like_id(cmd)
        ygoCard = get_card_info_by_id(cardId)

    if ygoCard:

        messageSegment = await get_send_msg(ygoCard)

        await bot.send(event, messageSegment)
        directory = f"D:\\nb2\my_nonebot2\plugins\\nonebot_plugin_masterduel\\nonebot_plugin_masterduel\img\\{ygoCard.id}"
        if os.path.exists(directory):
            files = os.listdir(directory)
            print(directory)
            print(random.choice(files))
            file = directory + "\\" + random.choice(files)
            print(file)
            await bot.send(event, MessageSegment.image(file))
    else:
        await bot.send(event, MessageSegment.text("暂时只支持全名查询，后续会支持别名，模糊搜索等功能，后续功能完善"))


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
        await bot.send(event, MessageSegment.text(
            "暂时只支持全名查询，后续会支持别名，模糊搜索等功能， 后续功能完善"))
        return
    ygoCardList = ygoCardList[:20]
    msgs = ""
    for card in ygoCardList:
        msgs += MessageSegment.text(f"卡号：{card.id}      {card.name}\n\n")
    await bot.send(event=event, message=msgs)


# 合并消息
async def send_forward_msg_group(
        bot: Bot,
        event: GroupMessageEvent,
        name: str,
        msgs: List[str],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": bot.self_id, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )
