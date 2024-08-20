import os
import bcrypt
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, create_engine, text
from sqlalchemy.ext.declarative import declarative_base

db = declarative_base()

class Users(db):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    is_admin = Column(Boolean, default=False)


class Database:
    def __init__(self):
        engine = create_engine("sqlite:////tmp/the_hell.db")
        db.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        self.session = session
        # create admin user
        admin = self.session.query(Users).filter(Users.is_admin == True).first()
        if not admin:
            password =  os.urandom(32).hex()
            password_bytes = password.encode("utf-8")
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password_bytes, salt).decode()
            new_admin = Users(username="administrator", password=password_hash, is_admin=True)
            self.session.add(new_admin)
            self.session.commit()
    
    def create_user(self, username, password):
        user = self.session.query(Users).filter(Users.username == username).first()
        if user:
            return False

        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode()

        new_user = Users(username=username, password=password_hash)
        self.session.add(new_user)
        self.session.commit()

        return True

    def get_user(self, username, password):
        password_bytes = password.encode("utf-8")
        query = text(f"SELECT * FROM users WHERE username = '{username}'")
        user = self.session.execute(query).fetchone()
        if not user:
            return None, False
        if bcrypt.checkpw(password_bytes, user.password.encode("utf-8")):
            return user, True
        return None, False