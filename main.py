from fastapi import FastAPI, Request, responses
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pymessenger import Bot
from room_location import ntub_room_location
from all_calendar import all_calendar
from link_result import link_result
from init_menu import init_menu
from search_contacts import show_phone
from quick_replies import quick_replies
from search_contacts import search_name, search_name_text, research_phone, finish_phone
from config import Settings
import sqlalchemy
import requests
import orm

app = FastAPI()

PAGE_ACCESS_TOKEN = Settings().PAGE_ACCESS_TOKEN

bot = Bot(PAGE_ACCESS_TOKEN)

flag = {}
conf = ConnectionConfig(
    MAIL_USERNAME=Settings().MAIL_USERNAME,
    MAIL_PASSWORD=Settings().MAIL_PASSWORD,
    MAIL_FROM=Settings().MAIL_FROM,
    MAIL_PORT=Settings().MAIL_PORT,
    MAIL_SERVER=Settings().MAIL_SERVER,
    MAIL_TLS=Settings().MAIL_TLS,
    MAIL_SSL=Settings().MAIL_SSL,
    USE_CREDENTIALS=Settings().USE_CREDENTIALS
)
mapping = {
    'NTUB_ROOM_LOCATION': ntub_room_location,
    'ALL_CALENDAR': all_calendar,
    'LINK_RESULT': link_result,
    'NAME_SEARCH_TEXT': search_name_text,
    'SEARCH_NAME': search_name,
    'MORE_CONTACT': show_phone,
    'RESEARCH_PHONE': research_phone,
    'FINISH_PHONE': finish_phone
}


@app.get("/phone")
async def phone(phone_number: str):
    return responses.RedirectResponse(f"tel:{phone_number}", status_code=302)


@app.get("/email")
async def email(email: str):
    return responses.RedirectResponse(f"mailto:{email}", status_code=302)


@app.get("/")
async def verify(request: Request):
    print("hub.mode = ", request.query_params['hub.mode'])
    if request.query_params['hub.mode'] == "subscribe" and request.query_params['hub.challenge']:
        if not request.query_params['hub.verify_token'] == Settings().VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return int(request.query_params['hub.challenge'])
    return "Hello world", 200

headers = {
    'Content-Type': 'application/json',
}
params = (
    ('access_token', PAGE_ACCESS_TOKEN),
)


def process_postback(messaging, postback):
    # 1. user
    # 2. state
    # 3. get all sub states
    # 4. compare postback in sub states
    # 5. response
    global headers, params
    db = orm.SessionLocal()
    user_fb_id = messaging['sender']['id']
    user = db.query(orm.User).filter(
        orm.User.fb_id == user_fb_id
    ).one_or_none()
    if user is None:
        db_user = orm.User()
        db_user.fb_id = user_fb_id
        db.add(db_user)
        db.commit()
        user = db_user
    sub_states = db.query(orm.State).filter(
        orm.State.parent_id == user.state_id
    ).all()
    if not sub_states:
        pass
    sub_state_names = [
        sub_state.name
        for sub_state
        in sub_states
    ]
    payload = postback['payload']
    if payload in sub_state_names:
        # Change user state to input state
        state = db.query(orm.State).filter(
            orm.State.name == payload
        ).first()
        user.state_id = state.id
        db.add(user)
        db.commit()
        # Execute state function
        print(state.function)
        if state.function:
            function = mapping.get(state.function)
            function(sender_id=user.fb_id, headers=headers,
                     params=params, name=payload)
            if not db.query(orm.State).filter(
                orm.State.parent_id == user.state_id
            ).all():
                user.state_id = sqlalchemy.sql.null()
            db.add(user)
            db.commit()
            return
        sub_states = db.query(orm.State).filter(
            orm.State.parent_id == user.state_id
        ).all()
        # Find next states
        data = {
            "recipient": {
                "id": user.fb_id
            },
            "messaging_type": "RESPONSE",
            "message": {
                "text": state.label,
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": sub_state.label,
                        "payload": sub_state.name,
                    }
                    for sub_state in sub_states
                ]
            }
        }
        requests.post(
            'https://graph.facebook.com/v10.0/me/messages',
            headers=headers,
            params=params,
            json=data
        )
    db.close()


