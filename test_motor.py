import ast
import pytest
import normalizador
import similitud


def calcular_score_entre_codigos(codigo_a: str, codigo_b: str, n: int = 3) -> float:

    nodo_a = ast.parse(codigo_a).body[0]
    nodo_b = ast.parse(codigo_b).body[0]

    norm_a = normalizador.normalizar_arbol(nodo_a)
    norm_b = normalizador.normalizar_arbol(nodo_b)


    tokens_a = similitud.ast_a_secuencia_preorder(norm_a)
    tokens_b = similitud.ast_a_secuencia_preorder(norm_b)

    return similitud.similitud_jaccard(tokens_a, tokens_b, n=n)


def test_caso_positivo_1_renombrado_total():
    codigo_original = """
def calcular_hipotenusa(cateto_a, cateto_b):
    cuadrado_a = cateto_a ** 2
    cuadrado_b = cateto_b ** 2
    suma = cuadrado_a + cuadrado_b
    raiz = suma ** 0.5
    return raiz
"""

    codigo_clonado = """
def obtener_distancia(x, y):
    val_x = x ** 2
    val_y = y ** 2
    total = val_x + val_y
    resultado = total ** 0.5
    return resultado
"""

    score = calcular_score_entre_codigos(codigo_original, codigo_clonado)
    
    assert score == pytest.approx(1.0, abs=1e-4), f"Esperado 1.0, pero dio {score}"
    assert similitud.es_duplicado(score) is True


def test_caso_positivo_2_lineas_reordenadas():
    codigo_base = """
def configurar_usuario(nombre, edad, rol):
    nombre_normalizado = nombre.strip().lower()
    edad_verificada = max(0, edad)
    rol_asignado = rol.upper()
    mensaje = f"{nombre_normalizado}-{edad_verificada}-{rol_asignado}"
    return mensaje
"""

    codigo_reordenado = """
def registrar_perfil(nom, ed, r):
    nom_norm = nom.strip().lower()
    r_asig = r.upper()
    ed_verif = max(0, ed)
    msj = f"{nom_norm}-{ed_verif}-{r_asig}"
    return msj
"""

    score = calcular_score_entre_codigos(codigo_base, codigo_reordenado)
    
    assert score >= 0.80, f"Se esperaba score >= 0.80 para líneas reordenadas, dio {score}"
    assert similitud.es_duplicado(score) is True



def test_caso_negativo_1_aritmetica_vs_iteracion():
    codigo_aritmetico = """
def calcular_promedio(a, b, c):
    suma = a + b + c
    return suma / 3
"""

    codigo_iterativo = """
def buscar_mayores(lista_valores, corte):
    seleccionados = []
    for item in lista_valores:
        if item > corte:
            seleccionados.append(item)
    return seleccionados
"""

    score = calcular_score_entre_codigos(codigo_aritmetico, codigo_iterativo)
    
    assert score < 0.35, f"Score esperado bajo (< 0.35), pero dio {score}"
    assert similitud.es_duplicado(score) is False


def test_caso_negativo_2_recursivo_vs_diccionario():
    codigo_recursivo = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

    codigo_diccionario = """
def obtener_info_capital(pais, registros):
    capital = registros.get(pais, "No encontrado")
    return {"pais": pais, "capital": capital}
"""

    score = calcular_score_entre_codigos(codigo_recursivo, codigo_diccionario)

    assert score < 0.30, f"Score esperado bajo (< 0.30), pero dio {score}"
    assert similitud.es_duplicado(score) is False