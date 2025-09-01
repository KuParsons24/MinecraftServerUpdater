import tkinter, typing, threading

class GuiWindow:

    def __init__(self, closingCallback: typing.Callable = None):
        self.createWidgets()

        self.closingCallback = closingCallback

        self.root.protocol('WM_DELETE_WINDOW', lambda: self.onClosing(self.closingCallback))

    def runMainWindow(self):
        self.layoutWindowWidgets()
        self.root.mainloop()

    def createWidgets(self):        
        self.root = tkinter.Tk()
        self.root.title('Minecraft Easy Server') # set the title of the window
        self.root.minsize(600, 400) # set minimum window size

        # Widgets
        self.titleLabel=tkinter.Label(self.root, text="Minecraft Easy Server")
        self.outputTextWindow = tkinter.Text(self.root, state="disabled")
        self.run_stopButton = tkinter.Button(self.root, text='Run', width=30)

    def layoutWindowWidgets(self):
        # Configure rows/columns expanding
        # default weight = 0
        self.root.rowconfigure(0, weight=1) # ID, Should widget resize: 0 = no resize, 1 = resize
        self.root.rowconfigure(1, weight=0) # row 1 (button row) stays fixed
        self.root.columnconfigure(0, weight=0) # column 0 (title) fixed width
        self.root.columnconfigure(1, weight=1) # column 1 (output box) expands horizontally

        self.titleLabel.grid(row=0, column=0)
        self.outputTextWindow.grid(row=0, column=1, sticky="nsew")
        self.run_stopButton.grid(row=1, column=1)

    def printOutput(self, text :str):
        self.outputTextWindow.config(state="normal") # allow code to insert
        self.outputTextWindow.insert(tkinter.END, text)
        self.outputTextWindow.see(tkinter.END) # scroll to the end
        self.outputTextWindow.config(state="disabled") # read-only no typing allowed

    def onClosing(self, callback: typing.Callable):
        if callback:
            callback()
        else:
            self.root.destroy()

