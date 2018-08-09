from Tkinter import *

class Ahh(Frame):
    def __init__(self,master=None):
            Frame.__init__(self,master)
            self.var = IntVar()
            self.var2 = [0,0]
            for k in range(0,2):
                self.var2[k] = IntVar()
            #self.var2 = IntVar()
            self.c0 = Button(master, text="Expand", command=self.All)
            self.c0.grid(row=0, column=0, sticky=W)
            self.c1 = Button(master, text="Maybe", command=self.Nopl)
            self.c1.grid(row=1, column=0, sticky=W)
            self.c2 = Checkbutton(master, text="Okay", variable=self.var2[0])
            self.c2.grid(row=2, column=0, sticky=W)
            self.c3 = Checkbutton(master, text="Wow", variable=self.var2[1])
            self.c3.grid(row=3, column=0, sticky=W)
            self.c4 = Button(master, text="Print!", command=self.getValues)
            self.c4.grid(row=4, column=0, sticky=W)

            self.c5 = Label(master, text="List: ")
            self.c5.grid(row=5, column=0, sticky=W)
            arrVal = ["Hey","Listen!","You","Better","Work!"]
            self.default_var = StringVar(master)
            self.default_var.set(arrVal[0])
            self.c6 = apply(OptionMenu, (master,self.default_var) + tuple(arrVal))
            self.c6.grid(row=5, column=1, sticky=W)
            
            self.c7 = Button(master, text="Option val", command=self.getOption)
            self.c7.grid(row=6, column=0, sticky=W)
 
   # def Czero(self):
   #     print "C0", self.c0 # self.var.get()
   #     print "C2", self.var2.get()

    def getValues(self):
        if self.var2[0].get() == 1:
            print "C2: ", self.c2
        if self.var2[1].get() == 1:
            print "C3: ", self.c3

    def getOption(self):
        print "Option chosen: ", self.default_var.get()

    def All(self):
        self.var2[0].set(1)
        self.var2[1].set(1)

    def Nopl(self):
        self.var2[0].set(0)
        self.var2[1].set(0)

root = Tk()
root.geometry("200x200")
Ahh(master=root).grid(row=0,column=0,sticky=W)
root.mainloop()
