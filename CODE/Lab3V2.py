import re
import networkx as nx
import matplotlib.pyplot as plt

# Step 1: Function to read regular expressions from a text file
def read_expressions_from_file(file_path):
    expressions = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                expressions.append(line.strip())
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return expressions

# Step 2: Transforming regular expression extensions (+ and ?)
def transform_extensions(regex):
    longitud = len(regex)
    resultado = []

    for i in range(longitud):
        if regex[i] == '+':
            if resultado and resultado[-1] == ')':
                balance = 0
                j = len(resultado) - 1
                while j >= 0:
                    if resultado[j] == ')':
                        balance += 1
                    elif resultado[j] == '(':
                        balance -= 1
                    if balance == 0:
                        break
                    j -= 1
                grupo = ''.join(resultado[j:])
                resultado = resultado[:j]
                resultado.append(f"({grupo}{grupo}*)")
            elif resultado and resultado[-1].isalnum():
                ultimo_caracter = resultado.pop()
                resultado.append(f"({ultimo_caracter}{ultimo_caracter}*)")
        elif regex[i] == '?':
            if resultado and resultado[-1] == ')':
                balance = 0
                j = len(resultado) - 1
                while j >= 0:
                    if resultado[j] == ')':
                        balance += 1
                    elif resultado[j] == '(':
                        balance -= 1
                    if balance == 0:
                        break
                    j -= 1
                grupo = ''.join(resultado[j:])
                resultado = resultado[:j]
                resultado.append(f"({grupo}|ε)")
            elif resultado and resultado[-1].isalnum():
                ultimo_caracter = resultado.pop()
                resultado.append(f"({ultimo_caracter}|ε)")
        else:
            resultado.append(regex[i])
    return ''.join(resultado)

# Step 3: Ensuring correct infix to postfix conversion using Shunting Yard algorithm
def getPrecedence(c):
    precedences = {'(': 1, '|': 2, '.': 3, '?': 4, '*': 4, '+': 4, '^': 5}
    return precedences.get(c, 0)

def formatRegEx(regex):
    allOperators = {'|', '?', '+', '*', '^'}
    res = []
    
    i = 0
    while i < len(regex):
        c1 = regex[i]
        
        if c1 == '\\':
            if i + 1 < len(regex) and regex[i + 1] in ['(', ')', '\\', '[', ']', '{', '}', '+', '.']:
                res.append(c1)
                res.append(regex[i + 1])
                i += 1
        else:
            if c1 not in allOperators and (i + 1 < len(regex) and regex[i + 1] not in allOperators):
                res.append(c1)
                res.append('.')
            else:
                res.append(c1)
        i += 1
    
    return ''.join(res)

def checkParenthesesBalance(regex):
    stack = []
    escaped = False
    for c in regex:
        if c == '\\':
            escaped = not escaped
        elif not escaped:
            if c == '(':
                stack.append(c)
            elif c == ')':
                if not stack:
                    return False
                stack.pop()
        else:
            escaped = False
    return not stack

# Ajustar la lógica de concatenación implícita y precedencia de operadores en infixToPostfix
def infixToPostfix(regex):
    if not checkParenthesesBalance(regex):
        raise ValueError("Mismatched parentheses")

    postfix = []
    stack = []
    formattedRegEx = formatRegEx(regex)

    for i, c in enumerate(formattedRegEx):
        if c.isalnum() or c in ['ε']:
            postfix.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
            else:
                raise ValueError("Mismatched parentheses")
        else:
            while stack and getPrecedence(stack[-1]) >= getPrecedence(c):
                postfix.append(stack.pop())
            stack.append(c)

    while stack:
        if stack[-1] == '(':
            raise ValueError("Mismatched parentheses")
        postfix.append(stack.pop())

    return ''.join(postfix)

# Función de simplificación ajustada
def simplify_expression(expression):
    # Eliminar paréntesis redundantes alrededor de caracteres individuales
    expression = re.sub(r'\(\s*(\w|\s*ε\s*)\s*\)', r'\1', expression)

    # Simplificar expresiones con ε, preservando la estructura
    while True:
        new_expr = re.sub(r'\(\s*ε\s*\)', 'ε', expression)
        new_expr = re.sub(r'\(\s*\(\s*ε\s*\)\s*\)', 'ε', new_expr)  # Eliminar paréntesis anidados
        if new_expr == expression:
            break
        expression = new_expr

    return expression

# Step 4: Defining the AST and drawing it using NetworkX
class ASTNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

def postfix_to_ast(postfix):
    stack = []
    for char in postfix:
        if char.isalnum() or char == 'ε':
            stack.append(ASTNode(char))
        elif char in ['*', '?', '+']:
            if stack:
                operand = stack.pop()
                stack.append(ASTNode(char, operand))
        elif char in ['|', '.']:
            if len(stack) >= 2:
                right = stack.pop()
                left = stack.pop()
                stack.append(ASTNode(char, left, right))
        else:
            stack.append(ASTNode(char))
    
    if len(stack) != 1:
        raise ValueError(f"Invalid postfix expression: {postfix}")
    
    return stack[0]

def draw_ast(root):
    graph = nx.DiGraph()
    
    def add_edges(node):
        if not node:
            return
        if node.left:
            graph.add_edge(node.value, node.left.value)
            add_edges(node.left)
        if node.right:
            graph.add_edge(node.value, node.right.value)
            add_edges(node.right)

    add_edges(root)
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, arrows=True)
    plt.show()

# Step 5: Main logic
def main():
    expressions = read_expressions_from_file('regexs.txt')
    for expression in expressions:
        print(f"Original Expression: {expression}")
        transformed_expression = transform_extensions(expression)
        print(f"Transformed Expression: {transformed_expression}")
        simplified_expression = simplify_expression(transformed_expression)
        print(f"Simplified Expression: {simplified_expression}")
        postfix_expression = infixToPostfix(simplified_expression)
        print(f"Postfix Expression: {postfix_expression}")
        try:
            ast_root = postfix_to_ast(postfix_expression)
            draw_ast(ast_root)
        except IndexError as e:
            print(f"Error in constructing AST for expression: {expression}")
            print(e)

main()
