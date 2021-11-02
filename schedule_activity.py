import asyncio
import orm
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler
from activity_crawling import activity_crawling, object_as_dict

sched = BlockingScheduler()


def schedule_activity():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coroutine = activity_crawling()
    loop.run_until_complete(coroutine)


def schedule_user_activity():
    result_activity = []
    db = orm.SessionLocal()

    users = db.query(orm.User).all()
    items = db.query(orm.Activity).all()

    for user in users:
        print("fb_id: ", user.fb_id)
        print("subcribed: ", user.subscribed)
        if user.subscribed:
            role = db.query(orm.Role).filter(orm.Role.id == user.role_id).one_or_none()

            for item in items:
                identify = {
                    'STUDENT': '學生',
                    'EMPLOYEE': '教職'
                }.get(role.name)
                if identify in item.apply_qualification_list:
                    if item.apply_start_date == date.today():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        coroutine = object_as_dict(item)
                        activity = loop.run_until_complete(coroutine)

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

                        result_activity.append({
                            "title": f"{activity_name}",
                            "image_url": "https://i.imgur.com/QAcuOst.jpeg",
                            "subtitle": text,
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "我要報名",
                                    "url": url
                                }
                            ]
                        })
        print(result_activity)
        result_activity.clear()


sched.add_job(schedule_activity, 'cron', day_of_week='mon-sun', hour=7, minute=30)
sched.add_job(schedule_user_activity, 'cron', day_of_week='mon-sun', hour=9, minute=00)

sched.start()
