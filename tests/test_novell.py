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
async def testing_novell():

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

       # Удаляем все записи из пользователей
       session = Session()
       request_content = delete(UsersTable)
       await session.execute(request_content)
       await session.commit()
       await session.close()       
       
       # Cоздаем тестового пользователя
       session = Session()
       request_content = insert(UsersTable).\
                            values(login_mail = "TestLogin",
                                   password = "TestPass",
                                   username = "TestUserName",
                                   date_of_birth = datetime(1987,1,1),
                                   date_of_registration = datetime(1987,1,1),
                                   is_confirm = True,
                                   key = "TestToken")  
       await session.execute(request_content)
       await session.commit()
       await session.close() 
       print("Пользователь TestLogin создан")

       # Получаем id пользователя
       session = Session()
       request_content = select(UsersTable.id).where(UsersTable.login_mail == "TestLogin")
       result = (await session.execute(request_content)).scalar()
       await session.close()
 
       curent_user_id = result
       print(f"Текущий ID пользователя {curent_user_id}")
    
       # Создаем тестовую новеллу №1 
       session = Session()
       request_content = insert(NovellsTable).\
                            values(title = "Интересная история №1", 
                                   description = "Эта занимательная история началась с того, что я начал изучать основы Python, строчка за строчкой и вот я уже хочу стать разработчиком.", 
                                   poster = "novells/img_novells/poster.png",
                                   genre = "Триллер",
                                   status = "Опубликовано",
                                   id_author = curent_user_id,
                                   id_illustrator = curent_user_id)
       await session.execute(request_content)
       await session.commit()
       await session.close()
       print("Новелла Интересная история №1 создана")

       # Создаем тестовую новеллу №2 
       session = Session()
       request_content = insert(NovellsTable).\
                            values(title = "Другая интересная история", 
                                   description = "Другая история о том как я начал изучать основы Python, строчка за строчкой и вот я уже хочу стать разработчиком.", 
                                   poster = "novells/img_novells/poster2.png",
                                   genre = "Детектив",
                                   status = "Опубликовано",
                                   id_author = curent_user_id,
                                   id_illustrator = curent_user_id)
       await session.execute(request_content)
       await session.commit()
       await session.close()
       print("Новелла Другая интересная история создана")

       # Выводим тестовую новеллу №1
       session = Session()
       request_content = select(NovellsTable).where(NovellsTable.title == "Интересная история №1")
       result = (await session.execute(request_content)).scalar()
       await session.close()
       
       curent_novell_id = result.id
       print(f"Текущий ID новеллы №1 {curent_novell_id}")


       # И добавляем для нее шаги для новеллы №1 - ЧЕРЕЗ ПАРАМЕТРЫ
       session = Session()
       request_content = insert(StepsTable)
       steps_list = [
              {
              "id": 10001,
              "id_novell": curent_novell_id,                     # Старт
              "text": "Эта занимательная история началась с того, что я начал изучать основы Python, строчка за строчкой и вот я уже хочу стать разработчиком.", 
              "img": "step1.jpg",
              "variants": json.dumps([{"button_text": "Сделать оффер", "step_id": 10002},
                                     {"button_text": "Смотреть дальше", "step_id": 10003}]),
              "is_start": True,
              "is_finish": False 
              },
              {
              "id": 10002,
              "id_novell": curent_novell_id,                     # Первая ветка
              "text": "Благодарю за сделанное предложение, готов выходить.",   
              "img":"step2.jpg",
              "variants": json.dumps([{"button_text": "Завершить чтение", "step_id": 10004}]),
              "is_start": False,
              "is_finish": False             
              },
              {
              "id": 10003,
              "id_novell": curent_novell_id,                     # Вторая ветка
              "text": "Так же на GitHub есть и другие проекты, например интернет магазин.", 
              "img": "step3.jpg",
              "variants": json.dumps([{"button_text": "Все таки предложить вакансию", "step_id": 10004}]),
              "is_start": False,
              "is_finish": False             
              },
              {
              "id": 10004,
              "id_novell": curent_novell_id,                     # Финал
              "text": "Это финальный шаг.", 
              "img": "step4.jpg",
              "variants": json.dumps([]),
              "is_start": False,
              "is_finish": True             
              }
       ]
       await session.execute(request_content, steps_list)
       await session.commit()
       await session.close() 
       print("Шаги для новеллы Интересная история №1 созданы") 

       # Получаем шаги новеллы №1 и выводим
       session = Session()
       request_content = select(StepsTable).where(StepsTable.id_novell == curent_novell_id)
       result = (await session.execute(request_content)).all()
       await session.close()

       print(f"Текущийе ID-ники шагов новеллы №1")
       for step in result:
              print(f"{step.StepsTable.id}")   



