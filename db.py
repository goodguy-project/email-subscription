import json
import logging
import os
from contextlib import contextmanager
from typing import List

from sqlalchemy import String, Column, create_engine, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import SingletonThreadPool

from const import ROOT

_ORM_BASE = declarative_base()


def _to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


_ORM_BASE.dict = _to_dict


class User(_ORM_BASE):
    __tablename__ = 'USER'
    email = Column(String(50), primary_key=True)
    pwd = Column(String(40))
    subscribe = Column(Integer, default=1)


class Sender(_ORM_BASE):
    __tablename__ = 'SENDER'
    email = Column(String(50), primary_key=True)
    pwd = Column(String(20))
    smtp_server = Column(String(50))
    smtp_port = Column(Integer, default=465)


_DB_PATH = os.path.join(ROOT, 'E-mail Subscriptions System.sqlite3')
_ENGINE = create_engine(f'sqlite:///{_DB_PATH}', poolclass=SingletonThreadPool,
                        connect_args={'check_same_thread': False})
_SESSION_CLZ = sessionmaker(bind=_ENGINE)

# create table if not exist
User.__table__.create(bind=_ENGINE, checkfirst=True)
Sender.__table__.create(bind=_ENGINE, checkfirst=True)


@contextmanager
def session() -> Session:
    try:
        s = _SESSION_CLZ()
        yield s
        s.commit()
    except Exception as e:
        logging.exception(e)
        raise


def all_subscriber() -> List[str]:
    with session() as s:
        ret: List[User] = s.query(User).filter(User.subscribe > 0).all()
        return [e.email for e in ret]


def debug() -> str:
    ret = {}
    with session() as s:
        user: List[User] = s.query(User).all()
        ret['user'] = [e.dict() for e in user]
        sender: List[Sender] = s.query(Sender).all()
        ret['sender'] = [e.dict() for e in sender]
    return json.dumps(ret)


if __name__ == '__main__':
    print(debug())
