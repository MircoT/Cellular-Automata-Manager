from cae.wxui import App
from sys import exit, argv
import logging
from cae.utils import debug

def main():
    if len(argv) == 1:
        my_app = App()
        my_app.MainLoop()
    elif len(argv) == 2 and argv[1] == "debug":
        logging.basicConfig(level=logging.DEBUG)
        debug("APP STARTED")
        my_app = App()
        my_app.MainLoop()
        debug("APP FINISHED")
    elif len(argv) == 3 and argv[1] == "debug" and argv[2] == "onfile":
        logging.basicConfig(filename='app.log', level=logging.DEBUG)
        debug("APP STARTED")
        my_app = App()
        my_app.MainLoop()
        debug("APP FINISHED")
    else:
        print("Command not recognized")
        return 1


if __name__ == '__main__':
    exit(main())