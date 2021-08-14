from fastapi import FastAPI, Request, responses, Header
from pymessenger import Bot
from link_result import link_result
from search_contacts import show_phone
from quick_replies import quick_replies
from feedback import feedback, send_feedback
from search_contacts import (
    search_name,
    search_name_text,
    research_phone,
    finish_phone,
    search_subject,
    search_location
)
from init_menu import init_menu
from activity_crawling import user_identify, show_activity, create_formated_activities
from config import Settings
from typing import Optional
import sqlalchemy
import requests
import orm
import re

app = FastAPI()

PAGE_ACCESS_TOKEN = Settings().PAGE_ACCESS_TOKEN
bot = Bot(PAGE_ACCESS_TOKEN)

flag = {}

mapping = {
    'LINK_RESULT': link_result,
    'NAME_SEARCH_TEXT': search_name_text,
    'SEARCH_NAME': search_name,
    'MORE_CONTACT': show_phone,
    'RESEARCH_PHONE': research_phone,
    'SEARCH_SUBJECT': search_subject,
    "SEARCH_LOCATION": search_location,
    'FINISH_PHONE': finish_phone,
    'FEEDBACK': feedback,
    'SEND_FEEDBACK': send_feedback,
    'USER_IDENTIFY': user_identify,
    'MORE_ACTIVITY': show_activity,
    'NEWEST_ACTIVITY': create_formated_activities
}


@app.get("/phone")
async def phone(phone_number: str, user_agent: Optional[str] = Header(None)):
    print("User-Agent", user_agent)
    if re.findall("Android|webOS|iPhone|iPad|iPod|BlackBerry|Windows Phone", user_agent):
        return responses.RedirectResponse(f"tel:{phone_number}", status_code=302)
    return responses.Response("Please use you phone to call number.")


@app.get("/email")
async def email(email: str, user_agent: Optional[str] = Header(None)):
    print("User-Agent", user_agent)
    if re.findall("Android|webOS|iPhone|iPad|iPod|BlackBerry|Windows Phone", user_agent):
        return responses.RedirectResponse(f"mailto:{email}", status_code=302)
    return responses.Response("Please use you phone to write email.")


@app.get("/")
async def verify(request: Request):
    print("hub.mode = ", request.query_params['hub.mode'])
    if request.query_params['hub.mode'] == "subscribe" and request.query_params['hub.challenge']:
        if not request.query_params['hub.verify_token'] == Settings().VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return int(request.query_params['hub.challenge'])
    return "Hello world", 200

headers = {
    'Content-Type': 'application/json',
}
params = (
    ('access_token', PAGE_ACCESS_TOKEN),
)


async def process_postback(messaging, postback):
    # 1. user
    # 2. state
    # 3. get all sub states
    # 4. compare postback in sub states
    # 5. response
    global headers, params
    db = orm.SessionLocal()

    user_fb_id = messaging['sender']['id']
    user = db.query(orm.User).filter(
        orm.User.fb_id == user_fb_id
    ).one_or_none()
    if user is None:
        db_user = orm.User()
        db_user.fb_id = user_fb_id
        db.add(db_user)
        db.commit()
        init_menu(user_fb_id, headers, params)
        user = db_user

    payload = postback['payload']
    if payload == 'QUICK_REPLY':
        user.state_id = sqlalchemy.sql.null()
        db.add(user)
        db.commit()

    sub_states = db.query(orm.State).filter(
        orm.State.parent_id == user.state_id
    ).all()

    if not sub_states:
        pass
    sub_state_names = [
        sub_state.name
        for sub_state
        in sub_states
    ]

    if payload in sub_state_names:
        # Change user state to input state
        state = db.query(orm.State).filter(
            orm.State.name == payload
        ).first()
        user.state_id = state.id
        db.add(user)
        db.commit()
        # Execute state function
        print(state.function)
        if state.function:
            if not db.query(orm.State).filter(
                orm.State.parent_id == user.state_id
            ).all():
                user.state_id = sqlalchemy.sql.null()
            db.add(user)
            db.commit()
            function = mapping.get(state.function)
            await function(sender_id=user.fb_id, headers=headers,
                           params=params, name=payload)
            return
        sub_states = db.query(orm.State).filter(
            orm.State.parent_id == user.state_id
        ).all()
        # Find next states
        data = {
            "recipient": {
                "id": user.fb_id
            },
            "messaging_type": "RESPONSE",
            "message": {
                "text": state.prompt or state.label,
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": sub_state.label,
                        "payload": sub_state.name,
                    }
                    for sub_state in sub_states
                ]
            }
        }
        requests.post(
            'https://graph.facebook.com/v10.0/me/messages',
            headers=headers,
            params=params,
            json=data
        )
    db.close()


