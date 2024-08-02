import re
from graphviz import Digraph

# Paso 1: Función para leer expresiones regulares desde un archivo de texto
def read_expressions_from_file(file_path):
    expressions = []
    try:
        with open(file_path, 'r') as file:
            for linea in file:
                expressions.append(linea.strip())  
    except FileNotFoundError:
        print(f"El archivo {file_path} no se encontró.")
    except Exception as e:
        print(f"Se produjo un error: {e}")
    return expressions

"""
(a*|b*)+
((e|a)|b*)*
(a|b)*abb(a|b)*
0?(1?)?0*
"""

# Paso 2: Transformar las extensiones de expresiones regulares (+ y ?)
def transform_extensions(regex):
    regex = regex.replace('+', '{PLUS}')
    regex = regex.replace('?', '{QUESTION}')
    transformed = re.sub(r'(\w)\{PLUS\}', r'\1\1*', regex)
    transformed = re.sub(r'\{QUESTION\}', r'|ε', transformed)
    
    return transformed

# Paso 3: Conversión de Infix a Postfix (ya implementado anteriormente)
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
                res.append(c1)
        else:
            res.append(c1)
            if i + 1 < len(regex):
                c2 = regex[i + 1]
                if (c1 not in allOperators and c1 != '(' and c1 != ')') and (c2 not in allOperators and c2 != ')' and c2 != '('):
                    res.append('.')
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

def infixToPostfix(regex):
    if not checkParenthesesBalance(regex):
        raise ValueError("Mismatched parentheses")

    postfix = []
    stack = []
    formattedRegEx = formatRegEx(regex)
    
    i = 0
    while i < len(formattedRegEx):
        c = formattedRegEx[i]
        if c == '\\':
            if i + 1 < len(formattedRegEx):
                postfix.append(formattedRegEx[i])
                postfix.append(formattedRegEx[i + 1])
                i += 1
        elif c.isalnum() or c in ['[', ']', '{', '}', '+', '.']:
            postfix.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            if stack:
                stack.pop()
            else:
                raise ValueError("Mismatched parentheses")
        else:
            while stack and getPrecedence(stack[-1]) >= getPrecedence(c):
                postfix.append(stack.pop())
            stack.append(c)
        i += 1

    while stack:
        top = stack.pop()
        if top == '(':
            raise ValueError("Mismatched parentheses")
        postfix.append(top)

    return ''.join(postfix)

# Paso 4: Definir las clases para el árbol sintáctico

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

# Paso 5: Construir el árbol sintáctico a partir de la expresión postfix

def build_ast(postfix):
    stack = []
    for char in postfix:
        if char.isalnum() or char in ['[', ']', '{', '}', '+', '.']:
            stack.append(Node(char))
        else:
            if char in {'*', '?', '+'}:
                node = Node(char, stack.pop())
            else:
                right = stack.pop()
                left = stack.pop()
                node = Node(char, left, right)
            stack.append(node)
    return stack.pop()

def print_ast(node, level=0):
    if node:
        print_ast(node.right, level + 1)
        print(' ' * 4 * level + '->', node.value)
        print_ast(node.left, level + 1)

# Paso 6: Dibujar el árbol utilizando Graphviz

def draw_ast(node):
    dot = Digraph()
    def add_nodes_edges(node):
        if node:
            dot.node(str(id(node)), node.value)
            if node.left:
                dot.edge(str(id(node)), str(id(node.left)))
                add_nodes_edges(node.left)
            if node.right:
                dot.edge(str(id(node)), str(id(node.right)))
                add_nodes_edges(node.right)
    add_nodes_edges(node)
    return dot

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

# Ejemplo de uso: Leer expresiones desde un archivo de texto y procesarlas

expresiones = read_expressions_from_file("regexs.txt")  

for expresion in expresiones:
    try:
        print(f"Processing expression: {expresion}")
        transformed_expression = transform_extensions(expresion)
        postfix = infixToPostfix(transformed_expression)
        print(f"Expresión Infix: {expresion}")
        print(f"Expresión Postfix: {postfix}")
        ast = build_ast(postfix)
        print_ast(ast)
        sanitized_expression = sanitize_filename(expresion)
        dot = draw_ast(ast)
        dot.render(f'ast_{sanitized_expression}', format='png', view=True)
        print("\n")
    except ValueError as e:
        print(f"Error processing expression {expresion}: {e}")
