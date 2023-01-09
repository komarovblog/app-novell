# Импортируем подключение из config.py
from config import Session, engine
# Импортируем Base для создания таблиц из config.py
from config import Base
from config import Table, Column, Integer, Float, String, Date, ForeignKey, Boolean, CheckConstraint, JSON, Numeric
# Импортируем BaseModel
from pydantic import BaseModel
# Импортируем Enum
from enum import Enum
# Импортируем  методы для запросов к БД
from sqlalchemy import func, select, insert, update, delete
# Импортируем для работы с пользовтелем
from users.user import UsersTable
# Импортируем для работы с json
import json


# Enum
class NovellGenreEnum(str, Enum):
    """Enum - Объект содержит список жанров"""
    thriller = "Триллер"
    detective = "Детектив"
    novel = "Роман"
    simulator = "Симулятор"

class NovellStatusEnum(str, Enum):
    """Enum - Объект содержит список статусов для всех сущностей"""
    in_work = "В работе"
    moderation = "На модерации"
    published = "Опубликовано"
    blocked = "Заблокировано"  


# Новелла
class NovellsTable(Base):
    """Класс для создание таблицы novells в БД"""
    __tablename__ = "novells"
    id = Column(Integer, primary_key = True, nullable = False)
    title = Column(String, nullable = False)
    description = Column(String, nullable = False)
    poster = Column(String, nullable = False)
    genre = Column(String, nullable = False)
    status = Column(String, nullable = False)
    id_author = Column(Integer, ForeignKey("users.id"), nullable = False)
    id_illustrator = Column(Integer, ForeignKey("users.id"), nullable = False)
    summary_rating = Column(Float, nullable = False, default = 0)
    price = Column(Numeric(precision = 7, scale = 2), nullable = False, default = 0)

class Novell(BaseModel):
    """Дата класс BaseModel"""
    id: int = None
    title: str = None
    description: str = None
    poster: str = None
    genre: NovellGenreEnum = None
    status: NovellStatusEnum = "В работе"
    price: float = 0
    author: str = "Komarov"
    illustrator: str = "Komarov"

# Шаг новеллы
class StepsTable(Base):
    """Класс для создание таблицы в БД"""
    __tablename__ = "steps"
    id = Column(Integer, primary_key = True, nullable = False)
    id_novell = Column(Integer, ForeignKey("novells.id"), nullable = False)
    text = Column(String, nullable = False)
    img = Column(String, nullable = False)
    variants = Column(JSON, nullable = False)
    is_start = Column(Boolean, nullable = False, default = False)
    is_finish = Column(Boolean, nullable = False, default = False)

class StepVariant(BaseModel):
    button_text: str = None
    step_id: int = None

class Step(BaseModel):
    """Дата класс BaseModel"""
    id: int = None
    id_novell: int = None
    text: str = None
    img: str = None
    variants: list[StepVariant]
    is_finish: bool = False

# Оценка отзыв
class ReviewsTable(Base):
    """Класс для создание таблицы в БД"""
    __tablename__ = "reviews"
    # Составной первичный ключ  id новеллы  id пользователя
    id_user = Column(Integer, ForeignKey("users.id"), nullable = False, primary_key = True)
    id_novell = Column(Integer, ForeignKey("novells.id"), nullable = False, primary_key = True) 
    rating = Column(Integer, nullable = False) # нужно добавить проверку от 1 до 10
    comment = Column(String) # нужно добавить проверку до 1500 символов

class Review(BaseModel):
    """Дата класс BaseModel"""
    rating: int = 5
    comment: str = None


