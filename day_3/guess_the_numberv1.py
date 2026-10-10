import random

def stop(text):
    return text.lower() in ('exit', 'стоп')

secret = random.randint(1, 100)
print('Programma загадал число от 1 до 100. Попробуйте угадать его!')

guess = None

while guess != secret:
    guess = input('Введетте число: ')

    if stop(guess): break

    try:
        guess = int(guess)
    except ValueError:
        print('Ошибка: введено не число')
        continue

    if guess > secret:
        print('Загаданное число меньше.')
    elif guess < secret:
        print('Загаданное число больше.')
    else:
        print('Поздравляем! Вы угадали число: ', secret)
        break

        # replay = input('Хотите сыгарть еще раз или выйти (да и yes продолжит или exit и стоп выход): ')

        # if stop(replay):
        #    break

        # if replay.lower() in ('yes', 'да'):
        #    continue
        # else:
        #    print('Введите правильный выбор: ')
            
