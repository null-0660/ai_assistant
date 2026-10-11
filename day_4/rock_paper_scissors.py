import random

wins = {
    'камень': 'ножницы',
    'ножницы': 'бумага',
    'бумага': 'камень',
}

losses = {
    'камень': 'бумага',
    'ножницы': 'камень',
    'бумага': 'ножницы',
}

while True:
    user = input('Выберите камень, ножницы или бумага (или введите стоп для завершения): ')

    if user.lower() == 'стоп':
        break

    user = user.lower().strip()

    if user not in wins:
        print('неверный выбор')
        continue

    bot = random.choice(['камень', 'ножницы', 'бумага'])

    print('Ты:', user)
    print('Бот:', bot)

    if user == bot:
        print('Ничья')
    elif wins[user] == bot:
        print('Ты победил')
    elif losses[user] == bot:
        print('Ты проиграл')
