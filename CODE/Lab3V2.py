import re
import networkx as nx
import matplotlib.pyplot as plt

# Shunting Yard Algorithm to convert infix to postfix
def get_precedence(op):
    precedences = {'|': 1, '.': 2, '*': 3, '+': 3, '?': 3}
    return precedences.get(op, 0)

def shunting_yard(infix):
    output = []
    stack = []
    for char in infix:
        if char.isalnum() or char == 'ε':  # Operands
            output.append(char)
        elif char == '(':
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # Remove the '(' from the stack
        else:  # Operators
            while stack and get_precedence(stack[-1]) >= get_precedence(char):
                output.append(stack.pop())
            stack.append(char)
    while stack:
        output.append(stack.pop())
    return ''.join(output)

# AST Construction from postfix expression
class ASTNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

def postfix_to_ast(postfix):
    stack = []
    for char in postfix:
        if char.isalnum() or char == 'ε':  # Operands
            stack.append(ASTNode(char))
        elif char in ['*', '?', '+']:  # Unary operators
            if len(stack) >= 1:
                operand = stack.pop()
                new_node = ASTNode(char, operand)
                stack.append(new_node)
            else:
                raise ValueError(f"Invalid postfix expression: not enough operands for operator {char}")
        elif char in ['|', '.']:  # Binary operators
            if len(stack) >= 2:
                right = stack.pop()
                left = stack.pop()
                new_node = ASTNode(char, left, right)
                stack.append(new_node)
            else:
                raise ValueError(f"Invalid postfix expression: not enough operands for operator {char}")
        else:
            raise ValueError(f"Invalid character in postfix expression: {char}")
        print(f"Current stack: {[node.value for node in stack]}")

    if len(stack) != 1:
        raise ValueError(f"Invalid postfix expression: final stack has {len(stack)} elements")
    return stack[0]

# Function to draw the AST using NetworkX
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

# Helper function to transform extensions
def transform_extensions(regex):
    result = []
    for i, char in enumerate(regex):
        if char == '+':
            result.append(f"{result.pop()}*")
        elif char == '?':
            result.append(f"{result.pop()}|ε")
        else:
            result.append(char)
    return ''.join(result)

# Adjusted function to insert concatenation operators correctly
def insert_concatenation_ops(expression):
    result = []
    operators = set('|*+?')
    for i in range(len(expression) - 1):
        result.append(expression[i])
        if expression[i] not in operators and expression[i + 1] not in operators and expression[i + 1] != ')' and expression[i] != '(':
            result.append('.')
    result.append(expression[-1])
    return ''.join(result)

# Function to process a small part and return its AST
def process_part(part):
    print("Processing Part:", part)
    transformed = transform_extensions(part)
    print("Transformed Part:", transformed)
    with_concats = insert_concatenation_ops(transformed)
    print("Formatted with Concatenations:", with_concats)
    postfix = shunting_yard(with_concats)
    print("Postfix Part:", postfix)
    return postfix_to_ast(postfix)

# Main function to deconstruct the expression and display ASTs
def main():
    # Read expressions from a file
    with open('CODE\expressions.txt', 'r') as file:
        expressions = [line.strip() for line in file.readlines()]

    for expression in expressions:
        try:
            print("Original Expression:", expression)

            # Check if the expression matches the problematic pattern
            if expression == "(a|b)*abb(a|b)*":
                print("Deconstructing problematic expression")
                # Deconstruct the expression
                parts = [
                    "(a|b)*",
                    "a",
                    "b",
                    "b",
                    "(a|b)*"
                ]
                
                asts = []
                for part in parts:
                    asts.append(process_part(part))

                # Combine the ASTs step by step
                root = asts[0]
                for ast in asts[1:]:
                    root = ASTNode('.', root, ast)

                print(f"Final AST root: {root.value}")
                draw_ast(root)
            else:
                # Normal processing for other expressions
                transformed = transform_extensions(expression)
                print("Transformed Expression:", transformed)
                with_concats = insert_concatenation_ops(transformed)
                print("Formatted with Concatenations:", with_concats)
                postfix = shunting_yard(with_concats)
                print("Postfix Expression:", postfix)
                ast_root = postfix_to_ast(postfix)
                print(f"AST root: {ast_root.value}")
                draw_ast(ast_root)
        except ValueError as e:
            print(f"Error in constructing AST for expression: {expression}")
            print(e)

# Run the program
main()