###################################################################################
###################################################################################

      # Выводим тестовую новеллу №2
       session = Session()
       request_content2 = select(NovellsTable).where(NovellsTable.title == "Другая интересная история")
       result2 = (await session.execute(request_content2)).scalar()
       await session.close()
       
       curent_novell_id2 = result2.id
       print(f"Текущий ID новеллы №2 {curent_novell_id2}")


       # И добавляем для нее шаги для новеллы №2 - ЧЕРЕЗ ПАРАМЕТРЫ
       session = Session()
       request_content2 = insert(StepsTable)
       steps_list = [
              {
              "id": 20001,
              "id_novell": curent_novell_id2,                     # Старт
              "text": "Эта занимательная история началась с того, что я начал изучать основы Python, строчка за строчкой и вот я уже хочу стать разработчиком.", 
              "img": "step1.jpg",
              "variants": json.dumps([{"button_text": "Сделать оффер", "step_id": 20002},
                                     {"button_text": "Смотреть дальше", "step_id": 20003}]),
              "is_start": True,
              "is_finish": False 
              },
              {
              "id": 20002,
              "id_novell": curent_novell_id2,                     # Первая ветка
              "text": "Благодарю за сделанное предложение, готов выходить.",   
              "img":"step2.jpg",
              "variants": json.dumps([{"button_text": "Завершить чтение", "step_id": 20004}]),
              "is_start": False,
              "is_finish": False             
              },
              {
              "id": 20003,
              "id_novell": curent_novell_id2,                     # Вторая ветка
              "text": "Так же на GitHub есть и другие проекты, например интернет магазин.", 
              "img": "step3.jpg",
              "variants": json.dumps([{"button_text": "Все таки предложить вакансию", "step_id": 20004}]),
              "is_start": False,
              "is_finish": False             
              },
              {
              "id": 20004,
              "id_novell": curent_novell_id2,                     # Финал
              "text": "Это финальный шаг.", 
              "img": "step4.jpg",
              "variants": json.dumps([]),
              "is_start": False,
              "is_finish": True             
              }
       ]
       await session.execute(request_content2, steps_list)
       await session.commit()
       await session.close() 
       print("Шаги для новеллы Другая интересная история созданы") 

       # Получаем шаги новеллы №2 и выводим
       session = Session()
       request_content2 = select(StepsTable).where(StepsTable.id_novell == curent_novell_id2)
       result2 = (await session.execute(request_content2)).all()
       await session.close()

       print(f"Текущийе ID-ники шагов новеллы №2")
       for step in result2:
              print(f"{step.StepsTable.id}") 


###################################################################################
###################################################################################








       ########   ЗАПРСЫ К СЕРВЕРУ #########
       
       # Запрос №1 - Выводим список новелл
       async with AsyncClient(app = app, base_url = "http://test") as client:
              result = await client.get(f"{curent_user_id}/novells", headers = {"token": "TestToken"})
              print(f"Выводим ответ по список новелл")
              print(result)

              print(f"Выводим тело ответа json - Список новелл")
              print(result.json())

              print(f"Выводим в ответе список методов класса")              
              print(dir(result))


       # Запрос №2 - Выводим конкретную новеллу       
       async with AsyncClient(app = app, base_url = "http://test") as client:
              result = await client.get(f"{curent_user_id}/novells/{curent_novell_id}", headers = {"token": "TestToken"})
              print(f"Выводим ответ по конкретной новелле")
              print(result)
              print(f"Выводим тело ответа json - Конкретную новеллу с ID {curent_user_id}")
              print(result.json())

       # Запрос №3 - Отдаем первый слайд после сигнала старт
       async with AsyncClient(app = app, base_url = "http://test") as client:
              result = await client.get(f"{curent_user_id}/novells/{curent_novell_id}/start", headers = {"token": "TestToken"})
              print(f"Выводим ответ по первому шагу")
              print(result)
              print(f"Выводим тело ответа json - По первому шагу")
              print(result.json())
              for var in result.json()['variants']:
                     print(f"{var['button_text']} ведет на {var['step_id']}")

       # Запрос №4 - Отдаем слайд после выбора варианта
       async with AsyncClient(app = app, base_url = "http://test") as client:
              result = await client.get(f"{curent_user_id}/novells/{curent_novell_id}/10003", headers = {"token": "TestToken"})      
              print(f"Выводим ответ по следующему шагу")
              print(result)
              print(f"Выводим тело ответа json - По следующему шагу")
              print(result.json())
              for var in result.json()['variants']:
                     print(f"{var['button_text']} ведет на {var['step_id']}")

       # Запрос №5 - Отдаем последний слайд
       async with AsyncClient(app = app, base_url = "http://test") as client:
              result = await client.get(f"{curent_user_id}/novells/{curent_novell_id}/10004", headers = {"token": "TestToken"})  
              print(f"Выводим ответ по последнему шагу")
              print(result)
              print(f"Выводим тело ответа json - По последнему шагу")
              print(result.json())
              for var in result.json()['variants']:
                     print(f"{var['button_text']} ведет на {var['step_id']}")


       # Запрос №6 - отдаем изображение в байтах
       async with AsyncClient(app = app, base_url = "http://test") as client:
              result = await client.get(f"/image", headers = {"img-name": "step1.jpg"})  
              print(f"Выводим ответ по изображению")
              print(result)
              print(f"Выводим тело ответа json - По изображению")
              print(result.content)






