import Input
import Parser

filepath = "syntax_and_control_files/Full_TPTP_Syntax.txt"

syntax_file_content = Input.read_text_from_file(filepath)
parser = Parser.TPTPParser()
rules_list = parser.run(syntax_file_content)

index = len(rules_list.list)-1
number_of_productions = 0
number_of_syntax_productions = 0
number_of_rules = 0
number_of_syntax_rules = 0
for element in reversed(rules_list.list):
    if not isinstance(element,Parser.COMMENT_BLOCK):
        number_of_productions += len(element.productions_list.list)
        number_of_rules += 1
    if isinstance(element,Parser.GRAMMAR_RULE):
        number_of_syntax_productions += len(element.productions_list.list)
        number_of_syntax_rules += 1
    index -= 1

print("Total number of productions in TPTP syntax: " + str(number_of_productions))
print("Total number of syntax productions in TPTP syntax: " + str(number_of_syntax_productions))
print("")
print("Total number of rules in TPTP syntax: " + str(number_of_rules))
print("Total number of syntax rules in TPTP syntax: " + str(number_of_syntax_rules))