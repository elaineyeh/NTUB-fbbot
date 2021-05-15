import requests
import orm
import sqlalchemy
from pymessenger import Bot
from config import Settings


PAGE_ACCESS_TOKEN = Settings().PAGE_ACCESS_TOKEN
bot = Bot(PAGE_ACCESS_TOKEN)
ngrok = "https://5f848e2eb394.ap.ngrok.io"


def search_name(sender_id, headers, params, name, **kwargs):
    print('called--------------------------------------')
    phone_list = []
    result_responses = requests.get(
        'https://api-auth.ntub.edu.tw/api/contacts/?staff_name={name}'.format(name=name))
    for result_response in result_responses.json():
        phone = "+88634506333"

        print(result_response)
        if result_response['ext'][0] != '8':
            phone = "+886233222777"
        phone = phone+","+result_response['ext']
        email = result_response['staff']['user']['email']

        datum = {
            "title": result_response['staff']['user']['chineseFullName'],
            "image_url": "https://i.imgur.com/MfU6ejy.jpg",
            "buttons": [
                {
                    "type": "web_url",
                    "title": "撥打電話",
                    "url": f'{ngrok}/phone?phone_number={phone}'
                },
                {
                    "type": "web_url",
                    "title": "撰寫信件",
                    "url": f'{ngrok}/email?email={email}'
                }
            ]
        }

        phone_list.append(datum)

    data = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": phone_list[-10:],
                }
            }
        }
    }
    print(data)

    response = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        headers=headers,
        params=params,
        json=data
    )
    print(response.content)


def search_name_text(sender_id, **kwargs):
    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()

    state = db.query(orm.State).filter(orm.State.name == 'REAL_NAME_SEARCH').one_or_none()
    if state.label:
        sending_text = state.label
        bot.send_text_message(sender_id, sending_text)

    user.state_id = state.id
    db.add(user)
    db.commit()
