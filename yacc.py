import ply.yacc as yacc
import os
from enum import Enum
from lexer import tokens
import lexer

class ProductionProperty(Enum):
    NONE = 1
    REPETITION = 2
    OPTIONAL = 3
    XOR = 4

class T_SYMBOL:
    def __init__(self, value):
        self.value = value

class NT_SYMBOL:
    def __init__(self, value):
        self.value = value

class GRAMMAR_EXPRESSION:
  def __init__(self, name, productions_list):
    self.name = name
    self.productions_list = productions_list

class TOKEN_EXPRESSION:
  def __init__(self, name, productions_list):
    self.name = name
    self.productions_list = productions_list

class STRICT_EXPRESSION:
  def __init__(self, name, productions_list):
    self.name = name
    self.productions_list = productions_list

class MACRO_EXPRESSION:
  def __init__(self, name, productions_list):
    self.name = name
    self.productions_list = productions_list

class GRAMMAR_LIST:
  def __init__(self, grammar_list):
    self.list = grammar_list

class PRODUCTIONS_LIST:
  def __init__(self, productions_list):
    self.list = productions_list

class PRODUCTION:
  def __init__(self, list, productionProperty=ProductionProperty.NONE):
    self.list = list
    self.productionProperty = productionProperty

class PRODUCTION_ELEMENT:
    def __init__(self, name, productionProperty=ProductionProperty.NONE):
        self.name = name
        self.productionProperty = productionProperty  # none, repetition or optional

class COMMENT_BLOCK:
  def __init__(self, list):
    self.list = list


def p_grammar_list(p):
    """
    grammar_list : comment_block
                |  grammar_list grammar_expression
                |  grammar_list token_expression
                |  grammar_list strict_expression
                |  grammar_list macro_expression
                |  grammar_list comment_block
    """
    if len(p) == 2:
        p[0]  = GRAMMAR_LIST([p[1]])
    elif len(p) == 3:
        p[1].list.append(p[2])
        p[0] = p[1]

def p_comment_block(p):
    """
    comment_block : COMMENT
                |   comment_block COMMENT
    """

    if len(p) == 2:
        p[0] = COMMENT_BLOCK([p[1]])
    elif len(p) == 3:
        p[1].list.append(p[2])
        p[0] = p[1]

def p_grammar_expression(p):
    """
    grammar_expression : LGRAMMAR_EXPRESSION productions_list
    """
    p[0] = GRAMMAR_EXPRESSION(p[1],p[2])

def p_token_expression(p):
    """
    token_expression : LTOKEN_EXPRESSION productions_list
    """
    p[0] = TOKEN_EXPRESSION(p[1],p[2])

def p_strict_expression(p):
    """
    strict_expression : LSTRICT_EXPRESSION productions_list
    """
    p[0] = STRICT_EXPRESSION(p[1],p[2])

def p_macro_expression(p):
    """
    macro_expression : LMACRO_EXPRESSION productions_list
    """
    p[0] = MACRO_EXPRESSION(p[1],p[2])

def p_productions_list(p):
    """
    productions_list : production
                    | productions_list ALTERNATIVE_SYMBOL production
    """
    if len(p) == 2:
        p[0] = PRODUCTIONS_LIST([p[1]])
    elif len(p) == 4:
        p[1].list.append(p[3])
        p[0] = p[1]

def p_t_symbol_production(p):
    """
        t_symbol_production : OPEN_SQUARE_BRACKET T_SYMBOL CLOSE_SQUARE_BRACKET
                         |    OPEN_SQUARE_BRACKET REPETITION_SYMBOL CLOSE_SQUARE_BRACKET
                         |    OPEN_SQUARE_BRACKET ALTERNATIVE_SYMBOL CLOSE_SQUARE_BRACKET
                         |    T_SYMBOL
        """
    if len(p) == 2:
        p[0] = T_SYMBOL(p[1])
    elif len(p) == 4:
        p[0] = T_SYMBOL(p[2])

