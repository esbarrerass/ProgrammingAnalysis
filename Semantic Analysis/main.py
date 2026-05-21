# ------- INTEGRANTES ----------

'''Esteban Barrera Sanabria
Michael Daniels Oviedo Quiroga
Julian David Rodriguez Fernandez'''

import sys
import math
import io

# Tipos especiales

class _Nulo:
    def __repr__(self): return "nulo"

class _Indefinido:
    def __repr__(self): return "indefinido"

NULO = _Nulo()
INDEFINIDO = _Indefinido()

class ExcRetornar(Exception):
    def __init__(self, valor): self.valor = valor

class ExcRomper(Exception): pass
class ExcContinuar(Exception): pass

class EsFuncion:
    def __init__(self, nombre, params, tok_inicio, env_cierre, expr_flecha=False):
        self.nombre = nombre
        self.params = params
        self.tok_inicio = tok_inicio   # indice del { 
        self.env_cierre = env_cierre
        self.expr_flecha = expr_flecha

class EsFuncionNativa:
    def __init__(self, fn): self.fn = fn

class LValue:
    def __init__(self, tipo, env=None, nombre=None, obj=None, clave=None):
        self.tipo = tipo 
        self.env = env
        self.nombre = nombre
        self.obj = obj
        self.clave = clave

    def obtener(self):
        if self.tipo == "var":
            return self.env.obtener(self.nombre)
        if self.tipo == "prop":
            return obtener_propiedad(self.obj, self.clave)
        return obtener_indice(self.obj, self.clave)

    def asignar(self, valor):
        if self.tipo == "var":
            self.env.asignar(self.nombre, valor)
        elif self.tipo == "prop":
            asignar_propiedad(self.obj, self.clave, valor)
        else:
            asignar_indice(self.obj, self.clave, valor)

#Entorno
class Entorno:
    def __init__(self, padre=None, es_funcion=False):
        self.vars = {}
        self.padre = padre
        self.es_funcion = es_funcion

    def obtener(self, nombre):
        if nombre in self.vars:
            return self.vars[nombre]
        if self.padre:
            return self.padre.obtener(nombre)
        return INDEFINIDO

    def asignar(self, nombre, valor):
        env = self
        while env:
            if nombre in env.vars:
                env.vars[nombre] = valor
                return
            env = env.padre
        raiz = self
        while raiz.padre:
            raiz = raiz.padre
        raiz.vars[nombre] = valor

    def definir(self, nombre, valor):
        self.vars[nombre] = valor

    def definir_var(self, nombre):
        env = self
        while env.padre and not env.es_funcion:
            env = env.padre
        if nombre not in env.vars:
            env.vars[nombre] = INDEFINIDO

#Utilidades de coerción y comparación
def es_verdadero(v):
    if isinstance(v, (_Nulo, _Indefinido)): return False
    if isinstance(v, bool): return v
    if isinstance(v, float): return v != 0.0 and v == v
    if isinstance(v, int): return v != 0
    if isinstance(v, str): return len(v) > 0
    return True

def a_numero(v):
    if isinstance(v, bool): return 1.0 if v else 0.0
    if isinstance(v, (int, float)): return float(v)
    if isinstance(v, str):
        s = v.strip()
        if s == "": return 0.0
        try: return float(s)
        except: return float('nan')
    if isinstance(v, _Nulo): return 0.0
    return float('nan')

def a_cadena(v):
    if isinstance(v, bool): return "verdadero" if v else "falso"
    if isinstance(v, _Nulo): return "nulo"
    if isinstance(v, _Indefinido): return "indefinido"
    if isinstance(v, float):
        if v == float('inf'): return "Infinito"
        if v == float('-inf'): return "-Infinito"
        if v != v: return "NuN"
        if v == int(v) and abs(v) < 1e15: return str(int(v))
        return repr(v)
    if isinstance(v, int): return str(v)
    if isinstance(v, str): return v
    if isinstance(v, list): return "[" + ",".join(a_cadena(x) for x in v) + "]"
    if isinstance(v, dict): return "[object Object]"
    if isinstance(v, EsFuncion): return "function " + (v.nombre or "")
    if isinstance(v, EsFuncionNativa): return "function"
    return str(v)

def igual_laxo(a, b):
    if isinstance(a, (_Nulo, _Indefinido)) and isinstance(b, (_Nulo, _Indefinido)):
        return True
    if isinstance(a, (_Nulo, _Indefinido)) or isinstance(b, (_Nulo, _Indefinido)):
        return False
    na = 1 if (isinstance(a, bool) and a) else (0 if isinstance(a, bool) else a)
    nb = 1 if (isinstance(b, bool) and b) else (0 if isinstance(b, bool) else b)
    a, b = na, nb
    if isinstance(a, str) and isinstance(b, (int, float)):
        try: a = float(a)
        except: return False
    elif isinstance(b, str) and isinstance(a, (int, float)):
        try: b = float(b)
        except: return False
    if isinstance(a, float) and isinstance(b, float):
        return a == b
    return a == b

def igual_estricto(a, b):
    if type(a) is bool or type(b) is bool:
        return type(a) is type(b) and a == b
    if isinstance(a, (_Nulo,)) and isinstance(b, (_Nulo,)): return True
    if isinstance(a, (_Indefinido,)) and isinstance(b, (_Indefinido,)): return True
    if isinstance(a, (_Nulo, _Indefinido)) or isinstance(b, (_Nulo, _Indefinido)):
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        af, bf = float(a), float(b)
        if af != af: return False
        return af == bf
    if isinstance(a, str) and isinstance(b, str): return a == b
    return a is b

def aplicar_op_asig(op, actual, derecho):
    if op == "=":  return derecho
    if op == "+=":
        if isinstance(actual, str) or isinstance(derecho, str):
            return a_cadena(actual) + a_cadena(derecho)
        return a_numero(actual) + a_numero(derecho)
    if op == "-=": return a_numero(actual) - a_numero(derecho)
    if op == "*=": return a_numero(actual) * a_numero(derecho)
    if op == "/=":
        d = a_numero(derecho)
        return float('nan') if d == 0 else a_numero(actual) / d
    if op == "%=":
        d = a_numero(derecho)
        return float('nan') if d == 0 else math.fmod(a_numero(actual), d)
    if op == "**=": return a_numero(actual) ** a_numero(derecho)
    return derecho

# Propiedades y métodos nativos
def _js_exponencial(num, decimales=None):
    if num != num: return "NuN"
    if num == float('inf'): return "Infinito"
    if num == float('-inf'): return "-Infinito"
    if num == 0:
        s = "0" if decimales is None else "0." + "0" * decimales
        return s + "e+0"
    neg = num < 0
    num = abs(num)
    exp = int(math.floor(math.log10(num)))
    mantissa = num / (10 ** exp)
    if decimales is None:
        s = f"{mantissa:.15f}".rstrip('0').rstrip('.')
        dec = len(s) - s.index('.') - 1 if '.' in s else 0
        mantissa_str = f"{mantissa:.{dec}f}"
    else:
        mantissa_str = f"{mantissa:.{decimales}f}"
    signo = "+" if exp >= 0 else "-"
    return ("-" if neg else "") + mantissa_str + "e" + signo + str(abs(exp))

