from bs4 import BeautifulSoup
import urllib
import os


def import_tptp_syntax_from_web() -> str:
    with urllib.request.urlopen("http://www.tptp.org/TPTP/SyntaxBNF.html") as url:
        html_doc = url.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    tptp_grammar = soup.get_text()
    # Delete Header
    tptp_grammar = '\n'.join(tptp_grammar.split('\n')[1:])
    return tptp_grammar

# def import_tptp_syntax(filename: str) -> str:
#     """Import TPTP grammar file.
#
#     :param filename: Filename of the TPTP grammar file.
#     :return: grammar file content as string.
#     """
#     THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
#     my_file = os.path.join(THIS_FOLDER, filename)
#     file = open(my_file, "r", encoding='UTF-8')
#     data = file.read()
#     return data

def read_text_from_file(filename: str) -> str:
    with open(filename, 'r') as text_file:
        text = text_file.read()
    return text

