import os

def import_tptp_file(filename: str):
    """Import TPTP grammar file.

    :param filename: Filename of the TPTP grammar file.
    :return:   grammar file content as string.
    """
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(THIS_FOLDER, filename)
    file = open(my_file, "r", encoding='UTF-8')
    data = file.read()
    return data