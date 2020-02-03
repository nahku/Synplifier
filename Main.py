import sys
import view
import lexer
from PyQt5.QtWidgets import QApplication


if __name__== "__main__":
  #tptpLexer = lexer.TPTPLexer()
  #tptpLexer.debug("<comment_line>         ::- bla <test>  \n<comment_line>         ::- <test>  bla")
  #<comment_line>         ::- [%]<printable_char>*
  app = QApplication(sys.argv)
  mainWindow = view.View()
  sys.exit(app.exec_())