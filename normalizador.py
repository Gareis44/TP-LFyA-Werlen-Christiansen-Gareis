import ast
import copy
import builtins


NOMBRES_RESERVADOS = set(dir(builtins))

class NormalizadorAST(ast.NodeTransformer):
    
    def __init__(self):
        super().__init__()
        self.tabla_simbolos = {}
        self.contador_vars = 0

    def _obtener_token_var(self, nombre_original: str) -> str:
        if nombre_original in NOMBRES_RESERVADOS:
            return nombre_original
        if nombre_original not in self.tabla_simbolos:
            self.contador_vars += 1
            self.tabla_simbolos[nombre_original] = f"VAR{self.contador_vars}"

        return self.tabla_simbolos[nombre_original]

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        # Aca se tiene en cuenta que el nombre del afuncion no influye en la comparacion
        node.name = "FUNC"
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        node.name = "FUNC"
        return self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> ast.AST:
        node.arg = self._obtener_token_var(node.arg)
        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> ast.AST:
        node.id = self._obtener_token_var(node.id)
        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, (int, float, str, bytes)) and not isinstance(node.value, bool):
            node.value = "LIT"
        return self.generic_visit(node)


def normalizar_arbol(arbol_funcion: ast.AST) -> ast.AST:

    arbol_copia = copy.deepcopy(arbol_funcion)
    normalizador = NormalizadorAST()
    arbol_normalizado = normalizador.visit(arbol_copia)
    ast.fix_missing_locations(arbol_normalizado)
    return arbol_normalizado

