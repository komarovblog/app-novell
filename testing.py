import asyncio
from tests.test_user import testing_user
from tests.test_novell import testing_novell

# Просто в фале мы не можем вызывать аснхронные функции, для этого нужен цикл событий.asyncio.run как раз и является циклом событий, добавляет туда наш testing, выплняет и закрывает цикл событий.

# В таком виде не работает, создается другой цикл
# asyncio.run(testing_novell())

# Рабочий вариант уикла событий:
#asyncio.get_event_loop().run_until_complete(testing_user())
asyncio.get_event_loop().run_until_complete(testing_novell())




