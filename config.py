#------------------------------------------- Подключение к БД

# Импортируем коннект к БД 
# https://docs.sqlalchemy.org/en/14/core/engines.html

# Cинхронный, старый вариант.
#from sqlalchemy import create_engine - Это синхронный, старый вариант

# Fсинхроннный вариант подключения к БД
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio


# Основной объект для подключения к БД 
# dialect+driver(pg8000)://username:password@host:port/database
engine = create_async_engine("postgresql+asyncpg://myadmin:postgres@localhost/novelldb")
images_folder = "Адрес того где картинки"


#------------------------------------------- Запросы в БД


# Вместо стандарного коннектиона
from sqlalchemy.orm import sessionmaker

# Старый вариант
# 1 - cздаем соединение,
# connection = engine.connect() 
# 2 - запрос передаем как аргумент в execute()
# connection.execute(запрос)
# 3 - комит это просто слово commit в аргументе
# connection.execute("commit"), 

# Новый вариант надстройка Session, асинхронный
Session = sessionmaker(engine, expire_on_commit = False, class_ = AsyncSession)

# 1 - это делаем каждый раз, открываем соединение
# session = Session() 
# 2 - делаем запрос
# session.execute('SLECT ...')
# 3 - коммитим
# session.commit()
# 4 - закрываем соединение
# session.close()

# Если с  транзакцией. Открыть транзакцию если это транзакция, на самом деле люой запрос к базе, даже единичный это транзакция, просто с одним запросом она автоматически открывает транзакцию и коммитит.
# session.begin() 
# session.execute('SLECT ...')
# session.commit()
# session.rollback() (если нужно)
# session.close()


# Контекстный менеджер
# Класс Session() это еще и контекстный менеджер, это просто класс со специфическими методами
# _enter_
# _exet_

# Нужен для того чтобы можно было написать блок with Session() as session: и перед этим блоком выполнится _enter_, а после того как выйдем из блока _exet_. В случае ниже будет session.close()

# with Session() as session:
#     session.execute('SLECT ...')
#     session.commit()

# Если хотим сделать транзакцию
# with Session.begin() as session:

# Плюс конекстного менеджера в том, что если в блоке будет ошибка то метод _exet_ все равно сработает, в данном случае закроется соединение, а только потом программа вылетит.


#------------------------------------------- Создание таблиц в БД


# Класс для создания таблиц в БД, для отправки запросов в БД используем asyncpg
# https://docs.sqlalchemy.org/en/14/orm/declarative_tables.html
from sqlalchemy.orm import declarative_base, relationship


# Для каждой колонки импортируем тип
from sqlalchemy import Table, Column, Integer, Float, String, Date, ForeignKey, Boolean, CheckConstraint, JSON, Numeric

# Класс для создания сущностей
Base = declarative_base()

# Создает таблицы в БД
# Base.metadata.create_all(engine)
# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)

# asyncio.run(init_models())

# Удаляет таблицы в БД
# Base.metadata.drop_all(engine)
