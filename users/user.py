# Импортируем подключение из config.py
from config import Session, engine
# Импортируем Base для создания таблиц из config.py
from config import Base
from config import Table, Column, Integer, Float, String, Date, ForeignKey, Boolean, CheckConstraint, JSON, Numeric
# Импортируем BaseModel
from pydantic import BaseModel
# Импортируем Enum
from enum import Enum
# Позволяет вывести ошибку try except
import traceback
# Импортируем  методы для запросов к БД
# https://docs.sqlalchemy.org/en/20/core/dml.html#sqlalchemy.sql.expression.insert
# https://lectureswww.readthedocs.io/6.www.sync/2.codding/9.databases/2.sqlalchemy/index.html
from sqlalchemy import func, select, insert, update, delete
# Импортируем класс для работы с датой 
# https://www.dmitrymakarov.ru/python/datetime-05/#9-sravnenie-dat
from datetime import datetime, date, timedelta
import random


# Пользователь
class UsersTable(Base):
    """Класс для создание таблицы в БД"""
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, nullable = False)
    login_mail = Column(String, unique = True, nullable = False)
    password = Column(String, nullable = False)
    username = Column(String, nullable = False)
    avatar =  Column(String, nullable = True)
    date_of_birth = Column(Date, nullable = False)
    is_author = Column(Boolean, nullable = False, default = False)
    is_illustrator = Column(Boolean, nullable = False, default = False)
    date_of_registration = Column(Date, nullable = False)
    is_confirm = Column(Boolean, nullable = False, default = False)
    key = Column(String, nullable = False, default = "")

class User(BaseModel):
    """Дата класс BaseModel"""
    id: int = None
    login_mail: str = None
    password: str = None
    username: str = None
    avatar: str = None
    date_of_birth: datetime = None
    is_author: bool = False
    is_illustrator: bool = False

class UsersConfirmTable(Base):
    """Класс для создание таблицы в БД"""
    __tablename__ = "users_confirm"
    id = Column(Integer, primary_key = True, nullable = False)
    id_user = Column(Integer, ForeignKey("users.id"), nullable = False)  # ВЫДАВАЛ ОШИБКУ, ВИДИМО ИЗ ЗА ТОГО
    # id_user = Column(Integer, nullable = False)
    confirm_code = Column(Integer, nullable = False)

class OpenNovellsTable(Base):
    """Класс для создание таблицы в БД - Начатая новелла"""
    __tablename__ = "open_novells"
    # Составной первичный ключ  id новеллы  id пользователя
    id_user = Column(Integer, ForeignKey("users.id"), nullable = False, primary_key = True)
    id_novell = Column(Integer, ForeignKey("novells.id"), nullable = False, primary_key = True)
    id_step = Column(Integer, ForeignKey("steps.id"), nullable = False)



class UserRepository():
    """Класс содержит методы для работы с БД"""


    async def registration(self, user: User = None) -> bool:
        """Регистрация пользователя, сначала добавляем, и если не добавилось из за уникальности ..."""
        today = date.today()
        request_content = insert(UsersTable).values(
                                                login_mail = user.login_mail,
                                                password = user.password,
                                                username = user.username,
                                                avatar = user.avatar,
                                                date_of_birth = user.date_of_birth,
                                                date_of_registration = today)
        try:
            session = Session()
            await session.execute(request_content)
            await session.commit()
            await session.close()
            return True
        except:
             print("Такой логин уже зарегистиррован, восстановите пароль и зайдите")
             await session.close()
             return False


    async def login(self, login: str = None, password: str = None) -> str|bool:
        """Возвращает токен (ключ) или False"""
        # Получили пользователя
        session = Session()
        request_content = select(UsersTable.login_mail, UsersTable.password, UsersTable.id).\
                            where(UsersTable.login_mail == login)
        result = (await session.execute(request_content)).first()
        await session.close()

        if result.login_mail is None:
            print("Такой логин не найден")
            return False
        if result.password != password:
            print("Не верный пароль")
            return False

        alphabet = "abcdefghijklmnopqrstuvwxyz"
        key_list = []

        for symbol in alphabet:
            key_list.append(random.choice(alphabet))       
        key_string = "".join(key_list)
        key_id = result.id
        key = f"{key_id}-{date.today()}-{key_string}"
        # Прописываем пользователю актуальный ключ
        session = Session()
        request_content = update(UsersTable).\
                            where(UsersTable.id == result.id).\
                                values(key = key)
        await session.execute(request_content) 
        await session.commit()
        await session.close()
        return key

       
    async def confirmation(self, user_id: int = None, code: int = None) -> bool:
        """Подтверждение регистрации, если код совпадает"""
        session = Session()
        await session.begin()
        
        request_content = select(UsersConfirmTable.confirm_code).\
                            where(UsersConfirmTable.id_user == user_id)
        result = (await session.execute(request_content)).scalar()
      
        if result == code:
            # Ставим пользователю статус подтвержден
            request_content = update(UsersTable).\
                                where(UsersTable.id == user_id).\
                                    values(is_confirm = True)
            await session.execute(request_content) 
            # Удаляем код из таблицы подтверждения
            request_content = delete(UsersConfirmTable).\
                                where(UsersConfirmTable.id_user == user_id)
            await session.execute(request_content) 
            await session.commit()
            await session.close()
            print (f"Пользователь подтвержден с ID {user_id} подтвержден")
            return True        
        elif result == None:
            print ("Код устарел, запросите код заново")
            await session.close()
            return False
        elif result != code:
            print ("Код не совпадает")
            await session.close()
            return False


    async def clear_confirm_code(self):
        """Удаляет коды подтверждения пользователей зарегистрирован
             больше трех дней назад"""
        clear_date = date.today() - timedelta(days=3)
        session = Session()
        request_content = delete(UsersConfirmTable).\
                            where(UsersConfirmTable.user_id in 
                                (select(UsersTable.id).\
                                    where(UsersTable.date_of_registration < clear_date )))          
        await session.execute(request_content) 
        await session.commit()
        await session.close()


    async def edit_user(self, 
                        user_id: int = None, 
                        password: str = None, 
                        avatar: str = None) -> bool:
        """Редактировать профиль, юзернейм, аватарка"""

        ##################################
        print("Функция не будет рабоать если несколько значений, понять как переписать на SQLAlchemy")  
        ##################################  
      
        session = Session()       
        request_content = update(UsersTable).where(UsersTable.id == user_id)

        if password != None:
            request_content = request_content.values(password = password)
        if avatar != None:
            request_content = request_content.values(avatar = avatar)

        await session.execute(request_content)     
        await session.commit()
        await session.close()     
        print("Пользовател отредактирован")
        return True


    async def logout(self, user_id: int = None) -> bool:
        """Выход"""
        # Обнуляем ключ для пользователя в БД
        session = Session()
        request_content = update(UsersTable).\
                            where(UsersTable.id == user_id).\
                                values(key = "")
        await session.execute(request_content)         
        await session.commit()
        await session.close()
        print("Вы вышли из ЛК")
        return True
    
    # Записывает шаг по прохождению новелл
    # Записывает где находится пользователь


rep_user = UserRepository()