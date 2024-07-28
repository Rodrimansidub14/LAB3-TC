import graphviz

class NodoAST:
    def __init__(self, valor):
        self.valor = valor
        self.izquierdo = None
        self.derecho = None

def crear_arbol_sintactico(postfix):
    stack = []

    for char in postfix:
        if char.isalnum():
            nodo = NodoAST(char)
            stack.append(nodo)
        else:
            nodo = NodoAST(char)
            if char in {'*', '?', '+'}:
                nodo.izquierdo = stack.pop()
            else:
                nodo.derecho = stack.pop()
                nodo.izquierdo = stack.pop()
            stack.append(nodo)

    return stack.pop()

def dibujar_arbol(root, graph=None):
    if graph is None:
        graph = graphviz.Digraph()

    graph.node(str(id(root)), root.valor)

    if root.izquierdo:
        graph.edge(str(id(root)), str(id(root.izquierdo)))
        dibujar_arbol(root.izquierdo, graph)

    if root.derecho:
        graph.edge(str(id(root)), str(id(root.derecho)))
        dibujar_arbol(root.derecho, graph)

    return graph

def procesar_expresiones(archivo):
    with open(archivo, 'r') as f:
        expresiones = f.readlines()

    for expresion in expresiones:
        expresion = expresion.strip()
        try:
            print(f"Procesando expresión: {expresion}")
            postfix = infixToPostfix(expresion)
            print(f"Expresión Infix: {expresion}")
            print(f"Expresión Postfix: {postfix}")

            ast = crear_arbol_sintactico(postfix)
            graph = dibujar_arbol(ast)
            graph.render(f'arbol_{expresion}.gv', view=True)
            print(f"Árbol sintáctico generado y guardado como arbol_{expresion}.gv\n")
        except ValueError as e:
            print(f"Error al procesar la expresión {expresion}: {e}")

# Ejemplo de uso
archivo = 'regexs.txt'
procesar_expresiones(archivo)
