import re


def regex_options(text):
    return re.split(r'\s{3,}|\n+', text.strip())
