def calcular_descuento_comercial(precio_base, porcentaje):
    monto_descuento = precio_base * (porcentaje / 100)
    precio_final = precio_base - monto_descuento
    return precio_final

def aplicar_rebaja(p, desc):
    sub = p * (desc / 100)
    res = p - sub
    return res

def obtener_numeros_primos(hasta):
    primos = []
    for n in range(2, hasta):
        es_primo = True
        for d in range(2, n):
            if n % d == 0:
                es_primo = False
                break
        if es_primo:
            primos.append(n)
    return primos