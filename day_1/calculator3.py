while True:
    def stop(text):
        return text.lower() in ('exit', 'стоп')
    
    a = input("Первое число: ")
    if stop(a): break
    # if a.lower() == 'exit' or a.lower() == 'стоп': break    # if a.lower() in ('exit', 'стоп'):

    b = input("Второе число: ")
    if stop(b): break
    # if b.lower() == 'exit' or b.lower() == 'стоп': break    # if b.lower() in ('exit', 'стоп'):

    operation = input("Введите операцию (+, -, *, /, ^, %): ")
    if stop(operation): break
    # if operation.lower() == 'exit' or operation.lower() == 'стоп': break    # if operation.lower() in ('exit', 'стоп'):

    result = ''
    
    try:
        a = int(a)
        b = int(b)
    except ValueError:
        print("Ошибка: введены не числа")
        continue

    if operation in ('/', '%') and b == 0:
        print("Ошибка: деление на 0")
        continue

    if operation == '+':
        result = a + b
    elif operation == '-':
        result = a - b
    elif operation == '*':
        result = a * b
    elif operation == '/':
        result = a / b
    elif operation == '^':
        result = a ** b
    elif operation == '%':
        result = a % b
    else:
        result = 'Ошибка: неверная операция'
    
    print(result)
