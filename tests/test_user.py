# Импортируем класс который эмулирует посетителя
# from fastapi.testclient import TestClient - НЕ АКТУАЛЬНО
from main import app
from httpx import AsyncClient

# Импортируем подключение из config.py
from config import Session, engine
from sqlalchemy import func, select, insert, update, delete
from users.user import User, UsersTable, UsersConfirmTable
from novells.novell import Novell, NovellsTable, StepsTable
from config import Base
import json
from datetime import datetime, date, timedelta

# Для тестов клиент это не пользователь, а объект, который будет посылвать запросы на сервер. Этот объект как раз и есть TestClient, он нужен ТОЛЬКО для тестирования запросов. Он работает без запуска сервера. Для теста просто функций такое не нужно. 
# client = TestClient(app)
# НЕ АКТУАЛЬНО, ИСПОЛЬЗУЕМ АСИНХРОННЫЙ from httpx import AsyncClient




# Тестируем  http://127.0.0.1:8000/redoc, localhost:8000/docs
async def testing_user():

       # Удаляем все записи из шагов
       session = Session()
       request_content = delete(StepsTable)
       await session.execute(request_content)
       await session.commit()
       await session.close()

       # Удаляем все записи из новелл
       session = Session()
       request_content = delete(NovellsTable)
       await session.execute(request_content)
       await session.commit()
       await session.close()

       # Удаляем все записи из подтверждения
       session = Session()
       request_content = delete(UsersConfirmTable)
       await session.execute(request_content)
       await session.commit()
       await session.close()

       # Удаляем все записи из юзера
       session = Session()
       request_content = delete(UsersTable)
       await session.execute(request_content)
       await session.commit()
       await session.close()


       # Регистрация
       user = User(login_mail = "My_login", 
                   password = "My_password", 
                   username = "My_username", 
                   date_of_birth = datetime(1987,1,1))



       ########   ЗАПРСЫ К СЕРВЕРУ #########

       # Запрос №1 - Регистрация
       async with AsyncClient(app = app, base_url = "http://test") as client:
              await client.post("/user/registration", data = user.json())

       # Выводим созданного юзера
       session = Session()
       request_content = select(UsersTable.id).where(UsersTable.login_mail == "My_login")
       result = (await session.execute(request_content)).first()
       await session.close()
       
       curent_user_id = result.id
       print(f"Текущий ID пользователя {curent_user_id}")

       # Запрос №2 - Авторизация в приложении
       async with AsyncClient(app = app, base_url = "http://test") as client:
              await client.post(f"/user/login", headers = {"login": "My_login", "password": "My_password"})

       # Выводим ключ
       session = Session()
       request_content = select(UsersTable.key).where(UsersTable.login_mail == "My_login")
       result = (await session.execute(request_content)).scalar()
       await session.close()
     
       curent_key = result
       print(f"Текущий KEY пользователя {curent_key}") 

       session = Session()
       request_content = insert(UsersConfirmTable).values(id_user = curent_user_id, confirm_code = 1234)
       result = await session.execute(request_content)
       await session.commit()
       await session.close()
       print (f"Внесли код в таблицу Конфирм для пользователя {curent_user_id}")


       # Запрос №3 - Подтверждение регистрации пользователя
       async with AsyncClient(app = app, base_url = "http://test") as client:
              await client.post(f"/user/confirmation/{curent_user_id}", headers = {'code': '1234', 'token': curent_key})

       # Выводим созданного юзера, смотрим подтверждение
       session = Session()
       request_content = select(UsersTable.is_confirm).\
                            where(UsersTable.login_mail == "My_login").\
                            where(UsersTable.is_confirm == True)
       result = (await session.execute(request_content)).scalar()
       await session.close()
       print (f"И теперь статус пользователя {curent_user_id} - {result}")


       # Запрос №4 - Редактировать пользователя, меняем пароль, не меняем аватар
       async with AsyncClient(app = app, base_url = "http://test") as client:
              await client.post(f"/user/edit/{curent_user_id}", headers = {'token': curent_key, "password": "Newpassword"})
       
       # Выводим пользователя с новым
       session = Session()
       request_content = select(UsersTable).where(UsersTable.login_mail == "My_login")
       result = (await session.execute(request_content)).scalar()
       await session.close()
       print(f"Новый пароль пользователя с ID {curent_user_id} - {result.password}")


       # Запрос №5 - Выйти из личного кабинета
       async with AsyncClient(app = app, base_url = "http://test") as client:
              await client.post(f"/user/logout/{curent_user_id}", headers = {'token': curent_key})

       # Выводим ключ, его теперь не должно быть
       session = Session()
       request_content = select(UsersTable.key).where(UsersTable.login_mail == "My_login")
       result = (await session.execute(request_content)).scalar()
       await session.close()
     
       curent_key = result
       print(f"Текущий KEY пользователя - {curent_key} - (его не долно быть)") 


