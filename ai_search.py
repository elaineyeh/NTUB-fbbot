import orm
import requests
import pypinyin
from pypinyin import pinyin
from fuzzywuzzy import fuzz
from pymessenger import Bot
from config import Settings

from subscribed_activity import subscribed_activity
from quick_replies import quick_replies
from activity_crawling import create_formated_activities
from link_result import link_result
from search_contacts import show_result


PAGE_ACCESS_TOKEN = Settings().PAGE_ACCESS_TOKEN
bot = Bot(PAGE_ACCESS_TOKEN)


async def change_pinyin(message):
    messages = pinyin(message, style=pypinyin.NORMAL)
    result_message = ""

    for message in messages:
        for item in message:
            result_message += item

    return result_message


def send_response(sender_id, headers, params, datum, **kwargs):
    data = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": datum,
                }
            }
        }
    }

    response = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        headers=headers,
        params=params,
        json=data
    )
    print(response.content)


def show_map(message, sender_id, headers, params):
    letters = ['taibei', 'taoyuan']
    message = change_pinyin(message)

    for letter in letters:
        score = fuzz.ratio(letter, message)

        if score >= 50:
            if letter == 'taibei':
                datum = {
                    "title": "臺北校區教室配置圖",
                    "image_url": "https://i.imgur.com/vCL7hQk.jpg",
                    "subtitle": "點此查看臺北校區教室配置圖",
                    "default_action": {
                        "type": "web_url",
                        "url": "https://acad.ntub.edu.tw/var/file/4/1004/attach/83/pta_49070_6919927_50529.pdf",
                        "messenger_extensions": False,
                        "webview_height_ratio": "tall",
                    },
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": "https://acad.ntub.edu.tw/var/file/4/1004/attach/83/pta_49070_6919927_50529.pdf",
                            "title": "臺北校區教室配置圖"
                        }
                    ]
                }
            else:
                datum = {
                    "title": "桃園校區教室配置圖",
                    "image_url": "https://i.imgur.com/vCL7hQk.jpg",
                    "subtitle": "點此查看桃園校區教室配置圖",
                    "default_action": {
                        "type": "web_url",
                        "url": "https://gen.ntub.edu.tw/var/file/9/1009/img/1596/6.2.Buildinglayout.pdf",
                        "messenger_extensions": False,
                        "webview_height_ratio": "tall",
                    },
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": "https://gen.ntub.edu.tw/var/file/9/1009/img/1596/6.2.Buildinglayout.pdf",
                            "title": "桃園校區教室配置圖"
                        }
                    ]
                }

        send_response(sender_id, headers, params, datum)


def set_subscribe(message, sender_id, hearders, params):
    letters = ['huodong']
    message = change_pinyin(message)

    for letter in letters:
        score = fuzz.ratio(letter, message)

        if score >= 50:
            subscribed_activity(sender_id, hearders, params)
        else:
            db = orm.SessionLocal()
            user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
            state = db.query(orm.State).filter(orm.State.name == 'QUICK_REPLY').one_or_none()
            user.state_id = state.id
            db.add(user)
            db.commit()

            quick_replies(sender_id, hearders, params, state)


def show_newest_activity(sender_id, hearders, params):
    create_formated_activities(sender_id, hearders, params)


def show_calendar(message, sender_id, hearders, params):
    annuals = ["103", "104", "105", "106", "107", "108", "109", "110"]

    for annual in annuals:
        if annual in message:
            name = "CALENDAR_" + annual
            link_result(sender_id, name, hearders, params)
            return

    name = "CALENDAR_110"
    link_result(sender_id, name, hearders, params)


def detect_action(message, sender_id, headers, params, **kwargs):
    # 1. 判斷功能
    # 2. 拿掉功能關鍵字
    # 3. 跑對應的 funcion
    action_list = [
        {
            "keys": ["打電話", "打給", "撥打", "撥給", "電話", "號碼"],
            "function": fake_function,
        },
        {
            "keys": ["email", "寫信", "信箱", "郵件", "寄信", "郵箱"],
            "function": fake_function,
        },
        {
            "keys": ["地圖", "校園地圖", "在哪裡", "怎麼去", "教室"],
            "function": show_map,
        },
        {
            "keys": ["學分", "課程科目表", "課程", "課表"],
            "function": fake_function,
        },
        {
            "keys": ["訂閱"],
            "function": set_subscribe,
        },
        {
            "keys": ["最新活動", "活動"],
            "function": show_newest_activity,
        },
        {
            "keys": ["行事曆"],
            "function": show_calendar,
        }
    ]

    for action in action_list:
        for key in action["keys"]:
            if key in message:
                message = message.replace(key, "")
                action["function"](message, sender_id, headers, params)