def process_message(messaging, message):
    # 1. user
    # 2. state
    # 3. get all sub states
    # 4. compare message in sub states
    # 5. response
    global headers, params
    db = orm.SessionLocal()
    user_fb_id = messaging['sender']['id']
    user = db.query(orm.User).filter(
        orm.User.fb_id == user_fb_id
    ).one_or_none()
    if user is None:
        db_user = orm.User()
        db_user.fb_id = user_fb_id
        db.add(db_user)
        db.commit()
        user = db_user
    sub_states = db.query(orm.State).filter(
        orm.State.parent_id == user.state_id
    ).all()
    if not sub_states:
        pass
    sub_state_names = [
        sub_state.name
        for sub_state
        in sub_states
    ]
    # NTUB_ROOM_LOCATION
    payload = None
    if 'quick_reply' in message:
        payload = message['quick_reply']['payload']
    elif 'text' in message:
        payload = message['text']

    state = db.query(orm.State).filter(
        orm.State.id == user.state_id).one_or_none()
    print(payload, sub_state_names)
    if payload in sub_state_names:
        state = db.query(orm.State).filter(
            orm.State.name == payload
        ).first()
        # Change user state to input state
        user.state_id = state.id
        db.add(user)
        db.commit()
        # Execute state function
        print(state.function)
        if state.function:
            if not db.query(orm.State).filter(
                orm.State.parent_id == user.state_id
            ).all():
                user.state_id = sqlalchemy.sql.null()
            db.add(user)
            db.commit()
            function = mapping.get(state.function)
            function(sender_id=user.fb_id, headers=headers,
                     params=params, name=payload)
            return
        # Find next states
        quick_replies(user.fb_id, headers, params, state)
    elif state and state.is_input and state.function:
        print('in ', state, state.is_input, state.function)
        function = mapping.get(state.function)
        function(sender_id=user.fb_id, headers=headers,
                 params=params, name=payload)
        if not db.query(orm.State).filter(
            orm.State.parent_id == user.state_id
        ).all():
            user.state_id = sqlalchemy.sql.null()
        db.add(user)
        db.commit()
        return

    db.close()


def process_messaging(messaging):
    if 'postback' in messaging:
        process_postback(messaging, messaging['postback'])
    if 'message' in messaging:
        process_message(messaging, messaging['message'])


@app.post("/")
async def new(request: Request):
    print(await request.json())
    data = await request.json()
    for entry in data['entry']:
        for messaging in entry['messaging']:
            process_messaging(messaging)
    return "Success", 200
    # is_postback = 'postback' in data['entry'][0]
    '''
    # postback
    {
        'object': 'page',
        'entry': [
            {'id': '112374620901935',
             'time': 1620468150834,
             'messaging': [
                 {
                     'sender': {'id': '3843687509051581'},
                     'recipient': {'id': '112374620901935'},
                     'timestamp': 1620468150655,
                     'postback': {'title': '顯示快捷按鈕', 'payload': 'QUICK_REPLY'}
                 }
             ]
             }
        ]
    }
    '''
    '''
    text
    {
        'object': 'page',
        'entry': [
            {'id': '112374620901935',
             'time': 1620468157945,
             'messaging': [
                 {'sender': {'id': '3843687509051581'},
                  'recipient': {'id': '112374620901935'},
                  'timestamp': 1620468157832,
                  'message': {
                     'mid': 'm_MeUVO9WfB3gaQ9NsQegMC9Y5gb9XBhcIq6OgbtUm9g6sp_zKkcQ0cAc-sssygb0_W02eu_SoTOlrTYQCD-8Khw',
                     'text': '教室配置圖',
                     'quick_reply': {'payload': 'NTUB_ROOM_LOCATION'}
                 }
                 }
             ]
             }
        ]
    }
    '''


