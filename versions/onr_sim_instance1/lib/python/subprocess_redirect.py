from threading import Thread, currentThread
import subprocess



class ThreadPrinter:
    def __init__(self, name=None, base_filename='./output/'):
        self.name = name
        self.fhs = {}
        self.baseFilename = base_filename
        self.extension = '.log'

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
    #     baseFilename = "./output/"
    #     fname = baseFilename + str(self.name) + ".log"
    #     f = open(fname, "a")
    #     return f

process = "ls"

#f = open('./output/A.log', 'a')

outside_process = subprocess.Popen(process, stdin=subprocess.PIPE, stdout=ThreadPrinter("A"))

