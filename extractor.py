import os
import ast
from dataclasses import dataclass
from typing import List

@dataclass
class FuncionExtraida:
    nombre: str
    archivo: str
    linea: int
    arbol: ast.AST

def extraer_funciones_de_archivo(ruta_archivo: str) -> List[FuncionExtraida]:
    funciones = []
    
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
            
        arbol_completo = ast.parse(contenido, filename=ruta_archivo)
        
        for nodo in ast.walk(arbol_completo):
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                info_funcion = FuncionExtraida(
                    nombre=nodo.name,
                    archivo=ruta_archivo,
                    linea=nodo.lineno,
                    arbol=nodo 
                )
                funciones.append(info_funcion)
                
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"[Aviso] No se pudo parsear {ruta_archivo}: {e}")
        
    return funciones

def extraer_funciones_de_directorio(directorio_raiz: str) -> List[FuncionExtraida]:
    todas_las_funciones = []
    
    for raiz, _, archivos in os.walk(directorio_raiz):
        for archivo in archivos:
            if archivo.endswith(".py"):
                ruta_completa = os.path.join(raiz, archivo)
                funciones_archivo = extraer_funciones_de_archivo(ruta_completa)
                todas_las_funciones.extend(funciones_archivo)
                
    return todas_las_funciones
