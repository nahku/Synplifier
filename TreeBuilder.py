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
        self.children = []

    def add_children(self, children):
       self.children.append(children)

class Tree():
    def __init__(self, start):
        self.start = start
        self.children = []

    def add_children(self, children):
        self.children.append(children)

class TPTPTreeBuilder():

    def init_tree(self, start_symbol):
        #self.treeBNF = Tree(self.nodes_dictionary.pop(start_symbol))
        start = self.nodes_dictionary.get(start_symbol)
        self.build_tree_rek(start)
        self.print_tree(self.nodes_dictionary.get(start_symbol), 0)

    def build_tree_rek(self, node):
        #children = self.search_productions_list_for_nt(node, symbol)
        if len(node.children) == 0:
            self.search_productions_list_for_nt(node, node.productions_list)
            #self.print_tree(self.nodes_dictionary.get("<TPTP_file>"), 0)
            if len(node.children) != 0:
                for i in node.children:
                #if node.children != []:
                #node.add_children(children)
                #print(i.value)
                    if i != []:
                        for j in i:
                            self.build_tree_rek(j)
                    else:
                        node.children.remove(i)


    def build_tree(self, start_symbol):

        for key,value in self.nodes_dictionary.items():
            if key != start_symbol:
                self.find_nt_rule(key, value)

        #self.treeBNF = self.nodes_dictionary.get(start_symbol)
        self.print_tree(self.nodes_dictionary.get(start_symbol),0)

    def search_productions_list(self,productions_list, nt_name):
        for i in productions_list.list:
            if self.search_production(i,nt_name):
               return True

    def search_productions_list_for_nt(self, node, productions_list):
        for i in productions_list.list:
            self.search_production_for_nt(node, i)


    def search_production_for_nt(self, node, production):
        children = []
        for i in production.list:
            if (isinstance(i, yacc.PRODUCTION)):
                self.search_production_for_nt(node, i)
            elif (isinstance(i, yacc.XOR_PRODUCTIONS_LIST)):
                self.search_productions_list_for_nt(node, i)
            elif (isinstance(i, yacc.PRODUCTION_ELEMENT)):
                if not isinstance(i.name, yacc.T_SYMBOL):
                    childrenNote = self.find_nt_key(i, i.name.value)
                    for j in childrenNote:
                        children.append(j) #all children of production
                    i.name = childrenNote

        node.children.append(children)

    def search_production(self, production, nt_name):
        for i in production.list:
            if (isinstance(i, yacc.PRODUCTION)):
                if self.search_production(i, nt_name):
                    return True
            elif (isinstance(i, yacc.XOR_PRODUCTIONS_LIST)):
                self.search_productions_list(i, nt_name)
            elif (isinstance(i, yacc.PRODUCTION_ELEMENT)):
                if not isinstance(i.name, yacc.T_SYMBOL):
                    if i.name.value == nt_name:
                        return True

        return False

    def print_tree(self, node, level):
        if level == 0:
            self.print_tree_nt(node.value, level)
        if len(node.children) > 0:
            if len(node.children[0]) >= 0:
                for i in node.children:
                    print("")
                    for j in i:
                        self.print_tree_nt(j.value, level+1)
                        self.print_tree(j, level+2)

    def print_tree_nt(self, nt_name, level):
        for i in range(0,level):
            print("  ",end = "")

        print(nt_name, end = "")

    def print_rules_from_graph(self,node,visited):
        self.print_rule_from_nt_node(node)
        visited.add()
        #for i in node.children todo
        print("")

    def find_nt_rule(self, key, value):
        for i in self.nodes_dictionary.values():
            if self.search_productions_list(i.productions_list, key):
                if i == value:
                    print(i.value)
                else:
                    i.add_children(value)

    def find_nt_key(self, node, nt_name):
        children = []
        for key, value in self.nodes_dictionary.items():
            if key == nt_name:
                node = self.nodes_dictionary.get(key)
                children.append(value)
        return children

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

    def print_rule_from_nt_node(self, node):
        self.print_wo_newline(node.name)
        if(node.rule_type == RuleType.GRAMMAR):
            self.print_wo_newline(" ::= ")
        elif(node.rule_type == RuleType.TOKEN):
            self.print_wo_newline(" ::- ")
        elif(node.rule_type == RuleType.STRICT):
            self.print_wo_newline(" :== ")
        elif(node.rule_type == RuleType.MACRO):
            self.print_wo_newline(" ::: ")
        self.print_productions_list(node.productions_list)

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

    # def print_symbol(self,symbol):
    #     if isinstance(symbol,yacc.T_SYMBOL):
    #         if (symbol.property == yacc.ProductionProperty.NONE):
    #             if(len(symbol.value) < 2):
    #                 self.print_wo_newline("[")
    #                 self.print_wo_newline(symbol.value)
    #                 self.print_wo_newline("]")
    #             else:
    #                 self.print_wo_newline(symbol.value)
    #         elif (symbol.property == yacc.ProductionProperty.REPETITION):
    #             if (len(symbol.value) < 2):
    #                 self.print_wo_newline("[")
    #                 self.print_wo_newline(symbol.value)
    #                 self.print_wo_newline("]")
    #             else:
    #                 self.print_wo_newline(symbol.value)
    #             self.print_wo_newline("*")
    #         elif (symbol.property == yacc.ProductionProperty.OPTIONAL):
    #             self.print_wo_newline("[")
    #             self.print_wo_newline(symbol.value)
    #             self.print_wo_newline("]")
    #         elif (symbol.property == yacc.ProductionProperty.XOR):
    #             self.print_wo_newline("(")
    #             if (len(symbol.value) < 2):
    #                 self.print_wo_newline("[")
    #                 self.print_wo_newline(symbol.value)
    #                 self.print_wo_newline("]")
    #             else:
    #                 self.print_wo_newline(symbol.value)
    #             self.print_wo_newline(")")
    #     else:
    #         self.print_wo_newline(symbol.value)

    def print_symbol(self, symbol):
        if isinstance(symbol,yacc.T_SYMBOL):
                if (symbol.property == yacc.ProductionProperty.NONE):
                    self.print_wo_newline(symbol.value)
                elif (symbol.property == yacc.ProductionProperty.REPETITION):
                    self.print_wo_newline("*")
                elif (symbol.property == yacc.ProductionProperty.OPTIONAL):
                    self.print_wo_newline("[")
                    self.print_wo_newline(symbol.value)
                    self.print_wo_newline("]")
                elif (symbol.property == yacc.ProductionProperty.XOR):
                    self.print_wo_newline("(")
                    self.print_wo_newline(symbol.value)
                    self.print_wo_newline(")")
        elif(isinstance(symbol,yacc.NT_SYMBOL)):
            self.print_wo_newline(symbol.value)
        elif(isinstance(symbol,list)):
            self.print_wo_newline(symbol[0].value)
            self.print_wo_newline(" ")

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
        #self.input_tree = None
        self.treeBNF = None
        self.parser = yacc.TPTPParser()
        rules_list = self.parser.run(filename)
        #rules_list = self.parser.run('TPTP_Test.txt')
        #self.build_tree(rules_list)
        self.build_nodes_dictionary(rules_list)
        #self.find_nt_rule("<annotated_formula>")
        #self.build_tree("<TPTP_file>")
        #self.init_tree("<TPTP_file>")
        for i in rules_list.list:
            if(isinstance(i,yacc.MACRO_EXPRESSION)|isinstance(i,yacc.STRICT_EXPRESSION)|isinstance(i,yacc.GRAMMAR_EXPRESSION)|isinstance(i,yacc.TOKEN_EXPRESSION)):
                self.print_expression(i)
                print("")
            else:
                self.print_comment_block(i)
        #self.print_expression(rules_list.list[2])
        print("")