async def process_message(messaging, message):
    # 1. user
    # 2. state
    # 3. get all sub states
    # 4. compare message in sub states
    # 5. response
    global headers, params
    db = orm.SessionLocal()
    user_fb_id = messaging['sender']['id']
    user = db.query(orm.User).filter(
        orm.User.fb_id == user_fb_id
    ).one_or_none()
    if user is None:
        db_user = orm.User()
        db_user.fb_id = user_fb_id
        db.add(db_user)
        db.commit()
        init_menu(user_fb_id, headers, params)
        user = db_user
    sub_states = db.query(orm.State).filter(
        orm.State.parent_id == user.state_id
    ).all()
    if not sub_states:
        pass
    sub_state_names = [
        sub_state.name
        for sub_state
        in sub_states[::-1]
    ]
    # NTUB_ROOM_LOCATION
    payload = None
    if 'quick_reply' in message:
        payload = message['quick_reply']['payload']
        label = message['text']
    elif 'text' in message:
        payload = message['text']

    state = db.query(orm.State).filter(
        orm.State.id == user.state_id).one_or_none()
    print(payload, sub_state_names)
    if payload in sub_state_names:
        state = db.query(orm.State).filter(
            orm.State.name == payload
        ).first()
        # Change user state to input state
        user.state_id = state.id
        db.add(user)
        db.commit()
        # Execute state function
        print(state.function)
        if state.function:
            if not db.query(orm.State).filter(
                orm.State.parent_id == user.state_id
            ).all():
                user.state_id = sqlalchemy.sql.null()
            db.add(user)
            db.commit()
            function = mapping.get(state.function)
            await function(sender_id=user.fb_id, headers=headers,
                           params=params, name=payload, label=label)
            return
        # Find next states
        await quick_replies(user.fb_id, headers, params, state)
    elif state and state.is_input and state.function:
        print('in ', state, state.is_input, state.function)
        function = mapping.get(state.function)
        await function(sender_id=user.fb_id, headers=headers,
                       params=params, name=payload)
        if not db.query(orm.State).filter(
            orm.State.parent_id == user.state_id
        ).all():
            user.state_id = sqlalchemy.sql.null()
        db.add(user)
        db.commit()
        return

    db.close()


async def process_messaging(messaging):
    if 'postback' in messaging:
        await process_postback(messaging, messaging['postback'])
    if 'message' in messaging:
        await process_message(messaging, messaging['message'])


@app.post("/")
async def new(request: Request):
    print(await request.json())
    data = await request.json()
    for entry in data['entry']:
        for messaging in entry['messaging']:
            await process_messaging(messaging)
    return "Success", 200
    # is_postback = 'postback' in data['entry'][0]
    '''
    # postback
    {
        'object': 'page',
        'entry': [
            {'id': '112374620901935',
             'time': 1620468150834,
             'messaging': [
                 {
                     'sender': {'id': '3843687509051581'},
                     'recipient': {'id': '112374620901935'},
                     'timestamp': 1620468150655,
                     'postback': {'title': '顯示快捷按鈕', 'payload': 'QUICK_REPLY'}
                 }
             ]
             }
        ]
    }
    '''
    '''
    text
    {
        'object': 'page',
        'entry': [
            {'id': '112374620901935',
             'time': 1620468157945,
             'messaging': [
                 {'sender': {'id': '3843687509051581'},
                  'recipient': {'id': '112374620901935'},
                  'timestamp': 1620468157832,
                  'message': {
                     'mid': 'm_MeUVO9WfB3gaQ9NsQegMC9Y5gb9XBhcIq6OgbtUm9g6sp_zKkcQ0cAc-sssygb0_W02eu_SoTOlrTYQCD-8Khw',
                     'text': '教室配置圖',
                     'quick_reply': {'payload': 'NTUB_ROOM_LOCATION'}
                 }
                 }
             ]
             }
        ]
    }
    '''
