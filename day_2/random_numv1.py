import random



while True:
    text = input("Введите диапазон чисел (пример: 1 10 без ,): ")
    
    if text.lower() in ('stop', 'стоп'):
        break
    
    parts = text.split()

    try:
        a = int(parts[0])
        b = int(parts[1])
    except ValueError:
        print("это не числа")
        continue

    if a >= b:
        print("первое число должно быть меньше второго")
        continue

    number = random.randint(a, b)
    print(number)