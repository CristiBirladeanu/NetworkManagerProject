from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Optional
from datetime import datetime

class CommandLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip: str
    username: str
    command: str
    output: str

class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hostname: str
    ip_address: str
    username: str
    password: str
    discovered: bool = True

sqlite_file = "database.db"
engine = create_engine(f"sqlite:///{sqlite_file}", echo=False)

def get_session():
    return Session(engine)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def reset_database():
    with Session(engine) as session:
        from sqlmodel import delete
        session.exec(delete(CommandLog))
        session.exec(delete(Device))
        session.commit()

