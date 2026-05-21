grammar ESJS;

programa : sentencia (';'? sentencia)* ';'? EOF ;

sentencia
    : sentenciaDeclaracionVariable
    | sentenciaFuncion
    | bloque
    | sentenciaControlFlujo
    | sentenciaClase
    | sentenciaIntento
    | sentenciaRetorno
    | sentenciaRota
    | sentenciaExpresion
    ;

// Declaraciones
sentenciaDeclaracionVariable
    : tipoVariable ID ('=' expresion)? (',' ID ('=' expresion)?)*
    ;

tipoVariable : 'var' | 'const' | 'mut' ;

// Expresión como sentencia / asignación
sentenciaExpresion
    : paramFuncionFlecha
    | expresion (operadorAsignacion expresion)?
    ;

paramFuncionFlecha
    : ID '=>' formaFuncion
    | '(' parametros? ')' '=>' formaFuncion
    ;

formaFuncion : bloque | expresion ;

operadorAsignacion
    : '=' | '+=' | '-=' | '*=' | '/=' | '%=' | '**='
    ;

// Funciones
sentenciaFuncion
    : 'funcion' ID '(' parametros? ')' bloque
    ;

funcionAnonima
    : 'funcion' '(' parametros? ')' bloque
    ;

parametros : ID (',' ID)* ;

argumentos : listaExpresiones? ;

// Control de flujo
sentenciaControlFlujo
    : sentenciaSi
    | sentenciaMientras
    | sentenciaHacer
    | sentenciaPara
    | sentenciaElegir
    ;

bloque : '{' (sentencia (';'? sentencia)* ';'?)? '}' ;

sentenciaSi
    : 'si' '(' expresion ')' bloqueOSentencia
      ('sino' bloqueOSentencia)?
    ;

bloqueOSentencia : bloque | sentencia ;

sentenciaMientras
    : 'mientras' '(' expresion ')' bloqueOSentencia
    ;

sentenciaHacer
    : 'hacer' bloqueOSentencia 'mientras' '(' expresion ')'
    ;

sentenciaPara
    : paraClasico
    | paraDeEn
    ;

paraClasico
    : 'para' '(' inicializador ';' expresion? ';' expresion? ')' bloqueOSentencia
    ;

inicializador
    : sentenciaDeclaracionVariable
    | expresion
    |  // epsilon
    ;

paraDeEn
    : 'para' '(' sentenciaDeclaracionVariable ('de' | 'en') expresion ')' bloqueOSentencia
    ;

// Switch / Elegir
sentenciaElegir : 'elegir' '(' expresion ')' '{' caso* porDefecto? '}' ;
caso          : 'caso' expresion ':' sentencia* ;
porDefecto    : 'porDefecto' ':' sentencia* ;

// Try / Intentar
sentenciaIntento
    : 'intentar' bloque 'capturar' ('(' ID ')')? bloque ('finalmente' bloque)?
    ;

// Retorno / Romper
sentenciaRetorno : ('retornar' | 'lanzar') expresion? ;
sentenciaRota    : 'romper' | 'continuar' ;

// Clases
sentenciaClase
    : 'clase' ID ('extiende' ID)? '{' miembroClase* '}'
    ;

miembroClase
    : ('constructor' | nombrePropiedad) '(' parametros? ')' bloque
    | nombrePropiedad '=' expresion
    ;

// EXPRESIONES (con jerarquía de precedencia)

expresion : exprTernaria ;

exprTernaria
    : exprLogica ('?' expresion ':' expresion)?
    ;

exprLogica
    : exprComparacion (('&&' | '||') exprComparacion)*
    ;

exprComparacion
    : exprAritmetica (operadorComparacion exprAritmetica)*
    ;

operadorComparacion
    : '==' | '!=' | '===' | '!==' | '<' | '>' | '<=' | '>=' | 'instanciaDe'
    ;

exprAritmetica
    : exprMultiplicativa (('+' | '-') exprMultiplicativa)*
    ;

exprMultiplicativa
    : exprUnaria (('*' | '/' | '%' | '**') exprUnaria)*
    ;

exprUnaria
    : operadorUnario? exprPostfija
    ;

operadorUnario
    : '+' | '-' | '!' | '++' | '--' | 'tipoDe' | 'vacio' | 'eliminar' | 'esperar'
    ;

exprPostfija : primaria postfijo* ;

postfijo
    : '.' nombrePropiedad
    | '[' expresion ']'
    | '(' argumentos ')'
    | '++'
    | '--'
    ;

primaria
    : ID
    | NUMERO
    | CADENA
    | 'verdadero'
    | 'falso'
    | 'nulo'
    | 'indefinido'
    | 'Infinito'
    | 'NuN'
    | builtin
    | crear
    | '(' expresion ')'
    | funcionAnonima
    | arregloLiteral
    | objetoLiteral
    ;

builtin
    : 'Arreglo' | 'Booleano' | 'Cadena' | 'Fecha' | 'Funcion' | 'Matriz'
    | 'Numero' | 'consola' | 'Mate'
    ;

crear : 'crear' constructor ;

constructor
    : ID | 'Arreglo' | 'Booleano' | 'Cadena' | 'Fecha' | 'Funcion' | 'Matriz' | 'Numero'
    ;

// Arreglos y objetos
arregloLiteral : '[' listaExpresiones? ']' ;

listaExpresiones : expresion (',' expresion)* ','? ;

objetoLiteral : '{' (propiedadObjeto (',' propiedadObjeto)* ','?)? '}' ;

propiedadObjeto
    : nombrePropiedad
    | nombrePropiedad ':' expresion
    | nombrePropiedad '(' parametros? ')' bloque
    ;

nombrePropiedad : ID | CADENA | NUMERO ;

// ============================================================
// LEXER RULES (MAYÚSCULAS)
// ============================================================

// Tokens terminales
NUMERO  : [0-9]+ ('.' [0-9]+)? | '.' [0-9]+ ;
CADENA  : '"' (~["\\] | '\\' .)* '"'
        | '\'' (~['\\] | '\\' .)* '\''
        ;

ID      : [a-zA-Z_$] [a-zA-Z_$0-9]* ;

// Tokens a ignorar
COMENTARIO_LINEA : '//' ~[\r\n]* -> skip ;
COMENTARIO_BLOQUE: '/*' .*? '*/' -> skip ;
WS               : [ \t\r\n]+    -> skip ;
