# -*- coding:utf-8 -*-

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///db.sqlite', echo=False)
session_scope = scoped_session(sessionmaker(autoflush=False, autocommit=False, bind=engine))
Base = declarative_base()

@contextmanager
def Session():
    session = session_scope()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()