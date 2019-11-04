import ply.lex as lex
import os

class TPTPLexer():
    #List of token names
    tokens = (
        'LGRAMMAR_EXPRESSION',
        'LTOKEN_EXPRESSION',
        'LSTRICT_EXPRESSION',
        'LMACRO_EXPRESSION',
        'NT_SYMBOL',
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

    def t_COMMENT(self,t):
        r'%-.*'
        #t.value = t.value.rstrip('\n')
        return t

    def t_OPEN_SQUARE_BRACKET(self,t):
        r'\['
        return t

    def t_CLOSE_SQUARE_BRACKET(self,t):
        r'\]'
        return t

    def t_REPETITION_SYMBOL(self,t):
        r'\*'
        return t

    def t_ALTERNATIVE_SYMBOL(self,t):
        r'\|'
        return t

    def t_OPEN_PARENTHESIS(self,t):
        r'\('
        return t

    def t_CLOSE_PARENTHESIS(self,t):
        r'\)'
        return t

    def t_LGRAMMAR_EXPRESSION(self,t):
        r'<[a-zA-Z_][a-zA-Z_0-9]*>[\s]*::='
        t.value = t.value[:-3]
        t.value = t.value.rstrip()
        return t

    def t_LTOKEN_EXPRESSION(self,t):
        r'<[a-zA-Z_][a-zA-Z_0-9]*>[\s]*::-'
        t.value = t.value[:-3]
        t.value = t.value.rstrip()
        return t

    def t_LSTRICT_EXPRESSION(self,t):
        r'<[a-zA-Z_][a-zA-Z_0-9]*>[\s]*:=='
        t.value = t.value[:-3]
        t.value = t.value.rstrip()
        return t

    def t_LMACRO_EXPRESSION(self,t):
        r'<[a-zA-Z_][a-zA-Z_0-9]*>[\s]*:::'
        t.value = t.value[:-3]
        t.value = t.value.rstrip()
        return t

    def t_NT_SYMBOL(self,t):
        r'<[a-zA-Z_][a-zA-Z_0-9]*>'
        #r'<..*?>'
        return t

    def t_T_SYMBOL(self,t):
        #r'[\.,a-zA-Z\_0-9\-<>][a-zA-Z\_0-9\-]*'
        r'[$\'\\\.,a-zA-Z\_0-9\0-9-\-<>&@!:{}~?^+=/"!^^/@/+-/%;][a-zA-Z\_0-9\-/"!?/@/+-/*/%;\->&+=$\'\\\.,]*'
        #r'[a-zA-Z\_0-9\_0-9-\-/"!?/@/+-/*/%;\->&+=$\'\\\.,^^+=^~{}:<>][a-zA-Z\_0-9\-/"!?/@/+-/*/%;\->&+=$\'\\\.,]*'
        #r'[$\'\\\.,a-zA-Z\_0-9\0-9-\-<>&@!:{}~?^+=/"!^^/@/+-/%;][$\'\\\.,a-zA-Z\_0-9\0-9-\->&+=/"!?/@/+-/*/%;]*'
        #r'..*'
        return t

    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def import_tptp_file(self,filename):
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        my_file = os.path.join(THIS_FOLDER, filename)
        file = open(my_file, "r", encoding='UTF-8')
        data = file.read()
        return data


    def run(self):
        # data = '<rule1> ::= <rule2> abcd <rule3> | <rule4>'
        data = r'<thf_unitary_formula>  ::= <thf_quantified_formula> | <thf_atomic_formula> | <variable> | (<thf_logic_formula>)'
        # data = import_tptp_file('tptp_bnf.txt')
        self.lexer.input(data)
        while 1:
            tok = lex.token()
            if not tok: break  # No more input
            print(tok)

    def __init__(self):
        # Build the lexer
        self.lexer = lex.lex(module=self)
