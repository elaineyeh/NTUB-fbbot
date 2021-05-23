import requests


def init_get_start(sender_id, headers, params):
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
