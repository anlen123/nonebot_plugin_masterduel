from typing import List, Any
from .config import Config
from nonebot.plugin import on_notice, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message, GroupMessageEvent
import nonebot

from .model.Card import YgoCard
from .mapper import *
from .utils import imgUtils

global_config = nonebot.get_driver().config
config = global_config.dict()

master_duel = on_regex(pattern="^ck ")


@master_duel.handle()
async def master_duel_rev(bot: Bot, event: Event):
    cmd = event.get_plaintext()[3:]

    ygoCard = mapper.get_card_info_by_name(cmd)

    if ygoCard:

        messageSegment = await get_send_msg(ygoCard)

        await bot.send(event, messageSegment)
    else:
        await bot.send(event, MessageSegment.text("暂时只支持全名查询，后续会支持别名，模糊搜索等功能，对了， 右上角的稀有度也是假的， 后续功能完善"))

async def get_send_msg(card: YgoCard) -> MessageSegment:
    urlBase64 = imgUtils.pin_quality(int(card.id), "SR")

    return MessageSegment.text(f"{card.name}\n") + MessageSegment.image(urlBase64) + MessageSegment.text(f"{card.desc}")


def is_int(n: str):
    try:
        float_n = float(n)
        int_n = int(float_n)
    except ValueError as e:
        return False
    else:
        return float_n == int_n


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
