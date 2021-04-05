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

                if messaging_event.get('message'):
                    # Extracting text message
                    if 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']
                    else:
                        messaging_text = 'no text'

                    # Echo
                    response = messaging_text
                    bot.send_text_message(sender_id, response)

                elif messaging_event.get('postback'):
                    if messaging_event['postback']['title'] == 'Get Started':
                        headers = {
                            'Content-Type': 'application/json',
                        }
                        params = (
                            ('access_token', PAGE_ACCESS_TOKEN),
                        )
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
                        return "Success", 200
    return messaging_text, 200
