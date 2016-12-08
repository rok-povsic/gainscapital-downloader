import tkinter

from mainframe import MainFrame


if __name__ == '__main__':
    main_window = tkinter.Tk()
    app = MainFrame(main_window)
    app.pack()

    app.mainloop()

