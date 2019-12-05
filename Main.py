from PyQt5.QtWidgets import QApplication
import sys
import TreeBuilder
import view
if __name__== "__main__":
  #parser = TPTPParser()
  #test_result = parser.run()
  #print(test_result)
  treeBuilder = TreeBuilder.TPTPTreeBuilder('TPTP_BNF_NEW.txt','disable_rules.txt')
  view.scrollbar(treeBuilder)

#treeBuilder.print_ordered_rules_from_graph()