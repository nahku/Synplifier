from collections import namedtuple
from enum import Enum
from typing import List
import InputOutput
import Parser


Node = namedtuple("Node", ["value", "productionProperty"])


class RuleType(Enum):
    GRAMMAR = 1
    TOKEN = 2
    STRICT = 3
    MACRO = 4


class NTNode:
    def __init__(self, value: str, productions_list: Parser.PRODUCTIONS_LIST, rule_type: RuleType,
                 comment_block: Parser.COMMENT_BLOCK, position: int):
        """Creates an NTNode.

        :param value: Non-terminal symbol name.
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

    def extend_comment_block(self, comment_block: Parser.COMMENT_BLOCK) -> None:
        """"Append comment block to comment block of this node.

        :param comment_block: COMMENT_BLOCK to append
        """
        if self.comment_block is None:
            self.comment_block = comment_block
        else:
            self.comment_block.comment_lines.extend(comment_block.comment_lines)


class TPTPGraphBuilder():

    def init_tree(self, start_symbol: str):
        """Initialise the TPTP grammar graph.

        :param start_symbol: Value of the non-terminal start symbol.
        """
        productions_list = Parser.PRODUCTIONS_LIST(
            [Parser.PRODUCTION([Parser.PRODUCTION_ELEMENT(Parser.NT_SYMBOL(start_symbol))])])

        new_start_node = NTNode("<start_symbol>", productions_list, RuleType.GRAMMAR, Parser.COMMENT_BLOCK([]), -1)
        self.nodes_dictionary[Node(new_start_node.value, new_start_node.rule_type)] = new_start_node
        self.build_graph_rek(new_start_node)

    def build_graph_rek(self, start_node: NTNode):
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

    def search_productions_list_for_nt(self, node: NTNode, productions_list: Parser.PRODUCTIONS_LIST):
        """
        Searches for every production that is part of the production list.
        :param node: Node from which the productions should be identified.
        :param productions_list: Production list of the node above.
        """
        for i in productions_list.list:
            children = []
            self.search_production_for_nt(node, i, children)
            node.children.append(children) #Append children that have been found to node

    def search_production_for_nt(self, node: NTNode, production: Parser.PRODUCTION, children: list):
        """
        Searches for NT symbols recursively that are part of the production. After the NT symbol has been identified,
        the node of the NT symbol is added to the list of children from the input node.
        :param node: Node from which the NT symbols should be identified.
        :param production: Production of one  productions list of the node above.
        :param children: List of children from that should be appended to the node above.
        """
        for i in production.list:
            if isinstance(i, Parser.PRODUCTION):
                self.search_production_for_nt(node, i, children)
            elif isinstance(i, Parser.XOR_PRODUCTIONS_LIST):
                self.search_productions_list_for_nt(node, i)
            elif isinstance(i, Parser.PRODUCTION_ELEMENT):
                if not isinstance(i.symbol, Parser.T_SYMBOL):
                    children_nodes = self.find_nt_key(i.symbol.value)
                    for j in children_nodes:
                        children.append(j)  # all children of production

    def find_nt_key(self, nt_name: str) -> list:
        """
        Searches for the node whose name is nt_name in nodes dictionary.
        :param nt_name: Name from which the node should be found.
        :return: List of nodes that matches nt_name.
        """
        children = []
        for key, value in self.nodes_dictionary.items():
            if key == Node(nt_name, RuleType.GRAMMAR) or key == Node(nt_name, RuleType.MACRO) \
                    or key == Node(nt_name, RuleType.STRICT) or key == Node(nt_name, RuleType.TOKEN):
                children.append(value)
        return children

    def disable_rules(self, disable_rules_string: str):
        """Disables rules specified in the control file from the TPTP grammar graph and select start symbol.

        :param disable_rules_string: Text of the control file.
        """
        lines = disable_rules_string.splitlines()
        start_symbol = lines[0]
        del lines[0]
        for i in lines:
            # i = i.strip("\n")
            data = i.split(",")
            nt_name = data[0]
            rule_symbol = data[1]
            rule_type = None
            if rule_symbol == "::=":
                rule_type = RuleType.GRAMMAR
            elif rule_symbol == "::-":
                rule_type = RuleType.TOKEN
            elif rule_symbol == ":==":
                rule_type = RuleType.STRICT
            elif rule_symbol == ":::":
                rule_type = RuleType.MACRO
            del data[0:2]
            data = list(map(int, data))
            data.sort(reverse=True)
            for index in data:
                del self.nodes_dictionary.get(Node(nt_name, rule_type)).productions_list.list[index]
                del self.nodes_dictionary.get(Node(nt_name, rule_type)).children[index]

        self.init_tree(start_symbol)
        self.remove_non_terminating_symbols(self.nodes_dictionary.get(Node('<start_symbol>', RuleType.GRAMMAR)))

    def remove_non_terminating_symbols(self, start_node: NTNode):
        """Removes non-terminating symbols from the TPTP grammar graph recursively.

        :param start_node: Start node of the TPTP grammar graph.
        """
        terminating = set()
        temp_terminating = set()
        while 1:  # repeat until set of terminating symbols does not change anymore
            visited = set()
            self.find_non_terminating_symbols(start_node, temp_terminating, visited)
            if terminating == temp_terminating:
                break
            else:
                terminating = temp_terminating
        visited = set()
        self.delete_non_terminating_productions(start_node, terminating, visited)
        self.delete_non_terminating_nodes(terminating)

    def delete_non_terminating_productions(self, node: NTNode, terminating: set, visited: set):
        """Removes productions, that contain non-terminating symbols from the TPTP grammar graph recursively.

        :param node: The node, from which removing non-terminating productions is started.
        :param terminating: Set of names (strings) of known terminating symbols.
        :param visited: Set of Nodes that are already visited.
        """
        if Node(node.value, node.rule_type) not in visited:
            visited.add(Node(node.value, node.rule_type))
            i = len(node.children) - 1
            for children_list in reversed(node.children):
                not_terminating = False  # every non terminal symbol in children_list has to be terminating in oder for this production to be terminating
                for child in children_list:
                    self.delete_non_terminating_productions(child, terminating, visited)
                    if child.value not in terminating:
                        not_terminating = True
                if not_terminating:
                    del node.children[i]
                    del node.productions_list.list[i]
                i = i - 1

    def delete_non_terminating_nodes(self, terminating: set):
        """Removes non-terminating nodes from TPTP grammar graph.

        :param terminating: Set of known terminating symbol names (strings).
        """

        # todo: maybe replace dictionary with set
        temporary_dictionary = {}
        for value in terminating:
            entry = self.nodes_dictionary.get(Node(value, RuleType.GRAMMAR), None)
            if entry is not None:
                temporary_dictionary.update({Node(value, RuleType.GRAMMAR): entry})
            entry = self.nodes_dictionary.get(Node(value, RuleType.STRICT), None)
            if entry is not None:
                temporary_dictionary.update({Node(value, RuleType.STRICT): entry})
            entry = self.nodes_dictionary.get(Node(value, RuleType.MACRO), None)
            if entry is not None:
                temporary_dictionary.update({Node(value, RuleType.MACRO): entry})
            entry = self.nodes_dictionary.get(Node(value, RuleType.TOKEN), None)
            if entry is not None:
                temporary_dictionary.update({Node(value, RuleType.TOKEN): entry})
        self.nodes_dictionary = temporary_dictionary

    def find_non_terminating_symbols(self, node: NTNode, terminating: set, visited: set):
        """Find non-terminating symbols in TPTP grammar graph recursively.

        :param node: NTNode in TPTP grammar graph from which fining non terminal_symbols is started.
        :param terminating: Set of the names (strings) of known terminating symbols.
        :param visited: Set of already visited Nodes.
        """

        if Node(node.value, node.rule_type) not in visited:
            visited.add(Node(node.value, node.rule_type))
            for children_list in node.children:
                if len(children_list) == 0:
                    terminating.add(node.value)
                else:
                    flag = True
                    # every non terminal child has to be terminating in order for the symbol to be terminating
                    for child in children_list:
                        self.find_non_terminating_symbols(child, terminating, visited)
                        if not (child.value in terminating):
                            flag = False
                    if flag:
                        terminating.add(node.value)
                        
    def build_nodes_dictionary(self, rules_list: Parser.GRAMMAR_LIST):
        """
        Builds a dictionary from a list of rules.
        :param rules_list: List of rules from which the dictionary should be build.
        """
        for expression in rules_list.list:
            if not isinstance(expression, Parser.COMMENT_BLOCK):
                rule_type = self.find_rule_type_for_expression(expression)
                self.nodes_dictionary.update({Node(expression.name, rule_type): NTNode(expression.name, expression.productions_list, rule_type,
                                                                                  None, expression.position)})
        self.assign_comments_to_rules(rules_list)

    def assign_comments_to_rules(self,rules_list: list):
        """ Assign comments to rules with heuristic method.

        :param rules_list: List of rules.
        """
        for index, expression in enumerate(rules_list.list):
            if isinstance(expression, Parser.COMMENT_BLOCK):
                comment_block_list = self.split_comment_block_by_top_of_page(expression)
                if len(comment_block_list) == 1:
                    if index < len(rules_list.list)-1:
                        # if comment is not at the end assign comment to expression after
                        next_expression = rules_list.list[index+1]
                        self.nodes_dictionary[Node(next_expression.name,self.find_rule_type_for_expression(next_expression))].extend_comment_block(comment_block_list[0])
                    else:
                        # if comment at the end of file append to rule before
                        previous_expression = rules_list.list[index-1]
                        self.nodes_dictionary[Node(previous_expression.name,self.find_rule_type_for_expression(previous_expression))].extend_comment_block(comment_block_list[0])
                elif len(comment_block_list) == 2:
                    if index != 0:
                        # if comment not at the beginning of file assign to rule before
                        previous_expression = rules_list.list[index-1]
                        self.nodes_dictionary[Node(previous_expression.name,self.find_rule_type_for_expression(previous_expression))].extend_comment_block(comment_block_list[0])
                    else:
                        # if comment at the beginning of file assign to rule after
                        next_expression = rules_list.list[index+1]
                        self.nodes_dictionary[Node(next_expression.name,self.find_rule_type_for_expression(next_expression))].extend_comment_block(comment_block_list[0])

                    if index < len(rules_list.list)-1:
                        # if comment not at the end of file assign to rule after
                        next_expression = rules_list.list[index+1]
                        self.nodes_dictionary[Node(next_expression.name,self.find_rule_type_for_expression(next_expression))].extend_comment_block(comment_block_list[1])
                    else:
                        # if comment at the end of file assign to rule before
                        previous_expression = rules_list.list[index-1]
                        self.nodes_dictionary[Node(previous_expression.name,self.find_rule_type_for_expression(previous_expression))].extend_comment_block(comment_block_list[1])
                elif len(comment_block_list) > 2:
                    print("Hallo")

    def find_rule_type_for_expression(self, expression):
        """Find the RuleType of an expression.

        :param expression: Expression of which rule type is checked.
        :return: RuleType of the input expression.
        :rtype: RuleType
        """
        rule_type = None
        if isinstance(expression, Parser.GRAMMAR_EXPRESSION):
            rule_type = RuleType.GRAMMAR
        elif isinstance(expression, Parser.TOKEN_EXPRESSION):
            rule_type = RuleType.TOKEN
        elif isinstance(expression, Parser.MACRO_EXPRESSION):
            rule_type = RuleType.MACRO
        elif isinstance(expression, Parser.STRICT_EXPRESSION):
            rule_type = RuleType.STRICT
        return rule_type

    def find_top_of_page_line_ids(self, comment_block: Parser.COMMENT_BLOCK) -> List[int]:
        """Find the IDs of top of page lines in a COMMENT_BLOCK ordered ascending.

        :param comment_block:
        :return: List of IDs of top of page lines.
        :rtype: List[int]
        """
        index = 0
        index_list = []
        for line in comment_block.comment_lines:
            if line == "%----Top of Page---------------------------------------------------------------":
                index_list.append(index)
            index += 1
        return index_list

    def split_comment_block_by_top_of_page(self, comment_block: Parser.COMMENT_BLOCK) -> List[Parser.COMMENT_BLOCK]:
        """Split a COMMENT_BLOCK by top of page lines and return a list of splitted COMMENT_BLOCKs without
        the top of page lines.

        :param comment_block: COMMENT_BLOCK to be splitted by top of page.
        :return: List of COMMENT_BLOCKs splitted by top of page.
        :rtype: List[Parser.COMMENT_BLOCK]
        """
        top_of_page_indexes = self.find_top_of_page_line_ids(comment_block)
        comment_block_list = []
        if top_of_page_indexes == []:
            comment_block_list = [comment_block]
        else:
            #potential leading comment block
            first_top_of_page_index = top_of_page_indexes[0]
            if first_top_of_page_index != 0:
                #if only first line
                if first_top_of_page_index-1 == 0:
                    first_comment_block = Parser.COMMENT_BLOCK([comment_block.comment_lines[0]])
                else:
                    first_comment_block = Parser.COMMENT_BLOCK(comment_block.comment_lines[0:first_top_of_page_index - 1])
                comment_block_list.append(first_comment_block)

            for index_in_list, index in enumerate(top_of_page_indexes):
                #if top of page is not last line
                if(index != len(comment_block.comment_lines)-1):
                    start = index + 1
                    if(index_in_list+1 < len(top_of_page_indexes)):
                        end = top_of_page_indexes[index_in_list+1]-1
                    else:
                        end = len(comment_block.comment_lines)-1

                    if start == end:
                        new_comment_block = Parser.COMMENT_BLOCK([comment_block.comment_lines[start]])
                    else:
                        new_comment_block = Parser.COMMENT_BLOCK(comment_block.comment_lines[start:end])
                    comment_block_list.append(new_comment_block)

        return comment_block_list

    def run(self, filename: str, start_symbol: str, file: str = None):
        """Runs the graph builder using the TPTP grammar file when specified
        and the start symbol, if not specified it uses the filename.

        :param filename: Filename of the TPTP grammar file.
        :param start_symbol: Desired start symbol for graph building.
        :param file: TPTP grammar file as string.
        """
        if (file is not None):
            rules_list = self.parser.run(file=file, filename=None)
        else:
            rules_list = self.parser.run(filename)
        self.build_nodes_dictionary(rules_list)
        self.init_tree(start_symbol)

    def reduce_grammar(self, control_string: str = None) -> None:
        """Reduce Grammar with control file.

        :param control_filename: Path for the control file.
        """
        lines = control_string.splitlines()
        start_symbol = lines[0]
        self.disable_rules(control_string)
        self.remove_non_terminating_symbols(self.nodes_dictionary.get(Node(start_symbol, RuleType.GRAMMAR)))

    def __init__(self, filename: str = None, disable_rules_filename: str = None):
        self.nodes_dictionary = {}
        self.parser = Parser.TPTPParser()
        if (filename is not None) and (disable_rules_filename is not None):
            rules_list = self.parser.run(filename)
            self.build_nodes_dictionary(rules_list)
            self.disable_rules(InputOutput.read_text_from_file(disable_rules_filename))
