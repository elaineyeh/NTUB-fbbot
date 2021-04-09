from fastapi import FastAPI, Request
from pymessenger import Bot
import requests

from config import Settings

app = FastAPI()

PAGE_ACCESS_TOKEN = Settings().PAGE_ACCESS_TOKEN

bot = Bot(PAGE_ACCESS_TOKEN)


@app.get("/")
async def verify(request: Request):
    print("hub.mode = ", request.query_params['hub.mode'])
    if request.query_params['hub.mode'] == "subscribe" and request.query_params['hub.challenge']:
        if not request.query_params['hub.verify_token'] == Settings().VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return int(request.query_params['hub.challenge'])
    return "Hello world", 200


@app.post("/")
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

                if messaging_event.get('message'):
                    if messaging_event['message'].get('quick_reply'):
                        if messaging_event['message']['quick_reply']['payload'] == "NTUB_STU_SITE":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "學生資訊系統",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "http://ntcbadm1.ntub.edu.tw/",
                                                    "title": "點此進入學生資訊系統"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "NTUB_FORM_SITE":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "各式表單",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://stud.ntub.edu.tw/p/412-1007-459.php?Lang=zh-tw",
                                                    "title": "點此進入北商大表單官網"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "NTUB_CALENDAR":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "109 學年度行事曆",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://acad.ntub.edu.tw/var/file/4/1004/img/392145602.pdf",
                                                    "title": "點此查看 109 學年度行事曆"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_103":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "103 學年度行事曆",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://acad.ntub.edu.tw/var/file/4/1004/img/1022/103-schedule.pdf",
                                                    "title": "點此查看103 學年度行事曆"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_104":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "104 學年度行事曆",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://acad.ntub.edu.tw/var/file/4/1004/img/1022/142701551.pdf",
                                                    "title": "點此查看104 學年度行事曆"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_105":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "105 學年度行事曆",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://acad.ntub.edu.tw/var/file/4/1004/img/1022/151074443.pdf",
                                                    "title": "點此查看105 學年度行事曆"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_106":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "106 學年度行事曆",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://acad.ntub.edu.tw/var/file/4/1004/img/394/169062160.pdf",
                                                    "title": "點此查看106 學年度行事曆"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_107":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "107 學年度行事曆",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://acad.ntub.edu.tw/var/file/4/1004/img/394/183391456.pdf",
                                                    "title": "點此查看107 學年度行事曆"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_108":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "108 學年度行事曆",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://acad.ntub.edu.tw/var/file/4/1004/img/451462435.pdf",
                                                    "title": "點此查看108 學年度行事曆"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_109":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "109 學年度行事曆",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://acad.ntub.edu.tw/var/file/4/1004/img/392145602.pdf",
                                                    "title": "點此查看109 學年度行事曆"
                                                },
                                            ]
                                        }
                                    }
                                }
                            }
                        elif messaging_event['message']['quick_reply']['payload'] == "CALENDAR_110":
                            data = {
                                "recipient": {
                                    "id": sender_id
                                },
                                "message": {
                                    "attachment": {
                                        "type": "template",
                                        "payload": {
                                            "template_type": "button",
                                            "text": "110 學年度行事曆",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://acad.ntub.edu.tw/var/file/4/1004/img/800579906.pdf",
                                                    "title": "點此查看110 學年度行事曆"
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
                    elif messaging_event['message']['text'] == '查詢歷年行事曆':
                        data = {
                            "recipient": {
                                "id": sender_id
                            },
                            "messaging_type": "RESPONSE",
                            "message": {
                                "text": "查詢年度",
                                "quick_replies": [
                                    {
                                        "content_type": "text",
                                        "title": "103 學年度",
                                        "payload": "CALENDAR_103",
                                    }, {
                                        "content_type": "text",
                                        "title": "104 學年度",
                                        "payload": "CALENDAR_104",
                                    }, {
                                        "content_type": "text",
                                        "title": "105 學年度",
                                        "payload": "CALENDAR_105",
                                    }, {
                                        "content_type": "text",
                                        "title": "106 學年度",
                                        "payload": "CALENDAR_106",
                                    }, {
                                        "content_type": "text",
                                        "title": "107 學年度",
                                        "payload": "CALENDAR_107",
                                    }, {
                                        "content_type": "text",
                                        "title": "108 學年度",
                                        "payload": "CALENDAR_108",
                                    }, {
                                        "content_type": "text",
                                        "title": "109 學年度",
                                        "payload": "CALENDAR_109",
                                    }, {
                                        "content_type": "text",
                                        "title": "110 學年度",
                                        "payload": "CALENDAR_110",
                                    }
                                ]
                            }
                        }

                        response = requests.post(
                            'https://graph.facebook.com/me/messages',
                            headers=headers,
                            params=params,
                            json=data
                        )
                        print(response.content)
                    elif 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']

                        response = messaging_text
                        bot.send_text_message(sender_id, response)
                    else:
                        messaging_text = 'no text'

                        response = messaging_text
                        bot.send_text_message(sender_id, response)

                if messaging_event.get('postback'):
                    if messaging_event['postback']['title'] == 'Get Started':
                        data = {
                            "psid": sender_id,
                            "persistent_menu": [
                                {
                                    "locale": "default",
                                    "composer_input_disabled": False,
                                    "call_to_actions": [
                                        {
                                            "type": "postback",
                                            "title": "顯示快捷按鈕",
                                            "payload": "QUICK_REPLY"
                                        },
                                        {
                                            "type": "web_url",
                                            "title": "國立臺北商業大學",
                                            "url": "www.ntub.edu.tw",
                                            "webview_height_ratio": "full"
                                        },
                                        {
                                            "type": "web_url",
                                            "title": "學生資訊系統",
                                            "url": "http://ntcbadm1.ntub.edu.tw/",
                                            "webview_height_ratio": "full"
                                        },
                                        {
                                            "type": "web_url",
                                            "title": "Blackboard",
                                            "url": "https://bb.ntub.edu.tw",
                                            "webview_height_ratio": "full"
                                        },
                                        {
                                            "type": "web_url",
                                            "title": "北商大圖書館",
                                            "url": "http://library.ntub.edu.tw/mp.asp?mp=1",
                                            "webview_height_ratio": "full"
                                        },
                                        {
                                            "type": "web_url",
                                            "title": "北商大活動報名系統",
                                            "url": "https://signupactivity.ntub.edu.tw/activity/main",
                                            "webview_height_ratio": "full"
                                        },
                                        {
                                            "type": "web_url",
                                            "title": "各式表單",
                                            "url": "https://stud.ntub.edu.tw/p/412-1007-459.php?Lang=zh-tw",
                                            "webview_height_ratio": "full"
                                        },
                                        {
                                            "type": "web_url",
                                            "title": "臺銀學雜費入口",
                                            "url": "https://school.bot.com.tw/newTwbank/index.aspx",
                                            "webview_height_ratio": "full"
                                        },
                                        {
                                            "type": "web_url",
                                            "title": "心靈諮商室諮詢",
                                            "url": "https://counseling.ntub.edu.tw/cs_ntub/apps/cs/ntub/index.aspx",
                                            "webview_height_ratio": "full"
                                        }
                                    ]
                                }
                            ]
                        }

                        response = requests.post(
                            'https://graph.facebook.com/v10.0/me/custom_user_settings',
                            headers=headers,
                            params=params,
                            json=data
                        )
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
                        #            "question": "如何進入學校官網？",
                        #            "payload": "NTUB_WEB_SITE"
                        #         },
                        #         {
                        #            "question": "最近學校有舉辦什麼活動？",
                        #            "payload": "NTUB_ACTIVITY"
                        #         },
                        #     ]
                        # }

                        # response = requests.post(
                        #     'https://graph.facebook.com/v10.0/me/messenger_profile',
                        #     headers=headers,
                        #     params=params,
                        #     json=data
                        # )
                        # print(response.content)

                        # return "Success", 200
                        return "Success", 200

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
                return "Success", 200

        # return messaging_text, 200
