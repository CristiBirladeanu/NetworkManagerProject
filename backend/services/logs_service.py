from sqlmodel import Session, create_engine
from models.database import CommandLog
from datetime import datetime


def save_command_log(ip: str, username: str, command: str, output: str):
    sqlite_file = "database.db"
    engine = create_engine(f"sqlite:///{sqlite_file}", echo=False)
    with Session(engine) as session:
        log_entry = CommandLog(
            ip=ip,
            username=username,
            command=command,
            output=output,
            timestamp=datetime.utcnow()
        )
        session.add(log_entry)
        session.commit()

