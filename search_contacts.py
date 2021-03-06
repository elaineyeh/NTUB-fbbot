import requests
import orm
from pymessenger import Bot
from config import Settings
from quick_replies import quick_replies


PAGE_ACCESS_TOKEN = Settings().PAGE_ACCESS_TOKEN
bot = Bot(PAGE_ACCESS_TOKEN)
ngrok = "https://36fd-27-240-176-17.ngrok.io"


async def research_phone(sender_id, headers, params, **kwargs):
    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
    state = db.query(orm.State).filter(orm.State.name == 'SEARCH_PHONE').one_or_none()
    user.state_id = state.id
    db.add(user)
    db.commit()
    print(user.fb_id, state.name, '----------- is me research phone')

    await quick_replies(sender_id, headers, params, state)
    db.close()


async def none_search(sender_id, headers, params, **kwargs):
    data = {
        "recipient": {
            "id": sender_id
        },
        "messaging_type": "RESPONSE",
        "message": {
            "text": "查無資料，請問要繼續查詢嗎？",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "重新查詢",
                    "payload": "RESEARCH_PHONE",
                }, {
                    "content_type": "text",
                    "title": "結束查詢",
                    "payload": "FINISH_PHONE",
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


async def finish_phone(sender_id, headers, params, **kwargs):
    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
    state = db.query(orm.State).filter(orm.State.name == 'QUICK_REPLY').one_or_none()
    user.state_id = state.id
    db.add(user)
    db.commit()
    db.close()

    await quick_replies(sender_id, headers, params, state)


async def show_result(sender_id, headers, params, result_responses, **kwargs):
    phone_list = []
    db = orm.SessionLocal()

    if not result_responses.json():
        user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
        state = db.query(orm.State).filter(orm.State.name == "NO_SEARCH").one_or_none()
        user.state_id = state.id
        db.add(user)
        db.commit()

        await none_search(sender_id, headers, params)
        return

    for result_response in result_responses.json():
        phone = "+88634506333"

        if result_response['ext'][0] != '8':
            phone = "0233222777"
        phone = phone+","+result_response['ext']
        email = result_response['staff']['user']['email']

        datum = {
            "title": result_response['staff']['user']['chineseFullName'],
            "image_url": "https://i.imgur.com/DjboxZ7.jpeg",
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

    contact = orm.Contact()
    contact.fb_id = sender_id
    contact.contact = phone_list
    db.add(contact)
    db.commit()
    db.close()

    await show_phone(sender_id, headers, params)


async def search_name(sender_id, headers, params, name, **kwargs):
    print('called name--------------------------------------')

    result_responses = requests.get(
        'https://api-auth.ntub.edu.tw/api/contacts/?staff_name={name}'.format(name=name))

    await show_result(sender_id, headers, params, result_responses, **kwargs)


async def search_location(sender_id, headers, params, label, **kwargs):
    print('called location--------------------------------------')
    result_responses = requests.get(
        'https://api-auth.ntub.edu.tw/api/contacts/?staff_group={label}'.format(label=label))

    await show_result(sender_id, headers, params, result_responses, **kwargs)


async def search_subject(sender_id, headers, params, label, **kwargs):
    print('called subject--------------------------------------')
    result_responses = requests.get(
        'https://api-auth.ntub.edu.tw/api/contacts/?staff_group={label}'.format(label=label))

    await show_result(sender_id, headers, params, result_responses, **kwargs)


async def show_phone(sender_id, headers, params, **kwargs):
    print("called---------------------------------")
    db = orm.SessionLocal()
    contact = db.query(orm.Contact).filter(
        orm.Contact.fb_id == sender_id).order_by(orm.Contact.id.desc()).first()
    phone = contact.contact

    phone_result = phone
    if len(phone) > 10:
        phone_result = phone[-9:]
        phone_result.append({
            "title": "沒有找到你想要的嗎？",
            "image_url": "https://i.imgur.com/DjboxZ7.jpeg",
            "buttons": [
                {
                    "type": "postback",
                    "title": "點我看更多",
                    "payload": "MORE_CONTACT"
                }
            ]
        })
        contact.contact = phone[:len(phone)-9]
        db.add(contact)
        db.commit()
    else:
        contact.contact = []

    if contact.contact:
        user = db.query(orm.User).filter(
            orm.User.fb_id == sender_id).one_or_none()
        state = db.query(orm.State).filter(
            orm.State.name == "REAL_NAME_SEARCH").one_or_none()
        user.state_id = state.id
        db.add(user)
        db.commit()

    data = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": phone_result,
                }
            }
        }
    }

    db.close()

    requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        headers=headers,
        params=params,
        json=data
    )


async def search_name_text(sender_id, **kwargs):
    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()

    state = db.query(orm.State).filter(
        orm.State.name == 'REAL_NAME_SEARCH').one_or_none()
    if state.label:
        sending_text = state.label
        bot.send_text_message(sender_id, sending_text)

    user.state_id = state.id
    db.add(user)
    db.commit()
    db.close()
