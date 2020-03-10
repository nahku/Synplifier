import Parser
import GraphBuilder
from collections import namedtuple

PrintListEntry = namedtuple("PrintListEntry", ["position", "line_list"])
INDENT_LENGTH = 20


def print_rules_from_rules_list(rules_list):
    for i in rules_list.list:
        if isinstance(i, Parser.MACRO_EXPRESSION) | isinstance(i, Parser.STRICT_EXPRESSION) | \
                isinstance(i, Parser.GRAMMAR_EXPRESSION) | isinstance(i, Parser.TOKEN_EXPRESSION):
            print_expression(i)
            print("")
        else:
            print_comment_block(i)


def print_rules_from_graph(start_node, visited):
    print_rule_from_nt_node(start_node)
    visited.update({GraphBuilder.Node(start_node.value, start_node.rule_type): start_node})
    for i in start_node.children:
        for j in i:
            if GraphBuilder.Node(j.value, j.rule_type) not in visited.keys():
                print_rules_from_graph(j, visited)
                visited.update({GraphBuilder.Node(j.value, j.rule_type): j})


def create_print_list(start_node, visited, print_list):
    print_list = get_print_list(start_node, print_list)
    visited.update({GraphBuilder.Node(start_node.value, start_node.rule_type): start_node})
    for i in start_node.children:
        for j in i:
            if GraphBuilder.Node(j.value, j.rule_type) not in visited.keys():
                print_list = create_print_list(j, visited, print_list)
                visited.update({GraphBuilder.Node(j.value, j.rule_type): j})
    return print_list


def get_print_list(node, print_list):
    print_list.append(PrintListEntry(node.position, []))
    if node.comment_block is not None:
        print_list[-1].line_list.extend(node.comment_block.comment_lines)
    rule_line = node.value
    rule_line = rule_line.ljust(INDENT_LENGTH)  # uniform length of left side of rule
    if node.rule_type == GraphBuilder.RuleType.GRAMMAR:
        rule_line += " ::= "
    elif node.rule_type == GraphBuilder.RuleType.TOKEN:
        rule_line += " ::- "
    elif node.rule_type == GraphBuilder.RuleType.STRICT:
        rule_line += " :== "
    elif node.rule_type == GraphBuilder.RuleType.MACRO:
        rule_line += " ::: "
    rule_line += get_productions_list_string(node.productions_list)
    print_list[-1].line_list.append(rule_line)
    return print_list


def print_rule_from_nt_node(node):
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


def print_ordered_rules_from_graph(start_node):
    visited = {}
    print_list = []
    print_list = create_print_list(start_node, visited, print_list)
    print_list.sort(key=lambda x: x[0])
    for tuple in print_list:
        if tuple.position >= 0:
            for line in tuple.line_list:
                print(line)


def save_ordered_rules_from_graph(filename, start_node, print_option="w"):
    visited = {}
    print_list = []
    print_list = create_print_list(start_node, visited, print_list)
    print_list.sort(key=lambda x: x[0])
    print_string = ""
    for tuple in print_list:
        if tuple.position >= 0:
            for line in tuple.line_list:
                print_string += line + "\n"
    with open(filename, print_option) as text_file:
        text_file.write(print_string)


def save_ordered_rules_from_graph_with_comments(filename: str, start_node):
    """Save the rules from graph with comment symbols at the end.

    :param filename: Filename where string should be stored.
    :param start_node: Start node of graph.
    """
    save_ordered_rules_from_graph(filename, start_node)

    graph_builder = GraphBuilder.TPTPGraphBuilder()
    graph_builder.run(start_symbol="<comment>", filename="comment.txt")
    start_node = graph_builder.nodes_dictionary.get(
        GraphBuilder.Node("<comment>", GraphBuilder.RuleType.TOKEN))
    save_ordered_rules_from_graph(filename, start_node, print_option="a")


def save_text_to_file(text: str, filename: str):
    with open(filename, "w") as text_file:
        text_file.write(text)


def print_expression(expression):
    print_wo_newline(expression.name)
    if isinstance(expression, Parser.GRAMMAR_EXPRESSION):
        print_wo_newline(" ::= ")
    elif isinstance(expression, Parser.TOKEN_EXPRESSION):
        print_wo_newline(" ::- ")
    elif isinstance(expression, Parser.STRICT_EXPRESSION):
        print_wo_newline(" :== ")
    elif isinstance(expression, Parser.MACRO_EXPRESSION):
        print_wo_newline(" ::: ")
    print_productions_list(expression.productions_list)


def print_production(production):
    for i in production.list:
        if isinstance(i, Parser.PRODUCTION):
            if i.productionProperty == Parser.ProductionProperty.NONE:
                print_production(i)
            elif i.productionProperty == Parser.ProductionProperty.REPETITION:
                print_wo_newline("(")
                print_production(i)
                print_wo_newline(")")
                print_wo_newline("*")
            elif i.productionProperty == Parser.ProductionProperty.OPTIONAL:
                print_wo_newline("[")
                print_production(i)
                print_wo_newline("]")
            elif i.productionProperty == Parser.ProductionProperty.XOR:
                print_wo_newline("(")
                print_production(i)
                print_wo_newline(")")
        elif isinstance(i, Parser.XOR_PRODUCTIONS_LIST):
            print_xor_productions_list(i)
        elif isinstance(i, Parser.PRODUCTION_ELEMENT):
            print_production_element(i)


def print_xor_productions_list(xor_productions_list):
    print_wo_newline("(")
    length = len(xor_productions_list.list)
    j = 1
    for i in xor_productions_list.list:
        print_production(i)
        if j < length:
            print_wo_newline("|")
        j = j + 1
    print_wo_newline(")")


