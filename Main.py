from PyQt5.QtWidgets import QApplication
import sys
import GraphBuilder
import view
if __name__== "__main__":
  #parser = TPTPParser()
  #test_result = parser.run()
  #print(test_result)
  graphBuilder = GraphBuilder.TPTPGraphBuilder('TPTP_BNF_NEW.txt', 'disable_rules.txt')
  view.scrollbar(graphBuilder)

#treeBuilder.print_ordered_rules_from_graph()