def obtener_propiedad(obj, prop):
    if isinstance(obj, str):
        if prop == "longitud": return float(len(obj))
        metodos = {
            "aCadena":     EsFuncionNativa(lambda a, o=obj: o),
            "aMinusculas": EsFuncionNativa(lambda a, o=obj: o.lower()),
            "aMayusculas": EsFuncionNativa(lambda a, o=obj: o.upper()),
            "recortar":    EsFuncionNativa(lambda a, o=obj: o.strip()),
            "incluye":     EsFuncionNativa(lambda a, o=obj: a_cadena(a[0]) in o if a else False),
            "empiezaCon":  EsFuncionNativa(lambda a, o=obj: o.startswith(a_cadena(a[0])) if a else False),
            "terminaCon":  EsFuncionNativa(lambda a, o=obj: o.endswith(a_cadena(a[0])) if a else False),
            "reemplazar":  EsFuncionNativa(lambda a, o=obj: o.replace(a_cadena(a[0]), a_cadena(a[1])) if len(a) >= 2 else o),
            "dividir":     EsFuncionNativa(lambda a, o=obj: o.split(a_cadena(a[0])) if a else list(o)),
            "subcadena":   EsFuncionNativa(lambda a, o=obj: o[int(a_numero(a[0])):int(a_numero(a[1])) if len(a) > 1 else None] if a else o),
            "en":          EsFuncionNativa(lambda a, o=obj: o[int(a_numero(a[0]))] if a and 0 <= int(a_numero(a[0])) < len(o) else INDEFINIDO),
            "slice":       EsFuncionNativa(lambda a, o=obj: o[int(a_numero(a[0])) if a else 0: int(a_numero(a[1])) if len(a) > 1 else None]),
            "concat":      EsFuncionNativa(lambda a, o=obj: o + "".join(a_cadena(x) for x in a)),
            "repetir":     EsFuncionNativa(lambda a, o=obj: o * int(a_numero(a[0])) if a else o),
            "indexOf":     EsFuncionNativa(lambda a, o=obj: float(o.find(a_cadena(a[0]))) if a else -1.0),
            "buscar":      EsFuncionNativa(lambda a, o=obj: float(o.find(a_cadena(a[0]))) if a else -1.0),
            "recortarInicio": EsFuncionNativa(lambda a, o=obj: o.lstrip()),
            "recortarFinal":  EsFuncionNativa(lambda a, o=obj: o.rstrip()),
        }
        return metodos.get(prop, INDEFINIDO)

    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        metodos = {
            "aExponencial": EsFuncionNativa(lambda a, o=obj: _js_exponencial(o, int(a_numero(a[0])) if a else None)),
            "fijarDecimales": EsFuncionNativa(lambda a, o=obj: format(o, f'.{int(a_numero(a[0]))}f') if a else str(o)),
            "aCadena":      EsFuncionNativa(lambda a, o=obj: a_cadena(o)),
            "valorDe":      EsFuncionNativa(lambda a, o=obj: float(o)),
            "toPrecision":  EsFuncionNativa(lambda a, o=obj: format(o, f'.{int(a_numero(a[0]))}g') if a else str(o)),
        }
        return metodos.get(prop, INDEFINIDO)

    if isinstance(obj, list):
        if prop == "longitud": return float(len(obj))
        metodos = {
            "agregar":   EsFuncionNativa(lambda a, o=obj: (o.extend(a), float(len(o)))[1]),
            "pop":       EsFuncionNativa(lambda a, o=obj: o.pop() if o else INDEFINIDO),
            "shift":     EsFuncionNativa(lambda a, o=obj: o.pop(0) if o else INDEFINIDO),
            "unshift":   EsFuncionNativa(lambda a, o=obj: (o.insert(0, a[0]), float(len(o)))[1] if a else float(len(o))),
            "eliminar":  EsFuncionNativa(lambda a, o=obj: o.pop(int(a_numero(a[0]))) if a else (o.pop() if o else INDEFINIDO)),
            "unir":      EsFuncionNativa(lambda a, o=obj: (a_cadena(a[0]) if a else ",").join(a_cadena(x) for x in o)),
            "invertir":  EsFuncionNativa(lambda a, o=obj: (o.reverse(), o)[1]),
            "ordenar":   EsFuncionNativa(lambda a, o=obj: (o.sort(key=lambda x: a_cadena(x)), o)[1]),
            "rebanar":   EsFuncionNativa(lambda a, o=obj: o[int(a_numero(a[0])) if a else 0: int(a_numero(a[1])) if len(a) > 1 else None]),
            "concat":    EsFuncionNativa(lambda a, o=obj: o[:] + (a[0] if a and isinstance(a[0], list) else list(a))),
            "incluye":   EsFuncionNativa(lambda a, o=obj: any(igual_estricto(x, a[0]) for x in o) if a else False),
            "indexOf":   EsFuncionNativa(lambda a, o=obj: next((float(i) for i, x in enumerate(o) if igual_estricto(x, a[0])), -1.0) if a else -1.0),
            "forEach":   EsFuncionNativa(lambda a, o=obj: [llamar_funcion(a[0], [v, float(i), o]) for i, v in enumerate(o)] if a else None),
            "map":       EsFuncionNativa(lambda a, o=obj: [llamar_funcion(a[0], [v, float(i), o]) for i, v in enumerate(o)] if a else []),
            "filter":    EsFuncionNativa(lambda a, o=obj: [v for i, v in enumerate(o) if es_verdadero(llamar_funcion(a[0], [v, float(i), o]))] if a else []),
            "find":      EsFuncionNativa(lambda a, o=obj: next((v for v in o if es_verdadero(llamar_funcion(a[0], [v]))), INDEFINIDO) if a else INDEFINIDO),
            "every":     EsFuncionNativa(lambda a, o=obj: all(es_verdadero(llamar_funcion(a[0], [v])) for v in o) if a else True),
            "some":      EsFuncionNativa(lambda a, o=obj: any(es_verdadero(llamar_funcion(a[0], [v])) for v in o) if a else False),
            "reduce":    EsFuncionNativa(lambda a, o=obj: _reducir(a, o)),
            "splice":    EsFuncionNativa(lambda a, o=obj: _empalmar(o, a)),
            "slice":     EsFuncionNativa(lambda a, o=obj: o[int(a_numero(a[0])) if a else 0: int(a_numero(a[1])) if len(a) > 1 else None]),
        }
        return metodos.get(prop, INDEFINIDO)

    if isinstance(obj, dict):
        return obj.get(prop, INDEFINIDO)

    return INDEFINIDO

def _reducir(args, obj):
    if not args: return INDEFINIDO
    fn = args[0]
    if len(args) > 1:
        acc = args[1]
        for v in obj: acc = llamar_funcion(fn, [acc, v])
    else:
        if not obj: return INDEFINIDO
        acc = obj[0]
        for v in obj[1:]: acc = llamar_funcion(fn, [acc, v])
    return acc

