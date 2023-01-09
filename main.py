from fastapi import Request
from fastapi import FastAPI, Header
from datetime import datetime, date, timedelta

# Чтобы вернуть изображение
from fastapi.responses import FileResponse

# Чтобы выкинуть исключение
from fastapi.exceptions import HTTPException

from users.user import User, rep_user
from novells.novell import rep_novell

# Импортируем Base для создания таблиц из config.py
from config import Base
from config import Table, Column, Integer, Float, String, Date, ForeignKey, Boolean, CheckConstraint, JSON, Numeric
from config import Session
from users.user import UsersTable

from sqlalchemy import func, select, insert, update, delete



# Проверка ключа
async def token_verification(user_id: int = None, token: str = None) -> bool:
    """Проверка токена при каждом запросе"""
    session = Session()
    # Ищем ключ в БД
    request_content = select(UsersTable.key).\
        where(UsersTable.id == user_id)
    result = (await session.execute(request_content)).scalar()
    await session.close()

    if len(result) == 0:
        print("Вы не авторизованы")
        return False
    if result != token:
        print("Ключ не совпадает")
        return False
    return True


# Получаем id пользователя для того чтобы протестировать работу в Kivy
async def get_user_id_for_token(token: str = None) -> int:
    """Метод отдает id пользователя по предоставлению токенаЮ нужен чтобы тестировать приложение на Kivi, так как приложение обращается к серверу от тестового пользователя у которого динамически меняется id"""
    session = Session()
    request_content = select(UsersTable.id).where(UsersTable.key == token)
    result = (await session.execute(request_content)).first()
    await session.close()
    return result.id



app = FastAPI()
# @app.get("/")
# async def root():
#     return {"greeting":"Hello world"}

@app.on_event("startup")
async def startup_event():
    # Тут выполняется любой код при запуске сервера
    pass


# В ФАСТАПИ НЕЛЬЗЯ В GET ЗАПРОСЕ ПЕРЕДАТЬ ТЕЛО, ГЕТ ЗАПРОС ТОЛЬКО ЗАПРАШИВАЕТ ДАННЫЕ И НЕ МОЖЕТ ПЕРЕЗАПИСАТЬ ДАННЫЕ. ЕСЛИ ХОТЬИМ ПЕРЕДАТЬ ТЕЛО ТО ДОЛЖЕН БЫТЬ POST


# ---------------------------------- User
@app.post("/user/registration")
async def api_registration(user: User) -> bool:
    return await rep_user.registration(user)

@app.post("/user/login")
async def api_login(login: str = Header(), password: str = Header()):
    return await rep_user.login (login = login, password = password)

@app.post("/user/confirmation/{user_id}")
async def api_confirmation(user_id: int = None, code: int = Header(None), token: str = Header(None)):
    if await token_verification(user_id = user_id, token = token):
        return await rep_user.confirmation(user_id = user_id, code = code)

@app.post("/user/edit/{user_id}")
async def api_edit_user(user_id: int, token: str = Header(None), password: str = Header(None), avatar: str = Header(None)):
    if await token_verification(user_id = user_id, token = token):
        return await rep_user.edit_user(user_id = user_id, password = password, avatar = avatar)

@app.post("/user/logout/{user_id}")
async def api_logout(user_id: int, token: str = Header(None)):
    if await token_verification(user_id = user_id, token = token):
        return await rep_user.logout(user_id = user_id)

# Отдаем id пользователя для того чтобы протестировать работу в Kivy
@app.get("/user/get_id")
async def api_get_user_id_for_token(token: str = Header(None)):
        return await get_user_id_for_token(token = token)


# ---------------------------------- Novell
@app.get("/{user_id}/novells")
async def api_show_all_novells(user_id: int, token: str = Header(None)):
    if await token_verification(user_id = user_id, token = token):
        return await rep_novell.show_all_novells()


@app.get("/{user_id}/novells/{novell_id}")
async def api_open_one_novell(novell_id: int, user_id: int, token: str = Header(None)):
    if await token_verification(user_id = user_id, token = token):
        return await rep_novell.open_one_novell(novell_id = novell_id)


@app.get("/{user_id}/novells/{novell_id}/start")
async def api_show_first_step_novell(novell_id: int, user_id: int, token: str = Header(None)):
    if await token_verification(user_id = user_id, token = token):
        return await rep_novell.show_first_step_novell(novell_id = novell_id)


@app.get("/{user_id}/novells/{novell_id}/{step_id}")
async def api_show_next_step_novell(novell_id: int, step_id: int, user_id: int, token: str = Header(None)):
    if await token_verification(user_id = user_id, token = token):
        return await rep_novell.show_next_step_novell(novell_id = novell_id, step_id = step_id)


# Оплата. Пока рано, но на будущее.
# @app.get("/{user_id}/novells/{novell_id}/buy/")
# async def api_bay_novell(user_id: int, novell_id: int, token: str = Header(None)):
#     if await token_verification(user_id, token):
#         return await rep_novell.bay_novell(user_id = user_id, novell_id = novell_id)



# ---------------------------------- Images
# Возврат изображения
async def show_image(img_path: str = None):
    file_byte = FileResponse(img_path)
    return file_byte


@app.get("/image")
async def api_show_image(img_name: str = Header()):
    img_path = f"novells/img_novells/{img_name}" 
    return await show_image(img_path = img_path)