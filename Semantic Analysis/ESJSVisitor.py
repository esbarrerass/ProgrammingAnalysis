# Generated from ESJS.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ESJSParser import ESJSParser
else:
    from ESJSParser import ESJSParser

# This class defines a complete generic visitor for a parse tree produced by ESJSParser.

class ESJSVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ESJSParser#programa.
    def visitPrograma(self, ctx:ESJSParser.ProgramaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentencia.
    def visitSentencia(self, ctx:ESJSParser.SentenciaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaDeclaracionVariable.
    def visitSentenciaDeclaracionVariable(self, ctx:ESJSParser.SentenciaDeclaracionVariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#tipoVariable.
    def visitTipoVariable(self, ctx:ESJSParser.TipoVariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaExpresion.
    def visitSentenciaExpresion(self, ctx:ESJSParser.SentenciaExpresionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#paramFuncionFlecha.
    def visitParamFuncionFlecha(self, ctx:ESJSParser.ParamFuncionFlechaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#formaFuncion.
    def visitFormaFuncion(self, ctx:ESJSParser.FormaFuncionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#operadorAsignacion.
    def visitOperadorAsignacion(self, ctx:ESJSParser.OperadorAsignacionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaFuncion.
    def visitSentenciaFuncion(self, ctx:ESJSParser.SentenciaFuncionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#funcionAnonima.
    def visitFuncionAnonima(self, ctx:ESJSParser.FuncionAnonimaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#parametros.
    def visitParametros(self, ctx:ESJSParser.ParametrosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#argumentos.
    def visitArgumentos(self, ctx:ESJSParser.ArgumentosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaControlFlujo.
    def visitSentenciaControlFlujo(self, ctx:ESJSParser.SentenciaControlFlujoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#bloque.
    def visitBloque(self, ctx:ESJSParser.BloqueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaSi.
    def visitSentenciaSi(self, ctx:ESJSParser.SentenciaSiContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#bloqueOSentencia.
    def visitBloqueOSentencia(self, ctx:ESJSParser.BloqueOSentenciaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaMientras.
    def visitSentenciaMientras(self, ctx:ESJSParser.SentenciaMientrasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaHacer.
    def visitSentenciaHacer(self, ctx:ESJSParser.SentenciaHacerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaPara.
    def visitSentenciaPara(self, ctx:ESJSParser.SentenciaParaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#paraClasico.
    def visitParaClasico(self, ctx:ESJSParser.ParaClasicoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#inicializador.
    def visitInicializador(self, ctx:ESJSParser.InicializadorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#paraDeEn.
    def visitParaDeEn(self, ctx:ESJSParser.ParaDeEnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaElegir.
    def visitSentenciaElegir(self, ctx:ESJSParser.SentenciaElegirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#caso.
    def visitCaso(self, ctx:ESJSParser.CasoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#porDefecto.
    def visitPorDefecto(self, ctx:ESJSParser.PorDefectoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaIntento.
    def visitSentenciaIntento(self, ctx:ESJSParser.SentenciaIntentoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaRetorno.
    def visitSentenciaRetorno(self, ctx:ESJSParser.SentenciaRetornoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaRota.
    def visitSentenciaRota(self, ctx:ESJSParser.SentenciaRotaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#sentenciaClase.
    def visitSentenciaClase(self, ctx:ESJSParser.SentenciaClaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#miembroClase.
    def visitMiembroClase(self, ctx:ESJSParser.MiembroClaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#expresion.
    def visitExpresion(self, ctx:ESJSParser.ExpresionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#exprTernaria.
    def visitExprTernaria(self, ctx:ESJSParser.ExprTernariaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#exprLogica.
    def visitExprLogica(self, ctx:ESJSParser.ExprLogicaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#exprComparacion.
    def visitExprComparacion(self, ctx:ESJSParser.ExprComparacionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#operadorComparacion.
    def visitOperadorComparacion(self, ctx:ESJSParser.OperadorComparacionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#exprAritmetica.
    def visitExprAritmetica(self, ctx:ESJSParser.ExprAritmeticaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#exprMultiplicativa.
    def visitExprMultiplicativa(self, ctx:ESJSParser.ExprMultiplicativaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#exprUnaria.
    def visitExprUnaria(self, ctx:ESJSParser.ExprUnariaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#operadorUnario.
    def visitOperadorUnario(self, ctx:ESJSParser.OperadorUnarioContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#exprPostfija.
    def visitExprPostfija(self, ctx:ESJSParser.ExprPostfijaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#postfijo.
    def visitPostfijo(self, ctx:ESJSParser.PostfijoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#primaria.
    def visitPrimaria(self, ctx:ESJSParser.PrimariaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#builtin.
    def visitBuiltin(self, ctx:ESJSParser.BuiltinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#crear.
    def visitCrear(self, ctx:ESJSParser.CrearContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#constructor.
    def visitConstructor(self, ctx:ESJSParser.ConstructorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#arregloLiteral.
    def visitArregloLiteral(self, ctx:ESJSParser.ArregloLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#listaExpresiones.
    def visitListaExpresiones(self, ctx:ESJSParser.ListaExpresionesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#objetoLiteral.
    def visitObjetoLiteral(self, ctx:ESJSParser.ObjetoLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#propiedadObjeto.
    def visitPropiedadObjeto(self, ctx:ESJSParser.PropiedadObjetoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ESJSParser#nombrePropiedad.
    def visitNombrePropiedad(self, ctx:ESJSParser.NombrePropiedadContext):
        return self.visitChildren(ctx)



del ESJSParser