def _empalmar(obj, args):
    if not args: return []
    start = int(a_numero(args[0]))
    if start < 0: start = max(0, len(obj) + start)
    delete_count = len(obj) - start if len(args) < 2 else int(a_numero(args[1]))
    removed = obj[start:start + delete_count]
    del obj[start:start + delete_count]
    for i, item in enumerate(args[2:]):
        obj.insert(start + i, item)
    return removed

def asignar_propiedad(obj, prop, valor):
    if isinstance(obj, dict):
        obj[prop] = valor
    elif isinstance(obj, list) and prop == "longitud":
        n = int(a_numero(valor))
        while len(obj) < n: obj.append(INDEFINIDO)
        while len(obj) > n: obj.pop()

def obtener_indice(obj, idx):
    if isinstance(obj, list):
        i = int(a_numero(idx))
        if 0 <= i < len(obj): return obj[i]
        return INDEFINIDO
    if isinstance(obj, str):
        i = int(a_numero(idx))
        if 0 <= i < len(obj): return obj[i]
        return INDEFINIDO
    if isinstance(obj, dict):
        return obj.get(a_cadena(idx), INDEFINIDO)
    return INDEFINIDO

def asignar_indice(obj, idx, valor):
    if isinstance(obj, list):
        i = int(a_numero(idx))
        while len(obj) <= i: obj.append(INDEFINIDO)
        obj[i] = valor
    elif isinstance(obj, dict):
        obj[a_cadena(idx)] = valor

# LLamar funcion
def llamar_funcion(fn, args, ambiente_obj=None):
    global indice
    if isinstance(fn, EsFuncionNativa):
        return fn.fn(args)
    if isinstance(fn, EsFuncion):
        indice_guardado = indice
        env_local = Entorno(fn.env_cierre, es_funcion=True)
        for i, param in enumerate(fn.params):
            env_local.definir(param, args[i] if i < len(args) else INDEFINIDO)
        if ambiente_obj is not None:
            env_local.definir("ambiente", ambiente_obj)
        else:
            env_local.definir("ambiente", INDEFINIDO)
        indice = fn.tok_inicio
        try:
            if fn.expr_flecha:
                resultado = evaluar_expresion(env_local)
            else:
                pre_escanear_bloque(env_local)
                ejecutar_bloque(env_local)
                resultado = INDEFINIDO
        except ExcRetornar as r:
            resultado = r.valor
        finally:
            indice = indice_guardado
        return resultado
    return INDEFINIDO

# Tokenizador
tokens = []
indice = 0

palabras_clave = {
    "funcion", "const", "let", "var", "mut", "retornar", "intentar", "capturar",
    "finalmente", "crear", "nuevo", "si", "sino", "mientras", "para", "hacer",
    "consola", "verdadero", "falso", "nulo", "indefinido", "elegir", "caso",
    "porDefecto", "continuar", "romper", "ambiente",
    "Arreglo", "Booleano", "Cadena", "Infinito", "Mate", "Matriz", "NuN", "Numero",
}

simbolos_multi = [
    "===", "!==", "=>", "==", "!=", "<=", ">=", "&&", "||", "++", "--",
    "**=", "**", "+=", "-=", "*=", "/=", "%=",
]
simbolos_uno = set("(){}[];,.:+-*/%=!<>?")

OPERADORES_ASIGNACION = {"=", "+=", "-=", "*=", "/=", "%=", "**="}
OPERADORES_OR = {"||"}
OPERADORES_AND = {"&&"}
OPERADORES_IGUALDAD = {"==", "!=", "===", "!=="}
OPERADORES_RELACIONALES = {"<", ">", "<=", ">="}
OPERADORES_ADITIVOS = {"+", "-"}
OPERADORES_MULTIPLICATIVOS = {"*", "/", "%", "**"}
OPERADORES_POSTFIJOS = {"++", "--"}
INICIOS_EXPRESION = {
    "ID", "NUM", "STR", "(", "[", "{", "consola", "verdadero", "falso",
    "nulo", "indefinido", "+", "-", "!", "++", "--", "crear", "nuevo",
    "Arreglo", "Booleano", "Cadena", "Infinito", "Mate", "Matriz", "NuN", "Numero",
    "ambiente",
}

def agregar_token(tipo, lexema, linea, columna):
    tokens.append({"tipo": tipo, "lexema": lexema, "linea": linea, "columna": columna})

def tokenizar(texto):
    linea = 1
    columna = 1
    i = 0
    n = len(texto)
    while i < n:
        c = texto[i]
        if c == "\r":
            i += 1
            if i < n and texto[i] == "\n": i += 1
            agregar_token("NL", "\\n", linea, 1)
            linea += 1; columna = 1
            continue
        if c == "\n":
            agregar_token("NL", "\\n", linea, 1)
            i += 1; linea += 1; columna = 1
            continue
        if c in " \t\v\f":
            i += 1; columna += 1
            continue
        if i + 1 < n and texto[i:i+2] == "//":
            i += 2
            while i < n and texto[i] not in "\r\n": i += 1
            continue
        if i + 1 < n and texto[i:i+2] == "/*":
            i += 2; columna += 2
            while i < n - 1 and texto[i:i+2] != "*/":
                if texto[i] == "\n":
                    agregar_token("NL", "\\n", linea, 1)
                    linea += 1; columna = 1; i += 1
                elif texto[i] == "\r":
                    i += 1
                    if i < n and texto[i] == "\n": i += 1
                    agregar_token("NL", "\\n", linea, 1)
                    linea += 1; columna = 1
                else:
                    i += 1; columna += 1
            if i < n - 1: i += 2; columna += 2
            continue
        if c in ('"', "'"):
            comilla = c; li = linea; co = columna
            i += 1; columna += 1; contenido = ""
            while i < n and texto[i] not in "\r\n" and texto[i] != comilla:
                if texto[i] == "\\" and i + 1 < n:
                    esc = texto[i+1]
                    mapa = {'n': '\n', 't': '\t', '\\': '\\', '"': '"', "'": "'", 'r': '\r', '0': '\0'}
                    contenido += mapa.get(esc, texto[i] + texto[i+1])
                    i += 2; columna += 2
                else:
                    contenido += texto[i]; i += 1; columna += 1
            if i < n and texto[i] == comilla: i += 1; columna += 1
            agregar_token("STR", contenido, li, co)
            continue
        encontro_multi = False
        for simbolo in simbolos_multi:
            largo = len(simbolo)
            if i + largo <= n and texto[i:i+largo] == simbolo:
                agregar_token(simbolo, simbolo, linea, columna)
                i += largo; columna += largo
                encontro_multi = True; break
        if encontro_multi: continue
        if c in simbolos_uno:
            agregar_token(c, c, linea, columna)
            i += 1; columna += 1
            continue
        if c.isdigit():
            li = linea; co = columna; num = c
            i += 1; columna += 1
            while i < n and (texto[i].isdigit() or texto[i] == "."):
                num += texto[i]; i += 1; columna += 1
            agregar_token("NUM", num, li, co)
            continue
        if c.isalpha() or c in "_$":
            li = linea; co = columna; palabra = c
            i += 1; columna += 1
            while i < n and (texto[i].isalnum() or texto[i] in "_$"):
                palabra += texto[i]; i += 1; columna += 1
            tipo = palabra if palabra in palabras_clave else "ID"
            agregar_token(tipo, palabra, li, co)
            continue
        agregar_token(c, c, linea, columna)
        i += 1; columna += 1
    eof_linea = linea; eof_col = columna
    if eof_col != 1: eof_linea += 1; eof_col = 1
    agregar_token("EOF", "final de archivo", eof_linea, eof_col)

