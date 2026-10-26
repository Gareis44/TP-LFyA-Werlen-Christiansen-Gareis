import ast
from typing import List, Set, Tuple

def ast_a_secuencia_preorder(nodo: ast.AST) -> List[str]:

    tokens = []

    tokens.append(nodo.__class__.__name__)

    if isinstance(nodo, ast.Name):
        tokens.append(str(nodo.id))
    elif isinstance(nodo, ast.arg):
        tokens.append(str(nodo.arg))
    elif isinstance(nodo, ast.Constant):
        tokens.append(str(nodo.value))
    for hijo in ast.iter_child_nodes(nodo):
        tokens.extend(ast_a_secuencia_preorder(hijo))

    return tokens


def generar_ngramas(tokens: List[str], n: int = 3) -> Set[Tuple[str, ...]]:

    if len(tokens) < n:
        return {tuple(tokens)}

    ngramas = set()
    for i in range(len(tokens) - n + 1):
        ventana = tuple(tokens[i : i + n])
        ngramas.add(ventana)
    return ngramas


def similitud_jaccard(tokens_1: List[str], tokens_2: List[str], n: int = 3) -> float:

    set_a = generar_ngramas(tokens_1, n=n)
    set_b = generar_ngramas(tokens_2, n=n)

    interseccion = set_a.intersection(set_b)
    union = set_a.union(set_b)

    if not union:
        return 0.0

    return len(interseccion) / len(union)


UMBRAL_DUPLICADO = 0.80

def es_duplicado(score: float, umbral: float = UMBRAL_DUPLICADO) -> bool:
    return score >= umbral
