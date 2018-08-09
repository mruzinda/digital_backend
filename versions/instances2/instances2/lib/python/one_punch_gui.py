from Tkinter import *
import dealer
import numpy

# Set players #########################################
class Banks(Frame):
    def createPlayers(self):
        self.Players = Label(self)
        self.Players["text"] = "Banks:"
        self.Players.grid(row = 0, column = 0, sticky=W)

        players = [["BankA", "BankE", "BankI", "BankM", "BankQ"],
                   ["BankB", "BankF", "BankJ", "BankN", "BankR"],
                   ["BankC", "BankG", "BankK", "BankO", "BankS"],
                   ["BankD", "BankH", "BankL", "BankP", "BankT"]]
        self.var = IntVar()
        self.sel_all = Checkbutton(self, text="All players", variable=self.var).grid(row=1, column=0, sticky=W)
        self.play = []
        for rIndex in range(0,4):
            for cIndex in range(0,4):
                self.play.append(Checkbutton(self, text = players[rIndex][cIndex]).grid(row=rIndex+2, column=cIndex))
                if self.var == 1:
                    self.play.append(Checkbutton(self, text = players[rIndex][cIndex], variable=1).grid(row=rIndex+2, column=cIndex))
                elif self.var == 0:
                    self.play.append(Checkbutton(self, text = players[rIndex][cIndex], variable=0).grid(row=rIndex+2, column=cIndex)) 

    def startPlayers(self):
        self.startplayer = Button(self, text="Start Banks").grid(row=6,column=0)

    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.createPlayers()
        self.startPlayers()

# Set mode #####################################
class setModes(Frame):
    def createModes(self):
        self.mode_label = Label(self, text = "Select Mode: ").grid(row=0, column=0, sticky=W) 
        default_var = StringVar(self)
        default_var.set("FLAG_CALCORR_MODE")
        self.mode = OptionMenu(self, default_var, "FLAG_CALCORR_MODE","FLAG_PFBCORR_MODE","FLAG_FRBCORR_MODE","FLAG_BX_MODE","FLAG_RTBF_MODE").grid(row=0,column=1, sticky=W)
        self.enterMode = Button(self, text="Set Mode").grid(row=1, column=0, sticky=W)

 
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.createModes()

# Add or Remove players ##################################
class addPlayers(Frame):
    def playersAdd(self):
        self.add_player = Label(self, text="Add players: ").grid(row=0,column=0, sticky=W)

        self.addplay = Button(self, text="Add").grid(row=1, column=0, sticky=W)
   
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.playersAdd()

class removePlayers(Frame):
    def remPlayers(self):
        self.rem_player = Label(self, text="Remove players: ").grid(row=0,column=0, sticky=W)
     
        self.remplay = Button(self, text="Remove").grid(row=1, column=0, sticky=W)   

    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.remPlayers()

# Set Parameters ####################################
class setParameters(Frame):
    def setParam(self):
        self.plabel = Label(self, text="Enter parameter(s): ").grid(row=0, column=0, sticky=W)

        # Integration length select
        self.int_label = Label(self, text="Integration len: ").grid(row=1, column=0, sticky=W)
        self.integration = Entry(self).grid(row=1, column=1, sticky=W)
        
        # Weight file select
        self.weight_label = Label(self, text="Weight file: ").grid(row=2, column=0, sticky=W)
        self.weightF = Entry(self).grid(row=2, column=1,sticky=W)
        
        # Channel select
        self.channel_label = Label(self, text="Channel sel: ").grid(row=3, column=0, sticky=W)
        self.channels = Entry(self).grid(row=3, column=1, sticky=W)

        self.paramEnter = Button(self, text="Set parameter(s)").grid(row=4, column=0, sticky=W)

    def __init__(self,master):
        Frame.__init__(self,master)
        self.setParam()

# Start scan #################################################
class startScan(Frame):
    def scanStart(self):
        self.scanlabel = Label(self, text="Scan coordinator: ").grid(row=0, column=0,sticky=W)
        self.start_scan = Button(self, text="Ready Scan").grid(row=1, column=0,sticky=W)

    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.scanStart()

# Stop scan ################################################
class stopScan(Frame):
    def scanStop(self):
        self.stopscan_label = Label(self, text="Stop scan: ").grid(row=0, column=0, sticky=W)
        self.stop_scan = Button(self, text="Stop").grid(row=1,column=0,sticky=W)

    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.scanStop()

# Quit ######################################################
class Quitting(Frame):
    def createQuit(self):
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit
        self.QUIT.grid(row = 0, column = 0)

    def __init__(self,master=None):
        Frame.__init__(self,master)
       # self.grid()
        self.createQuit()

# Create the window
root = Tk()
root.title("Dealer/player GUI")
root.geometry("500x500")
Banks(master=root).grid(row=0, column=0, sticky=W)
setModes(master=root).grid(row=1, column=0, sticky=W)
#addPlayers(master=root).grid(row=2, column=0, sticky=W)
#removePlayers(master=root).grid(row=3, column=0, sticky=W)
setParameters(master=root).grid(row=2, column=0, sticky=W)
startScan(master=root).grid(row=3, column=0, sticky=W)
stopScan(master=root).grid(row=4,column=0,sticky=W)
Quitting(master=root).grid(row=5, column=0, sticky=W)
root.mainloop()
root.destroy()
