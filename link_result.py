import sqlalchemy
import requests
import orm


def link_result(sender_id=None, name=None, headers=None, params=None, **kwargs):
    print("called")
    link_list = []
    db = orm.SessionLocal()
    links = db.query(orm.Link).filter(
        orm.Link.name == name
    ).all()

    for link in links:
        datum = {
            "title": link.title,
            "image_url": "https://i.imgur.com/MfU6ejy.jpg",
            "subtitle": link.discription,
            "default_action": {
                "type": "web_url",
                "url": link.img_url,
                "messenger_extensions": False,
                "webview_height_ratio": "tall",
            },
            "buttons": [
                {
                    "type": "web_url",
                    "url": link.url,
                    "title": link.button_label
                }
            ]
        }

        link_list.append(datum)

    data = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": link_list,
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
