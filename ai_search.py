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
            await link_result(sender_id, name, headers, params)
            return

    name = "CALENDAR_110"

    await link_result(sender_id, name, headers, params)


async def show_contact(message, sender_id, headers, params, flag=None, **kwargs):
    db = orm.SessionLocal()
    contactlist = db.query(orm.ContactList).all()

    print("called show_contect")

    for item in contactlist:
        message = await change_pinyin(message)
        key = await change_pinyin(item.name)
        if key in message:
            name = item.name
            print("use contactlist------------")
            print("name = ", name)
            await search_contact(sender_id, headers, params, name)
            db.close()
            return

    contactnamelist = db.query(orm.ContactNameList).order_by(
        orm.ContactNameList.id.desc()).all()
    for item in contactnamelist:
        if item.name in message:
            name = item.name
            print("use contactnamelist------------")
            await search_contact(sender_id, headers, params, name)
            db.close()
            return

    if flag:
        return True

    await show_result(sender_id, headers, params, result_responses=None)


async def search_contact(sender_id, headers, params, name):
    result_responses = requests.get(
        'https://api-auth.ntub.edu.tw/api/contacts/?search={name}'.format(name=name))

    await show_result(sender_id, headers, params, result_responses)


async def search_subject(message, sender_id, headers, params, **kwargs):
    years = ['100', '101', '102', '103', '104',
             '105', '106', '107', '108', '109']
    systems = {'wuzhuan': 'FIVE', 'erji': 'TWO', 'siji': 'FOUR',
               'shuoshi': 'MASTER_DEGREE', 'boshi': 'PHD'}
    results = {}
    max_val = 0
    max_score_name = ""

    pinyin_message = await change_pinyin(message)

    for year in years:
        if year in pinyin_message:
            search_year = year
            message = message.replace(year, "")
            for system in systems:
                if system in pinyin_message:
                    search_system = systems.get(system)
                    message = await change_pinyin(message)
                    db = orm.SessionLocal()
                    links = db.query(orm.Link).all()

                    for link in links:
                        if search_year in link.name and search_system in link.name:
                            title = link.title
                            title = title[8:]
                            title = await change_pinyin(title)
                            results[title] = link.name

                    for item in results:
                        score = fuzz.ratio(item, message)
                        print(item, results[item], score)
                        if score > max_val:
                            max_val = score
                            max_score_name = results[item]

                    if max_score_name:
                        print(max_score_name)
                        name = max_score_name

                        await link_result(sender_id, name, headers, params)
                        db.close()
                        return

            state_name = search_year + "_class"
            state = db.query(orm.State).filter(
                orm.State.name == state_name).one_or_none()
            user = db.query(orm.User).filter(
                orm.User.fb_id == sender_id).one_or_none()
            user.state_id = state.id
            db.add(user)
            db.commit()

            await quick_replies(sender_id, headers, params, state)
            db.close()

    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
    state = db.query(orm.State).filter(
        orm.State.name == 'QUICK_REPLY').one_or_none()
    user.state_id = state.id
    db.add(user)
    db.commit()

    bot.send_text_message(sender_id, "找不到相關資訊，可以使用下方快速搜尋你想要的資料喔～")

    await quick_replies(sender_id, headers, params, state)
    db.close()


async def show_form(message, sender_id, headers, params, **kwargs):
    db = orm.SessionLocal()
    links = db.query(orm.Link).all()
    results = {}
    max_val = 0
    max_score_name = ""

    message = await change_pinyin(message)

    for link in links:
        if "課程科目表" not in link.button_label and "配置圖" not in link.button_label and "行事曆" not in link.button_label:
            print(link.button_label)
            pinyin_link_button_label = await change_pinyin(link.button_label)
            score = fuzz.ratio(pinyin_link_button_label, message)
            print(link.name, " ", score)
            results[link.name] = score

    for item in results:
        if results[item] > max_val:
            max_val = results[item]
            max_score_name = item

    print("max_score_name", max_score_name)

    if max_score_name:
        name = max_score_name
        print("The max_score_name is ", name)

        await link_result(sender_id, name, headers, params)
        db.close()
        return

    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
    state = db.query(orm.State).filter(
        orm.State.name == 'QUICK_REPLY').one_or_none()
    user.state_id = state.id
    db.add(user)
    db.commit()

    bot.send_text_message(sender_id, "找不到相關資訊，可以使用下方快速搜尋你想要的資料喔～")

    await quick_replies(sender_id, headers, params, state)
    db.close()


async def detect_action(message, sender_id, headers, params, **kwargs):
    # 1. 判斷功能
    # 2. 拿掉功能關鍵字
    # 3. 跑對應的 funcion
    action_list = [
        {
            "keys": ["打電話", "打給", "撥打", "撥給", "電話", "號碼"],
            "function": show_contact,
        },
        {
            "keys": ["email", "寫信", "信箱", "郵件", "寄信", "郵箱"],
            "function": show_contact,
        },
        {
            "keys": ["地圖", "校園地圖", "在哪裡", "怎麼去", "教室"],
            "function": show_map,
        },
        {
            "keys": ["學分", "課程科目表", "課程", "課表"],
            "function": search_subject,
        },
        {
            "keys": ["訂閱", "訂閱活動"],
            "function": set_subscribe,
        },
        {
            "keys": ["最新活動", "活動"],
            "function": show_newest_activity,
        },
        {
            "keys": ["行事曆"],
            "function": show_calendar,
        },
        {
            "keys": ["表單", "表單連結", "連結"],
            "function": show_form,
        }
    ]

    if message is not None:
        for action in action_list:
            for key in action["keys"]:
                if key in message:
                    message = message.replace(key, "")
                    print("message ", message)
                    print("function ", action["function"])
                    await action["function"](message, sender_id, headers, params)
                    return

        print("call show_contact with teacher name")
        none_contact = await show_contact(message, sender_id, headers, params, flag=True)
        if none_contact:
            bot.send_text_message(sender_id, "找不到相關資訊，可以使用下方快速搜尋你想要的資料喔～")

        db = orm.SessionLocal()
        user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
        state = db.query(orm.State).filter(orm.State.name == 'QUICK_REPLY').one_or_none()
        user.state_id = state.id
        db.add(user)
        db.commit()

        await quick_replies(sender_id, headers, params, state)
        db.close()
