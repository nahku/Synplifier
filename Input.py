from bs4 import BeautifulSoup
import urllib


def import_tptp_grammar_from_web() -> str:
    with urllib.request.urlopen("http://www.tptp.org/TPTP/SyntaxBNF.html") as url:
        html_doc = url.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    tptp_grammar = soup.get_text()
    # Delete Header
    tptp_grammar = '\n'.join(tptp_grammar.split('\n')[1:])
    return tptp_grammar


def read_text_from_file(filename: str) -> str:
    with open(filename, 'r') as text_file:
        text = text_file.read()
    return text

