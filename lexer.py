import ply.lex as lex
import os

#List of token names
tokens = (
    'LGRAMMAR_EXPRESSION',
    'LTOKEN_EXPRESSION',
    'LSTRICT_EXPRESSION',
    'LMACRO_EXPRESSION',
    'NT_SYMBOL',
    'IDENTIFIER',
    'COMMENT',
    'OPEN_PARENTHESIS',
    'CLOSE_PARENTHESIS',
    'OPEN_SQUARE_BRACKET',
    'CLOSE_SQUARE_BRACKET',
    'ALTERNATIVE_SYMBOL',
    'REPETITION_SYMBOL',
    'T_SYMBOL'
)

literals = []

# Regular expression rules for simple tokens
#t_GRAMMAR_SYMBOL = r'::='
#t_TOKEN_SYMBOL = r'::-'
#t_STRICT_SYMBOL = r':=='
#t_MACRO_SYMBOL = r':::'
#t_NT_OPEN_SYMBOL   = r'<'
#t_NT_CLOSE_SYMBOL  = r'>'
#t_OR  = r'\|'
#t_OPEN_PARENTHESIS = r'\('
#t_CLOSE_PARENTHESIS = r'\)'
#t_ALTERNATIVE_SYMBOL = r'\|'
#t_REPETITION_SYMBOL = r'\*'

t_ignore = ' \t\n'

def t_COMMENT(t):
    r'%.*'
    #t.value = t.value.rstrip('\n')
    return t

def t_OPEN_SQUARE_BRACKET(t):
    r'\['
    return t

def t_CLOSE_SQUARE_BRACKET(t):
    r'\]'
    return t

def t_REPETITION_SYMBOL(t):
    r'\*'
    return t

def t_ALTERNATIVE_SYMBOL(t):
    r'\|'
    return t

def t_OPEN_PARENTHESIS(t):
    r'\('
    return t

def t_CLOSE_PARENTHESIS(t):
    r'\)'
    return t

def t_LGRAMMAR_EXPRESSION(t):
    r'<[a-zA-Z_][a-zA-Z_0-9]*>[\s]*::='
    t.value = t.value[:-4]
    return t

def t_LTOKEN_EXPRESSION(t):
    r'<[a-zA-Z_][a-zA-Z_0-9]*>[\s]*::-'
    t.value = t.value[:-4]
    return t

def t_LSTRICT_EXPRESSION(t):
    r'<[a-zA-Z_][a-zA-Z_0-9]*>[\s]*:=='
    t.value = t.value[:-4]
    return t

def t_LMACRO_EXPRESSION(t):
    r'<[a-zA-Z_][a-zA-Z_0-9]*>[\s]*:::'
    t.value = t.value[:-4]
    return t

def t_NT_SYMBOL(t):
    r'<[a-zA-Z_][a-zA-Z_0-9]*>'
    #r'<..*?>'
    return t

def t_T_SYMBOL(t):
    #r'[\.,a-zA-Z\_0-9\-<>][a-zA-Z\_0-9\-]*'
    r'[$\'\\\.,a-zA-Z\_0-9\-<>&@!:{}~?^+=/"][$\'\\\.,a-zA-Z\_0-9\->&+=/"]*'
    #r'..*'
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

#lex.lex(debug=1)
#lex.lex()


def lexer():
    lex.lex()

lexer()

def import_tptp_file(filename):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(THIS_FOLDER, filename)
    file = open(my_file, "r", encoding='UTF-8')
    data = file.read()
    return data

#data = '<rule1> ::= <rule2> abcd <rule3> | <rule4>'
data = '<tfx_let_types>        ::= <tff_atom_typing> | [<tff_atom_typing_list>]'
#data = import_tptp_file('tptp_bnf.txt')

lex.input(data)

if __name__ ==  "__main__" :
    while 1:
        tok = lex.token()
        if not tok: break  # No more input
        print(tok)