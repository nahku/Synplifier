import yacc
from enum import Enum

class RuleType(Enum):
    GRAMMAR = 1
    TOKEN = 2
    STRICT = 3
    MACRO = 4

class NTNode():
    def __init__(self, value, productions_list, rule_type, comment_block):
        self.value = value
        self.productions_list = productions_list
        self.rule_type = rule_type
        self.comment_block = comment_block

class TPTPTreeBuilder():

    def build_tree(self):
        tree = self.nodes_dictionary.pop("<TPTP_file>")
        #for i in tree.productions_list.list:
         #   BLUB = self.nodes_dictionary.pop(i,None)


        print(tree)
            #if(not isinstance(i,yacc.COMMENT_BLOCK)):
             #   self.rules_test.append(self.create_node_from_expression(i))

    #def find_nt_rule

    def build_nodes_dictionary(self,rules_list):

        puffer_comment_block = None
        for i in rules_list.list:
            if isinstance(i,yacc.COMMENT_BLOCK):
                puffer_comment_block = i
            else:
                if isinstance(i,yacc.GRAMMAR_EXPRESSION):
                    rule_type = RuleType.GRAMMAR
                elif isinstance(i, yacc.TOKEN_EXPRESSION):
                    rule_type = RuleType.TOKEN
                elif isinstance(i, yacc.MACRO_EXPRESSION):
                    rule_type = RuleType.MACRO
                elif isinstance(i, yacc.STRICT_EXPRESSION):
                    rule_type = RuleType.STRICT

                self.nodes_dictionary.update({i.name:NTNode(i.name,i.productions_list,rule_type,puffer_comment_block)})
                puffer_comment_block = None

    def create_node_from_expression(self, expression):
        return NTNode(None, expression.name,expression.productions_list)

    def print_expression(self, expression):
        self.print_wo_newline(expression.name)
        if(isinstance(expression,yacc.GRAMMAR_EXPRESSION)):
            self.print_wo_newline(" ::= ")
        elif(isinstance(expression,yacc.TOKEN_EXPRESSION)):
            self.print_wo_newline(" ::- ")
        elif (isinstance(expression, yacc.STRICT_EXPRESSION)):
            self.print_wo_newline(" :== ")
        elif (isinstance(expression, yacc.MACRO_EXPRESSION)):
            self.print_wo_newline(" ::: ")
        self.print_productions_list(expression.productions_list)

    def print_production(self, production):
        for i in production.list:
            if(isinstance(i, yacc.PRODUCTION)):
                if (i.productionProperty == yacc.ProductionProperty.NONE):
                    self.print_production(i)
                elif(i.productionProperty == yacc.ProductionProperty.REPETITION):
                    self.print_wo_newline("(")
                    self.print_production(i)
                    self.print_wo_newline(")")
                    self.print_wo_newline("*")
                elif(i.productionProperty == yacc.ProductionProperty.OPTIONAL):
                    self.print_wo_newline("[")
                    self.print_production(i)
                    self.print_wo_newline("]")
                elif (i.productionProperty == yacc.ProductionProperty.XOR):
                    self.print_wo_newline("(")
                    self.print_production(i)
                    self.print_wo_newline(")")
            elif(isinstance(i, yacc.XOR_PRODUCTIONS_LIST)):
                self.print_xor_productions_list(i)
            elif (isinstance(i, yacc.PRODUCTION_ELEMENT)):
                self.print_production_element(i)

    def print_xor_productions_list(self,xor_productions_list):
        self.print_wo_newline("(")
        self.print_productions_list(xor_productions_list)
        self.print_wo_newline(")")

    def print_production_element(self,production_element):
        if (production_element.productionProperty == yacc.ProductionProperty.NONE):
            self.print_symbol(production_element.name)
        elif (production_element.productionProperty == yacc.ProductionProperty.REPETITION):
            self.print_symbol(production_element.name)
            self.print_wo_newline("*")
        elif (production_element.productionProperty == yacc.ProductionProperty.OPTIONAL):
            self.print_wo_newline("[")
            self.print_symbol(production_element.name)
            self.print_wo_newline("]")
        elif (production_element.productionProperty == yacc.ProductionProperty.XOR):
            self.print_symbol(production_element.name)
            self.print_wo_newline("|")

    def print_symbol(self,symbol):
        if isinstance(symbol,yacc.T_SYMBOL):
            if (symbol.property == yacc.ProductionProperty.NONE):
                if(len(symbol.value) < 2):
                    self.print_wo_newline("[")
                    self.print_wo_newline(symbol.value)
                    self.print_wo_newline("]")
                else:
                    self.print_wo_newline(symbol.value)
            elif (symbol.property == yacc.ProductionProperty.REPETITION):
                if (len(symbol.value) < 2):
                    self.print_wo_newline("[")
                    self.print_wo_newline(symbol.value)
                    self.print_wo_newline("]")
                else:
                    self.print_wo_newline(symbol.value)
                self.print_wo_newline("*")
            elif (symbol.property == yacc.ProductionProperty.OPTIONAL):
                self.print_wo_newline("[")
                self.print_wo_newline(symbol.value)
                self.print_wo_newline("]")
            elif (symbol.property == yacc.ProductionProperty.XOR):
                self.print_wo_newline("(")
                if (len(symbol.value) < 2):
                    self.print_wo_newline("[")
                    self.print_wo_newline(symbol.value)
                    self.print_wo_newline("]")
                else:
                    self.print_wo_newline(symbol.value)
                self.print_wo_newline(")")
        else:
            self.print_wo_newline(symbol.value)

    def print_productions_list(self,productions_list):
        length = len(productions_list.list)
        j = 1
        for i in productions_list.list:
            self.print_production(i)
            if(j<length):
                self.print_wo_newline("| ")
            j = j + 1

    def print_comment_block(self,comment_block):
        for i in comment_block.list:
            print(i)

    def print_wo_newline(self,string):
        print(string, end = '')

    def __init__(self,filename):
        self.rules_test = []
        self.nodes_dictionary = {}
        self.input_tree = None
        self.parser = yacc.TPTPParser()
        rules_list = self.parser.run('TPTP_BNF_NEW.txt')
        #self.build_tree(rules_list)
        self.build_nodes_dictionary(rules_list)
        self.build_tree()
        for i in rules_list.list:
            if(isinstance(i,yacc.MACRO_EXPRESSION)|isinstance(i,yacc.STRICT_EXPRESSION)|isinstance(i,yacc.GRAMMAR_EXPRESSION)|isinstance(i,yacc.TOKEN_EXPRESSION)):
                self.print_expression(i)
                print("")
            else:
                self.print_comment_block(i)
        #self.print_expression(rules_list.list[2])
        print("")