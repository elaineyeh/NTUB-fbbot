import requests


def ntub_room_location(sender_id=None, name=None, headers=None, params=None, **kwargs):
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
    requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        headers=headers,
        params=params,
        json=data
    )
