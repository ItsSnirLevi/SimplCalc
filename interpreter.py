import re

class SimplCalcInterpreter:
    def __init__(self):
        self.symbol_table = {}

    def interpret(self, script):
        statements = self.parse_program(script)
        for statement in statements:
            if statement.startswith("(define"):
                self.evaluate_assignment(statement)
            elif statement.startswith("(print"):
                self.evaluate_print(statement)
            else:
                result = self.evaluate_expression(statement)
                print(result)

    def parse_program(self, script):
        commands = [cmd.strip() for cmd in script.split('\n') if cmd.strip()]
        return commands

    def remove_outer_parentheses(self, statement):
        return statement[1:-1]

    def evaluate_assignment(self, assignment):
        assignment = self.remove_outer_parentheses(assignment)
        _, variable, expression = assignment.split(maxsplit=2)
        result = self.evaluate_expression(expression)
        self.symbol_table[variable] = result

    def evaluate_expression(self, expression):
        stack = []
        expression = re.sub(r'\(|\)', '', expression)
        tokens = expression.split()
        for token in reversed(tokens):
            if token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
                stack.append(int(token))
            elif token in ["+", "-", "*", "/", "="]:
                if len(stack) < 2:
                    raise ValueError("Invalid expression")
                operand1 = stack.pop()
                operand2 = stack.pop()
                if token == "+":
                    result = operand1 + operand2
                elif token == "-":
                    result = operand1 - operand2
                elif token == "*":
                    result = operand1 * operand2
                elif token == "/":
                    if operand2 == 0:
                        raise ValueError("Division by zero")
                    result = operand1 // operand2
                elif token == "=":
                    result = int(operand1 == operand2)
                stack.append(result)
            else:
                if token in self.symbol_table:
                    stack.append(self.symbol_table[token])
                else:
                    print(f"Variable '{token}' not defined.")
        if len(stack) != 1:
            raise ValueError("Invalid expression")
        return stack[0]

    def evaluate_print(self, print_statement):
        print_statement = self.remove_outer_parentheses(print_statement)
        _, variable = print_statement.split()
        if variable in self.symbol_table:
            print(self.symbol_table[variable])
        else:
            print(f"Variable '{variable}' not defined.")

# Example usage
interpreter = SimplCalcInterpreter()
script = "(+ (* 2 4) (- 4 6))\n(define x 10)\n(print x)\n(define y (+ x 5))\n(print y)\n (= (+ x 5) y)\n"
interpreter.interpret(script)
