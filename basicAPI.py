# app_async.py
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Replace with your RDS connection info:
DATABASE_URL = "mysql+asyncmy://username:password@rds-endpoint.amazonaws.com:3306/yourdbname"
# For PostgreSQL: "postgresql+asyncpg://username:password@rds-endpoint.amazonaws.com:5432/yourdbname"

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker for async sessions
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

@app.get("/users")
async def get_users():
    async with async_session() as session:
        result = await session.execute(text("SELECT * FROM users"))
        users = [dict(row._mapping) for row in result]
    return {"users": users}
