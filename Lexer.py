import ply.lex as lex
import re


class TPTPLexer:
    # List of token names
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
    t_ignore = ' \t\n '

    # token definitions

    def t_COMMENT(self, t):
        r'^%.*$'
        return t

    def t_OPEN_SQUARE_BRACKET(self, t):
        r'\['
        return t

    def t_CLOSE_SQUARE_BRACKET(self, t):
        r'\]'
        return t

    def t_REPETITION_SYMBOL(self, t):
        r'\*'
        return t

    def t_ALTERNATIVE_SYMBOL(self, t):
        r'\|'
        return t

    def t_OPEN_PARENTHESIS(self, t):
        r'\('
        return t

    def t_CLOSE_PARENTHESIS(self, t):
        r'\)'
        return t

    def t_LGRAMMAR_EXPRESSION(self, t):
        r'<\w+>[\s]*::='
        t.value = t.value[:-3]
        t.value = t.value.rstrip()
        return t

    def t_LTOKEN_EXPRESSION(self, t):
        r'<\w+>[\s]*::-'
        t.value = t.value[:-3]
        t.value = t.value.rstrip()
        return t

    def t_LSTRICT_EXPRESSION(self, t):
        r'<\w+>[\s]*:=='
        t.value = t.value[:-3]
        t.value = t.value.rstrip()
        return t

    def t_LMACRO_EXPRESSION(self, t):
        r'<\w+>[\s]*:::'
        t.value = t.value[:-3]
        t.value = t.value.rstrip()
        return t

    def t_NT_SYMBOL(self, t):
        r'<\w+>'
        return t

    def t_T_SYMBOL(self, t):
        r'[$\'\\\.,a-zA-Z\_0-9\0-9-\-<>&@!:{}~?^+=/"!^^/@/+-/%;][a-zA-Z\_0-9\-/"!?/@/+-/*/%;\->&+=$\'\\\.,]*'
        return t

    # error handling
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def debug(self, data):
        self.lexer.input(data)
        while 1:
            tok = lex.token()
            if not tok: break  # No more input
            print(tok)

    def __init__(self):
        # Build the lexer
        self.lexer = lex.lex(module=self, reflags=re.M)
