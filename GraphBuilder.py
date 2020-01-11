import yacc
import InputOutput
from enum import Enum
from collections import namedtuple

Node = namedtuple("Node", ["value", "productionProperty"])


class RuleType(Enum):
    GRAMMAR = 1
    TOKEN = 2
    STRICT = 3
    MACRO = 4

class NTNode():
    def __init__(self, value: str, productions_list: yacc.PRODUCTIONS_LIST, rule_type: RuleType, comment_block: yacc.COMMENT_BLOCK, position: int):
        """Creates an NTNode.

        :param value: non-terminal symbol name.
        :param productions_list: PRODUCTIONS_LIST of productions that are specified in the production rules.
        :param rule_type: RuleType of the production in that the non-terminal symbol is used.
        :param comment_block: COMMENT_BLOCK that is associated with the production of the non-terminal symbol.
        :param position: Position of the production in the input file.
        """
        self.value = value
        self.productions_list = productions_list
        self.rule_type = rule_type
        self.comment_block = comment_block
        self.children = []
        self.position = position

    def add_children(self, children: list):
       """ Add children to children list of NTNode object.

       :param children: List of children that should be added to NTNode object.
       """
       self.children.append(children)

class TPTPGraphBuilder():

    def init_tree(self, start_symbol: str):
        """Initialise the TPTP grammar graph.

        :param start_symbol: value of the non-terminal start symbol
        """
        start_nodes = []

        #for ruleType in RuleType:
        #    start = self.nodes_dictionary.get(Node(start_symbol,ruleType))
        #    if start is not None:
        #        start_nodes.append(start)
        productions_list = yacc.PRODUCTIONS_LIST([yacc.PRODUCTION([yacc.PRODUCTION_ELEMENT(yacc.NT_SYMBOL(start_symbol))])])
        #for node in start_nodes:
        #    productions_list.list.append(yacc.PRODUCTION([yacc.PRODUCTION_ELEMENT(node.value)]))
        new_start_node = NTNode("<start_symbol>", productions_list,RuleType.GRAMMAR,yacc.COMMENT_BLOCK([]),-1)
        self.nodes_dictionary[Node(new_start_node.value,new_start_node.rule_type)] = new_start_node
        self.build_graph_rek(new_start_node)

    def build_graph_rek(self, start_node: Node):
        """Build the TPTP graph recursively.

        :param start_node: Start Node from which the TPTP grammar graph should be produced.
        """
        if len(start_node.children) == 0:
            self.search_productions_list_for_nt(start_node, start_node.productions_list)
            if len(start_node.children) != 0:
                for i in start_node.children:
                    if i != []:
                        for j in i:
                            self.build_graph_rek(j)
                    #else:
                        #node.children.remove(i)

    #def build_tree(self, start_symbol):
    #    for key,value in self.nodes_dictionary.items():
    #        if key != start_symbol:
    #            self.find_nt_rule(key, value)

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

    def disable_rules(self, disable_rules_string: str, start_symbol: str):
        """Disables rules specified in the control file from the TPTP grammar graph.

        :param disable_rules_filename: Filename of the control file.
        """
        for i in disable_rules_string.splitlines():
            #i = i.strip("\n")
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
                del self.nodes_dictionary.get(Node(nt_name, rule_type)).children[index]

        self.init_tree(start_symbol)
        self.remove_non_terminating_symbols(self.nodes_dictionary.get(Node('<start_symbol>', RuleType.GRAMMAR)))


    def remove_non_terminating_symbols(self,start_node: NTNode):
        """Removes non-terminating symbols from the TPTP grammar graph recursively.

        :param start_node: Start node of the TPTP grammar graph.
        """
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

    def delete_non_terminating_productions(self,node: NTNode, terminating: set, visited: set):
        """Removes productions, that contain non-terminating symbols from the TPTP grammar graph recursively.

        :param node: The node, from which removing non-terminating productions is started.
        :param terminating: Set of names (strings) of known terminating symbols.
        :param visited: Set of Nodes that are already visited.
        """
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

    def delete_non_terminating_nodes(self,terminating: set):
        """Removes non-terminating nodes from TPTP grammar graph.

        :param terminating: Set of known terminating symbol names (strings).
        """

        #todo: maybe replace dictionary with set
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

    def find_non_terminating_symbols(self, node: NTNode, terminating: set, visited: set):
        """Find non-terminating symbols in TPTP grammar graph recursively.

        :param node: NTNode in TPTP grammar graph from which fining non terminal_symbols is started.
        :param terminating: Set of the names (strings) of known terminating symbols.
        :param visited: Set of already visited Nodes.
        """

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

    #def create_node_from_expression(self, expression):
    #    return NTNode(None, expression.name,expression.productions_list)

    def run(self,filename: str):
        rules_list = self.parser.run(filename)
        self.build_nodes_dictionary(rules_list)
        self.init_tree("<TPTP_file>")

    def reduceGrammar(self, disable_rules_filname: str):
        self.disable_rules(disable_rules_filname)
        self.remove_non_terminating_symbols(self.nodes_dictionary.get(Node("<TPTP_file>", RuleType.GRAMMAR)))

    def __init__(self,filename: str= None,disable_rules_filname: str=None):
        self.nodes_dictionary = {}
        self.parser = yacc.TPTPParser()
        if((filename is not None) and (disable_rules_filname is not None)):
            rules_list = self.parser.run(filename)
            self.build_nodes_dictionary(rules_list)
            self.disable_rules(InputOutput.read_text_from_file(disable_rules_filname),'<TPTP_file>')
            #self.init_tree("<formula_role>")
            #self.remove_non_terminating_symbols(self.nodes_dictionary.get(Node("<start_symbol>", RuleType.GRAMMAR)))
            #InputOutput.print_ordered_rules_from_graph(self.nodes_dictionary.get(Node("<start_symbol>",RuleType.GRAMMAR)))
            InputOutput.save_ordered_rules_from_graph("output_TPTP.txt",self.nodes_dictionary.get(Node("<start_symbol>",RuleType.GRAMMAR)))
            #visited = {}
            #self.print_rules_from_graph(self.nodes_dictionary.get(Node("<TPTP_file>",RuleType.GRAMMAR)),visited)
            #self.print_rules_from_rules_list(rules_list)
        elif(filename is not None):
            rules_list = self.parser.run(filename)
            self.build_nodes_dictionary(rules_list)
            self.init_tree("<TPTP_file>")
            #self.remove_non_terminating_symbols(self.nodes_dictionary.get(Node("<TPTP_file>", RuleType.GRAMMAR)))
            InputOutput.print_ordered_rules_from_graph(self.nodes_dictionary.get(Node("<start_symbol>", RuleType.GRAMMAR)))



    #def __init__(self):
    #    self.rules_test = []
    #    self.nodes_dictionary = {}
    #    self.parser = yacc.TPTPParser()