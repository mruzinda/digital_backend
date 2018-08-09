import os, sys, signal, time, subprocess
from threading import Thread
from Tkinter import *
from FlagColorguard import FlagColorguard, ThreadPrinter, OverlordThread

from config.DibasParser import DibasParser
import dealer
import numpy

class OPGPrinter():
    def __init__(self, text_box):
        self.txtBox = text_box

    def write(self, str):
        self.txtBox.insert(END, str)
        self.txtBox.see(END)
        self.txtBox.update_idletasks()

class OPG():

    def __init__(self, root):
        #self.root = Tk()
        self.root = root
        self.root.title("Dealer/Player GUI")
        self.root.geometry("700x970")

        #self.infoHandle = Info(master=self.root).grid(row=0, column=0, sticky=W)

        self.projectDir  = self.Project(master=self.root).grid(row = 1, column=0, sticky=W)
        self.banksHandle = self.Banks(master=self.root).grid(row=2, column=0, sticky=W)
        self.modesHandle = self.setModes(master=self.root).grid(row=3, column=0, sticky=W)
        self.paramHandle = self.setParameters(master=self.root).grid(row=4, column=0, sticky=W)
        self.startHandle = self.startScan(master=self.root).grid(row=5, column=0, sticky=W)
        self.stopHandle  = self.stopScan(master=self.root).grid(row=6,column=0,sticky=W)
        self.quitHandle  = self.Quitting(master=self.root).grid(row=7, column=0, sticky=W)

        self.outputHandle = self.Output(master=self.root)
        self.outputHandle.grid(row=8, column=0, sticky=NSEW)



    def mainloop(self):
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()

    class Output(Frame):
        def __init__(self, master):
            Frame.__init__(self,master)
            self.txtBox = Text(self, wrap='word', height=15, width=90, background="white")

            self.scroll = Scrollbar(self)
            self.scroll.configure(command=self.txtBox.yview, background="yellow")

            self.txtBox.configure(yscrollcommand=self.scroll.set)

            self.scroll.pack(side="right", fill="y", expand=False)
            self.txtBox.pack(side="left", fill="both", expand=True)

            #sys.stdout = OPGPrinter(self.txtBox)


    class Project(Frame):
        def __init__(self, master):
            Frame.__init__(self,master)
            self.projectLabel = Label(self, text="Project Dir: ").grid(row=0, column=0, sticky=W)
            self.projectDirContent = StringVar(self)
            self.projectDirTextbox = Entry(self, bg="white", textvariable=self.projectDirContent)
            self.projectDirTextbox.grid(row=0, column=1, sticky=W)

            self.dirEnter = Button(self, text="Submit", command=self.set_dir)
            self.dirEnter.grid(row=0, column=2, sticky=W)

            Label(self, text="").grid(row=1, column=0, sticky=W)

        def set_dir(self):
            global statusFlag, logDirectory
            if statusFlag == "ERROR":
                clearStatus()

            if self.projectDirContent.get() is not "":
                logDirectory = self.projectDirContent.get()
            else:
                logDirectory = None

    # Start players #########################################
    class Banks(Frame):
        def __init__(self, master=None, infoLabel=None):
            Frame.__init__(self, master)
            self.infoLabel = infoLabel
            self.Players = Label(self, text="Players", font=13)
            self.Players.grid(row=0, column=0, sticky=W)

            self.players = [["BANKA", "BANKE", "BANKI", "BANKM", "BANKQ"],
                            ["BANKB", "BANKF", "BANKJ", "BANKN", "BANKR"],
                            ["BANKC", "BANKG", "BANKK", "BANKO", "BANKS"],
                            ["BANKD", "BANKH", "BANKL", "BANKP", "BANKT"]]
            self.var = IntVar()
            self.all_none = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for k in range(0, 24):
                self.all_none[k] = IntVar()
            self.all_play = Button(self, text="All players", command=self.All_players).grid(row=1, column=0, sticky=W)
            self.no_play = Button(self, text="No players", command=self.No_players).grid(row=1, column=1, sticky=W)

            self.play = []
            for rIndex in range(0, 4):
                for cIndex in range(0, 5):
                    self.play = Checkbutton(self, text=self.players[rIndex][cIndex], variable=self.all_none[rIndex * 5 + cIndex])
                    self.play.grid(row=rIndex + 2, column=cIndex)

            # Start player(s) button
            self.startplayer = Button(self, text="Start Banks", command=self.store_run).grid(row=6, column=0, sticky=W)

            ## self.infoText = StringVar(self)
            ## self.infoLabel = Label(self, textvariable=self.infoText).grid(row=7, column=0, sticky=W)
            Label(self, text="").grid(row=7, column=0)

        # store_run() function stores the added players and starts the players
        def store_run(self):
            global logDirectory, playersRunning, playerList

            if logDirectory is None:
                setError("Project dir must be set...")
                return

            setMsg("Setting up players...")

            self.playerList = []
            count = -1
            for rIdx in range(0, 4):
                for cIdx in range(0, 5):
                    if self.all_none[rIdx * 5 + cIdx].get() == 1:
                        count = count + 1
                        # playerList contains all of the added Banks
                        self.playerList.append(self.players[rIdx][cIdx])

            if not len(self.playerList) > 0:
                setMsg("No players selected...")
                return

            playerList = self.playerList

            # match banks selected to start with available banks and start
            for remote in remoteHost:
                players = db_info[remote]['players']
                tostart = []
                for player in players:
                    if player in self.playerList:
                        tostart.append(player)

                if len(tostart) > 0:
                    remoteRunning.append(remote)
                    user = os.getenv('USER')
                    env1 = "$HOME/.bash_profile"
                    env = "/home/groups/flag/dibas/dibas.bash"
                    #dir = "$DIBAS_DIR/versions/stableGUI/lib/python"
                    dir = "/home/groups/flag/dibas/versions/stableGUI/lib/python"
                    prgm = "CGRemote.py"
                    logDir = logDirectory

                    cmd = 'ssh -f %s@%s source %s; source %s; cd %s; python %s %s -d %s'
                    #cmd = 'ssh -f %s@%s bash -lc \'source %s; cd %s; python %s %s -d %s\''
                    cmd = cmd % (user, remote, env, env1, dir, prgm, " ".join(tostart), logDir)
                    print cmd
                    subprocess.Popen(cmd.split(" "))
                    time.sleep(.25)
                else:
                    print "OPG: No players to start for %s" % remote

            # start local players
            # localPlayers = db_info[thisMachine]['players']
            # localPlayersToStart = []
            # for player in localPlayers:
            #     if player in self.playerList:
            #         localRunning.append(player)
            #         localPlayersToStart.append(player)
            # print "OPG: starting local players: ", " ".join(localPlayersToStart)
            # cg.addBanks(bank_names=localPlayersToStart)
            # cg.startPlayers()
            playersRunning = True
            time.sleep(.25)
            clearStatus()


        # All_players() function checks all players by setting the checkbutton values to 1
        def All_players(self):
            for k in range(0, 24):
                self.all_none[k].set(1)

        # No_players() function unchecks all players by setting the checkbutton values to 0
        def No_players(self):
            for k in range(0, 24):
                self.all_none[k].set(0)


    # Set mode #####################################
    class setModes(Frame):

        def __init__(self,master=None):
            Frame.__init__(self,master)
            self.dealerTitle = Label(self, text="Dealer", font=13).grid(row=0, column=0, sticky=W)
            self.mode_label = Label(self, text = "Select Mode: ").grid(row=1, column=0, sticky=W)
            modes = ["FLAG_CALCORR_MODE", "FLAG_PFBCORR_MODE", "FLAG_FRBCORR_MODE", "FLAG_BX_MODE", "FLAG_RTBF_MODE"]
            self.optionVar = StringVar(self)
            self.optionVar.set(modes[0])
            self.mode = apply(OptionMenu, (self, self.optionVar) + tuple(modes)).grid(row=1,column=1, sticky=W)
            self.enterMode = Button(self, text="Set Mode", command=self.get_setMode).grid(row=2, column=0, sticky=W)
            Label(self, text="").grid(row=3, column=0, sticky=W)

        def get_setMode(self):
            global d, statusFlag, dealerRunning, playerList

            if logDirectory is None:
                setError("Project dir must be set...")
                return

            if not playersRunning:
                setError("No players running...")
                return

            print "OPG: Mode chosen: ", self.optionVar.get()
            mode = self.optionVar.get()

            # set log file in dibas.conf

            print playerList
            setMsg("Initializing dealer...")
            d=dealer.Dealer()
            d.remove_active_player("BANKA") # by default A is already there.
            d.add_active_player(*playerList)
            setMsg("Setting mode to %s" % mode)
            d.set_mode(mode=mode)
            dealerRunning = True
            clearStatus()

    # Set Parameters ####################################
    class setParameters(Frame):

        def __init__(self,master):
            Frame.__init__(self,master)
            self.plabel = Label(self, text="Enter parameter(s): ")
            self.plabel.grid(row=0, column=0, sticky=W)

            # Integration length select
            self.int_label = Label(self, text="Integration len: ").grid(row=1, column=0, sticky=W)
            self.intContent = DoubleVar(self)
            self.intContent.set(1.0)
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
            global d, dealerRunning
            # check if dealer exists
            if not dealerRunning:
                setError("Dealer is not running...")
                return

            if self.intContent.get() >= .1:
                print "OPG: Integration time: ", self.intContent.get()
                reqSTI = self.intContent.get()
                d.set_param(int_length=reqSTI)
            else:
                setMsg("invalid integration length")

            if self.weiContent.get() is not "":
                print "OPG: Weight File: ", self.weiContent.get()
                weightFile = self.weiContent.get()
                d.set_param(weight_file=weightFile)
            if self.chanContent.get() is not None:
                print "OPG: Channel selected: ", self.chanContent.get()
                chansel = self.chanContent.get()
                d.set_param(channel_select=chansel)

    # Start scan #################################################
    class startScan(Frame):
        def __init__(self,master=None):
            Frame.__init__(self,master)
            self.scanlabel = Label(self, text="Scan Control", font=13).grid(row=0, column=0,sticky=W)

            # self.play = []
            # for rIndex in range(0, 4):
            #     for cIndex in range(0, 5):
            #         self.play = Checkbutton(self, text=self.players[rIndex][cIndex],
            #                                 variable=self.all_none[rIndex * 5 + cIndex])
            #         self.play.grid(row=rIndex + 2, column=cIndex)

            self.overlord = IntVar(self)
            self.overlord.set(0)
            self.overlordMode =  Checkbutton(self, text="Scan Overlord", variable=self.overlord)
            self.overlordMode.grid(row=1, column=0, sticky=W)

            # Scan length select
            self.lengthLabel = Label(self, text="Scan length: ").grid(row=2, column=0, sticky=W)
            self.lengthContent = IntVar(self)
            self.lengthContent.set(60)
            self.scanLength = Entry(self, bg="white", textvariable=self.lengthContent)
            self.scanLength.grid(row=2, column=1, sticky=W)

            self.start_scan = Button(self, text="Ready Scan", command=self.readyScan).grid(row=3, column=0, sticky=W)


            self.runningLabel = Label(self, text="Scan status: ")
            self.runningLabel.grid(row=4, column=0, sticky=W)
            self.runningVar = StringVar(self)
            self.runningVar.set("No scan")
            self.runningStatusLabel = Label(self, textvariable=self.runningVar)
            self.runningStatusLabel.grid(row=4, column=1, sticky=W)

            self.checkScanStatus()
            Label(self, text="").grid(row=5, column=0, sticky=W)

        def checkScanStatus(self):
            global d, scanRunning, root


            if dealerRunning:
                if scanRunning:
                    cleanup = False

                    d_scan_info = d.get_status("SCANREM")
                    scanrem = d_scan_info[d_scan_info.keys()[0]] # all banks have the same info in this case and the dealer retruns a dictionary of messages per bank so get the first key of the dictionary and retrun the value.
                    self.runningVar.set(scanrem)

                    if scanrem == u'0':
                        self.runningVar.set("Cleaning up...")
                        cleanup = True

                    while cleanup:
                        d_stat_info = d.get_status("NETSTAT")
                        netstat = d_stat_info[d_stat_info.keys()[0]]
                        if netstat == "IDLE":
                            scanRunning = False
                            cleanup = False
                        else:
                            time.sleep(.25)
                else:
                    self.runningVar.set("No scan")

            root.after(1000, self.checkScanStatus)

        def readyScan(self):
            global d, overlordThread, scanRunning

            if not dealerRunning:
                setError("Dealer is not running...")
                return

            # start overlord
            if self.overlord.get():
                self.lengthContent.set(0)
                print "OPG: Overlord selected.. starting Overlord"
                overlordThread = OverlordThread(dealer=d, name="Scan Overlord", logDir=logDirectory)
                overlordThread.start()
            else:
                # set scan length
                scanLength = self.lengthContent.get()
                if scanLength >= 1:
                    scanLength = self.lengthContent.get()
                    d.set_param(scan_length=scanLength)

                    print "OPG: Scan length: ", self.lengthContent.get()
                    print "OPG: Ready for scan!... starting in approx. 5 seconds"
                    setMsg("Starting scan in %d seconds" % 5)
                    d.startin(5, scanLength)
                    scanRunning = True
                    clearStatus()

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


        def quit(self):
            handler(signal.SIGINT, None)
            super(Quitting, self).quit()
            #TODO: Do we need to add code to stop remote's here?

