from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from models.schemas import User
import os

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    hashed_password = Column(String)

class AuthService:
    def __init__(self):
        # 使用项目根目录下的 SQLite 数据库文件
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'stock_analysis.db')
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_user(self, username: str, password: str, email: str = None) -> bool:
        db = self.SessionLocal()
        try:
            if db.query(UserModel).filter(UserModel.username == username).first():
                return False
            
            hashed_password = pwd_context.hash(password)
            db_user = UserModel(
                username=username,
                email=email,
                hashed_password=hashed_password
            )
            db.add(db_user)
            db.commit()
            return True
        finally:
            db.close()

    def authenticate_user(self, username: str, password: str):
        db = self.SessionLocal()
        try:
            user = db.query(UserModel).filter(UserModel.username == username).first()
            if not user:
                return False
            if not pwd_context.verify(password, user.hashed_password):
                return False
            return user
        finally:
            db.close()

    def ensure_default_user(self):
        """确保默认用户存在"""
        db = self.SessionLocal()
        try:
            default_user = db.query(UserModel).filter(UserModel.username == "admin").first()
            if not default_user:
                self.create_user("admin", "admin123", "admin@example.com")
        finally:
            db.close()