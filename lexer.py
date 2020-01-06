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
    t_ignore = ' \t\n'

    #token definitions

    def t_COMMENT(self,t):
        #r'%-.*'
        #r'%[a-zA-Z\- ].*'
        r'%[^\]].*'
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

    #error handling
    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def import_tptp_file(self, filename: str) -> str:
        """Import TPTP grammar file.

        :param filename: Filename of the TPTP grammar file.
        :return:   grammar file content as string.
        """
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        my_file = os.path.join(THIS_FOLDER, filename)
        file = open(my_file, "r", encoding='UTF-8')
        data = file.read()
        return data

    #def run(self):
    #
    #    data = self.import_tptp_file('TPTP_BNF.txt')
    #    self.lexer.input(data)
    #    while 1:
    #        tok = lex.token()
    #        if not tok: break  # No more input
    #        print(tok)

    def __init__(self):
        # Build the lexer
        self.lexer = lex.lex(module=self)