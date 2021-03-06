import Lexer as lex
import os

def test_comment():
    tptpLexer = lex.TPTPLexer()
    lexer = tptpLexer.lexer
    dirpath = os.getcwd()
    lexer.input(tptpLexer.import_tptp_file(dirpath+ '/testfiles/TestCaseComment.txt'))
    type = True
    while 1:
        tok = lexer.token()
        if not tok: break  # No more input
        if tok.type != 'COMMENT':
            type = False
    assert type


def test_grammar_rule():
    lexer = lex.TPTPLexer().lexer
    lexer.input('<TPTP_TEST> ::=')
    type = True
    i = 0
    while 1:
        tok = lexer.token()
        if not tok: break  # No more input
        if (i == 1):
            if tok.type != 'GRAMMAR_SYMBOL':
                type = False
        i + 1
    assert type


def test_token_rule():
    lexer = lex.TPTPLexer().lexer
    lexer.input('<TPTP_TEST> ::-')
    type = True
    i = 0
    while 1:
        tok = lexer.token()
        if not tok: break  # No more input
        if (i == 1):
            if tok.type != 'TOKEN_SYMBOL':
                type = False
        i + 1
    assert type


def test_strict_rule():
    lexer = lex.TPTPLexer().lexer
    lexer.input('<TPTP_Test> :==')
    type = True
    i = 0
    while 1:
        tok = lexer.token()
        if not tok: break  # No more input
        if (i == 1):
            if tok.type != 'STRICT_SYMBOL':
                type = False
    assert type


def test_macro_rule():
    lexer = lex.TPTPLexer().lexer
    lexer.input('<TPTP_Test> :::')
    type = True
    i = 0
    while 1:
        tok = lexer.token()
        if not tok: break  # No more input
        if (i == 1):
            if tok.type != r'MACRO_SYMBOL':
                type = False
        i += 1
    assert type

def test_alternative_rule():
    lexer = lex.TPTPLexer().lexer
    lexer.input('|')
    type = True
    i = 0
    while 1:
        tok = lexer.token()
        if not tok: break  # No more input
        if tok.type != 'ALTERNATIVE_SYMBOL':
            type = False
        i += 1
    assert type