#Helpers para el Parser
def token_actual():
    return tokens[indice]

def token_en(pos):
    if pos < len(tokens): return tokens[pos]
    return tokens[-1]

def avanzar():
    global indice
    if indice < len(tokens) - 1: indice += 1

def es(tipo):
    return token_actual()["tipo"] == tipo

def consumir(tipo_esperado):
    if es(tipo_esperado):
        tok = token_actual(); avanzar(); return tok
    avanzar(); return None

def saltar_nuevas_lineas():
    while es("NL"): avanzar()

def inicio_expresion_tok(tok):
    return tok["tipo"] in INICIOS_EXPRESION

def es_fin_de_sentencia():
    return token_actual()["tipo"] in {";" , "NL", "}", "EOF"}

def consumir_fin_de_sentencia():
    if es(";"):
        avanzar()
        while es("NL"): avanzar()
        return
    if es("NL"):
        while es("NL"): avanzar()
        return
    if es("}") or es("EOF"): return

def es_inicio_arrow(pos):
    if token_en(pos)["tipo"] != "(": return False
    j = pos + 1
    if token_en(j)["tipo"] == ")": return token_en(j+1)["tipo"] == "=>"
    while True:
        if token_en(j)["tipo"] != "ID": return False
        j += 1
        if token_en(j)["tipo"] == ")": return token_en(j+1)["tipo"] == "=>"
        if token_en(j)["tipo"] != ",": return False
        j += 1

# Pre-escanear bloque para definir variables y funciones (este no consume {})
def pre_escanear_bloque(env):
    global indice
    pos_guardada = indice
    if es("{"): avanzar()
    j = indice
    prof = 0
    while j < len(tokens) and tokens[j]["tipo"] != "EOF":
        tipo = tokens[j]["tipo"]
        if tipo == "{": prof += 1; j += 1; continue
        if tipo == "}":
            if prof == 0: break
            prof -= 1; j += 1; continue
        if prof == 0:
            if tipo == "var":
                j += 1
                while j < len(tokens) and tokens[j]["tipo"] == "NL": j += 1
                while j < len(tokens) and tokens[j]["tipo"] not in {";", "EOF"}:
                    if tokens[j]["tipo"] == "ID":
                        nombre = tokens[j]["lexema"]
                        env.definir_var(nombre)
                    elif tokens[j]["tipo"] == "NL":
                        break
                    j += 1
                continue
            elif tipo == "funcion":
                k = j + 1
                while k < len(tokens) and tokens[k]["tipo"] == "NL": k += 1
                if k < len(tokens) and tokens[k]["tipo"] == "ID":
                    nombre_fn = tokens[k]["lexema"]
                    k += 1
                    while k < len(tokens) and tokens[k]["tipo"] != "(": k += 1
                    k += 1
                    params = []
                    while k < len(tokens) and tokens[k]["tipo"] != ")":
                        if tokens[k]["tipo"] == "ID": params.append(tokens[k]["lexema"])
                        k += 1
                    k += 1
                    while k < len(tokens) and tokens[k]["tipo"] == "NL": k += 1
                    if k < len(tokens) and tokens[k]["tipo"] == "{":
                        fn = EsFuncion(nombre_fn, params, k, env)
                        env.definir(nombre_fn, fn)
        j += 1
    indice = pos_guardada

# Ejecutar Bloque cuerpo (este no consume {})
def ejecutar_bloque_cuerpo(env):
    saltar_nuevas_lineas()
    while not es("}") and not es("EOF"):
        ejecutar_sentencia(env)
        saltar_nuevas_lineas()
    if es("}"): avanzar()

# Ejecutar bloque (este si consume {})
def ejecutar_bloque(env):
    consumir("{")
    env_bloque = Entorno(env)
    ejecutar_bloque_cuerpo(env_bloque)

# Sentencias 
def ejecutar_programa(env):
    pre_escanear_bloque(env)
    saltar_nuevas_lineas()
    while not es("EOF"):
        ejecutar_sentencia(env)
        saltar_nuevas_lineas()

def ejecutar_sentencia(env):
    if es("NL"): saltar_nuevas_lineas(); return
    if es("{"): ejecutar_bloque(env); return
    if es(";"): avanzar(); return
    if es("funcion"): ejecutar_funcion_decl(env); return
    if es("intentar"): ejecutar_intentar(env); return
    if es("si"): ejecutar_si(env); return
    if es("mientras"): ejecutar_mientras(env); return
    if es("hacer"): ejecutar_hacer_mientras(env); return
    if es("para"): ejecutar_para(env); return
    if es("elegir"): ejecutar_elegir(env); return
    if es("const") or es("let") or es("var") or es("mut"):
        ejecutar_declaracion(env); return
    if es("retornar"):
        avanzar()
        if es_fin_de_sentencia():
            consumir_fin_de_sentencia()
            raise ExcRetornar(INDEFINIDO)
        val = evaluar_expresion(env)
        consumir_fin_de_sentencia()
        raise ExcRetornar(val)
    if es("continuar"):
        avanzar(); consumir_fin_de_sentencia(); raise ExcContinuar()
    if es("romper"):
        avanzar(); consumir_fin_de_sentencia(); raise ExcRomper()
    if inicio_expresion_tok(token_actual()):
        evaluar_expresion(env)
        consumir_fin_de_sentencia()
        return
    avanzar()

def ejecutar_funcion_decl(env):
    avanzar()
    nombre = token_actual()["lexema"] if es("ID") else ""
    if es("ID"): avanzar()
    consumir("(")
    params = []
    while not es(")") and not es("EOF"):
        if es("ID"): params.append(token_actual()["lexema"]); avanzar()
        elif es(","): avanzar()
        else: avanzar()
    consumir(")")
    saltar_nuevas_lineas()
    tok_cuerpo = indice
    fn = EsFuncion(nombre, params, tok_cuerpo, env)
    env.definir(nombre, fn)
    saltar_bloque()

def saltar_bloque():
    if not es("{"): return
    avanzar(); prof = 1
    while prof > 0 and not es("EOF"):
        if es("{"): prof += 1
        elif es("}"): prof -= 1
        avanzar()

def ejecutar_si(env):
    avanzar()
    consumir("(")
    cond = evaluar_expresion(env)
    consumir(")")
    saltar_nuevas_lineas()
    if es_verdadero(cond):
        ejecutar_bloque(env)
        saltar_nuevas_lineas()
        if es("sino"):
            avanzar(); saltar_nuevas_lineas()
            saltar_bloque_o_si()
    else:
        saltar_bloque()
        saltar_nuevas_lineas()
        if es("sino"):
            avanzar(); saltar_nuevas_lineas()
            if es("si"):
                ejecutar_si(env)
            else:
                ejecutar_bloque(env)

def saltar_bloque_o_si():
    if es("si"): saltar_si_completo()
    else: saltar_bloque()

