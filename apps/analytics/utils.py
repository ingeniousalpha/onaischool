import re


def regex_options(text):
    return re.split(r'\s{3,}|\n+', text.strip())


def remove_latex_bracket(latex_string):
    return re.sub(r'\\\(|\\\)', '', latex_string)