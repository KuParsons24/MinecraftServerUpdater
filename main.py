import threading
from miner import Minerman
from gui import GuiWindow

class Main:

    def __init__(self):
        self.theGui = GuiWindow()
        self.theMine: Minerman = None
        self.mainThread: threading.Thread = None
        self.theGui.run_stopButton.config(command=self.runServer)
        self.theGui.runMainWindow()

    def runServer(self):
       # if not self.theMine.isServerRunning:
        self.theGui.allowClose = True
        self.theMine = Minerman()
        self.mainThread = threading.Thread(target=self.theMine.mainLoop, args=(self.theGui,))
        self.mainThread.start()
        self.theGui.closingCallback = self.killWindow
        self.theGui.run_stopButton.config(text='Stop', command=self.stopServer)

    def stopServer(self):
        self.theMine.kill_event.set()
        self.theGui.run_stopButton.config(text='Run', command=self.runServer)
        self.theGui.closingCallback = None

    def killWindow(self):
        if not self.theMine.isServerRunning:
            exit(0)
        elif self.theMine.kill_event.is_set():
            self.theGui.root.after(100, self.killWindow)
        else:
            self.stopServer()
            self.theGui.root.after(100, self.killWindow)


server = Main()