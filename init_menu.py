import asyncio
import requests
import orm
from config import Settings
from pymessenger import Bot


PAGE_ACCESS_TOKEN = Settings().PAGE_ACCESS_TOKEN

bot = Bot(PAGE_ACCESS_TOKEN)


async def init_menu(sender_id, headers, params):
    text = "請點選右下方第一個圖示選擇功能"
    bot.send_text_message(sender_id, text)

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
                        "type": "postback",
                        "title": "訂閱活動通知",
                        "payload": "SUBCRIBE_ACTIVITY"
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
                        "title": "臺銀學雜費入口",
                        "url": "https://school.bot.com.tw/newTwbank/index.aspx",
                        "webview_height_ratio": "full"
                    },
                    {
                        "type": "web_url",
                        "title": "心靈諮商室諮詢",
                        "url": "https://counseling.ntub.edu.tw/cs_ntub/apps/cs/ntub/index.aspx",
                        "webview_height_ratio": "full"
                    }, {
                        "type": "postback",
                        "title": "意見回饋",
                        "payload": "FEEDBACK"
                    }
                ]
            }
        ]
    }

    resp = requests.post(
        'https://graph.facebook.com/v10.0/me/custom_user_settings',
        headers=headers,
        params=params,
        json=data
    )
    print(resp.json())
    print("finished init menu")

print(__name__)
if __name__ == '__main__':
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('access_token', PAGE_ACCESS_TOKEN),
    )
    data = '{ "get_started": {"payload": "Hi I am UB jun"} }'

    db = orm.SessionLocal()
    users = db.query(orm.User).all()

    for user in users:
        psid = user.fb_id
        requests.delete(
            f'https://graph.facebook.com/v10.0/me/custom_user_settings?psid={psid}&'
            f'params=[%22persistent_menu%22]&access_token={PAGE_ACCESS_TOKEN}')

        response = requests.post(
            'https://graph.facebook.com/v2.6/me/messenger_profile',
            headers=headers,
            params=params,
            data=data)

        asyncio.run(init_menu(psid, headers, params))
