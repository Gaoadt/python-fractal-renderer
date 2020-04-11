from importlib.util import find_spec
from sys import exit

if __name__ == '__main__':
    tkinter = find_spec("tkinter")

    if tkinter is None:
        print("Canot find tkinter module")
        print("Please install tkinter https://tkdocs.com/tutorial/install.html ")

    from main_window import MainWindow
    MainWindow()