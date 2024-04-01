import re

class SimplCalcInterpreter:
    def __init__(self):
        self.symbol_table = {}
        self.max_result_length = 50     # calculation result length
        self.max_program_length = 1000  # script length
        self.max_exp_length = 50        # expression length
        self.max_variable_length = 10
        self.max_variables_allowed = 10
        self.max_conditionals_level = 3

    # def interpret(self, script):
    #     if len(script) > self.max_program_length:
    #         print("Program length exceeds maximum allowed.")
    #         return
    #
    #     statements = self.parse_program(script)
    #     for statement in statements:
    #         if statement.startswith("(define"):
    #             self.evaluate_assignment(statement)
    #         elif statement.startswith("(print"):
    #             self.evaluate_print(statement)
    #         else:
    #             result = self.evaluate_expression(statement)
    #             if len(str(result)) > self.max_result_length:
    #                 print("Result length exceeds maximum allowed.")
    #                 return
    #             print(result)

    def interpret(self, script):
        if len(script) > self.max_program_length:
            print("Program length exceeds maximum allowed.")
            return

        statements = self.parse_program(script)
        self.interpret_statements(statements, 1)  # Start with conditional level 1

    def parse_program(self, script):
        commands = [cmd.strip() for cmd in script.split('\n') if cmd.strip()]
        return commands

    def remove_outer_parentheses(self, statement):
        return statement[1:-1]

    def evaluate_assignment(self, assignment):
        assignment = self.remove_outer_parentheses(assignment)
        _, variable, expression = assignment.split(maxsplit=2)
        if len(self.symbol_table) >= self.max_variables_allowed:
            print("Cannot declare a new variable. Max variable allowed reached!")
            return
        if len(variable) > self.max_variable_length:
            print("Variable name length exceeds maximum allowed. *Slicing to fit the maximum!*")
            variable = variable[:50]
        result = self.evaluate_expression(expression)
        self.symbol_table[variable] = result

    def evaluate_expression(self, expression):
        stack = []
        expression = re.sub(r'\(|\)', '', expression)
        if len(expression) > self.max_exp_length:
            print("Calculation length exceeds maximum allowed.")
            return
        tokens = expression.split()
        for token in reversed(tokens):
            if token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
                stack.append(int(token))
            elif token in ["+", "-", "*", "/", "=", "<", ">"]:
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
                elif token == "<":
                    result = int(operand1 < operand2)
                elif token == ">":
                    result = int(operand1 > operand2)
                stack.append(result)
            else:
                if token in self.symbol_table:
                    stack.append(self.symbol_table[token])
                else:
                    print(f"Variable '{token}' not defined.")
        if len(stack) != 1:
            raise ValueError("Invalid expression")
        return stack[0]

    def evaluate_conditional(self, conditional_statement, level):
        conditional_statement = self.remove_outer_parentheses(conditional_statement)
        conditional_statement = conditional_statement.split(maxsplit=1)
        predicate, consequent = conditional_statement[1].split(":", maxsplit=1)

        if level > self.max_conditionals_level:
            print("Maximum conditional level exceeded.")
            return

        predicate_result = self.evaluate_expression(predicate)
        consequent = consequent[1:]
        if predicate_result:
            self.interpret_statements([consequent], level + 1)

    def interpret_statements(self, statements, level):
        for statement in statements:
            if statement.startswith("(define"):
                self.evaluate_assignment(statement)
            elif statement.startswith("(print"):
                self.evaluate_print(statement)
            elif statement.startswith("(if"):
                self.evaluate_conditional(statement, level)
            else:
                result = self.evaluate_expression(statement)
                if len(str(result)) > self.max_result_length:
                    print("Result length exceeds maximum allowed.")
                    return
                print(result)

    def evaluate_print(self, print_statement):
        print_statement = self.remove_outer_parentheses(print_statement)
        _, variable = print_statement.split()
        if variable in self.symbol_table:
            print(self.symbol_table[variable])
        else:
            print(f"Variable '{variable}' not defined.")

# Example usage
interpreter = SimplCalcInterpreter()
script = "(+ (* 2 4) (- 4 6))\n(define x 10)\n(print x)\n(define y (+ x 5))\n(print y)\n (= (+ x 5) y)\n" \
        "(if (< 1 4) : (if (< 2 4) : (if (< 3 4) : (1000)))) \n"
interpreter.interpret(script)
