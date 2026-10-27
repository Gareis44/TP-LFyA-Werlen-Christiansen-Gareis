import argparse
import ast
import os
import sys
from typing import Optional, Tuple

import extractor
import normalizador
import similitud


def obtener_funcion_objetivo(especificacion: str) -> Tuple[str, ast.AST]:
    texto_limpio = especificacion.strip()
    if texto_limpio.startswith("def ") or texto_limpio.startswith("async def "):
        try:
            arbol_cadena = ast.parse(texto_limpio)
            for nodo in ast.walk(arbol_cadena):
                if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return f"codigo_en_linea:{nodo.name}", nodo
            print("Error: El texto proporcionado no contiene ninguna definicion de funcion valida.")
            sys.exit(1)
        except SyntaxError as e:
            print(f"Error de sintaxis al procesar el código inline: {e}")
            sys.exit(1)

    if ":" in especificacion:
        ruta_archivo, nombre_func = especificacion.split(":", 1)
        if not os.path.exists(ruta_archivo):
            print(f"Error: No existe el archivo '{ruta_archivo}'.")
            sys.exit(1)

        funciones = extractor.extraer_funciones_de_archivo(ruta_archivo)
        for fn in funciones:
            if fn.nombre == nombre_func:
                return f"{fn.archivo}:{fn.nombre}", fn.arbol

        print(f"Error: No se encontro la funcion '{nombre_func}' en '{ruta_archivo}'.")
        sys.exit(1)

    elif os.path.exists(especificacion):
        funciones = extractor.extraer_funciones_de_archivo(especificacion)
        if not funciones:
            print(f"Error: No se encontraron funciones dentro de '{especificacion}'.")
            sys.exit(1)
        return f"{funciones[0].archivo}:{funciones[0].nombre}", funciones[0].arbol

    try:
        arbol_cadena = ast.parse(especificacion)
        for nodo in ast.walk(arbol_cadena):
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return f"codigo_en_linea:{nodo.name}", nodo
        print(f"Error: No se encontro el archivo '{especificacion}' ni contiene codigo ejecutable")
        sys.exit(1)
    except SyntaxError:
        print(f"Error: No se reconoce la especificacion ni el archivo '{especificacion}'.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Motor de busqueda de funciones estructuralmente similares vía AST."
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Ruta al repositorio o carpeta que contiene los archivos .py a analizar.",
    )
    parser.add_argument(
        "--funcion",
        required=True,
        help="Función objetivo en formato 'ruta/archivo.py:nombre_funcion' o código inline.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Cantidad de resultados más similares a mostrar (por defecto: 5).",
    )
    parser.add_argument(
        "--umbral",
        type=float,
        default=similitud.UMBRAL_DUPLICADO,
        help=f"Umbral de similitud para notificar unposible duplicado (0.0 a 1.0, por defecto: {similitud.UMBRAL_DUPLICADO}).",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"Error: El directorio '{args.dir}' no existe o no es válido.")
        sys.exit(1)

    nombre_objetivo, ast_objetivo = obtener_funcion_objetivo(args.funcion)
    ast_objetivo_norm = normalizador.normalizar_arbol(ast_objetivo)
    tokens_objetivo = similitud.ast_a_secuencia_preorder(ast_objetivo_norm)

    print(f"\n[+] Función objetivo cargada: {nombre_objetivo}")
    print(f"[+] Cantidad de tokens estructurales: {len(tokens_objetivo)}")
    print(f"[+] Escaneando directorio: '{args.dir}'...")

    universo = extractor.extraer_funciones_de_directorio(args.dir)
    print(f"[+] Se encontraron {len(universo)} funciones en total.")

    resultados = []

    archivo_obj_ref = args.funcion.split(":")[0] if ":" in args.funcion else None
    nombre_obj_ref = args.funcion.split(":")[1] if ":" in args.funcion else None

    for candidata in universo:
        if (
            archivo_obj_ref
            and os.path.abspath(candidata.archivo) == os.path.abspath(archivo_obj_ref)
            and candidata.nombre == nombre_obj_ref
        ):
            continue

        ast_candidata_norm = normalizador.normalizar_arbol(candidata.arbol)
        tokens_candidata = similitud.ast_a_secuencia_preorder(ast_candidata_norm)

        score = similitud.similitud_jaccard(tokens_objetivo, tokens_candidata, n=3)

        resultados.append(
            {
                "nombre": candidata.nombre,
                "archivo": candidata.archivo,
                "linea": candidata.linea,
                "score": score,
                "es_duplicado": similitud.es_duplicado(score, umbral=args.umbral),
            }
        )

    resultados.sort(key=lambda x: x["score"], reverse=True)

    top_k = resultados[: args.top]

    print("\n" + "=" * 70)
    print(f" RESULTADOS TOP {args.top} - SIMILITUD ESTRUCTURAL")
    print("=" * 70)

    if not top_k:
        print("No se encontraron otras funciones para comparar.")
        return

    for i, res in enumerate(top_k, start=1):
        estado_duplicado = "[Clon Detectado!]" if res["es_duplicado"] else "[OK]"
        print(f"{i}. {estado_duplicado} Score: {res['score'] * 100:6.2f}%")
        print(f"   Función: {res['nombre']}")
        print(f"   Ubicación: {res['archivo']}:{res['linea']}")
        print("-" * 70)


if __name__ == "__main__":
    main()