import MySQLdb
#from pyslalib import slalib as s

statusFieldNames = [
       "scan_type",
       "scan_length",
       "remaining",
       "scan_sequence",
       "scan_number",
       "start_time",
       "time_to_start",
       "az_commanded",
       "el_commanded",
       "az_actual",
       "el_actual",
       "ant_motion",
       "time_to_target",
       "major_type",
       "minor_type",
       "major",
       "minor",
       "epoch",
       "receiver",
       "rcvr_pol",
       "freq",
       "if_rest_freq",
       "cal_state",
       "switch_period",
       "first_if_freq",
       "source",
       "observer",
       "last_update",
       "utc",
       "utc_date",
       "data_dir",
       "lst",
       "status",
       "time_to_set",
       "j2000_major",
       "j2000_minor"]

class FlagCommander:
    def __init__(self,sim=False):
        if sim:
            url="vegas-hpc10.gb.nrao.edu"
            user="gbtstatus"
            passwd="w3bqu3ry"
            db = "gbt_status_sim"
        else:
            url="gbtdata.gbt.nrao.edu"
            user="gbtstatus"
            passwd="w3bqu3ry"
            db = "gbt_status"

        self.db = self.db = MySQLdb.connect(passwd=passwd,db=db,host=url,user=user)
        self.cursor = self.db.cursor()
        self.fieldNames = statusFieldNames

        self.dbFields = []
        self.emptyField = "no value"
        self.query = ""
        self.query_result = {}

        self.prepQuery()

    def prepQuery(self):
        try:
            queryList = ""

            # Query all the columns in the table
            tmp_query = "Show Columns from status"
            self.cursor.execute(tmp_query)
            columns = self.cursor.fetchall()

            # Append to class db fields
            for i in columns:
                self.dbFields.append(i[0])

            # prepare a query for the fields we want
            for f in self.fieldNames:
                if f not in self.dbFields:
                    pass
                else:
                    queryList = queryList + f + ","

            # piece query together
            queryList = queryList[0:-1]
            self.query = "select %s from status" % queryList

        except:
            print "FC: Database connection error..."
            pass

    def executeQuery(self):
        try:
            # run query
            self.cursor.execute(self.query)
            values = self.cursor.fetchall()[0]
        except:
            print "FC: Database connection error..."

        for v, k in enumerate(self.fieldNames):
            if k not in self.dbFields:
                self.query_result[k] = self.emptyField
            else:
                self.query_result[self.fieldNames[v]] = values[v]

if __name__=="__main__":
    fc = FlagCommander()
    fc.executeQuery()

    print "exiting..."
