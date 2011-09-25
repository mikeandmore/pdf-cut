from window import MainWindow
import sys
from gi.repository import Gtk as gtk

def main():
    wnd = MainWindow()
    wnd.show()
    
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        wnd.load_file(filename)

    gtk.main()

if __name__ == '__main__':
    main()
