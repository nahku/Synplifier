import ply.yacc as yacc
from enum import Enum
import lexer
import Input


class ProductionProperty(Enum):
    NONE = 1
    REPETITION = 2
    OPTIONAL = 3

class T_SYMBOL:
    def __init__(self, value, property = ProductionProperty.NONE):
        self.value = value
        self.property = property

class NT_SYMBOL:
    def __init__(self, value):
        self.value = value

class GRAMMAR_EXPRESSION:
    def __init__(self, name, productions_list):
        self.name = name
        self.productions_list = productions_list
        self.position = None

class TOKEN_EXPRESSION:
    def __init__(self, name, productions_list):
        self.name = name
        self.productions_list = productions_list
        self.position = None

class STRICT_EXPRESSION:
    def __init__(self, name, productions_list):
        self.name = name
        self.productions_list = productions_list
        self.position = None

class MACRO_EXPRESSION:
    def __init__(self, name, productions_list):
        self.name = name
        self.productions_list = productions_list
        self.position = None

class GRAMMAR_LIST:
    def __init__(self, grammar_list):
        self.list = grammar_list

class PRODUCTIONS_LIST:
  def __init__(self, productions_list):
    self.list = productions_list

class XOR_PRODUCTIONS_LIST:
    def __init__(self, xor_productions_list):
        self.list = xor_productions_list

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

