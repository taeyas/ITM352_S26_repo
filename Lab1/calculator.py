def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid number. Please enter a numeric value.")


def get_operation():
    ops = {
        '+': 'add',
        '-': 'subtract',
        '*': 'multiply',
        '/': 'divide'
    }
    prompt = "Choose operation (+, -, *, /): "
    while True:
        op = input(prompt).strip()
        if op in ops:
            return op
        print("Invalid operation. Enter one of: +, -, *, /")


def calculate(a, b, op):
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b


def main():
    print("Simple Calculator (type 'q' to quit, 'h' for history)")
    history = []
    while True:
        inp = input("Enter first number (or 'q' to quit, 'h' for history): ").strip()
        if inp.lower() == 'q':
            break
        if inp.lower() == 'h':
            if not history:
                print("No history yet.")
            else:
                for i, entry in enumerate(history, 1):
                    print(f"{i}: {entry}")
            continue
        try:
            a = float(inp)
        except ValueError:
            print("Invalid number. Please enter a numeric value.")
            continue

        b_inp = input("Enter second number (or 'q' to quit, 'h' for history): ").strip()
        if b_inp.lower() == 'q':
            break
        if b_inp.lower() == 'h':
            if not history:
                print("No history yet.")
            else:
                for i, entry in enumerate(history, 1):
                    print(f"{i}: {entry}")
            continue
        try:
            b = float(b_inp)
        except ValueError:
            print("Invalid number. Please enter a numeric value.")
            continue

        op = get_operation()
        try:
            result = calculate(a, b, op)
        except ZeroDivisionError as e:
            print(f"Error: {e}")
            history.append(f"{a} {op} {b} = Error: {e}")
        else:
            out = f"{a} {op} {b} = {result}"
            print(f"Result: {out}")
            history.append(out)

    print("Goodbye.")


if __name__ == '__main__':
    main()
