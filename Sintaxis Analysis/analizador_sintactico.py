import sys
import re

ESCAPE = re.compile(r'\\u(?:\{([0-9A-Fa-f]{1,6})\}|([0-9A-Fa-f]{4}))')

KEYWORDS = {"capturar","caso","con","continuar","crear","desde","elegir","esperar","exportar","hacer","importar","mientras","para","retornar","sino","si","constructor",
              "eliminar","extiende","finalmente","instanciaDe","intentar","lanzar","longitud","romper","simbolo","subcad","tipoDe","vacio",
              "producir","ambiente","ambienteGlobal","super","de","en","asincrono","clase","const","var","mut","porDefecto","funcion","falso","nulo","verdadero","indefinido",
              "Infinito","NuN","consola","depurador","establecerTemporizador","establecerIntervalo","Fecha","Numero","Mate","Matriz","Arreglo","Booleano","Cadena","Funcion","Promesa","afirmar","limpiar","listar",
              "error","agrupar","info","escribir","tabla","enPosicion","caracterEn","codigoDeCaracterEn","puntoDeCodigoEn","concatenar",
              "terminaCon","desdeCodigoDeCaracter","desdePuntoDeCodigo","incluye","indiceDe","ultimoIndiceDe","compararLocalizada","coincidir",
              "coincidirTodo","normalizar","rellenarAlFinal","rellenarAlComienzo","crudo","repetir","reemplazar","reemplazarTodo","buscarRegex",
              "recortar","dividir","comienzaCon","subcadena","aMinusculasLocalizada","aMayusculasLocalizada","aMinusculas","aMayusculas",
              "aCadena","recortarEspacios","recortarEspaciosAlFinal","recortarEspaciosAlComienzo","valorDe","esNuN","esFinito","esEntero",
              "esEnteroSeguro","interpretarDecimal","interpretarEntero","aExponencial","fijarDecimales","aCadenaLocalizada","aPrecision",
              "absoluto","arcocoseno","arcocosenoHiperbolico","arcoseno","arcosenoHiperbolico","arcotangente","arcotangente2",
              "arcotangenteHiperbolica","raizCubica","redondearHaciaArriba","cerosALaIzquierdaEn32Bits","coseno","cosenoHiperbolico",
              "exponencial","exponencialMenos1","redondearHaciaAbajo","redondearAComaFlotante","hipotenusa","multiplicacionEntera","logaritmo",
              "logaritmoBase10","logaritmoDe1Mas","logaritmoBase2","maximo","minimo","potencia","aleatorio","redondear","signo","seno",
              "senoHiperbolico","raizCuadrada","tangente","tangenteHiperbolica","truncar","posicion","copiarDentro","entradas","cada","llenar",
              "filtrar","buscar","buscarIndice","buscarUltimo","buscarUltimoIndice","plano","planoMapear","paraCada","grupo","grupoAMapear",
              "juntar","claves","mapear","sacar","agregar","reducir","reducirDerecha","reverso","sacarPrimero","rodaja","algun","ordenar",
              "empalmar","agregarInicio","valores"}

SYMBOLS = ["&","|",".",",",";",":","{","}","[","]","(",")","+","-","*","/","%","=",">","<","!","?"]

THREE_OPER = {"**=":"power_assign","===":"strict_equal","!==":"strict_neq"}

TWO_OPER = {"&&":"and","||":"or","++":"increment","--":"decrement","%=":"mod_assign","/=":"div_assign","*=":"times_assign","-=":"minus_assign",
            "+=":"plus_assign","**":"power","==":"equal","!=":"neq","<=":"leq",">=":"geq","=>":"arrow"}

ONE_OPER = {".": "period",",": "comma",";": "semicolon",":": "colon", "{": "opening_key", "}": "closing_key", "[": "opening_bra", 
            "]": "closing_bra", "(": "opening_par", ")": "closing_par", "+": "plus", "-": "minus","*": "times","/": "div","%": "mod",
            ">": "greater","<": "less","=": "assign","!": "not","?": "ternary"}

NUMS = "0123456789"

def is_id_start(c):
    return c == '$' or c == '_' or (len(c) == 1 and c.isidentifier())

def is_id_continue(c):
    return c == '$' or c == '_' or c in ('\u200C', '\u200D') or (len(c) == 1 and c.isdigit()) or (len(c) == 1 and c.isidentifier())

def is_surrogate_pair(secuence):
    return 0xD800 <= secuence <= 0xDFFF

def escape_secuence_type(secuence):
    if secuence.group(1) is not None: escape = int(secuence.group(1), 16)
    else: escape = int(secuence.group(2), 16)
    return escape

def escape_to_char(secuence):
    escape = escape_secuence_type(secuence)
    if is_surrogate_pair(escape): return None
    return chr(escape) if escape <= 0x10FFFF else None

def add_token(tokens, partial_alpha_token, keywords, fila, alpha_token_start):
    if partial_alpha_token in keywords:
        tokens.append(f'<{partial_alpha_token},{fila},{alpha_token_start}>') 
    elif len(partial_alpha_token) > 0: 
        tokens.append(f'<id,{partial_alpha_token},{fila},{alpha_token_start}>')

