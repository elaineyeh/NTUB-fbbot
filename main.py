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

                # IDs
                sender_id = messaging_event['sender']['id']
                # recipient_id = messaging_event['recipient']['id']

                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', PAGE_ACCESS_TOKEN),
                )

                if messaging_event.get('message'):
                    # Extracting text message
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
                                            "text": "學生端官網",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://stud.ntub.edu.tw/p/412-1007-459.php?Lang=zh-tw",
                                                    "title": "點此進入北商學生端官網"
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
                                            "text": "各式申請表單",
                                            "buttons": [
                                                {
                                                    "type": "web_url",
                                                    "url": "https://stud.ntub.edu.tw/p/412-1007-459.php?Lang=zh-tw",
                                                    "title": "點此進入北商表單官網"
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
                                            "type": "web_url",
                                            "title": "NTUB",
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
                                  "text": "Hello {{user_first_name}}!"
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

                        data = {
                            "ice_breakers": [
                                {
                                   "question": "如何進入學校官網？",
                                   "payload": "NTUB_WEB_SITE"
                                },
                                {
                                   "question": "最近學校有舉辦什麼活動？",
                                   "payload": "NTUB_ACTIVITY"
                                },
                            ]
                        }

                        response = requests.post(
                            'https://graph.facebook.com/v10.0/me/messenger_profile',
                            headers=headers,
                            params=params,
                            json=data
                        )
                        print(response.content)

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
                        return "Success", 200
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
                        return "Success", 200

        return messaging_text, 200
