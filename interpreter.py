import re
import sys

class SimplCalcInterpreter:
    def __init__(self):
        self.symbol_table = {}
        self.max_result_length = 50     # calculation result length
        self.max_program_length = 1000  # script length
        self.max_exp_length = 50        # expression length
        self.max_variable_length = 10
        self.max_variables_allowed = 10
        self.max_conditionals_level = 3
        self.max_loops_level = 3
        self.max_loops_reached = 0

    def interpret(self, script):
        if len(script) > self.max_program_length:
            print("Program length exceeds maximum allowed.")
            return

        statements = self.parse_program(script)
        self.interpret_statements(statements, 1)  # Start with conditional level 1

    def interpret_statements(self, statements, level):
        for statement in statements:
            if statement.startswith("(define"):
                self.evaluate_assignment(statement)
            elif statement.startswith("(print"):
                self.evaluate_print(statement)
            elif statement.startswith("(if"):
                self.evaluate_conditional(statement, level)
            elif statement.startswith("(while"):
                self.evaluate_loop(statement, level)
            else:
                result = self.evaluate_expression(statement)
                if len(str(result)) > self.max_result_length:
                    print("Result length exceeds maximum allowed.")
                    return
                if result:
                    print(result)

    def parse_program(self, script):
        statements = []
        statement = ''
        balance = 0
        in_comment = False

        for char in script:
            # Check if within a comment
            if char == '#' and not in_comment:
                in_comment = True

            # If within a comment, skip characters until newline
            if in_comment and char != '\n':
                continue
            elif in_comment and char == '\n':
                in_comment = False
                continue

            # Keep track of parentheses balance unless within a comment
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1

            # Append character to the current statement if not within a comment
            if not in_comment:
                statement += char

            # If balance is 0 and the character is a semicolon, we have a complete statement
            if balance == 0 and char == ';':
                statements.append(statement.strip()[:-1])
                statement = ''  # Reset the statement

        # If there's a statement left after iteration, add it to the list
        if statement.strip():
            statements.append(statement.strip())

        return statements

    def remove_outer_parentheses(self, statement):
        if statement[0] == ' ':
            return statement[2:-1]
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
                        print("Error: Division by zero")
                        return
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
        if level > self.max_conditionals_level:
            print("Maximum conditional level exceeded.")
            return

        conditional_statement = self.remove_outer_parentheses(conditional_statement)
        _, conditional_statement = conditional_statement.split(maxsplit=1)
        predicate, consequent = conditional_statement.split(":", maxsplit=1)
        statements = self.parse_program(consequent)

        if self.evaluate_expression(predicate):
            self.interpret_statements(statements, level + 1)

    def evaluate_loop(self, loop_statement, level):
        if level > self.max_loops_level:
            print("Maximum loop level exceeded.")
            self.max_loops_reached = 1
            return

        loop_statement = self.remove_outer_parentheses(loop_statement)
        _, loop_statement = loop_statement.split(maxsplit=1)
        predicate, consequent = loop_statement.split(":", maxsplit=1)
        statements = self.parse_program(consequent)

        while self.evaluate_expression(predicate) and not self.max_loops_reached:
            self.interpret_statements(statements, level + 1)

        if level == 1 and self.max_loops_reached:
            self.max_loops_reached = 0
            return

    def evaluate_print(self, print_statement):
        print_statement = self.remove_outer_parentheses(print_statement)
        _, content = print_statement.split(maxsplit=1)
        if not content.startswith('('):
            print(f"Error: expected '(' after print")
            return
        content = self.remove_outer_parentheses(content)
        content = content.strip()

        # Check if the content is a string (enclosed in double quotes)
        if content.startswith('"') and content.endswith('"'):
            print(content.strip('"'))
        else:
            # Split the content into parts separated by commas
            parts = [part.strip() for part in re.split(r',(?![^\(]*\))', content)]

            for part in parts:
                if part.startswith('"') and part.endswith('"'):
                    print(part.strip('"'), end=' ')
                else:
                    try:
                        # Try to evaluate the part as an expression
                        result = self.evaluate_expression(part)
                        print(result, end=' ')
                    except ValueError:
                        # If it's not a valid expression, print the string representation of the variable
                        if part in self.symbol_table:
                            print(self.symbol_table[part], end=' ')
                        else:
                            # If the variable is not defined, print an error
                            print(f"Error: Variable '{part}' not defined.", end=' ')
            print()


interpreter = SimplCalcInterpreter()

# with open('script.txt', 'r') as file:
#     script = file.read()


if len(sys.argv) != 2:
    print("Usage: python interpreter.py <script_file>")
    sys.exit(1)

script_file = sys.argv[1]

try:
    with open(script_file, 'r') as file:
        script = file.read()
except FileNotFoundError:
    print(f"Error: File '{script_file}' not found.")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

interpreter.interpret(script)