# class Info(Frame):
#     def __init__(self, master):
#         Frame.__init__(self, master)
#         #self.infoText = StringVar(self)
#         self.infoLabel = Label(self, textvariable=infoText, bg="green")
#         self.infoLabel.grid(row=0, column=0, sticky=W)
#         infoText.set("Operational")
#
#     def setLabel(self, str):
#         self.infoText.set(str)
#
#     def setColor(self, color):
#         print "OPG: Trying to set color as", color
#         statusLabel.configure(bg='red')
#         print statusLabel['background']
#         root.update()
# def checkScanStatus():
#     global d, scanRunning, root
#
#     if scanRunning:
#         setMsg("Scanning")
#         print "OPG: scanning"
#     else:
#         print "OPG: no scan"
#
#     root.after(1000, checkScanStatus)

def handler(signum, frame):
    print "OPG: Handling signal", signum

    # print "OPG: Terminating local players..."
    # for thread in cg.getThreads():
    #     thread.stop_thread()
    if overlordThread:
        print "OPG: Terminating overlord..."
        overlordThread.stop_thread()

    user = os.getenv('USER')
    cmd1 = "ssh -q %s@%s"
    prgm = "CGRemote"
    sig = "SIGINT"
    for remote in remoteRunning:
        print "OPG: Terminating remote players..."
        cmd = ""
        cmd = cmd1 % (user, remote)
        cmd = cmd.split(" ")
        cmd.append("ps aux | grep -e %s | grep -v grep | awk '{print $2}' | xargs -r kill -%s" % (prgm, sig))
        subprocess.Popen(cmd)
        print cmd
        time.sleep(.15)

        cmd = ""
        cmd = cmd1 % (user, remote)
        cmd = cmd.split(" ")
        cmd.append("ps aux | grep -e %s | grep -v grep | awk '{print $2}' | xargs -r kill -%s" % ("hashpipe", sig))
        subprocess.Popen(cmd)
        print cmd
        #os.system(cmd % (user, remote, prgm, sig))
        time.sleep(.15)
    print "OPG: Exiting..."
    exit(0)

