def calculator():
    a = int(input("Первое число: "))
    b = int(input("Второе число: "))
    operation = input("Введите операцию (+, -, *, /, ^, %): ")
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

    print(result)

calculator()