def p_production_element(p):
    """
    production_element : OPEN_SQUARE_BRACKET NT_SYMBOL CLOSE_SQUARE_BRACKET
            |    NT_SYMBOL REPETITION_SYMBOL
            |    t_symbol_production REPETITION_SYMBOL
            |    OPEN_SQUARE_BRACKET CLOSE_SQUARE_BRACKET
            |    NT_SYMBOL
            |    t_symbol_production
    """
    if len(p) == 2: #NT_SYMBOL|t_symbol_production
        if(type(p[1]) is T_SYMBOL):
            p[0] = PRODUCTION_ELEMENT(p[1], ProductionProperty.NONE)
        else:
            p[0] = PRODUCTION_ELEMENT(NT_SYMBOL(p[1]), ProductionProperty.NONE)
    elif len(p) == 3 and p[1] == "[": #OPEN_SQUARE_BRACKET CLOSE_SQUARE_BRACKET
        p[0] = PRODUCTION_ELEMENT([], ProductionProperty.NONE)  #evt. Problem wegen leerer Liste
    elif len(p) == 3:  # NT_SYMBOL REPETITION_SYMBOL|t_symbol_production REPETITION_SYMBOL
        if (type(p[1]) is T_SYMBOL):
            p[0] = PRODUCTION_ELEMENT(p[1], ProductionProperty.REPETITION)
        else:
            p[0] = PRODUCTION_ELEMENT(NT_SYMBOL(p[1]), ProductionProperty.REPETITION)
    elif len(p) == 4 and p[1] == '[': #OPEN_SQUARE_BRACKET NT_SYMBOL CLOSE_SQUARE_BRACKET
        p[0] = PRODUCTION(NT_SYMBOL(p[2]), ProductionProperty.OPTIONAL)


def p_production(p):
    #missing optional production
    """
    production : production_element
            |    production production_element
            |    OPEN_PARENTHESIS production CLOSE_PARENTHESIS
            |    production OPEN_PARENTHESIS production CLOSE_PARENTHESIS
            |    OPEN_PARENTHESIS production CLOSE_PARENTHESIS production
            |    OPEN_PARENTHESIS production CLOSE_PARENTHESIS REPETITION_SYMBOL
            |    production OPEN_PARENTHESIS production CLOSE_PARENTHESIS REPETITION_SYMBOL
            |    production ALTERNATIVE_SYMBOL production_element

    """

    if len(p) == 2:
       p[0] = PRODUCTION([p[1]])
    elif len(p) == 3:
        p[1].list.append(p[2])
        p[0] = p[1]
    elif len(p) == 4 and p[2] == '|':
        p[1].productionProperty = ProductionProperty.XOR
        p[1].list.append(p[3])
        p[0] = p[1]
    elif len(p) == 4:
        p[2].list.insert(0, PRODUCTION_ELEMENT(NT_SYMBOL('(')))
        p[2].list.append(PRODUCTION_ELEMENT(NT_SYMBOL(')')))
        p[0] = p[2]
    elif len(p) == 5 and p[3] == ')':
        p[2].list.insert(0, PRODUCTION_ELEMENT(NT_SYMBOL('(')))
        p[2].list.append(PRODUCTION_ELEMENT(NT_SYMBOL(')')))
        p[4].list.insert(0,PRODUCTION(p[2]))
        p[0] = p[4]
    elif len(p) == 5 and p[4] == ')':
        p[3].list.insert(0, PRODUCTION_ELEMENT(NT_SYMBOL('(')))
        p[3].list.append(PRODUCTION_ELEMENT(NT_SYMBOL(')')))
        p[1].list.append(p[3])
        p[0] = p[1]
    elif len(p) == 5:
        p[2].productionProperty = ProductionProperty.REPETITION
        p[0] = PRODUCTION([p[2]])
    elif len(p) == 6 and p[5] == '*':
        p[3].productionProperty = ProductionProperty.REPETITION
        p[1].list.append(PRODUCTION([p[3]]))
        p[0] = p[1]
    #elif len(p) == 6:
    #    p[3].list.insert(0, PRODUCTION_ELEMENT(NT_SYMBOL('(')))
    #    p[3].list.append(PRODUCTION_ELEMENT(NT_SYMBOL(')')))
    #    p[1].list.append(PRODUCTION(p[2]))
    #    p[1].list.append(p[5])
    #    p[0] = p[1]


def p_error(t):
    print("Syntax error at '%s'" % t.value)

parser = yacc.yacc()

#while True:
   #try:
   #    s = raw_input('calc > ')
   #except EOFError:
   #    break
   #if not s: continue
#result = parser.parse('%HALLO\n%Test\n<rule1> ::= a(<rule3>) | <rule4>')
#result = parser.parse(lexer.import_tptp_file('TestCaseComment.txt'))
result = parser.parse("""%---blub
<thf_annotated>        ::= thf(<name>,<formula_role>,<thf_formula><annotations>).
""")
print(result)