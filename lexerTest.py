import unittest
import lexer

class TestExpressions(unittest.TestCase):
    def test_comment(self):
        lexer.lexer()
        lexer.lex.input(lexer.import_tptp_file('TestCaseComment.txt'))
        type = True
        while 1:
            tok = lexer.lex.token()
            if not tok: break  # No more input
            if tok.type != 'COMMENT':
                type = False
        self.assertEqual(True, type)


if __name__ == '__main__':
    unittest.main()
