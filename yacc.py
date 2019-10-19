import ply.yacc as yacc

from lexer import tokens

def p_comment_block(p):
    """
    comment_block: COMMENT
    comment_block: comment_block COMMENT
    """
    if len(p) == 1:
        p[0] = [p[1]]
    elif len(p) == 2:
        p[0] = p[1] + [p[2]]

def p_grammar_expression(p):
    """
    grammar_expression: NT_SYMBOL t_GRAMMAR_SYMBOL productions_list
    """
    p[0] = p[1] + [p[2]]

def p_productions_list(p):
    """
    production_list: production
    production_list: production_list OR production
    """
    if len(p) == 1:
        p[0] = [p[1]]
    elif len(p) == 2:
        p[0] = p[1] + [p[2]]

def p_production(p):
    #missing optional production
    """
    production: NT_SYMBOL
    production: T_SYMBOL
    production: production NT_SYMBOL
    production: production T_SYMBOL
    """
    if len(p) == 1:
        p[0] = [p[1]]
    elif len(p) == 2:
        p[0] = p[1] + [p[2]]

parser = yacc.yacc()

while True:
   #try:
   #    s = raw_input('calc > ')
   #except EOFError:
   #    break
   #if not s: continue
   result = parser.parse()
   print(result)