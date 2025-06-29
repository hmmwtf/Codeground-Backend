from sqlalchemy import Column, DateTime, Integer, String, func, Text, Float, Enum, ARRAY, Boolean
from src.app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    use_lang = Column(String(50), nullable=False, server_default="python3")  # 사용언어
    username = Column(String(255), nullable=False)
    nickname = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    role = Column(String(50), nullable=False, server_default="user")  # 회원권한
    my_tier = Column(Float, nullable=False, server_default="1000")  # 내 티어
    profile_img_url = Column(Text, nullable=True)  # 프로필 이미지 주소

class Problem(Base):
    __tablename__ = "problems"

    problem_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    difficulty = Column(Enum("easy", "medium", "hard"), nullable=False)
    language = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    problem_prefix = Column(ARRAY(String), nullable=False)
    testcase_prefix = Column(ARRAY(String), nullable=False)