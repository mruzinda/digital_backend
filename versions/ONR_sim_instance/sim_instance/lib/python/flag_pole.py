import shm_wrapper as shm
#import pyfits
import _possem
import hashpipe_key


#def header_from_string(str):
#    """
#    header_from_string(str):
#        Convert an input string (which should be the ASCII header from
#            a FITS HFU) into an instantiation of a pyfits 'Header' class.
#    """
#    cl = cardlist_from_string(str)
#    return pyfits.Header(cl)


#def card_from_string(str):
#    """
#    card_from_string(str):
#        Return a pyfits 'Card' based on the input 'str', which should
#            be an 80-character 'line' from a FITS header.
#    """
#    card = pyfits.Card()
#    return card.fromstring(str)


#def cardlist_from_string(str):
#    """
#    cardlist_from_string(str):
#        Return a list of pyfits 'Cards' from the input string.
#            'str' should be the ASCII from a FITS header.
#    """
#    cardlist = []
#    numcards = len(str) / 80
#    for ii in range(numcards):
#        str_part = str[ii * 80:(ii + 1) * 80]
#        if str_part.strip().find("END") == 0:
#            break
#        else:
#            cardlist.append(card_from_string(str_part))
#    return cardlist


class FlagPole:

    def __init__(self, instance_id=None, status_semid=None, status_key=None):
        print "\nBFBE: FlagPole:: Initializing shmem..."
        # Init and IPC key information
        if instance_id is None:
            instance_id = 0
        else:
            instance_id = instance_id
        if status_key is not None:
            self.status_key = status_key
        else:
            self.status_key = hashpipe_key.hashpipe_status_key(instance_id)

        if status_semid is not None:
            self.status_semid = status_semid
        else:
            self.status_semid = hashpipe_key.hashpipe_status_semname(instance_id)

        print "BFBE: FlagPole:: instance_id=%d" % instance_id
        print "BFBE: FlagPole:: status_key=%x" % self.status_key
        print "BFBE: FlagPole:: status_semid: %s" % self.status_semid

        # Create a handle to shared memory
        self.status_buffer = shm.SharedMemoryHandle(self.status_key)
        self.sem = _possem.sem_open(self.status_semid, _possem.O_CREAT, 00644, 1)
        #print "BFBE: FlagPole:: FlagPole.sem", self.sem

        # Create a header to hold the data read from shared memory
        self.hdr = None
        self.read()

    #def __getitem__(self, key):
    #    return self.hdr[key]

    #def keys(self):
    #    return [k for k, v in self.hdr.items()]

    #def values(self):
    #    return [v for k, v in self.hdr.items()]

    #def items(self):
    #    return self.hdr.items()

    def lock(self):
        return _possem.sem_wait(self.sem)

    def unlock(self):
        return _possem.sem_post(self.sem)

    def read(self):
        self.lock()
        #self.hdr = header_from_string(self.status_buffer.read())
        self.hdr = self.status_buffer.read()
        self.unlock()

    def write(self):
        self.lock()
        self.status_buffer.write(self.hdr)
        #self.stat_buf.write(repr(self.hdr.ascard)+"END"+" "*77)
        #self.status_buffer.write(self.hdr.tostring()) # pyfits 3.1
        self.unlock()

    #def update(self, key, value, comment=None):
        #self.hdr.update(key, value, comment)
        #self.hdr[key] = (value, comment) # for pyfits 3.1.2

    #def show(self):
    #    for k, v in self.hdr.items():
    #        print "'%8s' :"%k, v
    #    print ""