def saltar_si_completo():
    avanzar()
    consumir("(")
    prof = 1
    while prof > 0 and not es("EOF"):
        if es("("): prof += 1
        elif es(")"): prof -= 1
        avanzar()
    saltar_nuevas_lineas()
    saltar_bloque()
    saltar_nuevas_lineas()
    if es("sino"):
        avanzar(); saltar_nuevas_lineas()
        saltar_bloque_o_si()

def ejecutar_mientras(env):
    global indice
    avanzar()
    pos_cond = indice
    while True:
        indice = pos_cond
        consumir("(")
        cond = evaluar_expresion(env)
        consumir(")")
        if not es_verdadero(cond):
            saltar_nuevas_lineas(); saltar_bloque(); break
        saltar_nuevas_lineas()
        pos_bloque = indice
        try:
            ejecutar_bloque(env)
        except ExcRomper:
            break
        except ExcContinuar:
            continue

def ejecutar_hacer_mientras(env):
    global indice
    avanzar()
    saltar_nuevas_lineas()
    pos_bloque = indice
    while True:
        indice = pos_bloque
        try:
            ejecutar_bloque(env)
        except ExcRomper:
            saltar_nuevas_lineas()
            consumir("mientras"); consumir("(")
            evaluar_expresion(env)
            consumir(")"); consumir_fin_de_sentencia()
            break
        except ExcContinuar:
            pass
        saltar_nuevas_lineas()
        consumir("mientras"); consumir("(")
        cond = evaluar_expresion(env)
        consumir(")"); consumir_fin_de_sentencia()
        if not es_verdadero(cond): break
        indice = pos_bloque

def ejecutar_para(env):
    global indice
    avanzar()
    consumir("(")
    env_para = Entorno(env)

    # inicializacion
    if not es(";"):
        if es("const") or es("let") or es("var") or es("mut"):
            ejecutar_declaracion(env_para)
        else:
            evaluar_expresion(env_para)
            consumir(";")
    else:
        avanzar()

    pos_cond = indice

    while True:
        indice = pos_cond

        cond = True
        if not es(";"):
            cond = es_verdadero(evaluar_expresion(env_para))
        consumir(";")

        if not cond:
            # saltar actualizacion y bloque
            while not es(")") and not es("EOF"): avanzar()
            consumir(")")
            saltar_nuevas_lineas(); saltar_bloque()
            break

        # guardar posicion actualizacion
        pos_act = indice
        while not es(")") and not es("EOF"): avanzar()
        consumir(")")
        saltar_nuevas_lineas()
        pos_bloque = indice

        try:
            ejecutar_bloque(env_para)
        except ExcRomper:
            break
        except ExcContinuar:
            pass

        # ejecutar actualizacion
        indice = pos_act
        if not es(")"):
            evaluar_expresion(env_para)

def ejecutar_elegir(env):
    avanzar()
    consumir("(")
    val_elegir = evaluar_expresion(env)
    consumir(")")
    consumir("{")
    saltar_nuevas_lineas()
    encontro_caso = False
    ejecutando = False
    while not es("}") and not es("EOF"):
        if es("caso"):
            avanzar()
            val_caso = evaluar_expresion(env)
            saltar_nuevas_lineas()
            consumir(":")
            saltar_nuevas_lineas()
            if not ejecutando and igual_estricto(val_elegir, val_caso):
                ejecutando = True
            if ejecutando:
                try:
                    while not es("caso") and not es("porDefecto") and not es("}") and not es("EOF"):
                        ejecutar_sentencia(env)
                        saltar_nuevas_lineas()
                except ExcRomper:
                    while not es("}") and not es("EOF"): avanzar()
                    break
            else:
                while not es("caso") and not es("porDefecto") and not es("}") and not es("EOF"):
                    avanzar()
        elif es("porDefecto"):
            avanzar(); saltar_nuevas_lineas(); consumir(":"); saltar_nuevas_lineas()
            if not ejecutando:
                ejecutando = True
            if ejecutando:
                try:
                    while not es("}") and not es("EOF"):
                        ejecutar_sentencia(env)
                        saltar_nuevas_lineas()
                except ExcRomper:
                    break
            break
        else:
            avanzar()
    if es("}"): avanzar()

def ejecutar_declaracion(env):
    tipo_decl = token_actual()["tipo"]
    avanzar()
    while True:
        nombre = token_actual()["lexema"] if es("ID") else ""
        if es("ID"): avanzar()
        if es("="):
            avanzar()
            val = evaluar_expresion(env)
        else:
            val = INDEFINIDO
        if tipo_decl == "var":
            env.definir_var(nombre)
            env.asignar(nombre, val)
        else:
            env.definir(nombre, val)
        if es(","):
            avanzar()
        else:
            break
    consumir_fin_de_sentencia()

def ejecutar_intentar(env):
    avanzar(); saltar_nuevas_lineas()
    exc_capturada = None
    try:
        ejecutar_bloque(env)
    except (ExcRetornar, ExcRomper, ExcContinuar):
        raise
    except Exception as e:
        exc_capturada = e

    saltar_nuevas_lineas()
    tiene_capturar = es("capturar")
    if tiene_capturar:
        avanzar(); saltar_nuevas_lineas()
        nombre_err = None
        if es("("):
            avanzar()
            if es("ID"): nombre_err = token_actual()["lexema"]; avanzar()
            consumir(")")
        saltar_nuevas_lineas()
        if exc_capturada is not None:
            env_cap = Entorno(env)
            if nombre_err:
                msg = str(exc_capturada)
                env_cap.definir(nombre_err, msg)
            ejecutar_bloque(env_cap)
        else:
            saltar_bloque()

    saltar_nuevas_lineas()
    if es("finalmente"):
        avanzar(); saltar_nuevas_lineas()
        ejecutar_bloque(env)

#Evaluar expresiones
_ultimo_lvalue = None

def evaluar_expresion(env):
    if not inicio_expresion_tok(token_actual()):
        avanzar(); return INDEFINIDO
    return evaluar_asignacion(env)

def evaluar_asignacion(env):
    global _ultimo_lvalue
    val = evaluar_ternaria(env)
    lv = _ultimo_lvalue

    if token_actual()["tipo"] in OPERADORES_ASIGNACION:
        op = token_actual()["tipo"]; avanzar()
        val_der = evaluar_asignacion(env)
        if lv is not None:
            nuevo = aplicar_op_asig(op, val if op != "=" else None, val_der)
            if op != "=":
                nuevo = aplicar_op_asig(op, lv.obtener(), val_der)
            lv.asignar(nuevo)
            _ultimo_lvalue = lv
            return nuevo
        return val_der
    return val

def evaluar_ternaria(env):
    val = evaluar_or(env)
    if es("?"):
        avanzar()
        si_verdadero = evaluar_expresion(env)
        consumir(":")
        si_falso = evaluar_ternaria(env)
        return si_verdadero if es_verdadero(val) else si_falso
    return val

