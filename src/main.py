from importlib.util import find_spec
import sys

tkinter_install_text = """
Cannot find tkinter module
Please install tkinter https://tkdocs.com/tutorial/install.html
"""

if __name__ == '__main__':
    tkinter = find_spec("tkinter")
    if tkinter is None:
        print(tkinter_install_text)
        sys.exit(0)
    
    if len(sys.argv) > 1:
        import cli
        cli.launch(sys.argv[1:])
    else:
        from main_window import MainWindow
        MainWindow()
