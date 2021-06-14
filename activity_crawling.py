import requests
import json
import time

import orm

from sqlalchemy import inspect


async def activity_crawling():
    response = requests.get(
        "https://b-signupactivity.ntub.edu.tw/api/Activity/TestGetActivity")

    contents = response.text
    contents = json.loads(contents)
    # print(contents)

    db = orm.SessionLocal()

    # delete all row in specific table
    db.query(orm.Activity).delete()

    nowTime = int(time.time())

    for item in contents:
        # print(item)
        activity = orm.Activity()

        start_struct_date = time.strptime(
            item['ApplyStartDate'], "%Y-%m-%dT%H:%M:%S")
        start_time_stamp = int(time.mktime(start_struct_date))
        stop_struct_time = time.strptime(
            item['ApplyEndDate'], "%Y-%m-%dT%H:%M:%S")
        stop_time_stamp = int(time.mktime(stop_struct_time))
        # print(item['ApplyQualificationList'], '學生' in item['ApplyQualificationList'])
        if '學生' in item['ApplyQualificationList']:
            # print(nowTime > start_time_stamp, nowTime < stop_time_stamp, nowTime, start_time_stamp, stop_time_stamp)
            if nowTime > start_time_stamp and nowTime < stop_time_stamp:
                print(item['IsInApply'] and item['IsOutApply'] is False)
                if item['IsInApply'] and item['IsOutApply'] is False:
                    activity.activity_id = item['ActivityID']
                    activity.activity_name = item['ActivityName']
                    activity.unit_name = item['UnitName']
                    activity.apply_qualification_list = item['ApplyQualificationList']
                    activity.apply_start_date = item['ApplyStartDate']
                    activity.apply_start_time = item['ApplyStartTime']
                    activity.apply_end_date = item['ApplyEndDate']
                    activity.apply_end_time = item['ApplyEndTime']
                    activity.post_start_time = item['PostStartTime']
                    activity.post_end_time = item['PostEndTime']
                    activity.activity_period_list = item['ActivityPeriodList']

                    db.add(activity)
                    db.commit()


async def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


async def user_identify(sender_id, headers, params, name, **kwargs):
    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
    role = db.query(orm.Role).filter(orm.Role.name == name).one_or_none()
    user.role_id = role.id
    db.add(user)
    db.commit()

    await create_formated_activities(sender_id, headers, params)


async def is_select_user_identify(sender_id, headers, params, **kwargs):
    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()

    data = {
        "recipient": {
            "id": user.fb_id
        },
        "messaging_type": "RESPONSE",
        "message": {
            "text": "您的身份是？",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "教職員",
                    "payload": "EMPLOYEE",
                },
                {
                    "content_type": "text",
                    "title": "學生",
                    "payload": "STUDENT",
                }
            ]
        }
    }
    requests.post(
        'https://graph.facebook.com/v10.0/me/messages',
        headers=headers,
        params=params,
        json=data
    )

    state = db.query(orm.State).filter(orm.State.name == 'USER_IDENTIFY').one_or_none()
    user.state_id = state.id
    db.add(user)
    db.commit()


async def create_formated_activities(sender_id, headers, params, **kwargs):
    activities = []
    db = orm.SessionLocal()
    items = db.query(orm.Activity).all()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()

    if not user.role_id:
        await is_select_user_identify(sender_id, headers, params)
        return

    role = db.query(orm.Role).filter(orm.Role.id == user.role_id).one_or_none()

    for item in items:
        print("TYPE", role.name, type(item), item.apply_qualification_list)
        identify = {
            'STUDENT': '學生',
            'EMPLOYEE': '教職員'
        }.get(role.name)
        if identify in item.apply_qualification_list:
            activity = await object_as_dict(item)
            activity_id = activity['activity_id']
            activity_name = activity['activity_name']
            start_date = activity['post_start_time'].date()
            start_time = activity['activity_period_list'][0]['ActivityStartTime']
            start_time = start_time.split('T')[1]
            start_time = start_time[:5]
            end_date = activity['post_end_time'].date()
            end_time = activity['activity_period_list'][0]['ActivityEndTime']
            end_time = end_time.split('T')[1]
            end_time = end_time[:5]
            location = activity['activity_period_list'][0]['Location']

            text = f"{start_date} {start_time}-{end_date} {end_time}\n活動地點：{location}"
            url = f"https://signupactivity.ntub.edu.tw/activity/activityDetail/{activity_id}"

            activities.append({
                "title": f"{activity_name}",
                "image_url": "https://i.imgur.com/W3ILzTa.jpeg",
                "subtitle": text,
                "buttons": [
                    {
                        "type": "web_url",
                        "title": "我要報名",
                        "url": url
                    }
                ]
            })

    user_activity = orm.UserActivity()
    user_activity.fb_id = sender_id
    user_activity.activity = activities
    db.add(user_activity)
    db.commit()

    await show_activity(sender_id, headers, params)


async def show_activity(sender_id, headers, params, **kwargs):
    show_activity = []
    db = orm.SessionLocal()
    items = db.query(orm.UserActivity).filter(
        orm.UserActivity.fb_id == sender_id).order_by(orm.UserActivity.id.desc()).first()
    activity = items.activity

    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()

    if len(activity) > 10:
        show_activity = activity[-9:]
        show_activity.append({
            "title": "沒有找到你想要的嗎？",
            "image_url": "https://i.imgur.com/W3ILzTa.jpeg",
            "buttons": [
                {
                    "type": "postback",
                    "title": "點我看更多",
                    "payload": "MORE_ACTIVITY"
                }
            ]
        })

        items.activity = activity[:len(activity)-9]
        db.add(items)
        db.commit()
    else:
        show_activity = items.activity
        items.activity = []

    if items.activity:
        user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
        state = db.query(orm.State).filter(orm.State.name == "NEWEST_ACTIVITY").one_or_none()
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
                    "elements": show_activity,
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
