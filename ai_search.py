import orm
import requests
import pypinyin
from pypinyin import pinyin
from fuzzywuzzy import fuzz
from pymessenger import Bot
from config import Settings

from subscribed_activity import subscribed_activity
from quick_replies import quick_replies
from activity_crawling import create_formated_activities, object_as_dict, show_activity
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


# async def send_response(sender_id, headers, params, datum, **kwargs):
#     bot.send_text_message(sender_id, "這是你要找的資料嗎？")
#
#     print(datum)
#
#     data = {
#         "recipient": {
#             "id": sender_id
#         },
#         "message": {
#             "attachment": {
#                 "type": "template",
#                 "payload": {
#                     "template_type": "generic",
#                     "elements": datum,
#                 }
#             }
#         }
#     }
#
#     response = requests.post(
#         'https://graph.facebook.com/v2.6/me/messages',
#         headers=headers,
#         params=params,
#         json=data
#     )
#     print(response.content)


async def show_map(message, sender_id, headers, params, **kwargs):
    letters = ['taibei', 'taoyuan']
    message = await change_pinyin(message)

    print("Get into show map")

    for letter in letters:
        score = fuzz.ratio(letter, message)

        if score >= 40:
            if letter == 'taibei':
                print("Get into taipei map")

                data = {
                    "recipient": {
                        "id": sender_id
                    },
                    "message": {
                        "attachment": {
                            "type": "template",
                            "payload": {
                                "template_type": "generic",
                                "elements": [
                                    {
                                        "title": "台北校區教室配置圖",
                                        "image_url": "https://i.imgur.com/wGFmlNr.jpeg",
                                        "subtitle": "點此查看台北校區教室配置圖",
                                        "default_action": {
                                            "type": "web_url",
                                            "url": "shorturl.at/nAN25",
                                            "messenger_extensions": False,
                                            "webview_height_ratio": "tall",
                                        },
                                        "buttons": [
                                            {
                                                "type": "web_url",
                                                "url": "shorturl.at/nAN25",
                                                "title": "台北校區教室配置圖"
                                            }
                                        ]
                                    }
                                ]
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
            else:
                data = {
                    "recipient": {
                        "id": sender_id
                    },
                    "message": {
                        "attachment": {
                            "type": "template",
                            "payload": {
                                "template_type": "generic",
                                "elements": [
                                    {
                                        "title": "桃園校區教室配置圖",
                                        "image_url": "https://i.imgur.com/wGFmlNr.jpeg",
                                        "subtitle": "點此查看桃園校區教室配置圖",
                                        "default_action": {
                                            "type": "web_url",
                                            "url": "shorturl.at/jzCEO",
                                            "messenger_extensions": False,
                                            "webview_height_ratio": "tall",
                                        },
                                        "buttons": [
                                            {
                                                "type": "web_url",
                                                "url": "shorturl.at/jzCEO",
                                                "title": "桃園校區教室配置圖"
                                            }
                                        ]
                                    }
                                ]
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


async def set_subscribe(message, sender_id, headers, params, **kwargs):
    letters = ['huodong']
    message = await change_pinyin(message)

    for letter in letters:
        score = fuzz.ratio(letter, message)

        if score >= 50:
            await subscribed_activity(sender_id, headers, params)
        else:
            db = orm.SessionLocal()
            user = db.query(orm.User).filter(
                orm.User.fb_id == sender_id).one_or_none()
            state = db.query(orm.State).filter(
                orm.State.name == 'QUICK_REPLY').one_or_none()
            user.state_id = state.id
            db.add(user)
            db.commit()

            bot.send_text_message(sender_id, "找不到相關資訊，可以使用下方快速搜尋你想要的資料喔～")

            await quick_replies(sender_id, headers, params, state)
            db.close()


async def show_newest_activity(message, sender_id, headers, params, **kwargs):
    if message:
        print("Get into ai search message")
        db = orm.SessionLocal()
        result_activities = []
        items = db.query(orm.Activity).all()
        search_activity = await change_pinyin(message)
        for item in items:
            if message in item.activity_name:
                activity = await object_as_dict(item)
                activity_id = activity['activity_id']
                activity_name = activity['activity_name']
                start_date = activity['post_start_time'].date()
                start_time = activity['activity_period_list'][0]['ActivityStartTime']
                start_time = start_time.split('T')[1]
                start_time = start_time[:5]
                end_date = activity['post_end_time'].date()
                end_time = activity['activity_period_list'][0]['ActivityEndTime']
                end_time = end_time.split('T')[1]
                end_time = end_time[:5]
                location = activity['activity_period_list'][0]['Location']

                text = f"{start_date} {start_time}-{end_date} {end_time}\n活動地點：{location}"
                url = f"https://signupactivity.ntub.edu.tw/activity/activityDetail/{activity_id}"
                result_activities.append({
                    "title": f"{activity_name}",
                    "image_url": "https://i.imgur.com/QAcuOst.jpeg",
                    "subtitle": text,
                    "buttons": [
                        {
                            "type": "web_url",
                            "title": "我要報名",
                            "url": url
                        }
                    ]
                })
        if not result_activities:
            for item in items:
                pinyin_activity = await change_pinyin(item.activity_name)
                score = fuzz.ratio(pinyin_activity, search_activity)
                print(item.activity_name, score)
                if score > 20:
                    activity = await object_as_dict(item)
                    activity_id = activity['activity_id']
                    activity_name = activity['activity_name']
                    start_date = activity['post_start_time'].date()
                    start_time = activity['activity_period_list'][0]['ActivityStartTime']
                    start_time = start_time.split('T')[1]
                    start_time = start_time[:5]
                    end_date = activity['post_end_time'].date()
                    end_time = activity['activity_period_list'][0]['ActivityEndTime']
                    end_time = end_time.split('T')[1]
                    end_time = end_time[:5]
                    location = activity['activity_period_list'][0]['Location']

                    text = f"{start_date} {start_time}-{end_date} {end_time}\n活動地點：{location}"
                    url = f"https://signupactivity.ntub.edu.tw/activity/activityDetail/{activity_id}"
                    result_activities.append({
                        "title": f"{activity_name}",
                        "image_url": "https://i.imgur.com/QAcuOst.jpeg",
                        "subtitle": text,
                        "buttons": [
                            {
                                "type": "web_url",
                                "title": "我要報名",
                                "url": url
                            }
                        ]
                    })
        print(result_activities)

        user_activity = orm.UserActivity()
        user_activity.fb_id = sender_id
        user_activity.activity = result_activities
        db.add(user_activity)
        db.commit()
        db.close()
        await show_activity(sender_id, headers, params, **kwargs)
    else:
        await create_formated_activities(sender_id, headers, params)


async def show_calendar(message, sender_id, headers, params, **kwargs):
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
