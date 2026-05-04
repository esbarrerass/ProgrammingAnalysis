import sys
import re

ESCAPE = re.compile(r'\\u(?:\{([0-9A-Fa-f]{1,6})\}|([0-9A-Fa-f]{4}))')

KEYWORDS = {"capturar","caso","con","continuar","crear","elegir","esperar","hacer","mientras","para","retornar","sino","si","constructor",
              "eliminar","extiende","finalmente","instanciaDe","intentar","lanzar","longitud","romper","simbolo","subcad","tipoDe","vacio",
              "ambiente","super","de","en","clase","const","var","mut","porDefecto","funcion","falso","nulo","verdadero","indefinido",
              "Infinito","NuN","consola","Fecha","Numero","Mate","Matriz","Arreglo","Booleano","Cadena","Funcion","afirmar","limpiar","listar",
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

THREE_OPER = {"**=":"power_assign","===":"strict_equal","!==":"strict_neq","...":"spread"}

TWO_OPER = {"&&":"and","||":"or","++":"increment","--":"decrement","%=":"mod_assign","/=":"div_assign","*=":"times_assign","-=":"minus_assign",
            "+=":"plus_assign","**":"power","==":"equal","!=":"neq","<=":"leq",">=":"geq","=>":"arrow","??":"nulish"}

ONE_OPER = {".": "period",",": "comma",";": "semicolon",":": "colon", "{": "opening_key", "}": "closing_key", "[": "opening_bra", 
            "]": "closing_bra", "(": "opening_par", ")": "closing_par", "+": "plus", "-": "minus","*": "times","/": "div","%": "mod",
            ">": "greater","<": "less","=": "assign","!": "not","?": "ternary"}

NUMS = "0123456789"

def is_id_start(c):
    return c == '$' or c == '_' or (len(c) == 1 and c.isidentifier())

def is_id_continue(c):
    return c == '$' or c == '_' or c in ('\u200C', '\u200D') or (len(c) == 1 and c.isdigit()) or (len(c) == 1 and c.isidentifier())
                
def lexer_error(fila, columna):
  return f'>>> Error lexico (linea: {fila}, posicion: {columna})'

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

      #Comments

      if long_comment: #-> /* */ form
        if character == "*" and next_character == "/":
          long_comment = False
          skip = 1
        continue

      #Strings

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
        comment_token_start = (fila, columna)
        long_comment = True
        skip = 1

      elif character == "/" and next_character == "/": # -> // form
        break

      elif character in ('"', "'"):
        in_string = True
        string_delim = character
        string_start_col = columna
        partial_string = ""

      #Spaces -> FLUSH

      elif character == " ":
        add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
        partial_alpha_token = ""
        if partial_num:         
          tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
          partial_num = ""
          has_dot = False
  

      #Unicode Escape Sequences -> BOTH \u{X} and \uXXXX

      elif character == "\\": 
        escape_secuence = ESCAPE.match(line, columna - 1)
        if escape_secuence: 
          converted_char = escape_to_char(escape_secuence)
          if converted_char is None: 
            return tokens + [lexer_error(fila, columna)]
          checker = is_id_start if len(partial_alpha_token) == 0 else is_id_continue
          if converted_char and checker(converted_char):
            if len(partial_alpha_token) == 0: alpha_token_start = columna
            partial_alpha_token += converted_char   
            skip = len(escape_secuence.group(0)) - 1
          else:
            return tokens + [lexer_error(fila, columna)]
        else:
          return tokens + [lexer_error(fila, columna)] 

      #Identifiers and Keywords

      elif (is_id_start if len(partial_alpha_token) == 0 else is_id_continue)(character):
        if partial_num:                                      
          tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
          partial_num = ""
          has_dot = False
        if len(partial_alpha_token) == 0: alpha_token_start = columna
        partial_alpha_token += character

      #Numbers

      elif character in NUMS and len(partial_alpha_token) == 0:
        if not partial_num: num_start = columna
        partial_num += character

      #Special Case -> Period can be part of a number or a separate token

      elif character == ".":
        if len(partial_alpha_token) > 0:
          add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
          partial_alpha_token = ""

        if next_character == "." and next_next_character == ".":
          if partial_num:                    # ← flush número ANTES del spread
            tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
            partial_num = ""
            has_dot = False
          tokens.append(f'<tkn_spread,{fila},{columna}>')
          skip = 2

        elif partial_num and not has_dot and next_character in NUMS:
          partial_num += character           # 34.45 → sigue el número
          has_dot = True

        elif not partial_num and next_character in NUMS:
          # Solo comienza número con punto si el anterior NO es spread
          last_token = tokens[-1] if tokens else ""
          if not last_token.startswith("<tkn_spread"):
            num_start = columna                # .045 → número que comienza con punto
            partial_num = "."
            has_dot = True
          else:
            # Es período después de spread
            tokens.append(f'<tkn_period,{fila},{columna}>')

        else:
          if partial_num:
            tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
            partial_num = ""
            has_dot = False
          tokens.append(f'<tkn_period,{fila},{columna}>')

      #ReGex

      elif character == "/" and next_character not in ("*", "/"):
        if len(partial_alpha_token) > 0:
          add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
          partial_alpha_token = ""
        last = tokens[-1] if tokens else ""
        is_operand = (
          next_character == "=" or
          any(last.startswith(p) for p in (
            "<id,", "<tkn_num",
            "<tkn_closing_par", "<tkn_closing_bra",
            "<tkn_increment", "<tkn_decrement",
            "<tkn_plus", "<tkn_minus", "<tkn_times",
            "<tkn_mod", "<tkn_power", "<tkn_div"
          ))
        )
        if is_operand:
          add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
          partial_alpha_token = ""
          three = character + next_character + next_next_character
          if three in THREE_OPER:
            tokens.append(f'<tkn_{THREE_OPER[three]},{fila},{columna}>')
            skip = 2
          else:
            two = character + next_character
            if two in TWO_OPER:
              tokens.append(f'<tkn_{TWO_OPER[two]},{fila},{columna}>')
              skip = 1
            else:
              tokens.append(f'<tkn_{ONE_OPER["/"]},{fila},{columna}>')
        else:
          reg_start = columna
          partial_reg = ""
          i = columna       
          while i < len(line):
            c = line[i]
            if c == "\\" and i + 1 < len(line):
              partial_reg += c + line[i + 1]
              i += 2
              continue
            if c == "/":
              skip = i - (columna - 1)
              tokens.append(f'<tkn_reg,{partial_reg},{fila},{reg_start}>')
              break
            partial_reg += c
            i += 1
          else:
            return tokens + [lexer_error(fila, reg_start)]

      #Symbols and Operators

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
          else:
            return tokens + [lexer_error(fila, columna)]
        
      else:
        return tokens + [lexer_error(fila, columna)]
    
    if in_string:
      return tokens + [lexer_error(fila, string_start_col)]
    
    if partial_num:
      tokens.append(f'<tkn_num,{partial_num},{fila},{num_start}>')
      partial_num = ""
      has_dot = False

    add_token(tokens, partial_alpha_token, KEYWORDS, fila, alpha_token_start)
  
  if long_comment: 
    return tokens + [lexer_error(comment_token_start[0], comment_token_start[1])]

  return tokens

entry_lines = []
texto = sys.stdin.read()
entry_lines = [x for x in texto.splitlines()]

output = lexer(entry_lines)
for token in output:
  print(token)