import Input
import Parser

filepath = "syntax_and_control_files/Full_TPTP_Syntax.txt"

syntax_file_content = Input.read_text_from_file(filepath)
parser = Parser.TPTPParser()
rules_list = parser.run(syntax_file_content)
index = len(rules_list.list)-1
number_of_rules = 0
for element in reversed(rules_list.list):
    if not isinstance(element,Parser.COMMENT_BLOCK):
        number_of_rules += len(element.productions_list.list)
    index -= 1

print("Total number of rules in TPTP syntax: " + str(number_of_rules))