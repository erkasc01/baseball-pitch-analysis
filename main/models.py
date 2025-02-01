from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

DATABASE_URL = "sqlite:///baseball-db.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Pitch(Base):
    __tablename__ = "pitches"
    id = Column(Integer, primary_key=True)
    pitch_type = Column(String)
    pitcher_id = Column(Integer)
    game_id = Column(Integer)
    pitch_number = Column(Integer)
    pitch_result = Column(String)
    pa_result = Column(String)
    spin_rate = Column(Integer)
    pitch_mph = Column(Float)
    pitch_date = Column(String)


class Pitcher(Base):
    __tablename__ = "pitchers"
    id = Column(Integer, primary_key=True)
    pitcher_id = Column(Integer)
    pitcher_name = Column(String)
    pitcher_name_normalized = Column(String)


def init_db():
    Base.metadata.create_all(bind=engine)