class TPTPParser():

    #production rules

    def p_grammar_list(self,p):
        """
        grammar_list : comment_block
                    |  grammar_expression
                    |  token_expression
                    |  strict_expression
                    |  macro_expression
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

    def p_comment_block(self,p):
        """
        comment_block : COMMENT
                    |   comment_block COMMENT
        """

        if len(p) == 2:
            p[0] = COMMENT_BLOCK([p[1]])
        elif len(p) == 3:
            p[1].list.append(p[2])
            p[0] = p[1]

    def p_grammar_expression(self,p):
        """
        grammar_expression : LGRAMMAR_EXPRESSION productions_list
                            | LGRAMMAR_EXPRESSION

        """
        if len(p) == 3:
            p[0] = GRAMMAR_EXPRESSION(p[1],p[2])
        elif len(p) == 2: #for case <null> ::=
            p[0] = GRAMMAR_EXPRESSION(p[1], PRODUCTIONS_LIST([PRODUCTION([PRODUCTION_ELEMENT(T_SYMBOL(""))])]))

    def p_token_expression(self,p):
        """
        token_expression : LTOKEN_EXPRESSION productions_list
        """
        p[0] = TOKEN_EXPRESSION(p[1],p[2])

    def p_strict_expression(self,p):
        """
        strict_expression : LSTRICT_EXPRESSION productions_list
        """
        p[0] = STRICT_EXPRESSION(p[1],p[2])

    def p_macro_expression(self,p):
        """
        macro_expression : LMACRO_EXPRESSION productions_list
        """
        p[0] = MACRO_EXPRESSION(p[1],p[2])

    def p_productions_list(self,p):
        """
        productions_list : production
                        | productions_list ALTERNATIVE_SYMBOL production
        """
        if len(p) == 2:
            p[0] = PRODUCTIONS_LIST([p[1]])
        elif len(p) == 4:
            p[1].list.append(p[3])
            p[0] = p[1]

    def p_xor_productions_list(self,p):
        """
        xor_productions_list : production
                        | xor_productions_list ALTERNATIVE_SYMBOL production
        """
        if len(p) == 2:
            p[0] = XOR_PRODUCTIONS_LIST([p[1]])
        elif len(p) == 4:
            p[1].list.append(p[3])
            p[0] = p[1]

    def p_t_symbol_production(self,p):
        """
            t_symbol_production : OPEN_SQUARE_BRACKET T_SYMBOL CLOSE_SQUARE_BRACKET
                             |    OPEN_SQUARE_BRACKET REPETITION_SYMBOL CLOSE_SQUARE_BRACKET
                             |    OPEN_SQUARE_BRACKET ALTERNATIVE_SYMBOL CLOSE_SQUARE_BRACKET
                             |    T_SYMBOL
            """
        if len(p) == 2:
            p[0] = T_SYMBOL(p[1])
        elif len(p) == 4:
                p[0] = T_SYMBOL(p[2], ProductionProperty.OPTIONAL)

    def p_production_element(self,p):
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
            p[0] = PRODUCTION([], ProductionProperty.OPTIONAL)  #evt. Problem wegen leerer Liste
        elif len(p) == 3:  # NT_SYMBOL REPETITION_SYMBOL|t_symbol_production REPETITION_SYMBOL
            if (type(p[1]) is T_SYMBOL):
                p[0] = PRODUCTION_ELEMENT(p[1], ProductionProperty.REPETITION)
            else:
                p[0] = PRODUCTION_ELEMENT(NT_SYMBOL(p[1]), ProductionProperty.REPETITION)
        elif len(p) == 4 and p[1] == '[': #OPEN_SQUARE_BRACKET NT_SYMBOL CLOSE_SQUARE_BRACKET
            p[0] = PRODUCTION_ELEMENT(NT_SYMBOL(p[2]), ProductionProperty.OPTIONAL)

    def p_production(self,p):
        #missing optional production
        """
        production : production_element
                |    production production_element
                |    OPEN_PARENTHESIS xor_productions_list CLOSE_PARENTHESIS
                |    OPEN_PARENTHESIS production CLOSE_PARENTHESIS
                |    production OPEN_PARENTHESIS production CLOSE_PARENTHESIS
                |    production OPEN_PARENTHESIS xor_productions_list CLOSE_PARENTHESIS
                |    OPEN_PARENTHESIS production CLOSE_PARENTHESIS production
                |    OPEN_PARENTHESIS xor_productions_list CLOSE_PARENTHESIS production
                |    OPEN_PARENTHESIS production CLOSE_PARENTHESIS REPETITION_SYMBOL
                |    production OPEN_PARENTHESIS production CLOSE_PARENTHESIS REPETITION_SYMBOL


        """
        #|    production ALTERNATIVE_SYMBOL OPEN_PARENTHESIS production_element CLOSE_PARENTHESIS
        if len(p) == 2:
           p[0] = PRODUCTION([p[1]])
        elif len(p) == 3:
            p[1].list.append(p[2])
            p[0] = p[1]
        #elif len(p) == 4 and p[2] == '|':
         #   p[1].productionProperty = ProductionProperty.XOR
          #  p[1].list.append(p[3])
           # p[0] = p[1]
        elif len(p) == 4 and type(p[2]) is PRODUCTION:
            p[2].list.insert(0, PRODUCTION_ELEMENT(T_SYMBOL('(')))
            p[2].list.append(PRODUCTION_ELEMENT(T_SYMBOL(')')))
            p[0] = p[2]
        elif len(p) == 4 and p[1] == '(':
            p[0] = PRODUCTION([p[2]])
        elif len(p) == 5 and p[4] == '*':
            p[2].productionProperty = ProductionProperty.REPETITION
            p[0] = PRODUCTION([p[2]])
        elif len(p) == 5 and p[3] == ')' and isinstance(p[2],PRODUCTION):
            p[2].list.insert(0, PRODUCTION_ELEMENT(T_SYMBOL('(')))
            p[2].list.append(PRODUCTION_ELEMENT(T_SYMBOL(')')))
            p[4].list.insert(0,PRODUCTION(p[2]))
            p[0] = p[4]
        elif len(p) == 5 and p[3] == ')' and isinstance(p[2],XOR_PRODUCTIONS_LIST):
            p[4].list.insert(0,PRODUCTION([p[2]]))
            p[0] = p[4]
        elif len(p) == 5 and p[4] == ')' and isinstance(p[3], PRODUCTION):
            p[3].list.insert(0, PRODUCTION_ELEMENT(T_SYMBOL('(')))
            p[3].list.append(PRODUCTION_ELEMENT(T_SYMBOL(')')))
            p[1].list.append(p[3])
            p[0] = p[1]
        elif len(p) == 5 and p[4] == ')' and isinstance(p[3], XOR_PRODUCTIONS_LIST):
            p[1].list.append(PRODUCTION([p[3]]))
            p[0] = p[1]
        elif len(p) == 5:
            p[2].productionProperty = ProductionProperty.REPETITION
            p[0] = PRODUCTION([p[2]])
        elif len(p) == 6 and p[5] == '*':
            p[3].productionProperty = ProductionProperty.REPETITION
            p[1].list.append(PRODUCTION([p[3]]))
            p[0] = p[1]

    def p_error(self,t):
        print("Syntax error at '%s'" % t.value)

    def disambigue_square_brackets(self, rules_list: GRAMMAR_LIST) -> GRAMMAR_LIST:
        """Replaces ProductionProperty OPTIONAL by the terminal symbols
         open and closing square bracket for GRAMMAR and STRICT Expressions.

        :param rules_list: List of all rules from the TPTP grammar file.
        :return: List of all rules from TPTP grammar file with correct square bracket interpretation.
        """
        for production_rule in rules_list.list:
            if((isinstance(production_rule,GRAMMAR_EXPRESSION)) or (isinstance(production_rule,STRICT_EXPRESSION))):
                self.replace_optional_square_brackets_by_terminal(production_rule)
        return rules_list

    def replace_optional_square_brackets_by_terminal(self,rule: GRAMMAR_EXPRESSION):
        """Replaces ProductionProperty OPTIONAL by the terminal square brackets for all productions in a GRAMMAR_EXPRESSION.

        :param rule: GRAMMAR_EXPRESSION.
        """
        for production in rule.productions_list.list:
            self.replace_square_brackets_in_production(production)

    def replace_square_brackets_in_production(self, production: PRODUCTION):
        """Replaces ProductionProperty OPTIONAL by the terminal square brackets in a production recursively.

        :param production: Production, where ProductionProperty OPTIONAL is to be replaced by terminal square brackets
        """
        if(production.productionProperty == ProductionProperty.OPTIONAL):
            production.list.insert(0,PRODUCTION_ELEMENT(T_SYMBOL("[")))
            production.list.append(PRODUCTION_ELEMENT(T_SYMBOL("]")))
            production.productionProperty = ProductionProperty.NONE

        i=0
        for element in production.list:
            if(isinstance(element,PRODUCTION)):
                self.replace_square_brackets_in_production(element)
            elif(isinstance(element,PRODUCTION_ELEMENT) and (element.productionProperty == ProductionProperty.OPTIONAL)):
                element.productionProperty = ProductionProperty.NONE
                production.list[i] = PRODUCTION([PRODUCTION_ELEMENT(T_SYMBOL("[")),element,PRODUCTION_ELEMENT(T_SYMBOL("]"))])
            i = i + 1

    def number_rules(self,rules_list: GRAMMAR_LIST) -> GRAMMAR_LIST:
        """Number rules by occurence in TPTP gramar file.

        :param rules_list:  List of all rules from the TPTP grammar file.
        :return: List of all rules from TPTP grammar file numbered by occurence.
        """
        i = 0
        for element in rules_list.list:
            if(not isinstance(element,COMMENT_BLOCK)):
                element.position = i
                i = i + 1
        return rules_list

    def run(self,filename: str) -> GRAMMAR_LIST:
        """Run parser on TPTP grammar file.

        :param filename: Filename of the TPTP grammar file.
        :return: Grammar_List contatining the representation of the TPTP grammar.
        """
        result = self.parser.parse(Input.import_tptp_file(filename))
        result = self.number_rules(result)
        result = self.disambigue_square_brackets(result)
        return result

    def __init__(self):
        self.tokens = lexer.TPTPLexer.tokens
        self.lexer = lexer.TPTPLexer()
        self.parser = yacc.yacc(module=self)