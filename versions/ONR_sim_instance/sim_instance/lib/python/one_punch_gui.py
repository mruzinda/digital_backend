import os, sys, signal
from Tkinter import *
from FlagColorguard import FlagColorguard, ThreadPrinter
import dealer
import numpy

#
# # Create the window
# root = Tk()
# root.title("Dealer/player GUI")
# root.geometry("500x700")
# Banks(master=root).grid(row=0, column=0, sticky=W)
# setModes(master=root).grid(row=1, column=0, sticky=W)
# setParameters(master=root).grid(row=2, column=0, sticky=W)
# startScan(master=root).grid(row=3, column=0, sticky=W)
# stopScan(master=root).grid(row=4,column=0,sticky=W)
# Quitting(master=root).grid(row=5, column=0, sticky=W)
# root.mainloop()
# root.destroy()

class OPG():

    def __init__(self):
        self.root = Tk()
        self.root.title("Dealer/Player GUI")
        self.root.geometry("500x700")

        self.banksHandle = self.Banks(master=self.root).grid(row=0, column=0, sticky=W)
        self.modesHandle = self.setModes(master=self.root).grid(row=1, column=0, sticky=W)
        self.paramHandle = self.setParameters(master=self.root).grid(row=2, column=0, sticky=W)
        self.startHandle = self.startScan(master=self.root).grid(row=3, column=0, sticky=W)
        self.stopHandle  = self.stopScan(master=self.root).grid(row=4,column=0,sticky=W)
        self.quitHandle  = self.Quitting(master=self.root).grid(row=5, column=0, sticky=W)

    def mainloop(self):
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()

    # Start players #########################################
    class Banks(Frame):
        def __init__(self, master=None):
            Frame.__init__(self, master)
            self.Players = Label(self)
            self.Players["text"] = "Banks:"
            self.Players.grid(row=0, column=0, sticky=W)

            self.players = [["BANKA", "BANKE", "BANKI", "BANKM", "BANKQ"],
                            ["BANKB", "BANKF", "BANKJ", "BANKN", "BANKR"],
                            ["BANKC", "BANKG", "BANKK", "BANKO", "BANKS"],
                            ["BANKD", "BANKH", "BANKL", "BANKP", "BANKT"]]
            self.var = IntVar()
            self.all_none = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for k in range(0, 24):
                self.all_none[k] = IntVar()
            self.all_play = Button(self, text="All players", command=self.All_players).grid(row=1, column=0,
                                                                                            sticky=W)
            self.no_play = Button(self, text="No players", command=self.No_players).grid(row=1, column=1, sticky=W)

            self.play = []
            for rIndex in range(0, 4):
                for cIndex in range(0, 5):
                    self.play = Checkbutton(self, text=self.players[rIndex][cIndex],
                                            variable=self.all_none[rIndex * 5 + cIndex])
                    self.play.grid(row=rIndex + 2, column=cIndex)

            # Start player(s) button
            self.startplayer = Button(self, text="Start Banks", command=self.store_run).grid(row=6, column=0,
                                                                                             sticky=W)
            Label(self, text="").grid(row=7, column=0)

        # store_run() function stores the added players and starts the players
        def store_run(self):
            self.playerList = []
            count = -1
            for rIdx in range(0, 4):
                for cIdx in range(0, 5):
                    if self.all_none[rIdx * 5 + cIdx].get() == 1:
                        count = count + 1
                        # playerList contains all of the added Banks
                        self.playerList.append(self.players[rIdx][cIdx])
                        print "This is ", self.playerList[count]

            cg.addBanks(bank_names=self.playerList)
            cg.startPlayers()

        # All_players() function checks all players by setting the checkbutton values to 1
        def All_players(self):
            for k in range(0, 24):
                self.all_none[k].set(1)

        # No_players() function unchecks all players by setting the checkbutton values to 0
        def No_players(self):
            for k in range(0, 24):
                self.all_none[k].set(0)

        """
        # Start players #########################################
        class Banks(Frame):
    
            def __init__(self,master=None):
               Frame.__init__(self,master)
               self.createPlayers()
            
            # createPlayers() contains button and grid code for GUI
            def createPlayers(self, master=None):
                Frame.__init__(self,master)
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
            
    """
    # Set mode #####################################
    class setModes(Frame):

        def __init__(self,master=None):
            Frame.__init__(self,master)
            self.mode_label = Label(self, text = "Select Mode: ").grid(row=0, column=0, sticky=W)
            modes = ["FLAG_CALCORR_MODE", "FLAG_PFBCORR_MODE", "FLAG_FRBCORR_MODE", "FLAG_BX_MODE", "FLAG_RTBF_MODE"]
            self.optionVar = StringVar(self)
            self.optionVar.set(modes[0])
            self.mode = apply(OptionMenu, (self, self.optionVar) + tuple(modes)).grid(row=0,column=1, sticky=W)
            self.enterMode = Button(self, text="Set Mode", command=self.get_setMode).grid(row=1, column=0, sticky=W)
            Label(self, text="").grid(row=2, column=0, sticky=W)

        def get_setMode(self):
            print "OPG: Mode chosen: ", self.optionVar.get()
            mode = self.optionVar.get()
            global d
            d=dealer.Dealer()
            d.add_active_player(*cg.getActiveBanks()) # *d.list_avaliable_players()
            d.set_mode(mode=mode)

    # Set Parameters ####################################
    class setParameters(Frame):

        def __init__(self,master):
            Frame.__init__(self,master)
            self.plabel = Label(self, text="Enter parameter(s): ")
            self.plabel.grid(row=0, column=0, sticky=W)

            # Integration length select
            self.int_label = Label(self, text="Integration len: ").grid(row=1, column=0, sticky=W)
            self.intContent = IntVar(self)
            self.integrationT = Entry(self, bg="white", textvariable=self.intContent)
            self.integrationT.grid(row=1, column=1, sticky=W)

            # Weight file select
            self.weight_label = Label(self, text="Weight file: ").grid(row=2, column=0, sticky=W)
            self.weiContent = StringVar(self)
            self.weightF = Entry(self, bg="white", textvariable=self.weiContent)
            self.weightF.grid(row=2, column=1,sticky=W)

            # Channel select
            self.channel_label = Label(self, text="Channel sel: ").grid(row=3, column=0, sticky=W)
            self.chanContent = IntVar(self)
            self.channels = Entry(self, bg="white", textvariable=self.chanContent)
            self.channels.grid(row=3, column=1, sticky=W)

            self.paramEnter = Button(self, text="Set parameter(s)", command=self.get_setParam)
            self.paramEnter.grid(row=4, column=0, sticky=W)

            Label(self, text="").grid(row=5, column=0, sticky=W)

        def get_setParam(self):
            if self.intContent.get() is not None:
                print "OPG: Integration time: ", self.intContent.get()
                reqSTI = self.intContent.get()
                d.set_param(REQSTI=reqSTI)
            if self.weiContent.get() is not "":
                print "OPG: Weight File: ", self.weiContent.get()
                weightFile = self.weiContent.get()
                d.set_param(BWEIFILE=weightFile)
            if self.chanContent.get() is not None:
                print "OPG: Channel selected: ", self.chanContent.get()
                chansel = self.chanContent.get()
                d.set_param(CHANSEL=chansel)

    # Start scan #################################################
    class startScan(Frame):
        def __init__(self,master=None):
            Frame.__init__(self,master)
            self.scanlabel = Label(self, text="Scan coordinator: ").grid(row=0, column=0,sticky=W)

            # Scan length select
            self.lengthLabel = Label(self, text="Scan length: ").grid(row=1, column=0, sticky=W)
            self.lengthContent = DoubleVar(self)
            self.scanLength = Entry(self, bg="white", textvariable=self.lengthContent)
            self.scanLength.grid(row=1, column=1, sticky=W)

            self.start_scan = Button(self, text="Ready Scan", command=self.readyScan).grid(row=2, column=0, sticky=W)

            Label(self, text="").grid(row=3, column=0, sticky=W)

        def readyScan(self):

            if self.lengthContent is not None:
                scanLength = self.lengthContent.get()
                d.set_param(SCANLEN=scanLength)
            else:
                scanLength = 60
            print "OPG: Scan length: ", self.lengthContent.get()
            print "OPG: Ready for scan!... starting in approx. 5 seconds"
            d.startin(5, scanLength)


    # Stop scan ################################################
    class stopScan(Frame):
        def __init__(self,master=None):
            Frame.__init__(self,master)
            self.stopscan_label = Label(self, text="Stop scan: ").grid(row=0, column=0, sticky=W)
            self.stop_scan = Button(self, text="Stop", command=self.stoppingScan).grid(row=1,column=0,sticky=W)

            Label(self, text="").grid(row=2, column=0, sticky=W)

        def stoppingScan(self):
            print "OPG: Stopping scan!"
            d.stop()

    # Quit ######################################################
    class Quitting(Frame):

        def __init__(self,master=None):
            Frame.__init__(self,master)
            self.QUIT = Button(self, text="QUIT", fg="red", command=self.quit)
            #self.QUIT["text"] = "QUIT"
            #self.QUIT["fg"] = "red"
            #self.QUIT["command"] = self.quit
            self.QUIT.grid(row = 0, column = 0)


def handler(signum, frame):
    print "Handling signal", signum
    for thread in cg.getThreads():
        thread.stop_thread()

    print "ending..."
    exit(0)

signal.signal(signal.SIGINT, handler)
#sys.stdout = ThreadPrinter()

cg = FlagColorguard()
g = OPG()
g.mainloop()
g.destroy()