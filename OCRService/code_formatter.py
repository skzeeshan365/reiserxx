import autopep8


def format_code(code):
    checking = ''
    if '\n' in code:
        checking = code.replace('\n', '\n ')
    if '\n \n ' in checking:
        checking = checking.replace('\n \n ', '\n\n')

    return autopep8.fix_code(checking)

