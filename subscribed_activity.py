import orm
import sqlalchemy
from pymessenger import Bot
from config import Settings

from activity_crawling import is_select_user_identify

PAGE_ACCESS_TOKEN = Settings().PAGE_ACCESS_TOKEN
bot = Bot(PAGE_ACCESS_TOKEN)


async def subscribed_activity(sender_id, headers, params, **kwargs):
    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()

    if not user.role_id:
        await is_select_user_identify(sender_id, headers, params)
        return

    user.subscribed = True
    user.state_id = sqlalchemy.sql.null()
    db.add(user)
    db.commit()

    bot.send_text_message(sender_id, "訂閱成功！")
