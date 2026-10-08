def calculator(a:int, b:int, operation:str):
    result = ''
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

    return print(result)

calculator(2, 2, '^')