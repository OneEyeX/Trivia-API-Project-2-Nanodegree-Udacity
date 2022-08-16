import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
# import json
from flask_migrate import Migrate


database_name = 'trivia'
database_path = 'postgresql://{}/{}'.format(
    'postgres:oex@localhost:5432', database_name)

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    """
        local database configuration settings
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # create all tables models
    db.create_all()
    # manage migrations and structures changes
    migrate = Migrate(app, db)


"""
Question

"""


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


"""
Category

"""


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String, unique=True, nullable=False)

    def __init__(self, type):
        self.type = type

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }


# ----------------------------------------------------------------------------#
# CHALLENGE3: model user is used to save score for players
# ----------------------------------------------------------------------------#
class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, default='Player')
    score = Column(Integer, default=0)

    def __init__(self, username='Player', score=0):
        self.username = username
        self.score = score

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def add_score(self, score):
        self.score += score

    def initialize_score(self, score):
        self.score = score

    def format(self):
        return {
            'id': self.id,
            'username': self.username,
            'score': self.score,
        }
