from PyQt5.QtWidgets import QApplication
import sys
import GraphBuilder
import view
if __name__== "__main__":

  graphBuilder = GraphBuilder.TPTPGraphBuilder('TPTP_BNF_NEW.txt', 'disable_rules.txt')
  #view.scrollbar(graphBuilder)
  app = QApplication(sys.argv)
  mainWindow = view.MainWindow()
  sys.exit(app.exec_())
#treeBuilder.print_ordered_rules_from_graph()