from motor.motor_asyncio import AsyncIOMotorClient

async def get_db():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.expense_tracker
    try:
        yield db
    finally:
        client.close()
