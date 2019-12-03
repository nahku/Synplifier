import yacc
from enum import Enum
from collections import namedtuple

Node = namedtuple("Node", ["value", "productionProperty"])
#NodeTerminating = namedtuple("NodeTerminating", ["value", "productionProperty", "rule_number"]) #for checking if symbols are terminating
PrintListEntry = namedtuple("PrintListEntry", ["position", "line_list"])
INDENT_LENGTH = 30

class RuleType(Enum):
    GRAMMAR = 1
    TOKEN = 2
    STRICT = 3
    MACRO = 4

class NTNode():
    def __init__(self, value, productions_list, rule_type, comment_block, position):
        self.value = value
        self.productions_list = productions_list
        self.rule_type = rule_type
        self.comment_block = comment_block
        self.children = []
        self.position = position

    def add_children(self, children):
       self.children.append(children)

class TPTPTreeBuilder():

    def init_tree(self, start_symbol, start_rule):
        start = self.nodes_dictionary.get(Node(start_symbol,start_rule))
        self.build_tree_rek(start)

    def build_tree_rek(self, node):
        if len(node.children) == 0:
            self.search_productions_list_for_nt(node, node.productions_list)
            if len(node.children) != 0:
                for i in node.children:
                    if i != []:
                        for j in i:
                            self.build_tree_rek(j)
                    #else:
                        #node.children.remove(i)

    def build_tree(self, start_symbol):
        for key,value in self.nodes_dictionary.items():
            if key != start_symbol:
                self.find_nt_rule(key, value)

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

    def disable_rules(self, disable_rules_filename):
        with open(disable_rules_filename, "r") as infile:
            for i in infile:
                i = i.strip("\n")
                data = i.split(",")
                nt_name = data[0]
                rule_symbol = data[1]
                rule_type = None
                if(rule_symbol == "::="):
                    rule_type = RuleType.GRAMMAR
                elif(rule_symbol == "::-"):
                    rule_type = RuleType.TOKEN
                elif (rule_symbol == ":=="):
                    rule_type = RuleType.STRICT
                elif (rule_symbol == ":::"):
                    rule_type = RuleType.MACRO
                del data[0:2]
                data = list(map(int, data))
                data.sort(reverse=True)
                for index in data:
                    del self.nodes_dictionary.get(Node(nt_name,rule_type)).productions_list.list[index]

    def remove_non_terminating_symbols(self,start_node):
        terminating = set()
        tempTerminating = set()
        while 1:    #repeat until set of terminating symbols does not change anymore
            visited = set()
            self.find_non_terminating_symbols(start_node, tempTerminating, visited)
            if (terminating == tempTerminating):
                break
            else:
                terminating = tempTerminating
        visited = set()
        self.delete_non_terminating_productions(start_node,terminating,visited)
        self.delete_non_terminating_nodes(terminating)

    def delete_non_terminating_productions(self,node,terminating,visited):
        if (Node(node.value, node.rule_type) not in visited):
            visited.add(Node(node.value, node.rule_type))
            i = len(node.children)-1
            for children_list in reversed(node.children):
                notTerminating = False    #every non terminal symbol in children_list has to be terminating in oder for this production to be terminating
                for child in children_list:
                    self.delete_non_terminating_productions(child,terminating,visited)
                    if(child.value not in terminating):
                        notTerminating = True
                if(notTerminating):
                    del node.children[i]
                    del node.productions_list.list[i]
                i = i-1

    def delete_non_terminating_nodes(self,terminating):
        temporary_dictionary = {}
        for value in terminating:
            entry = self.nodes_dictionary.get(Node(value,RuleType.GRAMMAR),None)
            if(entry is not None):
                temporary_dictionary.update({Node(value,RuleType.GRAMMAR):entry})
            entry = self.nodes_dictionary.get(Node(value, RuleType.STRICT), None)
            if (entry is not None):
                temporary_dictionary.update({Node(value, RuleType.STRICT): entry})
            entry = self.nodes_dictionary.get(Node(value, RuleType.MACRO), None)
            if (entry is not None):
                temporary_dictionary.update({Node(value, RuleType.MACRO): entry})
            entry = self.nodes_dictionary.get(Node(value, RuleType.TOKEN), None)
            if (entry is not None):
                temporary_dictionary.update({Node(value, RuleType.TOKEN): entry})
        self.nodes_dictionary = temporary_dictionary

    def find_non_terminating_symbols(self,node,terminating,visited):
        if(Node(node.value,node.rule_type) not in visited):
            visited.add(Node(node.value,node.rule_type))
            for children_list in node.children:
                if(len(children_list) == 0):
                    terminating.add(node.value)
                else:
                    flag = True
                    #every non terminal child has to be terminating in order for the symbol to be terminating
                    for child in children_list:
                        self.find_non_terminating_symbols(child,terminating,visited)
                        if(not (child.value in terminating)):
                            flag = False
                    if(flag):
                        terminating.add(node.value)


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

    def print_rules_from_graph(self,start_node,visited):
        self.print_rule_from_nt_node(start_node)
        visited.update({Node(start_node.value, start_node.rule_type): start_node})
        for i in start_node.children:
            for j in i:
                if(Node(j.value,j.rule_type) not in visited.keys()):
                    self.print_rules_from_graph(j,visited)
                    visited.update({Node(j.value, j.rule_type): j})

    def print_ordered_rules_from_graph(self,start_node):
        visited = {}
        print_list = []
        print_list = self.create_print_list(start_node,visited,print_list)
        print_list.sort(key=lambda x: x[0])
        for tuple in print_list:
            for line in tuple.line_list:
                print(line)

    def create_print_list(self,start_node,visited,print_list):
        print_list = self.get_print_list(start_node, print_list)
        visited.update({Node(start_node.value, start_node.rule_type): start_node})
        for i in start_node.children:
            for j in i:
                if (Node(j.value, j.rule_type) not in visited.keys()):
                    print_list = self.create_print_list(j,visited, print_list)
                    visited.update({Node(j.value, j.rule_type): j})
        return print_list

    def get_print_list(self,node,print_list):
        print_list.append(PrintListEntry(node.position,[]))
        if (node.comment_block is not None):
            print_list[-1].line_list.extend(node.comment_block.list)
        rule_line = node.value
        rule_line = rule_line.ljust(INDENT_LENGTH) #uniform length of left side of rule
        if (node.rule_type == RuleType.GRAMMAR):
            rule_line += " ::= "
        elif (node.rule_type == RuleType.TOKEN):
            rule_line += " ::- "
        elif (node.rule_type == RuleType.STRICT):
            rule_line += " :== "
        elif (node.rule_type == RuleType.MACRO):
            rule_line += " ::: "
        rule_line += self.get_productions_list_string(node.productions_list)
        print_list[-1].line_list.append(rule_line)
        return print_list

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
                self.nodes_dictionary.update({Node(i.name, rule_type):NTNode(i.name,i.productions_list,rule_type,comment_block_buffer,i.position)})
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

    def get_production_string(self,production):
        production_string = ""
        for i in production.list:
            if(isinstance(i, yacc.PRODUCTION)):
                if (i.productionProperty == yacc.ProductionProperty.NONE):
                    production_string += self.get_production_string(i)
                elif(i.productionProperty == yacc.ProductionProperty.REPETITION):
                    production_string += "("
                    production_string += self.get_production_string(i)
                    production_string += ")"
                    production_string += "*"
                elif(i.productionProperty == yacc.ProductionProperty.OPTIONAL):
                    production_string += "["
                    production_string += self.get_production_string(i)
                    production_string += "]"
                elif (i.productionProperty == yacc.ProductionProperty.XOR):
                    production_string += "("
                    production_string += self.get_production_string(i)
                    production_string += ")"
            elif(isinstance(i, yacc.XOR_PRODUCTIONS_LIST)):
                production_string += self.get_xor_productions_list_string(i)
            elif (isinstance(i, yacc.PRODUCTION_ELEMENT)):
                production_string += self.get_production_element_string(i)
        return production_string

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

    def get_xor_productions_list_string(self,xor_productions_list):
        xor_productions_list_string = ""
        xor_productions_list_string += "("
        xor_productions_list_string += self.get_productions_list_string(xor_productions_list)
        xor_productions_list_string += ")"
        return xor_productions_list_string

    def print_xor_productions_list(self,xor_productions_list):
        self.print_wo_newline("(")
        self.print_productions_list(xor_productions_list)
        self.print_wo_newline(")")

    def get_production_element_string(self,production_element):
        production_element_string = ""
        if (production_element.productionProperty == yacc.ProductionProperty.NONE):
            production_element_string += self.get_symbol_string(production_element.name)
        elif (production_element.productionProperty == yacc.ProductionProperty.REPETITION):
            production_element_string += self.get_symbol_string(production_element.name)
            production_element_string += "*"
        elif (production_element.productionProperty == yacc.ProductionProperty.OPTIONAL):
            production_element_string += "["
            production_element_string += self.get_symbol_string(production_element.name)
            production_element_string += "]"
        elif (production_element.productionProperty == yacc.ProductionProperty.XOR):
            production_element_string += self.get_symbol_string(production_element.name)
            production_element_string += " | "
        return production_element_string

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

    def get_symbol_string(self,symbol):
        symbol_string = ""
        if isinstance(symbol,yacc.T_SYMBOL):
                if (symbol.property == yacc.ProductionProperty.NONE):
                    symbol_string += symbol.value
                elif (symbol.property == yacc.ProductionProperty.REPETITION):
                    symbol_string += symbol.value
                    symbol_string += "*"
                elif (symbol.property == yacc.ProductionProperty.OPTIONAL):
                    symbol_string += "["
                    symbol_string += symbol.value
                    symbol_string += "]"
                elif (symbol.property == yacc.ProductionProperty.XOR):
                    symbol_string += "("
                    symbol_string += symbol.value
                    symbol_string += ")"
        elif(isinstance(symbol,yacc.NT_SYMBOL)):
            symbol_string += symbol.value
        elif(isinstance(symbol,list)):
            symbol_string += symbol[0].value #only first because all list elements have the same name
        return symbol_string

    def print_symbol(self, symbol):
        if isinstance(symbol,yacc.T_SYMBOL):
                if (symbol.property == yacc.ProductionProperty.NONE):
                    self.print_wo_newline(symbol.value)
                elif (symbol.property == yacc.ProductionProperty.REPETITION):
                    self.print_wo_newline(symbol.value)
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

    def get_productions_list_string(self,productions_list):
        productions_list_string = ""
        length = len(productions_list.list)
        j = 1
        for i in productions_list.list:
            productions_list_string += self.get_production_string(i)
            if (j < length):
                productions_list_string += " | "
            j = j + 1
        return productions_list_string

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

    def __init__(self,filename,disable_rules_filnames):
        self.rules_test = []
        self.nodes_dictionary = {}
        self.parser = yacc.TPTPParser()
        rules_list = self.parser.run(filename)
        self.build_nodes_dictionary(rules_list)
        self.disable_rules(disable_rules_filnames)
        self.init_tree("<TPTP_file>",RuleType.GRAMMAR)
        self.remove_non_terminating_symbols(self.nodes_dictionary.get(Node("<TPTP_file>", RuleType.GRAMMAR)))
        #self.print_ordered_rules_from_graph(self.nodes_dictionary.get(Node("<TPTP_file>",RuleType.GRAMMAR)))
        #visited = {}
        #print_list = []
        #print_list = self.create_print_list(self.nodes_dictionary.get(Node("<TPTP_file>",RuleType.GRAMMAR)),visited,print_list)
        #print_list.sort(key=lambda x: x[0])
        #visited = {}
        #self.print_rules_from_graph(self.nodes_dictionary.get(Node("<TPTP_file>",RuleType.GRAMMAR)),visited)
        #self.print_rules_from_rules_list(rules_list)

        print("")