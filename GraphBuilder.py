from collections import namedtuple
from enum import Enum
from typing import List
import Parser

Node_Key = namedtuple("Node", ["value", "ruleType"])


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

    def __str__(self):
        node_string = ""
        if self.comment_block is not None:
            node_string += str(self.comment_block)

        node_string += self.value

        node_string = node_string.ljust(20)  # uniform length of left side of rule

        if self.rule_type == RuleType.GRAMMAR:
            node_string += " ::= "
        elif self.rule_type == RuleType.TOKEN:
            node_string += " ::- "
        elif self.rule_type == RuleType.STRICT:
            node_string += " :== "
        elif self.rule_type == RuleType.MACRO:
            node_string += " ::: "
        node_string += str(self.productions_list)

        return node_string

    def add_children(self, children: List):
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
            self.comment_block.extend(comment_block.comment_lines)


class TPTPGraphBuilder:

    def init_tree(self, start_symbol: str):
        """Initialise the TPTP grammar graph.

        :param start_symbol: Value of the non-terminal start symbol.
        """
        productions_list = Parser.PRODUCTIONS_LIST(
            [Parser.PRODUCTION([Parser.PRODUCTION_ELEMENT(Parser.NT_SYMBOL(start_symbol))])])

        new_start_node = NTNode("<start_symbol>", productions_list, RuleType.GRAMMAR, Parser.COMMENT_BLOCK([]), -1)
        self.nodes_dictionary[Node_Key(new_start_node.value, new_start_node.rule_type)] = new_start_node
        self.build_graph_rek(new_start_node)

    def count_rules(self):
        counter_nodes = [0];
        counter_productions = [0];
        counter_nodes = self.count_nodes_in_graph(set(),self.nodes_dictionary.get(Node_Key("<start_symbol>",RuleType.GRAMMAR)),counter_nodes)
        counter_productions = self.count_productions_in_graph(set(),self.nodes_dictionary.get(Node_Key("<start_symbol>",RuleType.GRAMMAR)),counter_productions)
        print("Productions: " + str(counter_productions[0]))
        print("Rules: " + str(counter_nodes[0]))

    def count_nodes_in_graph(self, visited: set, node: NTNode, counter):
        if node not in visited:
            visited.add(node)
            if node.value is not "<start_node>":
                counter[0] += 1
            for children_list in node.children:
                for child in children_list:
                    self.count_nodes_in_graph(visited,child,counter)
        return counter

    def count_productions_in_graph(self, visited: set, node: NTNode, counter):
        if node not in visited:
            visited.add(node)
            if node.value is not "<start_node>":
                counter[0] += len(node.productions_list.list)
            for children_list in node.children:
                for child in children_list:
                    self.count_productions_in_graph(visited,child,counter)
        return counter

    def build_graph_rek(self, start_node: NTNode):
        """Build the TPTP graph recursively.

        :param start_node: Start Node from which the TPTP grammar graph should be produced.
        """
        if len(start_node.children) == 0:
            self.search_productions_list_for_nt(start_node, start_node.productions_list)
            if len(start_node.children) != 0:
                for i in start_node.children:
                    if i:
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
            node.children.append(children)  # Append children to node

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
                for j in i.list:
                    self.search_production_for_nt(node, j, children)
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
            if key == Node_Key(nt_name, RuleType.GRAMMAR) or key == Node_Key(nt_name, RuleType.MACRO) \
                    or key == Node_Key(nt_name, RuleType.STRICT) or key == Node_Key(nt_name, RuleType.TOKEN):
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
            node = self.nodes_dictionary.get(Node_Key(nt_name, rule_type))
            for index in data:
                del node.productions_list.list[index]
                del node.children[index]
        self.remove_non_terminating_symbols(self.nodes_dictionary.get(Node_Key('<start_symbol>', RuleType.GRAMMAR)))
        self.init_tree(start_symbol)
        self.count_rules()

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
        node_key = Node_Key(node.value, node.rule_type)
        if node_key not in visited:
            visited.add(node_key)
            i = len(node.children) - 1
            for children_list in reversed(node.children):
                not_terminating = False  # every non terminal symbol in children_list has to be terminating in oder
                # for this production to be terminating
                for child in children_list:
                    self.delete_non_terminating_productions(child, terminating, visited)  # todo check
                    if not self.value_in_terminating(child.value, terminating):
                        not_terminating = True
                if not_terminating:
                    del node.children[i]
                    del node.productions_list.list[i]
                i = i - 1

    def delete_non_terminating_nodes(self, terminating: set):
        """Removes non-terminating nodes from TPTP grammar graph.

        :param terminating: Set of known terminating symbol names (strings).
        """

        temporary_dictionary = {}
        for node_key in terminating:
            value = self.nodes_dictionary.get(node_key, None)
            #if value is not None:
            temporary_dictionary.update({node_key: value})
        self.nodes_dictionary = temporary_dictionary

    def find_non_terminating_symbols(self, node: NTNode, terminating: set, visited: set):
        """Find non-terminating symbols in TPTP grammar graph recursively.

        :param node: NTNode in TPTP grammar graph from which fining non terminal_symbols is started.
        :param terminating: Set of the names (strings) of known terminating symbols.
        :param visited: Set of already visited Nodes.
        """
        node_key = Node_Key(node.value, node.rule_type)
        if node_key not in visited:
            visited.add(node_key)
            for children_list in node.children:
                if len(children_list) == 0:
                    terminating.add(node_key)
                else:
                    terminating_flag = True
                    # every non terminal child has to be terminating in order for the symbol to be terminating
                    for child in children_list:
                        self.find_non_terminating_symbols(child, terminating, visited)
                        if not self.value_in_terminating(child.value, terminating):
                            terminating_flag = False
                    if terminating_flag:
                        terminating.add(node_key)

    @staticmethod
    def value_in_terminating(value: str, terminating: set) -> bool:
        """Checks if nonterminal value is in set terminating (of any ruletype).

        :param value: Nonterminal name.
        :param terminating: Set of known terminating symbols.
        :return: Is value in terminating?
        :rtype: bool
        """
        if (Node_Key(value, RuleType.GRAMMAR) not in terminating) and \
                (Node_Key(value, RuleType.TOKEN) not in terminating) and \
                (Node_Key(value, RuleType.STRICT) not in terminating) and \
                (Node_Key(value, RuleType.MACRO) not in terminating):
            return False
        else:
            return True

    def build_nodes_dictionary(self, rules_list: Parser.GRAMMAR_LIST):
        """
        Builds a dictionary from a list of rules.
        :param rules_list: List of rules from which the dictionary should be build.
        """
        for expression in rules_list.list:
            if not isinstance(expression, Parser.COMMENT_BLOCK):
                rule_type = self.find_rule_type_for_rule(expression)
                node_key = Node_Key(expression.name, rule_type)
                if node_key not in self.nodes_dictionary:
                    nt_node = NTNode(expression.name, expression.productions_list, rule_type, None, expression.position)
                    self.nodes_dictionary.update({node_key: nt_node})
                else:
                    self.nodes_dictionary[node_key].productions_list.list.extend(expression.productions_list.list)
        self.assign_comments_to_rules(rules_list)

    def assign_comments_to_rules(self, rules_list: Parser.GRAMMAR_LIST):
        """ Assign comments to rules with heuristic method.

        :param rules_list: List of rules.
        """
        for index, expression in enumerate(rules_list.list):
            if isinstance(expression, Parser.COMMENT_BLOCK):
                comment_block_list = expression.split_comment_block_by_top_of_page()
                if len(comment_block_list) == 1:
                    if index < len(rules_list.list) - 1:
                        # if comment is not at the end assign comment to expression after
                        next_rule = rules_list.list[index + 1]
                        self.append_comment_block_to_node(next_rule,comment_block_list[0])
                    else:
                        # if comment at the end of file append to rule before
                        previous_rule = rules_list.list[index - 1]
                        self.append_comment_block_to_node(previous_rule,comment_block_list[0])
                elif len(comment_block_list) == 2:
                    if index != 0:
                        # if comment not at the beginning of file assign to rule before
                        previous_rule = rules_list.list[index - 1]
                        self.append_comment_block_to_node(previous_rule,comment_block_list[0])
                    else:
                        # if comment at the beginning of file assign to rule after
                        next_rule = rules_list.list[index + 1]
                        self.append_comment_block_to_node(next_rule,comment_block_list[0])
                    if index < len(rules_list.list) - 1:
                        # if comment not at the end of file assign to rule after
                        next_rule = rules_list.list[index + 1]
                        self.append_comment_block_to_node(next_rule,comment_block_list[1])
                    else:
                        # if comment at the end of file assign to rule before
                        previous_rule = rules_list.list[index - 1]
                        self.append_comment_block_to_node(previous_rule,comment_block_list[1])
                elif len(comment_block_list) > 2:
                    print("Hallo")
                    # todo attach comment blocks from second on

    def append_comment_block_to_node(self, rule: Parser.RULE, comment_block: Parser.COMMENT_BLOCK):
        """Appends comment block to node in nodes_dictionary idientified by rule.

        :param rule: Rule, that specifies the node to append the comment_block.
        :param comment_block: Comment block that is to be appended to node specified by rule.
        """
        node_key = Node_Key(rule.name, self.find_rule_type_for_rule(rule));
        self.nodes_dictionary[node_key].extend_comment_block(comment_block)

    @staticmethod
    def find_rule_type_for_rule(expression: Parser.RULE):
        """Find the RuleType of an expression.

        :param expression: Expression of which rule type is checked.
        :return: RuleType of the input expression.
        :rtype: RuleType
        """
        rule_type = None
        if isinstance(expression, Parser.GRAMMAR_RULE):
            rule_type = RuleType.GRAMMAR
        elif isinstance(expression, Parser.TOKEN_RULE):
            rule_type = RuleType.TOKEN
        elif isinstance(expression, Parser.MACRO_RULE):
            rule_type = RuleType.MACRO
        elif isinstance(expression, Parser.STRICT_RULE):
            rule_type = RuleType.STRICT
        return rule_type

    def run(self, start_symbol: str, file: str):
        """Runs the graph builder using the TPTP grammar file when specified
        and the start symbol, if not specified it uses the filename.

        :param start_symbol: Desired start symbol for graph building.
        :param file: TPTP grammar file as string.
        """
        if file is not None:
            rules_list = self.parser.run(file=file)
        else:
            rules_list = self.parser.run(file)
        self.build_nodes_dictionary(rules_list)
        self.init_tree(start_symbol)
        self.count_rules()

    def __init__(self, file: str = None, disable_rules_string: str = None):
        self.nodes_dictionary = {}
        self.parser = Parser.TPTPParser()
        if (file is not None) and (disable_rules_string is not None):
            start_symbol = disable_rules_string.splitlines()[0]
            self.run(start_symbol=start_symbol, file=file)
            self.disable_rules(disable_rules_string)