def evaluar_or(env):
    val = evaluar_and(env)
    while token_actual()["tipo"] in OPERADORES_OR:
        avanzar()
        if es_verdadero(val):
            prof = 0
            while True:
                t = token_actual()["tipo"]
                if t in {"EOF", ";", "NL"}: break
                if t in {")", "]", "}"} and prof == 0: break
                if t in {"?", ":"} and prof == 0: break
                if t == "||" and prof == 0: break
                if t in {"(", "[", "{"}: prof += 1
                elif t in {")", "]", "}"}: prof -= 1
                avanzar()
        else:
            val = evaluar_and(env)
    return val

def evaluar_and(env):
    val = evaluar_igualdad(env)
    while token_actual()["tipo"] in OPERADORES_AND:
        avanzar()
        if not es_verdadero(val):
            prof = 0
            while True:
                t = token_actual()["tipo"]
                if t in {"EOF", ";", "NL"}: break
                if t in {")", "]", "}"} and prof == 0: break
                if t in {"?", ":"} and prof == 0: break
                if t in {"||", "&&"} and prof == 0: break
                if t in {"(", "[", "{"}: prof += 1
                elif t in {")", "]", "}"}: prof -= 1
                avanzar()
        else:
            val = evaluar_igualdad(env)
    return val

def evaluar_igualdad(env):
    val = evaluar_relacional(env)
    while token_actual()["tipo"] in OPERADORES_IGUALDAD:
        op = token_actual()["tipo"]; avanzar(); saltar_nuevas_lineas()
        der = evaluar_relacional(env)
        if op == "==": val = igual_laxo(val, der)
        elif op == "!=": val = not igual_laxo(val, der)
        elif op == "===": val = igual_estricto(val, der)
        elif op == "!==": val = not igual_estricto(val, der)
    return val

def evaluar_relacional(env):
    val = evaluar_aditiva(env)
    while token_actual()["tipo"] in OPERADORES_RELACIONALES:
        op = token_actual()["tipo"]; avanzar(); saltar_nuevas_lineas()
        der = evaluar_aditiva(env)
        if op == "<": val = a_numero(val) < a_numero(der)
        elif op == ">": val = a_numero(val) > a_numero(der)
        elif op == "<=": val = a_numero(val) <= a_numero(der)
        elif op == ">=": val = a_numero(val) >= a_numero(der)
    return val

def evaluar_aditiva(env):
    val = evaluar_multiplicativa(env)
    while token_actual()["tipo"] in OPERADORES_ADITIVOS:
        op = token_actual()["tipo"]; avanzar(); saltar_nuevas_lineas()
        der = evaluar_multiplicativa(env)
        if op == "+":
            if isinstance(val, str) or isinstance(der, str):
                val = a_cadena(val) + a_cadena(der)
            else:
                val = a_numero(val) + a_numero(der)
        else:
            val = a_numero(val) - a_numero(der)
    return val

def evaluar_multiplicativa(env):
    val = evaluar_unaria(env)
    while token_actual()["tipo"] in OPERADORES_MULTIPLICATIVOS:
        op = token_actual()["tipo"]; avanzar(); saltar_nuevas_lineas()
        der = evaluar_unaria(env)
        a, b = a_numero(val), a_numero(der)
        if op == "*": val = a * b
        elif op == "/": val = float('nan') if b == 0 and a == 0 else (float('inf') * (1 if a >= 0 else -1) if b == 0 else a / b)
        elif op == "%": val = float('nan') if b == 0 else math.fmod(a, b)
        elif op == "**": val = a ** b
    return val

def evaluar_unaria(env):
    global _ultimo_lvalue
    tipo = token_actual()["tipo"]
    if tipo == "!":
        avanzar(); val = evaluar_unaria(env)
        _ultimo_lvalue = None
        return not es_verdadero(val)
    if tipo == "-":
        avanzar(); val = evaluar_unaria(env)
        _ultimo_lvalue = None
        return -a_numero(val)
    if tipo == "+":
        avanzar(); val = evaluar_unaria(env)
        _ultimo_lvalue = None
        return a_numero(val)
    if tipo == "++":
        avanzar(); val = evaluar_unaria(env)
        lv = _ultimo_lvalue
        nuevo = a_numero(val) + 1
        if lv: lv.asignar(nuevo)
        _ultimo_lvalue = None
        return nuevo
    if tipo == "--":
        avanzar(); val = evaluar_unaria(env)
        lv = _ultimo_lvalue
        nuevo = a_numero(val) - 1
        if lv: lv.asignar(nuevo)
        _ultimo_lvalue = None
        return nuevo
    if tipo == "crear" or tipo == "nuevo":
        avanzar(); saltar_nuevas_lineas()
        nombre_clase = token_actual()["lexema"]
        avanzar()
        args = []
        if es("("):
            args = evaluar_args(env)
        return construir_objeto(nombre_clase, args, env)
    return evaluar_postfija(env)

def construir_objeto(nombre, args, env):
    if nombre == "Arreglo":
        if len(args) == 1 and isinstance(args[0], (int, float)):
            return [INDEFINIDO] * int(args[0])
        return list(args)
    if nombre == "Cadena":
        return a_cadena(args[0]) if args else ""
    fn = env.obtener(nombre)
    if isinstance(fn, EsFuncion):
        obj = {}
        llamar_funcion(fn, args, ambiente_obj=obj)
        return obj
    return {}

def evaluar_postfija(env):
    global _ultimo_lvalue
    val, lv = evaluar_primaria_lv(env)
    _ultimo_lvalue = lv

    while True:
        if es("."):
            avanzar()
            prop = token_actual()["lexema"] if token_actual()["tipo"] in {"ID"} | palabras_clave else ""
            avanzar()
            nuevo_lv = LValue("prop", obj=val, clave=prop)
            val = obtener_propiedad(val, prop)
            _ultimo_lvalue = nuevo_lv
            continue

        if es("["):
            avanzar()
            idx = evaluar_expresion(env)
            consumir("]")
            nuevo_lv = LValue("idx", obj=val, clave=idx)
            val = obtener_indice(val, idx)
            _ultimo_lvalue = nuevo_lv
            continue

        if es("("):
            # Llamada a funcion
            obj_llamada = None
            if _ultimo_lvalue and _ultimo_lvalue.tipo == "prop":
                obj_llamada = _ultimo_lvalue.obj
            args = evaluar_args(env)
            if isinstance(val, EsFuncionNativa):
                val = val.fn(args)
            elif isinstance(val, EsFuncion):
                val = llamar_funcion(val, args, ambiente_obj=obj_llamada)
            else:
                val = INDEFINIDO
            _ultimo_lvalue = None
            continue

        if token_actual()["tipo"] in OPERADORES_POSTFIJOS:
            op = token_actual()["tipo"]; avanzar()
            old_val = a_numero(val)
            if _ultimo_lvalue:
                _ultimo_lvalue.asignar(old_val + (1 if op == "++" else -1))
            _ultimo_lvalue = None
            val = old_val
            continue

        break

    return val

def evaluar_args(env):
    consumir("(")
    args = []
    while not es(")") and not es("EOF"):
        args.append(evaluar_expresion(env))
        if es(","): avanzar()
    consumir(")")
    return args

