from collections import namedtuple

import yacc
import GraphBuilder

PrintListEntry = namedtuple("PrintListEntry", ["position", "line_list"])
INDENT_LENGTH = 20

# def print_tree( node, level):
#     if level == 0:
#         print_tree_nt(node.value, level)
#     if len(node.children) > 0:
#         if len(node.children[0]) >= 0:
#             for i in node.children:
#                 print("")
#                 for j in i:
#                     print_tree_nt(j.value, level+1)
#                     print_tree(j, level+2)
#
# def print_tree_nt( nt_name, level):
#     for i in range(0,level):
#         print("  ",end = "")
#     print(nt_name, end = "")

def print_rules_from_rules_list(rules_list):
    for i in rules_list.list:
        if(isinstance(i,yacc.MACRO_EXPRESSION)|isinstance(i,yacc.STRICT_EXPRESSION)|isinstance(i,yacc.GRAMMAR_EXPRESSION)|isinstance(i,yacc.TOKEN_EXPRESSION)):
            print_expression(i)
            print("")
        else:
            print_comment_block(i)

def print_rules_from_graph(start_node,visited):
    print_rule_from_nt_node(start_node)
    visited.update({GraphBuilder.Node(start_node.value, start_node.rule_type): start_node})
    for i in start_node.children:
        for j in i:
            if(GraphBuilder.Node(j.value,j.rule_type) not in visited.keys()):
                print_rules_from_graph(j,visited)
                visited.update({GraphBuilder.Node(j.value, j.rule_type): j})

def create_print_list(start_node,visited,print_list):
    print_list = get_print_list(start_node, print_list)
    visited.update({GraphBuilder.Node(start_node.value, start_node.rule_type): start_node})
    for i in start_node.children:
        for j in i:
            if (GraphBuilder.Node(j.value, j.rule_type) not in visited.keys()):
                print_list = create_print_list(j,visited, print_list)
                visited.update({GraphBuilder.Node(j.value, j.rule_type): j})
    return print_list

def get_print_list(node,print_list):
    print_list.append(PrintListEntry(node.position,[]))
    if (node.comment_block is not None):
        print_list[-1].line_list.extend(node.comment_block.list)
    rule_line = node.value
    rule_line = rule_line.ljust(INDENT_LENGTH) #uniform length of left side of rule
    if (node.rule_type == GraphBuilder.RuleType.GRAMMAR):
        rule_line += " ::= "
    elif (node.rule_type == GraphBuilder.RuleType.TOKEN):
        rule_line += " ::- "
    elif (node.rule_type == GraphBuilder.RuleType.STRICT):
        rule_line += " :== "
    elif (node.rule_type == GraphBuilder.RuleType.MACRO):
        rule_line += " ::: "
    rule_line += get_productions_list_string(node.productions_list)
    print_list[-1].line_list.append(rule_line)
    return print_list

def print_rule_from_nt_node( node):
    if(node.comment_block is not None):
        print_comment_block(node.comment_block)
    print_wo_newline(node.value)
    if(node.rule_type == GraphBuilder.RuleType.GRAMMAR):
        print_wo_newline(" ::= ")
    elif(node.rule_type == GraphBuilder.RuleType.TOKEN):
        print_wo_newline(" ::- ")
    elif(node.rule_type == GraphBuilder.RuleType.STRICT):
        print_wo_newline(" :== ")
    elif(node.rule_type == GraphBuilder.RuleType.MACRO):
        print_wo_newline(" ::: ")
    print_productions_list(node.productions_list)
    print("")


def print_ordered_rules_from_graph(start_node):
    visited = {}
    print_list = []
    print_list = create_print_list(start_node,visited,print_list)
    print_list.sort(key=lambda x: x[0])
    for tuple in print_list:
        for line in tuple.line_list:
            print(line)

def print_expression( expression):
    print_wo_newline(expression.name)
    if(isinstance(expression,yacc.GRAMMAR_EXPRESSION)):
        print_wo_newline(" ::= ")
    elif(isinstance(expression,yacc.TOKEN_EXPRESSION)):
        print_wo_newline(" ::- ")
    elif (isinstance(expression, yacc.STRICT_EXPRESSION)):
        print_wo_newline(" :== ")
    elif (isinstance(expression, yacc.MACRO_EXPRESSION)):
        print_wo_newline(" ::: ")
    print_productions_list(expression.productions_list)

def get_production_string(production):
    production_string = ""
    for i in production.list:
        if(isinstance(i, yacc.PRODUCTION)):
            if (i.productionProperty == yacc.ProductionProperty.NONE):
                production_string += get_production_string(i)
            elif(i.productionProperty == yacc.ProductionProperty.REPETITION):
                production_string += "("
                production_string += get_production_string(i)
                production_string += ")"
                production_string += "*"
            elif(i.productionProperty == yacc.ProductionProperty.OPTIONAL):
                production_string += "["
                production_string += get_production_string(i)
                production_string += "]"
            elif (i.productionProperty == yacc.ProductionProperty.XOR):
                production_string += "("
                production_string += get_production_string(i)
                production_string += ")"
        elif(isinstance(i, yacc.XOR_PRODUCTIONS_LIST)):
            production_string += get_xor_productions_list_string(i)
        elif (isinstance(i, yacc.PRODUCTION_ELEMENT)):
            production_string += get_production_element_string(i)
    return production_string

