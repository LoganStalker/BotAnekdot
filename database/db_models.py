# -*- coding:utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy import not_
from sqlalchemy.orm import relationship
from database.dbconnector import Base, Session
import json
from random import choice

class ContentCategory(Base):
    __tablename__ = "content_category"
    id = Column(Integer, primary_key=True)
    category = Column(String)
    theme = relationship('Themes')

    @classmethod
    def list(cls):
        with Session() as session:
            lst = session.query(ContentCategory).all()
            session.close()
        return lst

class Themes(Base):
    __tablename__ = "theme"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('content_category.id'))
    theme = Column(String)
    content = relationship('Content', backref='theme')

    @classmethod
    def list(cls, category):
        with Session() as session:
            lst = session.query(
                Themes.theme
            ).join(
                ContentCategory, ContentCategory.id == Themes.category_id,
            ).filter(
                ContentCategory.category == category,
            ).all()
            session.close()
        return lst

class Content(Base):
    __tablename__ = 'content'
    id = Column(Integer, primary_key=True)
    theme_id = Column(Integer, ForeignKey('theme.id'))
    title = Column(String)
    body = Column(String)

    @classmethod
    def get_random_content(cls, theme, chat_id):
        print('theme', theme)
        with Session() as session:
            ids_seen = User.get_seens(chat_id)
            if theme in ids_seen.keys():
                ids_seen = ids_seen[theme]
            else:
                ids_seen = []
            ids = session.query(
                cls.id
            ).join(
                Themes, Themes.id == cls.theme_id
            ).filter(
                not_(cls.id.in_(ids_seen)),
                Themes.theme == theme
            ).all()
            if not ids:
                User.clear_seen(chat_id, theme)
                ids = session.query(
                    cls.id
                ).join(
                    Themes, Themes.id == cls.theme_id
                ).filter(
                    Themes.theme == theme
                ).all()

            id = choice(ids).id
            User.add_seen_id(chat_id, theme, id)
            content = session.query(
                cls.title,
                cls.body,
            ).filter(
                cls.id == id,
            ).first()
            session.close()
        return content

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    chat_id = Column(Integer)
    memory = Column(JSON, default=json.dumps({}))
    seen = Column(JSON, default=json.dumps({}))

    @classmethod
    def get(cls, data):
        with Session() as session:
            user = session.query(
                cls
            ).filter(
                cls.chat_id == data.chat.id,
                cls.username == data.chat.username,
            ).first()
            session.close()
        return user

    @classmethod
    def create(cls, data):
        with Session() as session:
            session.add(cls(username=data.chat.username, chat_id=data.chat.id))
            session.commit()
        return cls.get(data)

    @classmethod
    def read_memory(cls, user_chat_id):
        with Session() as session:
            mem = session.query(User.memory).filter(cls.chat_id == user_chat_id).first()
            session.close()
        return json.loads(mem.memory)

    @classmethod
    def update_memory(cls, chat_id, datas):
        with Session() as session:
            mem = cls.read_memory(chat_id)
            mem.update(datas)
            session.query(cls).filter(cls.chat_id == chat_id).update({'memory': json.dumps(mem)})
            session.commit()
            session.close()

    @classmethod
    def add_seen_id(cls, chat_id, theme, id):
        with Session() as session:
            ids = cls.get_seens(chat_id)
            if theme not in ids.keys():
                ids.update({theme: []})
            ids[theme].append(id)
            session.query(cls).filter(cls.chat_id==chat_id).update({'seen': json.dumps(ids)})
            session.commit()
            session.close()

    @classmethod
    def clear_seen(cls, chat_id, theme):
        with Session() as session:
            seens = cls.get_seens(chat_id)
            seens.update({theme: []})
            session.query(cls).filter(cls.chat_id==chat_id).update({'seen': json.dumps(seens)})

    @classmethod
    def get_seens(cls, chat_id):
        with Session() as session:
            ids_q = session.query(cls.seen).filter(cls.chat_id == chat_id).first()
            ids = json.loads(ids_q.seen)
            session.close()
        return ids

if __name__ == "__main__":
    # Base.metadata.create_all(engine)
    from database.dbconnector import Session

    from content_description import categories, themes, content

    with Session() as session:
        for cat in categories:
            check = session.query(ContentCategory).filter(ContentCategory.category == cat).first()
            if not check:
                session.add(ContentCategory(category=cat))
        session.commit()

        for cat in themes.keys():
            cat_id = session.query(ContentCategory.id).filter(ContentCategory.category == cat).first()
            for th in themes.get(cat):
                check = session.query(Themes).filter(Themes.theme == th).first()
                if not check:
                    session.add(Themes(category_id=cat_id.id, theme=th))
        session.commit()

        for cat_key in content.keys():
            cat = content.get(cat_key)
            for th in cat.keys():
                th_id = session.query(Themes.id).filter(Themes.theme == th).first()
                for cont in cat.get(th):
                    check = session.query(Content).filter(Content.theme_id==th_id.id, Content.body==cont.get('body')).first()
                    if not check:
                        session.add(Content(theme_id=th_id.id, title=cont.get('title'), body=cont.get('body')))
        session.commit()

        session.close()