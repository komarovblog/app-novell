import users.user
import novells.novell
from config import Base, engine
import asyncio


# Тут мы заменили стандартное создание таблиц  - Base.metadata.create_all(engine), на такую обертку. Так как стандартный метод ожидает синхронный engene, а мы его сделали асинхронны. 
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())
