import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, CHAR
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:@127.0.0.1:5432/ub"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ActivityCategory(Base):
    __tablename__ = "ub_activitycategory"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class FastLink(Base):
    __tablename__ = "ub_fastlink"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    url = Column(String)


class Log(Base):
    __tablename__ = "ub_log"
    id = Column(Integer, primary_key=True, index=True)
    log = Column(JSONB)


class State(Base):
    __tablename__ = "ub_state"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
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
    fb_id = Column(Integer)
    google_token = Column(String)
    subscribe = Column(Boolean, default=False)
    activity_category_id = Column(ForeignKey('ub_activitycategory.id', ondelete='SET NULL', onupdate='SET NULL'))
    state_id = Column(ForeignKey('ub_state.id', ondelete='SET NULL', onupdate='SET NULL'))


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
