Для запуска проекта необходим Python 3.10.5, далее действуем по инструкции:
1. Открыть консоль в корневой папке и установить пакеты из файла, команда pip install -r requirements.txt
2. Создать БД PostgreSQL, после чего настроить подключение (ввести логин, ввести пароль) в файле config.py
3. Запустить файл simple_migrate_db.py, он создаст необходимые таблицы в БД
4. Запустить файл testing.py, он заполнит БД тестовыми данныим
5. Открыть консоль в корне и запустить файл run.py, данный файл запустит сервер, для полноценного тестирования БД должна быть запущена.