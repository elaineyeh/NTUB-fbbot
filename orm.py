from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:@127.0.0.1:5432/ub"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Role(Base):
    __tablename__ = "ub_role"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Link(Base):
    __tablename__ = "ub_link"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    discription = Column(String)
    button_label = Column(String)
    url = Column(String)
    title = Column(String)
    img_url = Column(String)


class Log(Base):
    __tablename__ = "ub_log"
    id = Column(Integer, primary_key=True, index=True)
    log = Column(JSONB)


class State(Base):
    __tablename__ = "ub_state"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    prompt = Column(String)
    label = Column(String)
    function = Column(String)
    is_input = Column(Boolean, default=False)
    parent_id = Column(ForeignKey('ub_state.id', ondelete='CASCADE', onupdate='SET NULL'))


'''
# Create
st = State()
st.name = 'new'
st.function = 'test'
st.is_input = False
st.parent_id = sqlalchemy.sql.null()
s = SessionLocal()
s.add(st)
s.commit()
'''


class User(Base):
    __tablename__ = "ub_user"
    id = Column(Integer, primary_key=True, index=True)
    fb_id = Column(String)
    token = Column(String)
    subscribed = Column(Boolean, default=False)
    role_id = Column(ForeignKey('ub_role.id', ondelete='SET NULL', onupdate='SET NULL'))
    state_id = Column(ForeignKey('ub_state.id', ondelete='SET NULL', onupdate='SET NULL'))


class Contact(Base):
    __tablename__ = "ub_contact"
    id = Column(Integer, primary_key=True, index=True)
    fb_id = Column(String)
    contact = Column(JSONB)


class Activity(Base):
    __tablename__ = "ub_activity"
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer)
    activity_name = Column(String)
    unit_name = Column(String)
    apply_qualification_list = Column(JSONB)
    apply_start_date = Column(DateTime)
    apply_start_time = Column(DateTime)
    apply_end_date = Column(DateTime)
    apply_end_time = Column(DateTime)
    post_start_time = Column(DateTime)
    post_end_time = Column(DateTime)
    activity_period_list = Column(JSONB)


class UserActivity(Base):
    __tablename__ = "ub_useractivity"
    id = Column(Integer, primary_key=True, index=True)
    fb_id = Column(String)
    activity = Column(JSONB)


class ContactList(Base):
    __tablename__ = "ub_contactlist"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class ContactNameList(Base):
    __tablename__ = "ub_contactnamelist"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


'''
# Create
user = User()
user.fb_id = 123
user.google_token = '123'
user.subscribe = False
user.activity_category_id = 1
user.state_id = 1
s = SessionLocal()
s.add(user)
s.commit()
'''

'''
# Query & Update
db_user = db.query(User).filter(User.id == 2).one_or_none()
db_user.fb_id = 456
db = SessionLocal()
db.add(db_user)
db.commit()
db_user = db.query(User).filter(User.id == 2).one_or_none()
db_user.fb_id
'''

'''
db.query(User).filter(User.id == 2).delete()
'''
