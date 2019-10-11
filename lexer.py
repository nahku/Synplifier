import ply.lex as lex
import os

#List of token names
tokens = (
    'GRAMMAR_SYMBOL',
    'TOKEN_SYMBOL',
    'STRICT_SYMBOL',
    'MACRO_SYMBOL',
    'NT_SYMBOL',
    'IDENTIFIER',
    'COMMENT',
    'LEFT_PARENTHESIS',
    'RIGHT_PARENTHESIS',
    'OR',
    'T_SYMBOL'
)

literals = ['[',']',',','*','.']

# Regular expression rules for simple tokens
#t_GRAMMAR_SYMBOL = r'::='
#t_TOKEN_SYMBOL = r'::-'
#t_STRICT_SYMBOL = r':=='
#t_MACRO_SYMBOL = r':::'
#t_NT_OPEN_SYMBOL   = r'<'
#t_NT_CLOSE_SYMBOL  = r'>'
#t_OR  = r'\|'
t_LEFT_PARENTHESIS = r'\('
t_RIGHT_PARENTHESIS = r'\)'
t_OR = r'\|'

t_ignore = ' \t\n'

def t_COMMENT(t):
    r'%.*'
    #t.value = t.value.rstrip('\n')
    return t

def t_GRAMMAR_SYMBOL(t):
    r'::='
    return t

def t_TOKEN_SYMBOL(t):
    r'::-'
    return t

def t_STRICT_SYMBOL(t):
    r':=='
    return t

def t_MACRO_SYMBOL(t):
    r':::'
    return t

def t_NT_SYMBOL(t):
    r'<[a-zA-Z_][a-zA-Z_0-9]*>'
    return t

def t_T_SYMBOL(t):
    r'[a-zA-Z_0-9\-][a-zA-Z_0-9\-]*'
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

#lex.lex(debug=1)
lex.lex()

#data = '::=::::==||     ||><bl a:==bla%----'


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'tptp_bnf.txt')
file = open(my_file, "r", encoding='UTF-8')
data = file.read()

lex.input(data)



if __name__ ==  "__main__" :
    while 1:
        tok = lex.token()
        if not tok: break  # No more input
        print(tok)

