import requests


def all_calendar(sender_id, headers, params):
    data = {
        "recipient": {
            "id": sender_id
        },
        "messaging_type": "RESPONSE",
        "message": {
            "text": "向右滑動即可選擇查詢年度",
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
