import os, zmq, sys, signal, time
from ZMQJSONProxy import ZMQJSONProxyServer
from threading import Thread, currentThread

import ConfigParser
from player import Bank
from scanOverlord.scanOverlord import scanOverlord


class ThreadPrinter:
    def __init__(self, printer_name="", path="./logFiles/", dir_name=""):

        self.name = printer_name
        self.fhs = {}
        self.path = path
        self.extension = ".log"

        if dir_name != "":
            self.dir_name = self.path + dir_name + "/"
        else:
            self.dir_name = self.path

        if not os.path.isdir(self.dir_name):
            os.mkdir(self.dir_name)

    def write(self, value):

        f = self.getFID()
        f.write(value)
        f.close()

    def getFilename(self):

        fname = ""
        if self.name == "":
            fname = currentThread().name
        else:
            fname = self.name

        return fname


    def getFID(self):

        f = self.fhs.get(self.name)
        fname = self.getFilename()
        if f is None:
            file = self.dir_name + fname + self.extension
            f = open(file, "a")
            self.fhs[fname] = f

        return f

    def fileno(self):
        f = self.getFID()
        return f.fileno()

    # def getFID(self):
    #     baseFilename = "./output"
    #
    #     f = self.fhs.get(currentThread().name)
    #
    #     if f is None:
    #         fname = baseFilename + str(currentThread().name) + ".log"
    #         f = open(fname, "a")
    #         self.fhs[currentThread().name] = f
    #
    #     return f
    #
    # def getFID(self):
    #     baseFilename = "./output/"
    #     fname = baseFilename + str(currentThread().name) + ".log"
    #     f = open(fname, "a")
    #     return f

class OverlordThread(Thread):
    def __init__(self, dealer=None, name=None, sim=False, logDir=""):

        Thread.__init__(self, name=name)

        self.overlord = scanOverlord(D=dealer, sim=False)
        self.dir = logDir

    def run(self):
        self.overlord.start_overlord()

    def stop_thread(self):
        self.overlord.stop_overlord()

class BankThread(Thread):
    def __init__(self, bank_name=None, url=None, sim=False, logDir=""):

        Thread.__init__(self, name=bank_name)


        self.bank = Bank(bank_name=bank_name.upper(), simulate=sim)
        self.dir = logDir

        ctx = zmq.Context()
        self.proxy = ZMQJSONProxyServer(ctx, url)
        self.proxy.expose("bank", self.bank)
        self.proxy.expose("bank.roach", self.bank.roach)
        self.proxy.expose("bank.valon", self.bank.valon)

    def run(self):
        self.proxy.run_loop(watchdogfn=self.bank._watchdog)

    def stop_thread(self):
        self.proxy.quit_loop()


def handler(signum, frame):
    print "Handling singal", signum
    for thread in THREADS:
        thread.stop_thread()

    print "ending..."
    exit(0)

class FlagColorguard():
    def __init__(self, log_dir=""): # when creating the logdir it was hard to decide where to put it with dealer/player structure however

        self.threads = []
        self.bankNames = []
        self.baseURL = "tcp://0.0.0.0:%i"
        self.processRunning = False
        self.logDir = log_dir

        dibas_dir = os.getenv("DIBAS_DIR")
        if dibas_dir is None:
            print "FlagColorguard: Error, dibas_dir environment variable not set..."

        config_file = dibas_dir + "/etc/config/dibas.conf"
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(config_file))

    def addBanks(self, bank_names):

        if bank_names is None:
            print "FlagColorguard: bank_names cannot be empty."
            return

        for bank_name in bank_names:
            print "FlagColorguard:: Adding ", bank_name
            self.bankNames.append(bank_name)
            port = self.config.getint(bank_name, 'player_port')
            url = self.baseURL % port

            t = BankThread(bank_name=bank_name, url=url, sim=False, logDir=self.logDir)
            self.threads.append(t)

    def startPlayers(self):
        for t in self.threads:
            t.start()
        self.processRunning = True

    def getThreads(self):
        return self.threads

    def getActiveBanks(self):
        return self.bankNames

    def isRunning(self):
        return self.processRunning


# signal.signal(signal.SIGINT, handler)
# sys.stdout = ThreadPrinter()
#
# THREADS = []
# BANKNAMES = ["BANKA"]
# BASEURL = "tcp://0.0.0.0:%i"
#
# dibas_dir = os.getenv("DIBAS_DIR")
# config_file = dibas_dir + "/etc/config/dibas.conf"
# config = ConfigParser.ConfigParser()
# config.readfp(open(config_file))
#
# for bank_name in BANKNAMES:
#     port = config.getint(bank_name, 'player_port')
#     URL = BASEURL % port
#
#     t = BankThread(bank_name, URL, False)
#     THREADS.append(t)
#
# for t in THREADS:
#     t.start()
#
# while True:
#     #print "waiting..."
#     time.sleep(1)

# bank_name = "BANKA"
# player_port = config.getint(bank_name.upper(), 'player_port')
# url = "tcp://0.0.0.0:%i" % player_port
#
# ctx = zmq.Context()
# proxy = ZMQJSONProxyServer(ctx, url)
# bank = Bank(bank_name, False)
#
# proxy.expose("bank", bank)
# proxy.expose("bank.roach", bank.roach)
# proxy.expose("bank.valon", bank.valon)
#
#




