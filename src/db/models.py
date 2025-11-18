"""SQLAlchemy models (placeholder for future use)."""

# from sqlalchemy import Column, Integer, String, DateTime, JSON
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime

# Base = declarative_base()

# class User(Base):
#     """User model."""
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True)
#     username = Column(String, unique=True, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

# class Session(Base):
#     """Session model for conversation history."""
#     __tablename__ = "sessions"
#
#     id = Column(String, primary_key=True)
#     user_id = Column(Integer)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     metadata = Column(JSON)

# TODO: Implement actual database models when needed
pass
