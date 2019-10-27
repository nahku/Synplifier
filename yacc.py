import ply.yacc as yacc
import os
from lexer import tokens
import lexer

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
  def __init__(self, list):
    self.list = list

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
                    | OPEN_SQUARE_BRACKET production CLOSE_SQUARE_BRACKET
                    | productions_list ALTERNATIVE_SYMBOL productions_list
    """
    if len(p) == 2:
        p[0] = PRODUCTIONS_LIST([p[1]])
    elif len(p) == 4 and p[1] == "[":
        p[0] = PRODUCTIONS_LIST([p[1], p[2], p[3]])
    elif len(p) == 4:
        p[1].list.append(p[3])
        p[0] = p[1]

def p_production(p):
    #missing optional production
    """
    production : NT_SYMBOL
            |    T_SYMBOL
            |    NT_SYMBOL REPETITION_SYMBOL
            |    production NT_SYMBOL
            |    production T_SYMBOL
            |    production NT_SYMBOL REPETITION_SYMBOL
    """
    if len(p) == 2:
        p[0] = PRODUCTION([p[1]])
    elif len(p) == 3 and p[2] != "*":
        p[1].list.append(p[2])
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = PRODUCTION([p[1], p[2]])
    elif len(p) == 4:
        p[1].list.append(p[2], p[3])
        p[0] = p[1]

def p_error(t):
    print("Syntax error at '%s'" % t.value)

def import_tptp_file(filename):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(THIS_FOLDER, filename)
    file = open(my_file, "r", encoding='UTF-8')
    data = file.read()
    return data

parser = yacc.yacc()

#while True:
   #try:
   #    s = raw_input('calc > ')
   #except EOFError:
   #    break
   #if not s: continue
#result = parser.parse('%HALLO\n%Test\n<rule1> ::= ,<rule2> a <rule3> | <rule4>')
#error nt is not porduction
result = parser.parse("""%----v7.3.0.0 (TPTP version.internal development number)
%------------------------------------------------------------------------------
%----README ... this header provides important meta- and usage information
%----
%----Intended uses of the various parts of the TPTP syntax are explained
%----in the TPTP technical manual, linked from www.tptp.org.
%----
%----Four kinds of separators are used, to indicate different types of rules:
%----  ::= is used for regular grammar rules, for syntactic parsing.
%----  :== is used for semantic grammar rules. These define specific values
%----      that make semantic sense when more general syntactic rules apply.
%----  ::- is used for rules that produce tokens.
%----  ::: is used for rules that define character classes used in the
%----       construction of tokens.
%----
%----White space may occur between any two tokens. White space is not specified
%----in the grammar, but there are some restrictions to ensure that the grammar
%----is compatible with standard Prolog: a <TPTP_file> should be readable with
%----read/1.
%----
%----The syntax of comments is defined by the <comment> rule. Comments may
%----occur between any two tokens, but do not act as white space. Comments
%----will normally be discarded at the lexical level, but may be processed
%----by systems that understand them (e.g., if the system comment convention
%----is followed).
%----
%----Multiple languages are defined. Depending on your need, you can implement 
%----just the one(s) you need. The common rules for atoms, terms, etc, come 
%----after the definitions of the languages, and mostly all needed for all the 
%----languages.
%----Top of Page---------------------------------------------------------------
%----Files. Empty file is OK.
<TPTP_file>            ::= <TPTP_input>*
<tfx_let_types>        ::= <tff_atom_typing> | [<tff_atom_typing_list>] | <tff>
""")
print(result)