def setMsg(msg):
    global root, statusFlag
    statusFlag = "INFO"
    statusLabel.configure(bg="yellow")
    infoText.set("INFO: " + msg)
    root.update()

def setError(err=None):
    global root, statusFlag
    statusFlag = "ERROR"
    statusLabel.configure(bg="red")
    infoText.set("ERROR: " + err)
    root.update()

def clearStatus():
    global root, statusFlag
    statusFlag = "OK"
    statusLabel.configure(bg="green")
    infoText.set("Operational")
    root.update()

# def setColor(color):
#     print "OPG: Trying to set color as", color
#     statusLabel.configure(bg='red')
#     print statusLabel['background']
#     root.update()

signal.signal(signal.SIGINT, handler)
#sys.stdout = ThreadPrinter(dir_name="testLog")
logDirectory = None

#thisMachine = "flag3" #os.getenv("HOSTNAME")
remoteRunning = []
#localRunning = []
playerList = []
playersRunning = False
dealerRunning = False
scanRunning = False
configFile = os.getenv('DIBAS_DIR') + '/etc/config/dibas.conf'
db = DibasParser(dibas_conf_file=configFile)
db_info = db.get_dibas_info()
remoteHost = db_info['dest_comp']
#remoteHost.remove(thisMachine)

# Local players
#cg = FlagColorguard()
overlordThread = None


# Create gui and punch on
root = Tk()
infoText = StringVar()
infoText.set("Operational")
statusFlag = "OK"
#statusLabel = Info(master=root)
statusLabel = Label(root, textvariable=infoText, bg="green", font=14)
statusLabel.grid(row=0, column=0, sticky=W)
#checkScanStatus()

g = OPG(root)
g.mainloop()
g.destroy()
