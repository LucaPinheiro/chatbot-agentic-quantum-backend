from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    __abstract__ = True

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"


# ──────────────── User ────────────────
class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    permission = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    groups = relationship("Group", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    class_topics = relationship("ClassTopic", back_populates="user")
    enrollments = relationship("GroupEnrollment", back_populates="user", cascade="all, delete-orphan")


# ──────────────── Group ────────────────
class Group(Base):
    __tablename__ = "groups"

    group_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    year_semester = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)
    manager_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    user = relationship("User", back_populates="groups")
    classes = relationship("ClassModel", back_populates="group", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="group", cascade="all, delete-orphan")
    enrollments = relationship("GroupEnrollment", back_populates="group", cascade="all, delete-orphan")


# ──────────────── GroupEnrollment ────────────────
class GroupEnrollment(Base):
    __tablename__ = "group_enrollments"

    group_id = Column(String, ForeignKey("groups.group_id"), primary_key=True)
    student_id = Column(String, ForeignKey("users.user_id"), primary_key=True)

    group = relationship("Group", back_populates="enrollments")
    user = relationship("User", back_populates="enrollments")


# ──────────────── Class (renomeado para evitar conflito com palavra reservada) ────────────────
class ClassModel(Base):
    __tablename__ = "classes"

    class_id = Column(String, primary_key=True)
    group_id = Column(String, ForeignKey("groups.group_id"), nullable=False)
    title = Column(String, nullable=False)
    pdf_url = Column(String)
    status = Column(Boolean, default=True)
    last_access_class = Column(DateTime)
    created_at = Column(DateTime, nullable=False)
    order = Column(Integer)

    group = relationship("Group", back_populates="classes")
    class_topics = relationship("ClassTopic", back_populates="class_", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="class_", cascade="all, delete-orphan")


# ──────────────── ClassTopic ────────────────
class ClassTopic(Base):
    __tablename__ = "class_topics"

    class_topics_id = Column(String, primary_key=True)
    topic = Column(String, nullable=False)
    flag = Column(Boolean, default=False)
    class_id = Column(String, ForeignKey("classes.class_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    class_ = relationship("ClassModel", back_populates="class_topics")
    user = relationship("User", back_populates="class_topics")


# ──────────────── Session ────────────────
class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    class_id = Column(String, ForeignKey("classes.class_id"), nullable=False)
    group_id = Column(String, ForeignKey("groups.group_id"), nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")
    class_ = relationship("ClassModel", back_populates="sessions")
    group = relationship("Group", back_populates="sessions")
