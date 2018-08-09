import sys, signal, time
from FlagColorguard import FlagColorguard, ThreadPrinter
from optparse import OptionParser

def handler(signum, frame):
    print "FlagColorguard:: received signal", signum
    for thread in cg.getThreads():
        thread.stop_thread()

    cg.processRunning = False

signal.signal(signal.SIGINT, handler)

p = OptionParser()
p.set_usage('CGRemote.py BANK_NAMEs [options]')
p.add_option('-d', '--directory', dest='dir', type='str', help='directory for log files')

opts, args = p.parse_args(sys.argv[1:])

banks = []
for bank_name in args:
    banks.append(bank_name)


logDir = opts.dir

sys.stdout = ThreadPrinter(dir_name=logDir)

cg = FlagColorguard(log_dir=logDir)
cg.addBanks(bank_names=banks)
cg.startPlayers()

while cg.isRunning():
    time.sleep(1)

print "FlagColorguard:: Exiting..."