class NovellRepository():
    """Класс содержит методы для работы с БД"""

    async def show_all_novells(self) -> list[Novell]:
        """Показывает все новеллы одним списком"""
        session = Session()
        request_content = """SELECT n.id, n.title, n.description, n.poster, n.genre, n.status, n.price, au.username AS autor, au.username AS illust
            FROM novells AS n
            JOIN users AS au ON n.id_author = au.id
            JOIN users AS il ON n.id_illustrator = il.id
            WHERE n.status = 'Опубликовано'"""

        result = (await session.execute(request_content)).all()
        await session.close()
        novells = []
        for novell in result:
            print(novell[1])
            novells.append(Novell(  id = novell[0],
                                    title = novell[1],
                                    description = novell[2],
                                    poster = novell[3],
                                    genre = novell[4],
                                    status = novell[5],
                                    price = novell[6],
                                    author = novell[7],
                                    illustrator = novell[8]              
            ))
        return novells


    async def open_one_novell(self, novell_id: int = None) -> Novell:
        """Открывает одну конкретную новеллу"""
        session = Session()
        request_content = f"""SELECT n.id, n.title, n.description, n.poster, n.genre, n.status, n.price, au.username AS autor, au.username AS illust
            FROM novells AS n
            JOIN users AS au ON n.id_author = au.id
            JOIN users AS il ON n.id_illustrator = il.id
            WHERE n.id = {novell_id}"""
        result = await session.execute(request_content)
        await session.close()

        novell_list = list(result)
     
        novell = Novell(id = novell_list[0][0],
                        title = novell_list[0][1],
                        description = novell_list[0][2],
                        poster = novell_list[0][3],
                        genre = novell_list[0][4],
                        status = novell_list[0][5],
                        price = novell_list[0][6],
                        author = novell_list[0][7],
                        illustrator = novell_list[0][8]     
        )
        return novell


    # Пользователь нажимает "Cтарт" и ему от дается первый шаг. Потом он нажимает на "Вариант" который выбрал. Отсылаем в запросе id текушего шага а по Варианту вычисляем и отдаем следующий шаг. Если не предусмотрено вариантов, а только один (напрмер просто длинное описание в шаге), то на кнопке Далее, просто тоже будет вариант, ибо логика, та-же.

    async def show_first_step_novell(self, novell_id: int = None) -> Step:
        """Открывает первый шаг на старте"""
        session = Session()
        request_content = select(StepsTable).\
                            where(StepsTable.id_novell == novell_id).\
                            where(StepsTable.is_start == True)
        result = (await session.execute(request_content)).scalar()
        await session.close()

        step = Step(id = result.id,
                    id_novell = result.id_novell,
                    text = result.text,
                    img = result.img,
                    variants = json.loads(result.variants),
                    is_finish = result.is_finish
        )
        return step   
  

    async def show_next_step_novell(self, novell_id: int = None, step_id: int = None) -> Step:
        """Открывает следующий шаг"""
        session = Session()
        request_content = select(StepsTable).\
                            where(StepsTable.id_novell == novell_id).\
                            where(StepsTable.id == step_id)
        result = (await session.execute(request_content)).scalar()
        await session.close()

        if result.is_finish == False:
            step = Step(id = result.id,
                        id_novell = result.id_novell,
                        text = result.text,
                        img = result.img,
                        variants = json.loads(result.variants),
                        is_finish = result.is_finish)
            return step

        else:
            step = Step(id = result.id,
                        id_novell = result.id_novell,
                        text = result.text,
                        img = result.img,
                        variants = [StepVariant(button_text = "Конец", 
                                                step_id = None)],
                        is_finish = result.is_finish
            )
            return step


    async def review(self, novell_id: int = None, user_id: int = None, review: Review = None):
        """После завершения вносит оценку и отзыв в таблицу со статусом На модерации"""

        try:
            session = Session()
            request_content = insert(ReviewsTable).\
                                values(id_user = user_id, id_novell = novell_id, rating = review.rating, comment = review.comment)
            result = await session.execute(request_content)
            await session.commit()
            await session.close()
            return True
        except:
            print("Вы уже оставили отзыв")
            return False


    # При покупке новеллы открывает доступ конаретному пользователю к конкретной новелле (как с банком). Тут либо создать таблицу для купленных новел или записывать купленные к пользователям.
    async def bay_novell(self, user_id: int = None, novell_id: int = None):
        """Покупка новеллы"""
        pass


    # Записывает где находится пользователь
    async def write_progress(self, user_id: int = None, novell_id: int = None):
        """Записывает где находится пользователь"""
        pass

rep_novell = NovellRepository()