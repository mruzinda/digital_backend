from player import *
import threading

BANKNAMES = ['BANKA', 'BANKB']
BANKS = []
PROXIES = []
THREADS = []

BASEURL = "tcp://0.0.0.0:%i"

DIBAS_DIR = os.getenv('DIBAS_DIR')

config_file = DIBAS_DIR + '/etc/config/dibas.conf'
config = ConfigParser.ConfigParser()
config.readfp(open(config_file))

for bankName in BANKNAMES:
    port = config.getint(bankName, 'player_port')
    URL = BASEURL % port

    ctx = zmq.Context()
    proxy = ZMQJSONProxyServer(ctx, URL)
    bank = Bank(bankName, False)

    proxy.expose("bank", bank)
    proxy.expose("bank.roach", bank.roach)
    proxy.expose("bank.valon", bank.valon)

    BANKS.append(bank)
    PROXIES.append(proxy)

    t = threading.Thread(target=proxy.run_loop, args=[bank._watchdog])
    THREADS.append(t)

for t in THREADS:
    t.start()

print "Waiting for threads to join"

for t in THREADS:
    t.join()