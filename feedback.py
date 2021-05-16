import orm
import sqlalchemy
from pymessenger import Bot
from config import Settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


conf = ConnectionConfig(
    MAIL_USERNAME=Settings().MAIL_USERNAME,
    MAIL_PASSWORD=Settings().MAIL_PASSWORD,
    MAIL_FROM=Settings().MAIL_FROM,
    MAIL_PORT=Settings().MAIL_PORT,
    MAIL_SERVER=Settings().MAIL_SERVER,
    MAIL_TLS=Settings().MAIL_TLS,
    MAIL_SSL=Settings().MAIL_SSL,
    USE_CREDENTIALS=Settings().USE_CREDENTIALS
)
PAGE_ACCESS_TOKEN = Settings().PAGE_ACCESS_TOKEN

bot = Bot(PAGE_ACCESS_TOKEN)


async def feedback(sender_id, headers, params, **kwargs):
    text = "感謝您的使用，如有遇到任何使用上的問題，請在下方寫下您寶貴的意見"
    bot.send_text_message(sender_id, text)

    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
    state = db.query(orm.State).filter(orm.State.name == 'SEND_FEEDBACK').one_or_none()
    user.state_id = state.id
    db.add(user)
    db.commit()


async def send_feedback(sender_id, headers, params, name, **kwargs):
    message = MessageSchema(
        subject="UB 醬意見回饋",
        recipients=Settings().RECEPI_EMAIL,
        body=name,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    text = "謝謝您留下寶貴的意見，我們將盡快處理"
    bot.send_text_message(sender_id, text)

    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
    user.state_id = sqlalchemy.sql.null()
    db.add(user)
    db.commit()
