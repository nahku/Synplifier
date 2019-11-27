import yacc
from enum import Enum
from collections import namedtuple

Node = namedtuple("Node", ["value", "productionProperty"])

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

    def init_tree(self, start_symbol, start_rule):
        #self.treeBNF = Tree(self.nodes_dictionary.pop(start_symbol))
        start = self.nodes_dictionary.get(Node(start_symbol,start_rule))
        self.build_tree_rek(start)
        #self.print_tree(self.nodes_dictionary.get(start_symbol), 0)

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
        #self.print_tree(self.nodes_dictionary.get(start_symbol),0)

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
                    childrenNode = self.find_nt_key(i, i.name.value)
                    for j in childrenNode:
                        children.append(j) #all children of production
                    i.name = childrenNode

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

    def print_rules_from_rules_list(self,rules_list):
        for i in rules_list.list:
            if(isinstance(i,yacc.MACRO_EXPRESSION)|isinstance(i,yacc.STRICT_EXPRESSION)|isinstance(i,yacc.GRAMMAR_EXPRESSION)|isinstance(i,yacc.TOKEN_EXPRESSION)):
                self.print_expression(i)
                print("")
            else:
                self.print_comment_block(i)
            #self.print_expression(rules_list.list[2])

    def print_rules_from_graph(self,node,visited):
        #visited = {}
        self.print_rule_from_nt_node(node)
        visited.update({Node(node.value, node.rule_type): node})
        for i in node.children:
            for j in i:
                if(Node(j.value,j.rule_type) not in visited.keys()):
                    self.print_rules_from_graph(j,visited)
                    visited.update({Node(j.value, j.rule_type): j})

    def print_rule_from_nt_node(self, node):
        if(node.comment_block is not None):
            self.print_comment_block(node.comment_block)
        self.print_wo_newline(node.value)
        if(node.rule_type == RuleType.GRAMMAR):
            self.print_wo_newline(" ::= ")
        elif(node.rule_type == RuleType.TOKEN):
            self.print_wo_newline(" ::- ")
        elif(node.rule_type == RuleType.STRICT):
            self.print_wo_newline(" :== ")
        elif(node.rule_type == RuleType.MACRO):
            self.print_wo_newline(" ::: ")
        self.print_productions_list(node.productions_list)
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
            if key == Node(nt_name,RuleType.GRAMMAR) or key == Node(nt_name,RuleType.MACRO) \
                    or key == Node(nt_name,RuleType.STRICT) or key == Node(nt_name,RuleType.TOKEN):
                node = self.nodes_dictionary.get(key)
                children.append(value)
        return children

    def build_nodes_dictionary(self,rules_list):

        comment_block_buffer = None
        index = 0
        for i in rules_list.list:
            if isinstance(i,yacc.COMMENT_BLOCK):
                comment_block_buffer_list = self.split_comment_block_by_top_of_page(i)
                if(len(comment_block_buffer_list) == 1):
                    comment_block_buffer = comment_block_buffer_list[0]
                elif(index == 0):
                    comment_block_buffer = yacc.COMMENT_BLOCK(comment_block_buffer_list[0].list + comment_block_buffer_list[1].list)
                else:
                    rule_type = self.find_rule_type_for_expression(rules_list.list[index-1])
                    if(self.nodes_dictionary.get(Node(rules_list.list[index-1].name,rule_type)).comment_block is None):
                        rules_list.list[index-1].comment_block = comment_block_buffer_list[0]
                    else:
                        rules_list.list[index-1].comment_block.list = rules_list.list[index-1].comment_block.list + comment_block_buffer_list[0]
                    comment_block_buffer = comment_block_buffer_list[1]
            else:
                rule_type = self.find_rule_type_for_expression(i)
                #self.nodes_dictionary.update({i.name:NTNode(i.name,i.productions_list,rule_type,comment_block_buffer)})
                self.nodes_dictionary.update({Node(i.name, rule_type):NTNode(i.name,i.productions_list,rule_type,comment_block_buffer)})
                comment_block_buffer = None
            index = index+1

    def find_rule_type_for_expression(self, expression):

        if isinstance(expression, yacc.GRAMMAR_EXPRESSION):
            rule_type = RuleType.GRAMMAR
        elif isinstance(expression, yacc.TOKEN_EXPRESSION):
            rule_type = RuleType.TOKEN
        elif isinstance(expression, yacc.MACRO_EXPRESSION):
            rule_type = RuleType.MACRO
        elif isinstance(expression, yacc.STRICT_EXPRESSION):
            rule_type = RuleType.STRICT
        return rule_type

    #todo commentblock just consisting of 1 line with top of page
    def split_comment_block_by_top_of_page(self,comment_block):
        comment_block_list = [comment_block]
        i = 0
        for line in comment_block.list:
            if(line == "%----Top of Page---------------------------------------------------------------"):
                list_end_index = len(comment_block.list)-1
                del comment_block.list[i]
                if((i is not 0) and (i is not list_end_index)):
                    comment_block_list = [yacc.COMMENT_BLOCK(comment_block.list[0:i]), yacc.COMMENT_BLOCK(comment_block.list[i:len(comment_block.list)])]
                else:
                    comment_block_list = [comment_block]

            i = i + 1
        return comment_block_list

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
            self.print_wo_newline(" |")

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
            self.print_wo_newline(symbol[0].value)  #only first because all list elements have the same name
            self.print_wo_newline("")

    def print_productions_list(self,productions_list):
        length = len(productions_list.list)
        j = 1
        for i in productions_list.list:
            self.print_production(i)
            if(j<length):
                self.print_wo_newline(" | ")
            j = j + 1

    def print_comment_block(self,comment_block):
        for i in comment_block.list:
            print(i)

    def print_wo_newline(self,string):
        print(string, end = '')

    def __init__(self,filename):
        self.rules_test = []
        self.nodes_dictionary = {}
        self.parser = yacc.TPTPParser()
        rules_list = self.parser.run(filename)
        self.build_nodes_dictionary(rules_list)
        self.init_tree("<name>",RuleType.GRAMMAR)
        visited = {}
        self.print_rules_from_graph(self.nodes_dictionary.get(Node("<name>",RuleType.GRAMMAR)),visited)
        #self.print_rules_from_rules_list(rules_list)
        print("")