def lexer(entry_lines):
    tokens = []
    long_comment = False

    for fila in range(1, len(entry_lines) + 1):
        line = entry_lines[fila - 1]
        partial_alpha_token = ""
        partial_num = ""
        in_string = False 
        string_delim = ""      
        partial_string = ""      
        string_start_col = 0  
        num_start = 0
        has_dot = False
        skip = 0
        alpha_token_start = 0

        for columna in range(1, len(line) + 1):
            if skip > 0:    
                skip -= 1
                continue

            character = line[columna - 1]
            next_character = line[columna] if columna < len(line) else ""
            next_next_character = line[columna + 1] if columna < len(line) - 1 else ""

            # Comments
            if long_comment:
                if character == "*" and next_character == "/":
                    long_comment = False
                    skip = 1
                continue

            # Strings
            elif in_string:
                if character == "\\" and next_character == string_delim:
                    partial_string += character + next_character
                    skip = 1
                elif character == string_delim:
                    in_string = False
                    tokens.append(f'<tkn_str,{partial_string},{fila},{string_start_col}>')
                    partial_string = ""
                else:
                    partial_string += character

            elif character == "/" and next_character == "*": 
                long_comment = True
                skip = 1

            elif character == "/" and next_character == "/":
                break

            elif character in ('"', "'", "`"):
                add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
                partial_alpha_token = ""
                if partial_num:
                    tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
                    partial_num = ""
                    has_dot = False
                in_string = True
                string_delim = character
                string_start_col = columna
                partial_string = ""

            # Spaces -> FLUSH
            elif character.isspace():
                add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
                partial_alpha_token = ""
                if partial_num:         
                    tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
                    partial_num = ""
                    has_dot = False

            # Unicode Escape Sequences
            elif character == "\\": 
                escape_secuence = ESCAPE.match(line, columna - 1)
                if escape_secuence: 
                    converted_char = escape_to_char(escape_secuence)
                    if converted_char is None: 
                        return tokens
                    checker = is_id_start if len(partial_alpha_token) == 0 else is_id_continue
                    if converted_char and checker(converted_char):
                        if len(partial_alpha_token) == 0: alpha_token_start = columna
                        partial_alpha_token += converted_char   
                        skip = len(escape_secuence.group(0)) - 1
                    else:
                        return tokens
                else:
                    return tokens

            # Identifiers and Keywords
            elif (is_id_start if len(partial_alpha_token) == 0 else is_id_continue)(character):
                if partial_num:                                      
                    tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
                    partial_num = ""
                    has_dot = False
                if len(partial_alpha_token) == 0: alpha_token_start = columna
                partial_alpha_token += character

            # Numbers
            elif character in NUMS and len(partial_alpha_token) == 0:
                if not partial_num: num_start = columna
                partial_num += character

            # Period - puede ser parte del número o un token separado, tambien hace FLUSH
            elif character == ".":
                if len(partial_alpha_token) > 0:
                    add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
                    partial_alpha_token = ""

                elif partial_num and not has_dot and next_character and next_character in NUMS:
                    partial_num += character
                    has_dot = True

                elif not partial_num and next_character and next_character in NUMS:
                    last_token = tokens[-1] if tokens else ""
                    if not last_token.startswith("<tkn_spread"):
                        num_start = columna
                        partial_num = "."
                        has_dot = True
                    else:
                        tokens.append(f'<tkn_period,{fila},{columna}>')

                else:
                    if partial_num:
                        tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
                        partial_num = ""
                        has_dot = False
                    tokens.append(f'<tkn_period,{fila},{columna}>')

            # Symbols and Operators
            elif character in SYMBOLS:
                if len(partial_alpha_token) > 0:
                    add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
                    partial_alpha_token = ""
                if partial_num:
                    tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
                    partial_num = ""
                    has_dot = False
                three = character + next_character + next_next_character
                if three in THREE_OPER:
                    tokens.append(f'<tkn_{THREE_OPER[three]},{fila},{columna}>')
                    skip = 2
                else:
                    two = character + next_character
                    if two in TWO_OPER:
                        tokens.append(f'<tkn_{TWO_OPER[two]},{fila},{columna}>')
                        skip = 1
                    elif character in ONE_OPER:
                        tokens.append(f'<tkn_{ONE_OPER[character]},{fila},{columna}>')
        
        if in_string:
            return tokens
        
        if partial_num:
            tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
            partial_num = ""
            has_dot = False

        add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
    
    if long_comment: 
        return tokens

    return tokens

class Token:
    def __init__(self, tipo, lexema, fila, columna):
        self.tipo = tipo
        self.lexema = lexema
        self.fila = fila
        self.columna = columna