def print_production_element(production_element):
    if production_element.productionProperty == Parser.ProductionProperty.NONE:
        print_symbol(production_element.name)
    elif production_element.productionProperty == Parser.ProductionProperty.REPETITION:
        print_symbol(production_element.name)
        print_wo_newline("*")
    elif production_element.productionProperty == Parser.ProductionProperty.OPTIONAL:
        print_wo_newline("[")
        print_symbol(production_element.name)
        print_wo_newline("]")
    elif production_element.productionProperty == Parser.ProductionProperty.XOR:
        print_symbol(production_element.name)
        print_wo_newline("|")


def print_symbol(symbol: Parser.SYMBOL) -> None:
    print_wo_newline(get_symbol_string(symbol))


def print_productions_list(productions_list: Parser.PRODUCTIONS_LIST) -> None:
    """Prints string that represents production list to console.

    :param productions_list: Productions list that should be printed.
    """
    length = len(productions_list.list)
    j = 1
    for i in productions_list.list:
        print_production(i)
        if j < length:
            print_wo_newline(" | ")
        j = j + 1


def print_comment_block(comment_block: Parser.COMMENT_BLOCK):
    """Prints all lines of a COMMENT_BLOCK object to console.

    :param comment_block: The comment block that should be printed.
    """
    for i in comment_block.comment_lines:
        print(i)


def print_wo_newline(string: str) -> None:
    """Prints a string without "\n at the end."

    :param string: The string that should be printed.
    """
    print(string, end='')


def get_production_string(production: Parser.PRODUCTION) -> str:
    """Creates print string of production.

    :param production: Production of which print string should be created
    :return: Print string that production represents.
    :rtype: str
    """
    production_string = ""
    for i in production.list:
        if isinstance(i, Parser.PRODUCTION):
            if i.productionProperty == Parser.ProductionProperty.NONE:
                production_string += get_production_string(i)
            elif i.productionProperty == Parser.ProductionProperty.REPETITION:
                production_string += "("
                production_string += get_production_string(i)
                production_string += ")"
                production_string += "*"
            elif i.productionProperty == Parser.ProductionProperty.OPTIONAL:
                production_string += "["
                production_string += get_production_string(i)
                production_string += "]"
            elif i.productionProperty == Parser.ProductionProperty.XOR:
                production_string += "("
                production_string += get_production_string(i)
                production_string += ")"
        elif isinstance(i, Parser.XOR_PRODUCTIONS_LIST):
            production_string += get_xor_productions_list_string(i)
        elif isinstance(i, Parser.PRODUCTION_ELEMENT):
            production_string += get_production_element_string(i)
    return production_string


def get_xor_productions_list_string(xor_productions_list: Parser.XOR_PRODUCTIONS_LIST) -> str:
    """Creates print string of xor productions list.

    :param xor_productions_list: Xor productions list of which print string should be created.
    :return: Print string that xor productions list represents.
    :rtype: str
    """
    xor_productions_list_string = ""
    xor_productions_list_string += "("
    productions_list_string = ""
    length = len(xor_productions_list.list)
    j = 1
    for i in xor_productions_list.list:
        productions_list_string += get_production_string(i)
        if j < length:
            productions_list_string += "|"
        j = j + 1
    xor_productions_list_string += productions_list_string
    xor_productions_list_string += ")"
    return xor_productions_list_string


def get_production_element_string(production_element: Parser.PRODUCTION_ELEMENT) -> str:
    """Creates print string of a production element.

    :param production_element: Production element of which the print string should be produced.
    :return: Print string that production element represents.
    """
    production_element_string = ""
    if production_element.productionProperty == Parser.ProductionProperty.NONE:
        production_element_string += get_symbol_string(production_element.symbol)
    elif production_element.productionProperty == Parser.ProductionProperty.REPETITION:
        production_element_string += get_symbol_string(production_element.symbol)
        production_element_string += "*"
    elif production_element.productionProperty == Parser.ProductionProperty.OPTIONAL:
        production_element_string += "["
        production_element_string += get_symbol_string(production_element.symbol)
        production_element_string += "]"
    elif production_element.productionProperty == Parser.ProductionProperty.XOR:
        production_element_string += get_symbol_string(production_element.symbol)
        production_element_string += "|"
    return production_element_string


def get_symbol_string(symbol: Parser.SYMBOL) -> str:
    """Creates print string of a symbol.

    :param symbol: Symbol of which print string should be created.
    :return: Print string that symbol represents.
    :rtype: str
    """
    symbol_string = ""
    if isinstance(symbol, Parser.T_SYMBOL):
        if symbol.property == Parser.ProductionProperty.NONE:
            symbol_string += symbol.value
        elif symbol.property == Parser.ProductionProperty.REPETITION:
            symbol_string += symbol.value
            symbol_string += "*"
        elif symbol.property == Parser.ProductionProperty.OPTIONAL:
            symbol_string += "["
            symbol_string += symbol.value
            symbol_string += "]"
        elif symbol.property == Parser.ProductionProperty.XOR:
            symbol_string += "("
            symbol_string += symbol.value
            symbol_string += ")"
    elif isinstance(symbol, Parser.NT_SYMBOL):
        symbol_string += symbol.value
    elif isinstance(symbol, list):
        symbol_string += symbol[0].value  # only first because all list elements have the same name
    return symbol_string


def get_productions_list_string(productions_list: Parser.PRODUCTIONS_LIST) -> str:
    """Creates print string of a productions list.

    :param productions_list: Productions list of which print string should be created.
    :return: Print string that productions list represents.
    :rtype: str
    """
    productions_list_string = ""
    length = len(productions_list.list)
    j = 1
    for i in productions_list.list:
        productions_list_string += get_production_string(i)
        if j < length:
            productions_list_string += " | "
        j = j + 1
    return productions_list_string