def evaluar_primaria_lv(env):
    global _ultimo_lvalue

    if es("("):
        if es_inicio_arrow(indice):
            return evaluar_arrow(env), None
        avanzar()
        val = evaluar_expresion(env)
        while es(",") and not es("EOF"):
            avanzar(); val = evaluar_expresion(env)
        consumir(")")
        return val, None

    if es("["):
        avanzar()
        elementos = []
        while not es("]") and not es("EOF"):
            if es(","): elementos.append(INDEFINIDO)
            else: elementos.append(evaluar_expresion(env))
            if es(","): avanzar()
        consumir("]")
        return elementos, None

    if es("{"):
        return evaluar_objeto_literal(env), None

    if es("verdadero"): avanzar(); return True, None
    if es("falso"): avanzar(); return False, None
    if es("nulo"): avanzar(); return NULO, None
    if es("indefinido"): avanzar(); return INDEFINIDO, None
    if es("Infinito"): avanzar(); return float('inf'), None
    if es("NuN"): avanzar(); return float('nan'), None

    if es("NUM"):
        lexema = token_actual()["lexema"]; avanzar()
        val = float(lexema) if "." in lexema else int(lexema)
        return val, None

    if es("STR"):
        val = token_actual()["lexema"]; avanzar(); return val, None

    if es("consola"):
        avanzar()
        lv = LValue("var", nombre="consola", env=env)
        return env.obtener("consola"), lv

    if es("ambiente"):
        nombre = "ambiente"; avanzar()
        lv = LValue("var", env=env, nombre=nombre)
        return env.obtener(nombre), lv

    if es("Numero"):
        avanzar()
        return env.obtener("Numero"), None

    if es("Mate"):
        avanzar()
        return env.obtener("Mate"), None

    if es("Cadena"):
        avanzar()
        return env.obtener("Cadena"), None

    if es("Arreglo"):
        avanzar()
        return env.obtener("Arreglo"), None

    if es("Booleano"):
        avanzar()
        return env.obtener("Booleano"), None

    if es("Matriz"):
        avanzar()
        return env.obtener("Matriz"), None

    if es("ID"):
        nombre = token_actual()["lexema"]; avanzar()
        lv = LValue("var", env=env, nombre=nombre)
        return env.obtener(nombre), lv

    if es("funcion"):
        return evaluar_funcion_expr(env), None

    avanzar()
    return INDEFINIDO, None

def evaluar_arrow(env):
    consumir("(")
    params = []
    while not es(")") and not es("EOF"):
        if es("ID"): params.append(token_actual()["lexema"]); avanzar()
        elif es(","): avanzar()
        else: avanzar()
    consumir(")")
    consumir("=>")
    saltar_nuevas_lineas()
    if es("{"):
        tok_inicio = indice
        fn = EsFuncion(None, params, tok_inicio, env, expr_flecha=False)
        saltar_bloque()
    else:
        tok_inicio = indice
        fn = EsFuncion(None, params, tok_inicio, env, expr_flecha=True)
        # saltar expresion (posiblemente multilinea)
        prof = 0
        ultimo_op = True  # Aca es como si se viniera del operador
        while True:
            t = token_actual()["tipo"]
            if t == "EOF": break
            if t == "NL" and prof == 0:
                if not ultimo_op: break
                avanzar(); continue
            if t == ";" and prof == 0: break
            if t in {")", "]", "}"} and prof == 0: break
            if t in {"(", "[", "{"}: prof += 1
            elif t in {")", "]", "}"}: prof -= 1
            ultimo_op = t in OPERADORES_ADITIVOS | OPERADORES_MULTIPLICATIVOS | OPERADORES_IGUALDAD | OPERADORES_RELACIONALES | {"&&", "||", "?", ":", ",", "=", "=>"}
            avanzar()
    return fn

def evaluar_funcion_expr(env):
    avanzar()
    nombre = ""
    if es("ID"): nombre = token_actual()["lexema"]; avanzar()
    consumir("(")
    params = []
    while not es(")") and not es("EOF"):
        if es("ID"): params.append(token_actual()["lexema"]); avanzar()
        elif es(","): avanzar()
        else: avanzar()
    consumir(")")
    saltar_nuevas_lineas()
    tok_inicio = indice
    fn = EsFuncion(nombre, params, tok_inicio, env)
    saltar_bloque()
    return fn

def evaluar_objeto_literal(env):
    consumir("{")
    saltar_nuevas_lineas()
    obj = {}
    while not es("}") and not es("EOF"):
        clave = ""
        if es("ID") or es("STR") or es("NUM"):
            clave = token_actual()["lexema"]; avanzar()
        else:
            avanzar()

        saltar_nuevas_lineas()

        if es("("):
            consumir("(")
            params = []
            while not es(")") and not es("EOF"):
                if es("ID"): params.append(token_actual()["lexema"]); avanzar()
                elif es(","): avanzar()
                else: avanzar()
            consumir(")")
            saltar_nuevas_lineas()
            tok_inicio = indice
            fn = EsFuncion(clave, params, tok_inicio, env)
            obj[clave] = fn
            saltar_bloque()
        else:
            consumir(":")
            val = evaluar_expresion(env)
            obj[clave] = val

        saltar_nuevas_lineas()
        if es(","): avanzar(); saltar_nuevas_lineas()
    consumir("}")
    return obj

# Built-ins
def hacer_numero():
    def es_finito(args):
        if not args: return False
        v = args[0]
        if isinstance(v, bool) or isinstance(v, (_Nulo, _Indefinido)): return False
        if not isinstance(v, (int, float)): return False
        f = float(v)
        return f == f and abs(f) != float('inf')

    def es_entero(args):
        if not args: return False
        v = args[0]
        if isinstance(v, bool): return False
        if not isinstance(v, (int, float)): return False
        f = float(v)
        return f == f and abs(f) != float('inf') and f == int(f)

    def es_entero_seguro(args):
        if not args: return False
        v = args[0]
        if isinstance(v, bool): return False
        if not isinstance(v, (int, float)): return False
        f = float(v)
        return f == f and abs(f) != float('inf') and f == int(f) and abs(f) <= 2**53 - 1

    def interpretar_decimal(args):
        if not args: return float('nan')
        return a_numero(args[0])

    def interpretar_entero(args):
        if not args: return float('nan')
        v = a_numero(args[0])
        if v != v or abs(v) == float('inf'): return float('nan')
        return float(int(v))

    return {
        "__tipo__": "Numero",
        "esFinito": EsFuncionNativa(es_finito),
        "esEntero": EsFuncionNativa(es_entero),
        "esEnteroSeguro": EsFuncionNativa(es_entero_seguro),
        "interpretarDecimal": EsFuncionNativa(interpretar_decimal),
        "interpretarEntero": EsFuncionNativa(interpretar_entero),
        "POSITIVE_INFINITY": float('inf'),
        "NEGATIVE_INFINITY": float('-inf'),
        "MAX_SAFE_INTEGER": float(2**53 - 1),
        "MIN_SAFE_INTEGER": float(-(2**53 - 1)),
        "NaN": float('nan'),
    }

