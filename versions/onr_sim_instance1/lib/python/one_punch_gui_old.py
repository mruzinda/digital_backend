from Tkinter import *
import dealer
import numpy

# Start players #########################################
class Banks(Frame):
    # createPlayers() contains button and grid code for GUI
    def createPlayers(self):
        self.Players = Label(self)
        self.Players["text"] = "Banks:"
        self.Players.grid(row = 0, column = 0, sticky=W)

        self.players = [["BANKA", "BANKE", "BANKI", "BANKM", "BANKQ"],
                        ["BANKB", "BANKF", "BANKJ", "BANKN", "BANKR"],
                        ["BANKC", "BANKG", "BANKK", "BANKO", "BANKS"],
                        ["BANKD", "BANKH", "BANKL", "BANKP", "BANKT"]]
        self.var = IntVar()
        self.all_none=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for k in range(0,24):
            self.all_none[k] = IntVar()
        self.all_play = Button(self, text="All players", command=self.All_players).grid(row=1, column=0, sticky=W)
        self.no_play = Button(self, text="No players", command=self.No_players).grid(row=1, column=1, sticky=W)

        self.play = []
        for rIndex in range(0,4):
            for cIndex in range(0,5):
                self.play = Checkbutton(self, text=self.players[rIndex][cIndex], variable=self.all_none[rIndex*5+cIndex])
                self.play.grid(row=rIndex+2, column=cIndex)

        # Start player(s) button
        self.startplayer = Button(self, text="Start Banks", command=self.store_run).grid(row=6,column=0, sticky=W)
        Label(self, text="").grid(row=7, column=0)

    # store_run() function stores the added players and starts the players
    def store_run(self):
        self.playerList = []
        count = -1
        for rIdx in range(0,4):
            for cIdx in range(0,5):
                if self.all_none[rIdx*5+cIdx].get() == 1:
                    count = count+1
                    # playerList contains all of the added Banks
                    self.playerList.append(self.players[rIdx][cIdx])
                    print "This is ", self.playerList[count]

    # All_players() function checks all players by setting the checkbutton values to 1
    def All_players(self):
        for k in range(0,24):
            self.all_none[k].set(1)

    # No_players() function unchecks all players by setting the checkbutton values to 0
    def No_players(self):
        for k in range(0,24):
            self.all_none[k].set(0)

    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.createPlayers()

# Set mode #####################################
class setModes(Frame):
    def createModes(self):
        self.mode_label = Label(self, text = "Select Mode: ").grid(row=0, column=0, sticky=W)
        modes = ["FLAG_CALCORR_MODE", "FLAG_PFBCORR_MODE", "FLAG_FRBCORR_MODE", "FLAG_BX_MODE", "FLAG_RTBF_MODE"] 
        self.optionVar = StringVar(self)
        self.optionVar.set(modes[0])
        self.mode = apply(OptionMenu, (self, self.optionVar) + tuple(modes)).grid(row=0,column=1, sticky=W)
        self.enterMode = Button(self, text="Set Mode", command=self.get_setMode).grid(row=1, column=0, sticky=W)
        Label(self, text="").grid(row=2, column=0, sticky=W)

    def get_setMode(self):
        print "Mode chosen: ", self.optionVar.get()

 
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.createModes()

# Set Parameters ####################################
class setParameters(Frame):
    def setParam(self):
        self.plabel = Label(self, text="Enter parameter(s): ")
        self.plabel.grid(row=0, column=0, sticky=W)

        # Integration length select
        self.int_label = Label(self, text="Integration len: ").grid(row=1, column=0, sticky=W)
        self.intContent = StringVar(self)
        self.integrationT = Entry(self, bg="white", textvariable=self.intContent)
        self.integrationT.grid(row=1, column=1, sticky=W)
        
        # Weight file select
        self.weight_label = Label(self, text="Weight file: ").grid(row=2, column=0, sticky=W)
        self.weiContent = StringVar(self)
        self.weightF = Entry(self, bg="white", textvariable=self.weiContent)
        self.weightF.grid(row=2, column=1,sticky=W)
        
        # Channel select
        self.channel_label = Label(self, text="Channel sel: ").grid(row=3, column=0, sticky=W)
        self.chanContent = StringVar(self)
        self.channels = Entry(self, bg="white", textvariable=self.chanContent)
        self.channels.grid(row=3, column=1, sticky=W)

        self.paramEnter = Button(self, text="Set parameter(s)", command=self.get_setParam)
        self.paramEnter.grid(row=4, column=0, sticky=W)

        Label(self, text="").grid(row=5, column=0, sticky=W)

    def get_setParam(self):
        if self.intContent.get() is not "":
            print "Integration time: ", self.intContent.get()
        if self.weiContent.get() is not "":
            print "Weight File: ", self.weiContent.get()
        if self.chanContent.get() is not "":
            print "Channel selected: ", self.chanContent.get()


    def __init__(self,master):
        Frame.__init__(self,master)
        self.setParam()

# Start scan #################################################
class startScan(Frame):
    def scanStart(self):
        self.scanlabel = Label(self, text="Scan coordinator: ").grid(row=0, column=0,sticky=W)
        self.start_scan = Button(self, text="Ready Scan", command=self.readyScan).grid(row=1, column=0,sticky=W)

        Label(self, text="").grid(row=2, column=0, sticky=W)

    def readyScan(self):
        print "Ready for scan"

    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.scanStart()

# Stop scan ################################################
class stopScan(Frame):
    def scanStop(self):
        self.stopscan_label = Label(self, text="Stop scan: ").grid(row=0, column=0, sticky=W)
        self.stop_scan = Button(self, text="Stop", command=self.stoppingScan).grid(row=1,column=0,sticky=W)

        Label(self, text="").grid(row=2, column=0, sticky=W)

    def stoppingScan(self):
        print "Stopping scan!"

    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.scanStop()

# Quit ######################################################
class Quitting(Frame):
    def createQuit(self):
        self.QUIT = Button(self, text="QUIT", fg="red", command=self.quit)
        #self.QUIT["text"] = "QUIT"
        #self.QUIT["fg"] = "red"
        #self.QUIT["command"] = self.quit
        self.QUIT.grid(row = 0, column = 0)

    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.createQuit()

# Create the window
root = Tk()
root.title("Dealer/player GUI")
root.geometry("500x700")
Banks(master=root).grid(row=0, column=0, sticky=W)
setModes(master=root).grid(row=1, column=0, sticky=W)
setParameters(master=root).grid(row=2, column=0, sticky=W)
startScan(master=root).grid(row=3, column=0, sticky=W)
stopScan(master=root).grid(row=4,column=0,sticky=W)
Quitting(master=root).grid(row=5, column=0, sticky=W)
root.mainloop()
root.destroy()
