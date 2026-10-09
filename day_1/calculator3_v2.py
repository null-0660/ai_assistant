def stop(text):
    return text.lower() in ('exit', 'стоп')

def calculate(a, b, operation):
    if operation in ('/', '%') and b == 0:
        return "Ошибка: деление на 0"
    
    if operation == '+': 
        return a + b
    elif operation == '-': 
        return a - b
    elif operation == '*': 
        return a * b
    elif operation == '/': 
        return a / b
    elif operation == '%': 
        return a % b
    elif operation == '^': 
        return a ** b
    else: 
        return 'Ошибка: неверная операция'

while True:
    a = input("Первое число: ")
    if stop(a): break
    # if a.lower() == 'exit' or a.lower() == 'стоп': break    # if a.lower() in ('exit', 'стоп'):

    b = input("Второе число: ")
    if stop(b): break
    # if b.lower() == 'exit' or b.lower() == 'стоп': break    # if b.lower() in ('exit', 'стоп'):

    operation = input("Введите операцию (+, -, *, /, ^, %): ")
    if stop(operation): break
    # if operation.lower() == 'exit' or operation.lower() == 'стоп': break    # if operation.lower() in ('exit', 'стоп'):

    try:
        a = float(a)
        b = float(b)
    except ValueError:
        print("Ошибка: введены не числа")
        continue

    result = calculate(a, b, operation)
    print(result)