def hacer_mate():
    return {
        "__tipo__": "Mate",
        "PI": math.pi,
        "E": math.e,
        "LN2": math.log(2),
        "LN10": math.log(10),
        "LOG2E": math.log2(math.e),
        "LOG10E": math.log10(math.e),
        "SQRT2": math.sqrt(2),
        "SQRT1_2": math.sqrt(0.5),
        "abs":    EsFuncionNativa(lambda a: abs(a_numero(a[0])) if a else float('nan')),
        "ceil":   EsFuncionNativa(lambda a: float(math.ceil(a_numero(a[0]))) if a else float('nan')),
        "floor":  EsFuncionNativa(lambda a: float(math.floor(a_numero(a[0]))) if a else float('nan')),
        "round":  EsFuncionNativa(lambda a: float(round(a_numero(a[0]))) if a else float('nan')),
        "sqrt":   EsFuncionNativa(lambda a: math.sqrt(max(0, a_numero(a[0]))) if a else float('nan')),
        "pow":    EsFuncionNativa(lambda a: a_numero(a[0]) ** a_numero(a[1]) if len(a) >= 2 else float('nan')),
        "max":    EsFuncionNativa(lambda a: max(a_numero(x) for x in a) if a else float('-inf')),
        "min":    EsFuncionNativa(lambda a: min(a_numero(x) for x in a) if a else float('inf')),
        "log":    EsFuncionNativa(lambda a: math.log(a_numero(a[0])) if a and a_numero(a[0]) > 0 else float('nan')),
        "log2":   EsFuncionNativa(lambda a: math.log2(a_numero(a[0])) if a and a_numero(a[0]) > 0 else float('nan')),
        "log10":  EsFuncionNativa(lambda a: math.log10(a_numero(a[0])) if a and a_numero(a[0]) > 0 else float('nan')),
        "sin":    EsFuncionNativa(lambda a: math.sin(a_numero(a[0])) if a else float('nan')),
        "cos":    EsFuncionNativa(lambda a: math.cos(a_numero(a[0])) if a else float('nan')),
        "tan":    EsFuncionNativa(lambda a: math.tan(a_numero(a[0])) if a else float('nan')),
        "trunc":  EsFuncionNativa(lambda a: float(math.trunc(a_numero(a[0]))) if a else float('nan')),
        "sign":   EsFuncionNativa(lambda a: (1.0 if a_numero(a[0]) > 0 else (-1.0 if a_numero(a[0]) < 0 else 0.0)) if a else float('nan')),
        "hypot":  EsFuncionNativa(lambda a: math.hypot(*[a_numero(x) for x in a])),
        "random": EsFuncionNativa(lambda a: __import__('random').random()),
        "exp":    EsFuncionNativa(lambda a: math.exp(a_numero(a[0])) if a else float('nan')),
        "cbrt":   EsFuncionNativa(lambda a: (abs(a_numero(a[0])) ** (1/3)) * (1 if a_numero(a[0]) >= 0 else -1) if a else float('nan')),
        "atan2":  EsFuncionNativa(lambda a: math.atan2(a_numero(a[0]), a_numero(a[1])) if len(a) >= 2 else float('nan')),
        "atan":   EsFuncionNativa(lambda a: math.atan(a_numero(a[0])) if a else float('nan')),
        "asin":   EsFuncionNativa(lambda a: math.asin(a_numero(a[0])) if a else float('nan')),
        "acos":   EsFuncionNativa(lambda a: math.acos(a_numero(a[0])) if a else float('nan')),
    }

def hacer_cadena():
    def desde_codigo(args):
        if not args: return ""
        return "".join(chr(int(a_numero(x))) for x in args)
    return {
        "__tipo__": "Cadena",
        "desdeCodigoDeCaracter": EsFuncionNativa(desde_codigo),
        "desdeCodigo": EsFuncionNativa(desde_codigo),
    }

def hacer_consola():
    def escribir(args):
        print(" ".join(a_cadena(a) for a in args))
        return INDEFINIDO
    def limpiar(args):
        return INDEFINIDO
    def error_fn(args):
        print(" ".join(a_cadena(a) for a in args))
        return INDEFINIDO
    def info(args):
        print(" ".join(a_cadena(a) for a in args))
        return INDEFINIDO
    def advertencia(args):
        print(" ".join(a_cadena(a) for a in args))
        return INDEFINIDO
    def afirmar(args):
        if args and not es_verdadero(args[0]):
            msg = "Assertion failed"
            if len(args) > 1:
                msg += ": " + " ".join(a_cadena(a) for a in args[1:])
            print(msg)
        return INDEFINIDO
    def tabla(args):
        if args: print(a_cadena(args[0]))
        return INDEFINIDO
    return {
        "escribir":    EsFuncionNativa(escribir),
        "error":       EsFuncionNativa(error_fn),
        "limpiar":     EsFuncionNativa(limpiar),
        "info":        EsFuncionNativa(info),
        "advertencia": EsFuncionNativa(advertencia),
        "afirmar":     EsFuncionNativa(afirmar),
        "tabla":       EsFuncionNativa(tabla),
        "listar":      EsFuncionNativa(escribir),
        "depurar":     EsFuncionNativa(escribir),
        "tiempo":      EsFuncionNativa(lambda a: INDEFINIDO),
        "finalizarTiempo": EsFuncionNativa(lambda a: INDEFINIDO),
        "agrupar":     EsFuncionNativa(lambda a: INDEFINIDO),
        "finalizarAgrupacion": EsFuncionNativa(lambda a: INDEFINIDO),
        "contar":      EsFuncionNativa(lambda a: INDEFINIDO),
        "reiniciarContador": EsFuncionNativa(lambda a: INDEFINIDO),
    }

#Entorno global
def crear_entorno_global():
    env = Entorno(es_funcion=True)
    env.definir("Numero", hacer_numero())
    env.definir("Mate", hacer_mate())
    env.definir("Cadena", hacer_cadena())
    env.definir("consola", hacer_consola())
    env.definir("Arreglo", {"__tipo__": "Arreglo"})
    env.definir("Booleano", {"__tipo__": "Booleano"})
    env.definir("Matriz", {"__tipo__": "Matriz"})
    env.definir("Infinito", float('inf'))
    env.definir("NuN", float('nan'))
    env.definir("verdadero", True)
    env.definir("falso", False)
    env.definir("nulo", NULO)
    env.definir("indefinido", INDEFINIDO)

    def parse_int(args):
        if not args: return float('nan')
        base = int(a_numero(args[1])) if len(args) > 1 else 10
        s = a_cadena(args[0]).strip()
        try: return float(int(s, base))
        except: return float('nan')

    def parse_float(args):
        if not args: return float('nan')
        return a_numero(args[0])

    def is_nan(args):
        if not args: return True
        v = a_numero(args[0])
        return v != v

    def is_finite(args):
        if not args: return False
        v = a_numero(args[0])
        return v == v and abs(v) != float('inf')

    env.definir("interpretarEntero", EsFuncionNativa(parse_int))
    env.definir("interpretarDecimal", EsFuncionNativa(parse_float))
    env.definir("esNuN", EsFuncionNativa(is_nan))
    env.definir("esFinito", EsFuncionNativa(is_finite))
    return env

# Ejecucion
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
codigo = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8').read()

tokenizar(codigo)
env_global = crear_entorno_global()
ejecutar_programa(env_global)