@app.post("/old")
async def echo(request: Request):
    print(await request.json())
    data = await request.json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                # recipient_id = messaging_event['recipient']['id']
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', PAGE_ACCESS_TOKEN),
                )

                init_menu(sender_id, headers, params)

                if messaging_event.get('message'):
                    if messaging_event['message'].get('quick_reply'):
                        web_url = ""
                        title = ""
                        text = ""
                        if messaging_event['message']['quick_reply']['payload'] == "NTUB_STU_SITE":
                            web_url = "http://ntcbadm1.ntub.edu.tw/"
                            title = "點此進入學生資訊系統"
                            text = "學生資訊系統"
                        elif messaging_event['message']['quick_reply']['payload'] == "NTUB_FORM_SITE":
                            web_url = "https://stud.ntub.edu.tw/p/412-1007-459.php?Lang=zh-tw"
                            title = "點此進入北商大表單官網"
                            text = "各式表單"
                        elif messaging_event['message']['quick_reply']['payload'] == "NTUB_CALENDAR":
                            web_url = "https://acad.ntub.edu.tw/var/file/4/1004/img/392145602.pdf"
                            title = "點此查看 109 學年度行事曆"
                            text = "109 學年度行事曆"
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_103":
                            web_url = "https://acad.ntub.edu.tw/var/file/4/1004/img/1022/103-schedule.pdf"
                            title = "點此查看103 學年度行事曆"
                            text = "103 學年度行事曆"
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_104":
                            web_url = "https://acad.ntub.edu.tw/var/file/4/1004/img/1022/142701551.pdf"
                            title = "點此查看104 學年度行事曆"
                            text = "104 學年度行事曆"
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_105":
                            web_url = "https://acad.ntub.edu.tw/var/file/4/1004/img/1022/151074443.pdf"
                            title = "點此查看105 學年度行事曆"
                            text = "105 學年度行事曆"
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_106":
                            web_url = "https://acad.ntub.edu.tw/var/file/4/1004/img/394/169062160.pdf"
                            title = "點此查看106 學年度行事曆"
                            text = "106 學年度行事曆"
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_107":
                            web_url = "https://acad.ntub.edu.tw/var/file/4/1004/img/394/183391456.pdf"
                            title = "點此查看107 學年度行事曆"
                            text = "107 學年度行事曆"
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_108":
                            web_url = "https://acad.ntub.edu.tw/var/file/4/1004/img/451462435.pdf"
                            title = "點此查看108 學年度行事曆"
                            text = "108 學年度行事曆"
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_109":
                            web_url = "https://acad.ntub.edu.tw/var/file/4/1004/img/392145602.pdf"
                            title = "點此查看109 學年度行事曆"
                            text = "109 學年度行事曆"
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_110":
                            web_url = "https://acad.ntub.edu.tw/var/file/4/1004/img/800579906.pdf"
                            title = "點此查看110 學年度行事曆"
                            text = "110 學年度行事曆"
                        elif messaging_event['message']['quick_reply']['payload'] == "NTUB_ROOM_LOCATION":
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
                                                    "image_url": "https://i.imgur.com/MfU6ejy.jpg",
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
                                                }, {
                                                    "title": "桃園校區教室配置圖",
                                                    "image_url": "https://i.imgur.com/MfU6ejy.jpg",
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

                        # data = {
                        #     "recipient": {
                        #         "id": sender_id
                        #     },
                        #     "message": {
                        #         "attachment": {
                        #             "type": "template",
                        #             "payload": {
                        #                 "template_type": "button",
                        #                 "text": text,
                        #                 "buttons": [
                        #                     {
                        #                         "type": "web_url",
                        #                         "url": web_url,
                        #                         "title": title
                        #                     },
                        #                 ]
                        #             }
                        #         }
                        #     }
                        # }

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
                                                "title": text,
                                                "image_url": "https://i.imgur.com/MfU6ejy.jpg",
                                                "subtitle": title,
                                                "default_action": {
                                                    "type": "web_url",
                                                    "url": web_url,
                                                    "messenger_extensions": False,
                                                    "webview_height_ratio": "tall",
                                                },
                                                "buttons": [
                                                    {
                                                        "type": "web_url",
                                                        "url": web_url,
                                                        "title": text
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
                    elif 'text' in messaging_event['message'] and messaging_event['message']['text'] == '查詢歷年行事曆':
                        all_calendar(sender_id, headers, params)
                    elif 'text' in messaging_event['message']:
                        if sender_id in flag:
                            if flag[sender_id] == 1:
                                feedback = messaging_event['message']['text']

                                message = MessageSchema(
                                    subject="UB 醬意見回饋",
                                    recipients=Settings().RECEPI_EMAIL,
                                    body=feedback,
                                    subtype="html"
                                )

                                fm = FastMail(conf)
                                await fm.send_message(message)
                                text = "謝謝您留下寶貴的意見，我們將盡快處理"
                                bot.send_text_message(sender_id, text)
                                flag[sender_id] = 0
                                print(flag[sender_id])
                            else:
                                messaging_text = messaging_event['message']['text']
                                response = messaging_text
                                bot.send_text_message(sender_id, response)
                        else:
                            messaging_text = messaging_event['message']['text']
                            response = messaging_text
                            bot.send_text_message(sender_id, response)
                    else:
                        messaging_text = 'no text'

                        response = messaging_text
                        bot.send_text_message(sender_id, response)

                if messaging_event.get('postback'):
                    # Initialize
                    if messaging_event['postback']['title'] == 'Get Started':
                        print(response.content)

                        data = {
                            "psid": sender_id,
                            "greeting": [
                                {
                                    "locale": "default",
                                    "text": "Hello {{user_first_name}}! 我是 UB醬，很高興為您服務 !"
                                }
                            ]
                        }

                        response = requests.post(
                            'https://graph.facebook.com/v10.0/me/messenger_profile',
                            headers=headers,
                            params=params,
                            json=data
                        )
                        print(response.content)

                        # data = {
                        #     "ice_breakers": [
                        #         {
                        #             "question": "如何進入學校官網？",
                        #             "payload": "NTUB_WEB_SITE"
                        #         },
                        #         {
                        #             "question": "最近學校有舉辦什麼活動？",
                        #             "payload": "NTUB_ACTIVITY"
                        #         },
                        #     ]
                        # }
#
                        # response = requests.post(
                        #     'https://graph.facebook.com/v10.0/me/messenger_profile',
                        #     headers=headers,
                        #     params=params,
                        #     json=data
                        # )
                        # print(response.content)

                        # return "Success", 200

                    if messaging_event['postback']['payload'] == 'NTUB_WEB_SITE':
                        data = {
                            "recipient": {
                                "id": sender_id
                            },
                            "message": {
                                "attachment": {
                                    "type": "template",
                                    "payload": {
                                        "template_type": "button",
                                        "text": "國立臺北商業大學",
                                        "buttons": [
                                            {
                                                "type": "web_url",
                                                "url": "https://www.ntub.edu.tw",
                                                "title": "點此進入北商官網"
                                            },
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
                        # return "Success", 200
                    elif messaging_event['postback']['payload'] == 'QUICK_REPLY':
                        data = {
                            "recipient": {
                                "id": sender_id
                            },
                            "messaging_type": "RESPONSE",
                            "message": {
                                "text": "歡迎使用 UB 醬，下方有快速按鈕以及選單可以選擇",
                                "quick_replies": [
                                    {
                                        "content_type": "text",
                                        "title": "學生資訊系統",
                                        "payload": "NTUB_STU_SITE",
                                    }, {
                                        "content_type": "text",
                                        "title": "各式表單申請",
                                        "payload": "NTUB_FORM_SITE",
                                    }, {
                                        "content_type": "text",
                                        "title": "109 學年度行事曆",
                                        "payload": "NTUB_CALENDAR",
                                    }, {
                                        "content_type": "text",
                                        "title": "教室配置圖",
                                        "payload": "NTUB_ROOM_LOCATION",
                                    }
                                ]
                            }
                        }
                        response = requests.post(
                            'https://graph.facebook.com/v10.0/me/messages',
                            headers=headers,
                            params=params,
                            json=data
                        )
                        print(response.content)
                    elif messaging_event['postback']['payload'] == 'NTUB_ACTIVITY':
                        data = {
                            "recipient": {
                                "id": sender_id
                            },
                            "message": {
                                "attachment": {
                                    "type": "template",
                                    "payload": {
                                        "template_type": "button",
                                        "text": "活動報名系統",
                                        "buttons": [
                                            {
                                                "type": "web_url",
                                                "url": "https://signupactivity.ntub.edu.tw/activity/main",
                                                "title": "點此進入北商大活動報名系統"
                                            },
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
                        # return "Success", 200
                    elif messaging_event['postback']['payload'] == 'FEEDBACK':
                        flag[sender_id] = 1

                        response = "感謝您的使用，如有遇到任何使用上的問題，請在下方寫下您寶貴的意見"
                        bot.send_text_message(sender_id, response)
                        print(flag[sender_id])

                return "Success", 200

        # return messaging_text, 200