class Parser:
    EXPR_START = [
        'Arreglo', 'Booleano', 'Cadena', 'Infinito', 'Mate', 'Matriz', 'NuN',
        'Numero', 'tkn_str', 'consola', 'falso', 'id', 'indefinido', 'nulo',
        'tkn_minus', 'tkn_not', 'tkn_opening_bra', 'tkn_opening_key',
        'tkn_opening_par', 'tkn_plus', 'tkn_num', 'verdadero'
    ]
    CONDITION_START = [
        'Arreglo', 'Booleano', 'Cadena', 'Infinito', 'Mate', 'Matriz', 'NuN',
        'Numero', 'tkn_str', 'falso', 'id', 'indefinido', 'nulo',
        'tkn_minus', 'tkn_not', 'tkn_opening_bra', 'tkn_opening_key',
        'tkn_opening_par', 'tkn_plus', 'tkn_num', 'verdadero'
    ]
    STATEMENT_START = [
        'Arreglo', 'Booleano', 'Cadena', 'Infinito', 'Mate', 'Matriz', 'NuN',
        'Numero', 'tkn_str', 'consola', 'const', 'continuar', 'elegir',
        'falso', 'funcion', 'hacer', 'id', 'indefinido', 'intentar',
        'mientras', 'mut', 'nulo', 'para', 'retornar', 'romper', 'si',
        'tkn_minus', 'tkn_not', 'tkn_opening_bra', 'tkn_opening_key',
        'tkn_opening_par', 'tkn_plus', 'tkn_num', 'var', 'verdadero'
    ]
    DECL_CONTINUATION = [
        'Arreglo', 'Booleano', 'Cadena', 'Infinito', 'Mate', 'Matriz', 'NuN',
        'Numero', 'tkn_str', 'consola', 'const', 'continuar', 'elegir',
        'falso', 'EOF', 'funcion', 'hacer', 'id', 'indefinido', 'intentar',
        'mientras', 'mut', 'nulo', 'para', 'retornar', 'romper', 'si',
        'tkn_assign', 'tkn_comma', 'tkn_minus', 'tkn_not', 'tkn_opening_bra',
        'tkn_opening_key', 'tkn_opening_par', 'tkn_plus', 'tkn_semicolon',
        'tkn_num', 'var', 'verdadero'
    ]
    CONSOLE_METHODS = ['afirmar', 'agrupar', 'error', 'escribir', 'info', 'limpiar', 'tabla']
    BUILTIN_VALUES = {'Arreglo', 'Booleano', 'Cadena', 'Fecha', 'Funcion', 'Infinito',
                      'Mate', 'Matriz', 'NuN', 'Numero', 'Promesa', 'ambiente',
                      'ambienteGlobal', 'consola', 'establecerIntervalo',
                      'establecerTemporizador', 'importar', 'super'}
    ASSIGN_OPS = {'tkn_assign', 'tkn_plus_assign', 'tkn_minus_assign',
                  'tkn_times_assign', 'tkn_div_assign', 'tkn_mod_assign',
                  'tkn_power_assign'}
    EXPR_FOLLOW_OPERATORS = [
        'tkn_and', 'tkn_closing_par', 'tkn_comma', 'tkn_div', 'tkn_equal',
        'tkn_geq', 'tkn_greater', 'tkn_leq', 'tkn_less', 'tkn_minus',
        'tkn_mod', 'tkn_neq', 'tkn_or', 'tkn_plus', 'tkn_power',
        'tkn_strict_equal', 'tkn_strict_neq', 'tkn_ternary', 'tkn_times'
    ]

    def __init__(self, tokens_raw, eof_line=1):
        self.tokens_raw = tokens_raw
        self.eof_line = eof_line
        self.tokens = self._parse_tokens()
        self.pos = 0
        self.error = None
        self.last_atom = None
    
    def _parse_tokens(self):
        tokens = []
        
        for token_str in self.tokens_raw:
            if not token_str.strip():
                continue
            
            token_str = token_str.strip('<>')
            parts = token_str.split(',')
            
            try:
                if len(parts) == 3:
                    tipo = parts[0]
                    fila = int(parts[1])
                    columna = int(parts[2])
                    lexema = self._get_lexema_display(tipo)
                    tokens.append(Token(tipo, lexema, fila, columna))
                
                elif len(parts) >= 4:
                    tipo = parts[0]
                    valor = ','.join(parts[1:-2])
                    fila = int(parts[-2])
                    columna = int(parts[-1])
                    tokens.append(Token(tipo, valor, fila, columna))
            except:
                pass
        
        tokens.append(Token('EOF', 'final de archivo', self.eof_line, 1))
        return tokens
    
    @staticmethod
    def _get_lexema_display(token_type):
        mapping = {
            'tkn_period': '.', 'tkn_comma': ',', 'tkn_semicolon': ';', 'tkn_colon': ':',
            'tkn_opening_key': '{', 'tkn_closing_key': '}', 'tkn_opening_bra': '[',
            'tkn_closing_bra': ']', 'tkn_opening_par': '(', 'tkn_closing_par': ')',
            'tkn_plus': '+', 'tkn_minus': '-', 'tkn_times': '*', 'tkn_div': '/',
            'tkn_mod': '%', 'tkn_assign': '=', 'tkn_greater': '>', 'tkn_less': '<',
            'tkn_not': '!', 'tkn_ternary': '?', 'tkn_and': '&&', 'tkn_or': '||',
            'tkn_increment': '++', 'tkn_decrement': '--', 'tkn_power': '**',
            'tkn_equal': '==', 'tkn_neq': '!=', 'tkn_leq': '<=', 'tkn_geq': '>=',
            'tkn_strict_equal': '===', 'tkn_strict_neq': '!==', 'tkn_arrow': '=>',
            'tkn_spread': '...', 'tkn_nulish': '??',
            'tkn_plus_assign': '+=', 'tkn_minus_assign': '-=', 'tkn_times_assign': '*=',
            'tkn_div_assign': '/=', 'tkn_mod_assign': '%=', 'tkn_power_assign': '**=',
            'tkn_num': 'valor_numérico', 'tkn_str': 'cadena_de_caracteres',
        }
        return mapping.get(token_type, token_type)
    
    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]
    
    def peek(self, offset=1):
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def match(self, *tipos):
        return self.current().tipo in tipos
    
    def consume(self, tipo):
        if self.match(tipo):
            self.advance()
            return True
        return False
    
    def _error(self, esperados):
        if self.error is not None:
            return
        
        token = self.current()
        
        esperados_list = []
        vistos = set()
        for e in esperados:
            if e == 'EOF':
                valor = 'final de archivo'
            elif e.startswith('tkn_'):
                valor = self._get_lexema_display(e)
            else:
                valor = e
            if valor not in vistos:
                esperados_list.append(valor)
                vistos.add(valor)
        esperados_str = ', '.join(f'"{e}"' for e in esperados_list)
        
        if token.tipo == 'EOF':
            self.error = f'<{token.fila}:{token.columna}> Error sintactico: se encontro: "final de archivo"; se esperaba: {esperados_str}.'
        else:
            self.error = f'<{token.fila}:{token.columna}> Error sintactico: se encontro: "{token.lexema}"; se esperaba: {esperados_str}.'
    
    # ===== REGLAS GRAMATICALES =====
    
    def programa(self):
        """Programa → Sentencia*"""
        while not self.match('EOF'):
            antes = self.pos
            if not self.sentencia():
                return False
            if self.pos == antes:
                self._error(self.STATEMENT_START)
                return False
        return True
    
    def sentencia(self):
        """Sentencia → declaracion | bloque | control | funcion | salto | expresion"""
        while self.consume('tkn_semicolon'):
            pass

        if self.match('EOF', 'tkn_closing_key'):
            return self.error is None

        if self.match('var', 'const', 'mut'):
            resultado = self.declaracion_variable()
        elif self.match('tkn_opening_key'):
            resultado = self.bloque()
        elif self.match('si', 'mientras', 'para', 'hacer'):
            resultado = self.control_flujo()
        elif self.match('funcion') or (self.match('asincrono') and self.peek().tipo == 'funcion'):
            resultado = self.funcion_declaracion()
        elif self.match('elegir'):
            resultado = self.sentencia_elegir()
        elif self.match('importar'):
            resultado = self.sentencia_importar()
        elif self.match('exportar'):
            resultado = self.sentencia_exportar()
        elif self.match('con'):
            resultado = self.sentencia_con()
        elif self.match('intentar'):
            resultado = self.sentencia_try()
        elif self.match('retornar', 'lanzar', 'producir'):
            resultado = self.sentencia_retorno()
        elif self.match('romper', 'continuar', 'depurador'):
            self.advance()
            resultado = True
        elif self.match('clase'):
            resultado = self.clase_declaracion()
        else:
            resultado = self.sentencia_expresion()

        while self.consume('tkn_semicolon'):
            pass

        return resultado and self.error is None

    def sentencia_expresion(self):
        if self.expresion():
            if self.current().tipo in self.ASSIGN_OPS:
                self.advance()
                if not self.expresion():
                    return False
            resultado = self.error is None
        else:
            return False
        return resultado
    
    def declaracion_variable(self):
        """DeclaracionVariable → (var|const|mut) id (= Expresion)?"""
        if not self.consume('var') and not self.consume('const') and not self.consume('mut'):
            self._error(['var', 'const', 'mut'])
            return False
        
        if not self.patron(['id']):
            return False
        
        while True:
            if self.match('tkn_assign'):
                self.advance()
                if not self.expresion():
                    return False
            elif self.match('tkn_comma'):
                self.advance()
                if not self.match('id'):
                    self._error(['id'])
                    return False
                self.advance()
                continue
            elif self.match('tkn_plus_assign', 'tkn_minus_assign', 'tkn_times_assign',
                            'tkn_div_assign', 'tkn_mod_assign', 'tkn_power_assign'):
                self._error(self.DECL_CONTINUATION)
                return False
            break

        return self.error is None

    def parametros(self):
        if self.match('tkn_closing_par'):
            return True
        if not self.patron(['id']):
            self._error(['id'])
            return False
        while self.match('tkn_comma'):
            self.advance()
            if not self.patron(['id']):
                return False
        return self.error is None

    def patron(self, esperados):
        if self.match('id'):
            self.advance()
            return True
        if self.match('tkn_opening_bra'):
            self.advance()
            if not self.match('tkn_closing_bra'):
                if not self.patron(['id']):
                    return False
                while self.match('tkn_comma'):
                    self.advance()
                    if self.match('tkn_closing_bra'):
                        break
                    if not self.patron(['id']):
                        return False
            if not self.consume('tkn_closing_bra'):
                self._error(['tkn_closing_bra'])
                return False
            return True
        if self.match('tkn_opening_key'):
            self.advance()
            if not self.match('tkn_closing_key'):
                if not self.propiedad_patron():
                    return False
                while self.match('tkn_comma'):
                    self.advance()
                    if self.match('tkn_closing_key'):
                        break
                    if not self.propiedad_patron():
                        return False
            if not self.consume('tkn_closing_key'):
                self._error(['tkn_closing_key'])
                return False
            return True
        self._error(esperados)
        return False

    def propiedad_patron(self):
        if not self.nombre_propiedad() and not self.match('tkn_str', 'tkn_num'):
            self._error(['id'])
            return False
        self.advance()
        if self.match('tkn_colon'):
            self.advance()
            return self.patron(['id'])
        return True
    
    def expresion(self):
        """Expresion → ExprTernaria"""
        if self.es_funcion_flecha_simple():
            return self.funcion_flecha_simple()
        if self.match('asincrono') and (self.peek().tipo in ('id', 'tkn_opening_par', 'funcion')):
            if self.peek().tipo == 'funcion':
                return self.funcion_expresion()
            return self.funcion_flecha_simple()
        return self.expr_ternaria()

    def condicion(self):
        if self.match('tkn_closing_par', 'EOF'):
            self._error(self.CONDITION_START)
            return False
        return self.expresion()
    
    def expr_ternaria(self):
        """ExprTernaria → ExprLogica (? ExprLogica : ExprLogica)?"""
        if not self.expr_logica():
            return False
        
        if self.match('tkn_ternary'):
            self.advance()
            if not self.expresion():
                return False
            if not self.consume('tkn_colon'):
                self._error(['tkn_colon'])
                return False
            if not self.expresion():
                return False
        
        return self.error is None
    
    def expr_logica(self):
        """ExprLogica → ExprComparacion ((&&||) ExprComparacion)*"""
        if not self.expr_comparacion():
            return False
        
        while self.match('tkn_and', 'tkn_or'):
            self.advance()
            if not self.expr_comparacion():
                return False
        
        return self.error is None
    
    def expr_comparacion(self):
        """ExprComparacion → ExprAritmetica ((==|!=|===|!==|<|>|<=|>=) ExprAritmetica)*"""
        if not self.expr_aritmetica():
            return False
        
        while self.match('tkn_equal', 'tkn_neq', 'tkn_strict_equal', 'tkn_strict_neq',
                         'tkn_less', 'tkn_greater', 'tkn_leq', 'tkn_geq',
                         'instanciaDe'):
            self.advance()
            if not self.expr_aritmetica():
                return False
        
        return self.error is None
    
    def expr_aritmetica(self):
        """ExprAritmetica → ExprMultiplicativa ((+|-) ExprMultiplicativa)*"""
        if not self.expr_multiplicativa():
            return False
        
        while self.match('tkn_plus', 'tkn_minus'):
            self.advance()
            if not self.expr_multiplicativa():
                return False
        
        return self.error is None
    
    def expr_multiplicativa(self):
        """ExprMultiplicativa → ExprUnaria ((*|/|%) ExprUnaria)*"""
        if not self.expr_unaria():
            return False
        
        while self.match('tkn_times', 'tkn_div', 'tkn_mod', 'tkn_power'):
            self.advance()
            if not self.expr_unaria():
                return False
        
        return self.error is None
    
    def expr_unaria(self):
        """ExprUnaria → (+|-|!|++|--)?ExprPostfija"""
        if self.match('tkn_plus', 'tkn_minus', 'tkn_not', 'tkn_increment',
                      'tkn_decrement', 'tipoDe', 'vacio', 'eliminar', 'esperar'):
            self.advance()
        
        return self.expr_postfija()
    
    def expr_postfija(self):
        """ExprPostfija → Primaria (. id | [ Expresion ])*"""
        if not self.primaria():
            return False
        atom = self.last_atom
        
        while self.match('tkn_period', 'tkn_opening_bra', 'tkn_opening_par',
                         'tkn_increment', 'tkn_decrement') or (
                             self.match('tkn_str') and atom not in ('tkn_num', 'tkn_str')
                         ):
            if self.match('tkn_period'):
                self.advance()
                if atom == 'consola':
                    if not self.match(*self.CONSOLE_METHODS):
                        self._error(self.CONSOLE_METHODS)
                        return False
                elif not self.nombre_propiedad():
                    self._error(['id'])
                    return False
                atom = None
                self.advance()
            
            elif self.match('tkn_opening_bra'):
                self.advance()
                if not self.expresion():
                    return False
                if not self.consume('tkn_closing_bra'):
                    self._error([']'])
                    return False
            
            elif self.match('tkn_opening_par'):
                self.advance()
                if not self.match('tkn_closing_par'):
                    if not self.argumentos():
                        return False
                if not self.consume('tkn_closing_par'):
                    self._error([')'])
                    return False

            elif self.match('tkn_increment', 'tkn_decrement'):
                self.advance()

            elif self.match('tkn_str'):
                self.advance()
        
        if atom == 'consola' and self.match(*self.CONSOLE_METHODS):
            self._error(['tkn_period'])
            return False

        return self.error is None
    
    def primaria(self):
        """Primaria → id|numero|cadena|verdadero|falso|nulo|(Expresion)|[..]"""
        self.last_atom = None

        if self.match('id', 'tkn_num', 'tkn_str'):
            self.last_atom = self.current().tipo
            self.advance()
            return self.error is None
        
        if self.match('verdadero', 'falso', 'nulo', 'indefinido', 'Infinito', 'NuN'):
            self.last_atom = self.current().tipo
            self.advance()
            return self.error is None

        if self.match(*self.BUILTIN_VALUES):
            self.last_atom = self.current().tipo
            self.advance()
            return self.error is None

        if self.match('funcion', 'asincrono'):
            return self.funcion_expresion()
        
        if self.match('crear'):
            self.advance()
            if not self.match('id', 'Arreglo', 'Booleano', 'Cadena', 'Fecha', 'Funcion',
                              'Matriz', 'Numero'):
                self._error(['Arreglo', 'Cadena', 'Matriz', 'id'])
                return False
            self.advance()
            if self.match('tkn_opening_par'):
                self.advance()
                if not self.match('tkn_closing_par'):
                    if not self.argumentos():
                        return False
                if not self.consume('tkn_closing_par'):
                    self._error([')'])
                    return False
            return self.error is None
        
        if self.match('tkn_opening_par'):
            if self.es_funcion_flecha():
                return self.funcion_flecha()
            self.advance()
            if not self.expresion():
                return False
            if not self.consume('tkn_closing_par'):
                self._error([')'])
                return False
            return self.error is None
        
        if self.match('tkn_opening_bra'):
            self.advance()
            if not self.match('tkn_closing_bra'):
                if not self.lista_expresiones('tkn_closing_bra'):
                    return False
            if not self.consume('tkn_closing_bra'):
                self._error([']'])
                return False
            return self.error is None
        
        if self.match('tkn_opening_key'):
            return self.objeto_literal()

        self._error(self.EXPR_START)
        return False
    
    def argumentos(self):
        """Argumentos → Expresion (, Expresion)*"""
        return self.lista_expresiones('tkn_closing_par')

    def lista_expresiones(self, terminador):
        if self.match(terminador):
            return True
        if not self.expresion():
            return False
        
        while self.match('tkn_comma'):
            self.advance()
            if self.match(terminador):
                return True
            if not self.expresion():
                return False

        if not self.match(terminador):
            self._error(self.EXPR_FOLLOW_OPERATORS if terminador == 'tkn_closing_par'
                        else ['tkn_comma', terminador])
            return False
        
        return self.error is None
    
    def control_flujo(self):
        """ControlFlujo → si | mientras | para | repetir"""
        if self.match('si'):
            return self.sentencia_si()
        if self.match('mientras'):
            return self.sentencia_mientras()
        if self.match('para'):
            return self.sentencia_para()
        if self.match('hacer'):
            return self.sentencia_hacer()
        self._error(['si', 'mientras', 'para', 'hacer'])
        return False
    
    def funcion_declaracion(self):
        """FuncionDeclaracion → funcion id (Parametros) Bloque"""
        if self.match('asincrono'):
            self.advance()
            if not self.consume('funcion'):
                self._error(['funcion'])
                return False
        else:
            if not self.consume('funcion'):
                self._error(['funcion'])
                return False
        if not self.match('id'):
            self._error(['id'])
            return False
        self.advance()
        if not self.consume('tkn_opening_par'):
            self._error(['tkn_opening_par'])
            return False
        if not self.parametros():
            return False
        if not self.consume('tkn_closing_par'):
            self._error(['tkn_closing_par'])
            return False
        if not self.bloque():
            return False
        return self.error is None

    def funcion_expresion(self):
        if self.match('asincrono'):
            self.advance()
        if not self.consume('funcion'):
            self._error(['funcion'])
            return False
        if self.match('id'):
            self.advance()
        if not self.consume('tkn_opening_par'):
            self._error(['tkn_opening_par'])
            return False
        if not self.parametros():
            return False
        if not self.consume('tkn_closing_par'):
            self._error(['tkn_closing_par'])
            return False
        return self.bloque()

    def bloque(self):
        if not self.consume('tkn_opening_key'):
            self._error(['tkn_opening_key'])
            return False
        while not self.match('tkn_closing_key', 'EOF'):
            if not self.sentencia():
                return False
        if not self.consume('tkn_closing_key'):
            self._error(['tkn_closing_key'])
            return False
        return self.error is None

    def sentencia_si(self):
        self.advance()
        if not self.consume('tkn_opening_par'):
            self._error(['tkn_opening_par'])
            return False
        if not self.condicion():
            return False
        if not self.consume('tkn_closing_par'):
            self._error(['tkn_closing_par'])
            return False
        if not self.bloque_o_sentencia():
            return False
        if self.match('sino'):
            self.advance()
            if self.match('si'):
                return self.sentencia_si()
            if not self.match('tkn_opening_key'):
                self._error(['si', 'tkn_opening_key'])
                return False
            if not self.bloque():
                return False
        return self.error is None

    def sentencia_mientras(self):
        self.advance()
        if not self.consume('tkn_opening_par'):
            self._error(['tkn_opening_par'])
            return False
        if not self.condicion():
            return False
        if not self.consume('tkn_closing_par'):
            self._error(['tkn_closing_par'])
            return False
        return self.bloque_o_sentencia()

    def sentencia_hacer(self):
        self.advance()
        if not self.bloque_o_sentencia():
            return False
        if not self.consume('mientras'):
            self._error(['mientras'])
            return False
        if not self.consume('tkn_opening_par'):
            self._error(['tkn_opening_par'])
            return False
        if not self.condicion():
            return False
        if not self.consume('tkn_closing_par'):
            self._error(['tkn_closing_par'])
            return False
        return self.error is None

    def sentencia_para(self):
        self.advance()
        if not self.consume('tkn_opening_par'):
            self._error(['tkn_opening_par'])
            return False
        if not self.match('tkn_semicolon'):
            if self.match('var', 'const', 'mut'):
                if not self.declaracion_variable():
                    return False
            elif not self.sentencia_expresion():
                return False
        if self.match('de', 'en'):
            self.advance()
            if not self.expresion():
                return False
            if not self.consume('tkn_closing_par'):
                self._error(['tkn_closing_par'])
                return False
            return self.bloque_o_sentencia()
        if not self.consume('tkn_semicolon'):
            self._error(['tkn_semicolon'])
            return False
        if not self.match('tkn_semicolon'):
            if not self.expresion():
                return False
        if not self.consume('tkn_semicolon'):
            self._error(['tkn_semicolon'])
            return False
        if not self.match('tkn_closing_par'):
            if not self.sentencia_expresion():
                return False
        if not self.consume('tkn_closing_par'):
            self._error(['tkn_closing_par'])
            return False
        return self.bloque_o_sentencia()

    def sentencia_elegir(self):
        self.advance()
        if not self.consume('tkn_opening_par'):
            self._error(['tkn_opening_par'])
            return False
        if not self.expresion():
            return False
        if not self.consume('tkn_closing_par'):
            self._error(['tkn_closing_par'])
            return False
        if not self.consume('tkn_opening_key'):
            self._error(['tkn_opening_key'])
            return False

        while not self.match('tkn_closing_key', 'EOF'):
            if self.match('caso'):
                self.advance()
                if not self.expresion():
                    return False
                if not self.consume('tkn_colon'):
                    self._error(['tkn_colon'])
                    return False
            elif self.match('porDefecto'):
                self.advance()
                if not self.consume('tkn_colon'):
                    self._error(['tkn_colon'])
                    return False
            else:
                self._error(['caso', 'porDefecto', 'tkn_closing_key'])
                return False

            while not self.match('caso', 'porDefecto', 'tkn_closing_key', 'EOF'):
                if not self.sentencia():
                    return False

        if not self.consume('tkn_closing_key'):
            self._error(['tkn_closing_key'])
            return False
        return self.error is None

    def sentencia_importar(self):
        self.advance()
        if self.match('tkn_str'):
            self.advance()
            return True

        if self.match('id'):
            self.advance()
            if self.match('tkn_comma'):
                self.advance()
                if not self.importar_nombres():
                    return False
        elif self.match('tkn_opening_key'):
            if not self.importar_nombres():
                return False
        elif self.match('tkn_times'):
            self.advance()
            if not self.consume('id'):
                self._error(['id'])
                return False
        else:
            self._error(['id', 'tkn_opening_key', 'tkn_str'])
            return False

        if not self.consume('desde'):
            self._error(['desde'])
            return False
        if not self.match('tkn_str'):
            self._error(['tkn_str'])
            return False
        self.advance()
        return True

    def importar_nombres(self):
        if not self.consume('tkn_opening_key'):
            self._error(['tkn_opening_key'])
            return False
        if not self.match('tkn_closing_key'):
            if not self.match('id'):
                self._error(['id'])
                return False
            self.advance()
            while self.match('tkn_comma'):
                self.advance()
                if self.match('tkn_closing_key'):
                    break
                if not self.match('id'):
                    self._error(['id'])
                    return False
                self.advance()
        if not self.consume('tkn_closing_key'):
            self._error(['tkn_closing_key'])
            return False
        return True

    def sentencia_exportar(self):
        self.advance()
        if self.match('porDefecto'):
            self.advance()
            if self.match('funcion', 'asincrono'):
                if self.match('asincrono') and self.peek().tipo == 'funcion':
                    return self.funcion_declaracion()
                if self.match('funcion') and self.peek().tipo == 'id':
                    return self.funcion_declaracion()
            if self.match('clase'):
                return self.clase_declaracion()
            return self.expresion()

        if self.match('var', 'const', 'mut'):
            return self.declaracion_variable()
        if self.match('funcion', 'asincrono'):
            return self.funcion_declaracion()
        if self.match('clase'):
            return self.clase_declaracion()
        if self.match('tkn_opening_key'):
            return self.importar_nombres()

        self._error(['clase', 'const', 'funcion', 'mut', 'porDefecto', 'tkn_opening_key', 'var'])
        return False

    def sentencia_con(self):
        self.advance()
        if not self.consume('tkn_opening_par'):
            self._error(['tkn_opening_par'])
            return False
        if not self.expresion():
            return False
        if not self.consume('tkn_closing_par'):
            self._error(['tkn_closing_par'])
            return False
        return self.bloque_o_sentencia()

    def bloque_o_sentencia(self):
        if self.match('tkn_opening_key'):
            return self.bloque()
        return self.sentencia()

    def sentencia_try(self):
        self.advance()
        if not self.bloque():
            return False
        if not self.consume('capturar'):
            self._error(['capturar'])
            return False
        if self.match('tkn_opening_par'):
            self.advance()
            if not self.match('id'):
                self._error(['id'])
                return False
            self.advance()
            if not self.consume('tkn_closing_par'):
                self._error(['tkn_closing_par'])
                return False
        if not self.bloque():
            return False
        if self.match('finalmente'):
            self.advance()
            if not self.bloque():
                return False
        return self.error is None

    def sentencia_retorno(self):
        self.advance()
        if self.match('tkn_semicolon', 'tkn_closing_key', 'EOF'):
            return True
        return self.expresion()

    def nombre_propiedad(self):
        return self.match('id') or self.current().tipo in KEYWORDS

    def objeto_literal(self):
        self.advance()
        if self.match('tkn_closing_key'):
            self.advance()
            return True
        while not self.match('tkn_closing_key', 'EOF'):
            if not self.propiedad_objeto():
                return False
            if self.match('tkn_comma'):
                self.advance()
                if self.match('tkn_closing_key'):
                    break
            else:
                break
        if not self.consume('tkn_closing_key'):
            self._error(['tkn_closing_key'])
            return False
        return self.error is None

    def propiedad_objeto(self):
        if self.match('tkn_str', 'tkn_num') or self.nombre_propiedad():
            self.advance()
        else:
            self._error(['id', 'tkn_str', 'tkn_num'])
            return False

        if self.match('tkn_opening_par'):
            self.advance()
            if not self.parametros():
                return False
            if not self.consume('tkn_closing_par'):
                self._error(['tkn_closing_par'])
                return False
            return self.bloque()

        if self.match('tkn_colon'):
            self.advance()
            return self.expresion()

        return self.error is None

    def es_funcion_flecha(self):
        if not self.match('tkn_opening_par'):
            return False
        profundidad = 0
        i = self.pos
        while i < len(self.tokens):
            tok = self.tokens[i]
            if tok.tipo == 'tkn_opening_par':
                profundidad += 1
            elif tok.tipo == 'tkn_closing_par':
                profundidad -= 1
                if profundidad == 0:
                    return self.peek(i - self.pos + 1).tipo == 'tkn_arrow'
            i += 1
        return False

    def es_funcion_flecha_simple(self):
        if self.match('id') and self.peek().tipo == 'tkn_arrow':
            return True
        return self.match('asincrono') and (
            (self.peek().tipo == 'id' and self.peek(2).tipo == 'tkn_arrow') or
            self.peek().tipo == 'tkn_opening_par'
        )

    def funcion_flecha(self):
        self.advance()
        if not self.parametros():
            return False
        if not self.consume('tkn_closing_par'):
            self._error(['tkn_closing_par'])
            return False
        if not self.consume('tkn_arrow'):
            self._error(['tkn_arrow'])
            return False
        if self.match('tkn_opening_key'):
            return self.bloque()
        return self.expresion()

    def funcion_flecha_simple(self):
        if self.match('asincrono'):
            self.advance()
        if self.match('id'):
            self.advance()
        elif self.match('tkn_opening_par'):
            self.advance()
            if not self.parametros():
                return False
            if not self.consume('tkn_closing_par'):
                self._error(['tkn_closing_par'])
                return False
        else:
            self._error(['id', 'tkn_opening_par'])
            return False
        if not self.consume('tkn_arrow'):
            self._error(['tkn_arrow'])
            return False
        if self.match('tkn_opening_key'):
            return self.bloque()
        return self.expresion()

    def clase_declaracion(self):
        self.advance()
        if not self.match('id'):
            self._error(['id'])
            return False
        self.advance()
        if self.match('extiende'):
            self.advance()
            if not self.match('id'):
                self._error(['id'])
                return False
            self.advance()
        if not self.consume('tkn_opening_key'):
            self._error(['tkn_opening_key'])
            return False
        while not self.match('tkn_closing_key', 'EOF'):
            if not self.miembro_clase():
                return False
        if not self.consume('tkn_closing_key'):
            self._error(['tkn_closing_key'])
            return False
        return self.error is None

    def miembro_clase(self):
        if self.match('asincrono'):
            self.advance()
        if self.match('funcion'):
            self.advance()

        if self.match('constructor') or self.nombre_propiedad() or self.match('tkn_str', 'tkn_num'):
            self.advance()
        else:
            self._error(['constructor', 'id'])
            return False

        if self.match('tkn_opening_par'):
            self.advance()
            if not self.parametros():
                return False
            if not self.consume('tkn_closing_par'):
                self._error(['tkn_closing_par'])
                return False
            return self.bloque()

        if self.match('tkn_assign'):
            self.advance()
            if not self.expresion():
                return False
            while self.consume('tkn_semicolon'):
                pass
            return True

        while self.consume('tkn_semicolon'):
            pass
        return True
    
    def parse(self):
        """Inicia el análisis sintáctico"""
        if self.programa():
            return True
        return False


def main():
    texto = sys.stdin.read()
    entry_lines = [x for x in texto.splitlines()]
    
    tokens_output = lexer(entry_lines)
    
    parser = Parser(tokens_output, len(entry_lines) + 1)
    
    if parser.parse():
        print('El analisis sintactico ha finalizado exitosamente.')
    else:
        print(parser.error)

if __name__ == '__main__':
    main()
