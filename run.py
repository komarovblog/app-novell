# Подпроцесс для запуска консольной команды
import subprocess
# Запуск сервера, --reload перезапускает автоматом при каждом изменении кода.

subprocess.call("uvicorn main:app --reload", shell=True)  
# subprocess.run("uvicorn main:app --reload", shell=True)

# Предварительный запуск main.py не нужен, выше мы и сервер запускаем и main в нем.
# subprocess.call("python main.py")
