from fastapi import APIRouter, Query
from typing import Optional
from sqlmodel import Session, select, create_engine, delete
from models.database import CommandLog

router = APIRouter()

@router.get("/logs")
def get_all_logs(ip: Optional[str] = Query(None)):
    sqlite_file = "database.db"
    engine = create_engine(f"sqlite:///{sqlite_file}", echo=False)

    with Session(engine) as session:
        statement = select(CommandLog)
        if ip:
            statement = statement.where(CommandLog.ip == ip)

        logs = session.exec(statement).all()
        return logs

@router.delete("/logs")
def delete_all_logs():
    sqlite_file = "database.db"
    engine = create_engine(f"sqlite:///{sqlite_file}", echo=False)

    with Session(engine) as session:
        statement = delete(CommandLog)
        session.exec(statement)
        session.commit()
        return {"message": "Logurile au fost șterse cu succes"}

