from importlib.util import find_spec
from sys import exit

tkinter_install_text = """
Cannot find tkinter module
Please install tkinter https://tkdocs.com/tutorial/install.html
"""

if __name__ == '__main__':
    tkinter = find_spec("tkinter")

    if tkinter is None:
        print(tkinter_install_text)
        exit(0)

    from main_window import MainWindow
    MainWindow()
