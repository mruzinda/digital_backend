from player import Bank, BankData
import ConfigParser
from threading import Thread, currentThread

import os, sys, signal, time

import zmq
from ZMQJSONProxy import ZMQJSONProxyServer

class ThreadPrinter:
    def __init__(self, printer_name=None, base_filename="./output/"):

        self.name = printer_name
        self.fhs = {}
        self.baseFilename= base_filename
        self.extension = ".log"

    def write(self, value):

        f = self.getFID()
        f.write(value)
        f.close()

    def getFilename(self):

        fname = ""
        if self.name is None:
            fname = currentThread().name
        else:
            fname = self.name

        return fname


    def getFID(self):

        f = self.fhs.get(self.name)
        fname = self.getFilename()
        if f is None:
            file = self.baseFilename + fname + self.extension
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


class BankThread(Thread):
    def __init__(self, bank_name=None, url=None, sim=False):

        Thread.__init__(self, name=bank_name)

        self.bank = Bank(bank_name=bank_name.upper(), simulate=sim)

        ctx = zmq.Context()
        self.proxy = ZMQJSONProxyServer(ctx, url)
        self.proxy.expose("bank", self.bank)
        self.proxy.expose("bank.roach", self.bank.roach)
        self.proxy.expose("bank.valon", self.bank.valon)

    def run(self):
        self.proxy.run_loop(watchdogfn=self.bank._watchdog)

    def stop_thread(self):
        print "running quit thread"
        self.proxy.quit_loop()


def handler(signum, frame):
    print "Handling singal", signum
    for thread in THREADS:
        thread.stop_thread()

    print "ending..."
    exit(0)

class FlagColorguard():
    def __init__(self):

        self.threads = []
        self.bankNames = []
        self.baseURL = "tcp://0.0.0.0:%i"

        dibas_dir = os.getenv("DIBAS_DIR")
        if dibas_dir is None:
            print "FlagColorguard: Error, dibas_dir environment variable not set..."

        config_file = dibas_dir + "/etc/config/dibas.conf"
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(config_file))

    def addBanks(self, bank_names):
        """
        
        :param bank_names: 
        :return: 
        """
        if bank_names is None:
            print "FlagColorguard: bank_names cannot be empty."
            return

        for bank_name in bank_names:
            print "FlagColorguard: Adding ", bank_name
            self.bankNames.append(bank_name)
            port = self.config.getint(bank_name, 'player_port')
            url = self.baseURL % port

            t = BankThread(bank_name=bank_name, url=url, sim=False)
            self.threads.append(t)

    def startPlayers(self):
        for t in self.threads:
            t.start()

    def getThreads(self):
        return self.threads

    def getActiveBanks(self):
        return self.bankNames


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




