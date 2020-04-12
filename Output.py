import Parser
import Input
import GraphBuilder
from collections import namedtuple

PrintListEntry = namedtuple("PrintListEntry", ["position", "string"])
INDENT_LENGTH = 20


def print_rules_from_rules_list(rules_list):
    for i in rules_list.list:
        if isinstance(i, Parser.MACRO_RULE) | isinstance(i, Parser.STRICT_RULE) | \
                isinstance(i, Parser.GRAMMAR_RULE) | isinstance(i, Parser.TOKEN_RULE):
            print_expression(i)
            print("")
        else:
            print_comment_block(i)


def print_rules_from_graph(start_node: GraphBuilder.NTNode, visited: set):
    """Recursively prints syntax corresponding to grammar graph to console.

    :param start_node: Start node of the grammar graph.
    :param visited: Set of already visited nodes.
    """
    print_rule_from_nt_node(start_node)
    visited.add(start_node)
    for children_list in start_node.children:
        for child_node in children_list:
            if child_node not in visited:
                print_rules_from_graph(child_node, visited)
                visited.add(child_node)


def create_print_list(node: GraphBuilder.NTNode, visited: set, print_list):
    """

    :param node:
    :param visited:
    :param print_list:
    :return:
    """
    print_list.append(PrintListEntry(node.position, str(node)))
    visited.add(node)
    for node.children in node.children:
        for child_node in node.children:
            if child_node not in visited:
                print_list = create_print_list(child_node, visited, print_list)
                visited.add(child_node)
    return print_list

def print_rule_from_nt_node(node: GraphBuilder.NTNode):
    if node.comment_block is not None:
        print_comment_block(node.comment_block)
    print_wo_newline(node.value)
    if node.rule_type == GraphBuilder.RuleType.GRAMMAR:
        print_wo_newline(" ::= ")
    elif node.rule_type == GraphBuilder.RuleType.TOKEN:
        print_wo_newline(" ::- ")
    elif node.rule_type == GraphBuilder.RuleType.STRICT:
        print_wo_newline(" :== ")
    elif node.rule_type == GraphBuilder.RuleType.MACRO:
        print_wo_newline(" ::: ")
    print_productions_list(node.productions_list)
    print("")


def print_ordered_rules_from_graph(start_node: GraphBuilder.NTNode):
    visited = set()
    print_list = []
    print_list = create_print_list(start_node, visited, print_list)
    print_list.sort(key=lambda x: x[0])
    for tuple in print_list:
        if tuple.position >= 0:
            print(tuple.string)


def save_ordered_rules_from_graph(filename: str, start_node: GraphBuilder.NTNode, print_option="w"):
    visited = set()
    print_list = []
    print_list = create_print_list(start_node, visited, print_list)
    print_list.sort(key=lambda x: x[0])
    print_string = ""
    for tuple in print_list:
        if tuple.position >= 0:
            print_string += tuple.string + "\n"
    with open(filename, print_option) as text_file:
        text_file.write(print_string)


def save_ordered_rules_from_graph_with_comments(filename: str, start_node):
    """Save the rules from graph with comment symbols at the end.

    :param filename: Filename where string should be stored.
    :param start_node: Start node of graph.
    """
    save_ordered_rules_from_graph(filename, start_node)

    graph_builder = GraphBuilder.TPTPGraphBuilder()
    graph_builder.run(start_symbol = "<comment>", file = Input.read_text_from_file("comment.txt"))
    start_node = graph_builder.nodes_dictionary.get(
        GraphBuilder.Node_Key("<comment>", GraphBuilder.RuleType.TOKEN))
    save_ordered_rules_from_graph(filename, start_node, print_option="a")


def save_text_to_file(text: str, filename: str):
    with open(filename, "w") as text_file:
        text_file.write(text)


def print_expression(expression):
    print_wo_newline(expression.name)
    if isinstance(expression, Parser.GRAMMAR_RULE):
        print_wo_newline(" ::= ")
    elif isinstance(expression, Parser.TOKEN_RULE):
        print_wo_newline(" ::- ")
    elif isinstance(expression, Parser.STRICT_RULE):
        print_wo_newline(" :== ")
    elif isinstance(expression, Parser.MACRO_RULE):
        print_wo_newline(" ::: ")
    print_productions_list(expression.productions_list)


def print_production(production):
    print_wo_newline(str(production))


def print_xor_productions_list(xor_productions_list):
    print_wo_newline(str(xor_productions_list))


def print_production_element(production_element):
    print_wo_newline(str(production_element))


def print_symbol(symbol: Parser.SYMBOL):
    print_wo_newline(str(symbol))


def print_productions_list(productions_list: Parser.PRODUCTIONS_LIST):
    """Prints string that represents production list to console.

    :param productions_list: Productions list that should be printed.
    """
    print(str(productions_list))


def print_comment_block(comment_block: Parser.COMMENT_BLOCK):
    """Prints all lines of a COMMENT_BLOCK object to console.

    :param comment_block: The comment block that should be printed.
    """
    print(str(comment_block))


def print_wo_newline(string: str):
    """Prints a string without "\n at the end."

    :param string: The string that should be printed.
    """
    print(string, end='')