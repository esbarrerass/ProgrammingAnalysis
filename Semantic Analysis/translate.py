from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from ESJSLexer import ESJSLexer
from ESJSParser import ESJSParser
from ESJSVisitor import ESJSVisitor


class ESJSToPython(ESJSVisitor):
    def __init__(self):
        self.indent_level = 0

    def _ind(self):
        return "    " * self.indent_level

    # Programa
    def visitPrograma(self, ctx):
        lines = [self.visit(s) for s in ctx.sentencia()]
        return "\n".join(l for l in lines if l)

    # Declaración de variables
    def visitSentenciaDeclaracionVariable(self, ctx):
        # tipoVariable ID ('=' expresion)? (',' ID ('=' expresion)?)*
        ids = ctx.ID()
        exprs = ctx.expresion()
        result = []
        for i, id_node in enumerate(ids):
            name = id_node.getText()
            if i < len(exprs):
                value = self.visit(exprs[i])
                result.append(f"{self._ind()}{name} = {value}")
            else:
                result.append(f"{self._ind()}{name} = None")
        return "\n".join(result)

    # If / Si
    def visitSentenciaSi(self, ctx):
        cond = self.visit(ctx.expresion())
        bloques = ctx.bloqueOSentencia()

        out = f"{self._ind()}if {cond}:\n"
        self.indent_level += 1
        out += self.visit(bloques[0])
        self.indent_level -= 1

        if len(bloques) > 1:  # tiene "sino"
            out += f"\n{self._ind()}else:\n"
            self.indent_level += 1
            out += self.visit(bloques[1])
            self.indent_level -= 1
        return out

    # While / Mientras
    def visitSentenciaMientras(self, ctx):
        cond = self.visit(ctx.expresion())
        out = f"{self._ind()}while {cond}:\n"
        self.indent_level += 1
        out += self.visit(ctx.bloqueOSentencia())
        self.indent_level -= 1
        return out

    # Función
    def visitSentenciaFuncion(self, ctx):
        name = ctx.ID().getText()
        params = self.visit(ctx.parametros()) if ctx.parametros() else ""
        out = f"{self._ind()}def {name}({params}):\n"
        self.indent_level += 1
        out += self.visit(ctx.bloque())
        self.indent_level -= 1
        return out

    def visitParametros(self, ctx):
        return ", ".join(id_node.getText() for id_node in ctx.ID())

    # Bloque
    def visitBloque(self, ctx):
        sentencias = [self.visit(s) for s in ctx.sentencia()]
        if not sentencias:
            return f"{self._ind()}pass"
        return "\n".join(s for s in sentencias if s)

    # xpresiones aritméticas/lógicas
    def visitExprAritmetica(self, ctx):
        # exprMultiplicativa (('+' | '-') exprMultiplicativa)*
        parts = [self.visit(ctx.exprMultiplicativa(0))]
        for i in range(1, len(ctx.exprMultiplicativa())):
            op = ctx.getChild(2 * i - 1).getText()  # operador
            parts.append(f" {op} {self.visit(ctx.exprMultiplicativa(i))}")
        return "".join(parts)

    # Primaria
    def visitPrimaria(self, ctx):
        if ctx.ID():       return ctx.ID().getText()
        if ctx.NUMERO():   return ctx.NUMERO().getText()
        if ctx.CADENA():   return ctx.CADENA().getText()
        text = ctx.getText()
        # Mapeo ESJS → Python
        return {
            'verdadero': 'True',
            'falso':     'False',
            'nulo':      'None',
            'indefinido':'None',
            'consola':   'print',  # ojo: simplificado
        }.get(text, text)

    # Retorno
    def visitSentenciaRetorno(self, ctx):
        tipo = ctx.getChild(0).getText()  # 'retornar' o 'lanzar'
        keyword = 'return' if tipo == 'retornar' else 'raise'
        if ctx.expresion():
            return f"{self._ind()}{keyword} {self.visit(ctx.expresion())}"
        return f"{self._ind()}{keyword}"


def traducir(archivo_esjs):
    input_stream = FileStream(archivo_esjs, encoding='utf-8')
    lexer  = ESJSLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = ESJSParser(tokens)
    tree   = parser.programa()

    translator = ESJSToPython()
    return translator.visit(tree)


if __name__ == "__main__":
    import sys
    print(traducir(sys.argv[1]))
