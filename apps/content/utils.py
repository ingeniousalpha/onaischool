import re


def remove_latex_bracket(latex_string):
    return re.sub(r'\\\(|\\\)', '', latex_string)