def print_production( production):
    for i in production.list:
        if(isinstance(i, yacc.PRODUCTION)):
            if (i.productionProperty == yacc.ProductionProperty.NONE):
                print_production(i)
            elif(i.productionProperty == yacc.ProductionProperty.REPETITION):
                print_wo_newline("(")
                print_production(i)
                print_wo_newline(")")
                print_wo_newline("*")
            elif(i.productionProperty == yacc.ProductionProperty.OPTIONAL):
                print_wo_newline("[")
                print_production(i)
                print_wo_newline("]")
            elif (i.productionProperty == yacc.ProductionProperty.XOR):
                print_wo_newline("(")
                print_production(i)
                print_wo_newline(")")
        elif(isinstance(i, yacc.XOR_PRODUCTIONS_LIST)):
            print_xor_productions_list(i)
        elif (isinstance(i, yacc.PRODUCTION_ELEMENT)):
            print_production_element(i)

def get_xor_productions_list_string(xor_productions_list):
    xor_productions_list_string = ""
    xor_productions_list_string += "("
    xor_productions_list_string += get_productions_list_string(xor_productions_list)
    xor_productions_list_string += ")"
    return xor_productions_list_string

def print_xor_productions_list(xor_productions_list):
    print_wo_newline("(")
    print_productions_list(xor_productions_list)
    print_wo_newline(")")

def get_production_element_string(production_element):
    production_element_string = ""
    if (production_element.productionProperty == yacc.ProductionProperty.NONE):
        production_element_string += get_symbol_string(production_element.name)
    elif (production_element.productionProperty == yacc.ProductionProperty.REPETITION):
        production_element_string += get_symbol_string(production_element.name)
        production_element_string += "*"
    elif (production_element.productionProperty == yacc.ProductionProperty.OPTIONAL):
        production_element_string += "["
        production_element_string += get_symbol_string(production_element.name)
        production_element_string += "]"
    elif (production_element.productionProperty == yacc.ProductionProperty.XOR):
        production_element_string += get_symbol_string(production_element.name)
        production_element_string += " | "
    return production_element_string

def print_production_element(production_element):
    if (production_element.productionProperty == yacc.ProductionProperty.NONE):
        print_symbol(production_element.name)
    elif (production_element.productionProperty == yacc.ProductionProperty.REPETITION):
        print_symbol(production_element.name)
        print_wo_newline("*")
    elif (production_element.productionProperty == yacc.ProductionProperty.OPTIONAL):
        print_wo_newline("[")
        print_symbol(production_element.name)
        print_wo_newline("]")
    elif (production_element.productionProperty == yacc.ProductionProperty.XOR):
        print_symbol(production_element.name)
        print_wo_newline(" |")

def get_symbol_string(symbol):
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

def print_symbol( symbol):
    if isinstance(symbol,yacc.T_SYMBOL):
        if (symbol.property == yacc.ProductionProperty.NONE):
            print_wo_newline(symbol.value)
        elif (symbol.property == yacc.ProductionProperty.REPETITION):
            print_wo_newline(symbol.value)
            print_wo_newline("*")
        elif (symbol.property == yacc.ProductionProperty.OPTIONAL):
            print_wo_newline("[")
            print_wo_newline(symbol.value)
            print_wo_newline("]")
        elif (symbol.property == yacc.ProductionProperty.XOR):
            print_wo_newline("(")
            print_wo_newline(symbol.value)
            print_wo_newline(")")
    elif(isinstance(symbol,yacc.NT_SYMBOL)):
        print_wo_newline(symbol.value)
    elif(isinstance(symbol,list)):
        print_wo_newline(symbol[0].value)  #only first because all list elements have the same name

def get_productions_list_string(productions_list):
    productions_list_string = ""
    length = len(productions_list.list)
    j = 1
    for i in productions_list.list:
        productions_list_string += get_production_string(i)
        if (j < length):
            productions_list_string += " | "
        j = j + 1
    return productions_list_string

def print_productions_list(productions_list):
    length = len(productions_list.list)
    j = 1
    for i in productions_list.list:
        print_production(i)
        if(j<length):
            print_wo_newline(" | ")
        j = j + 1

def print_comment_block(comment_block: yacc.COMMENT_BLOCK):
    """Prints all lines of a COMMENT_BLOCK object to console.

    :param comment_block: The comment block that should be printed.
    """
    for i in comment_block.list:
        print(i)

def print_wo_newline(string: str):
    """Prints a string without "\n at the end."

    :param string: The string that shold be printed.
    """
    print(string, end = '')
