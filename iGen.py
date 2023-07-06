"""
Created on Mon April 04 2022
@author: Silvana R Nobre

--db_root "sqlite:///db/{0}"
"""
from support.dbquery import SqlAlchemy
import ReadDB as db
import WriteDB as wdb
from InferenceEngine import BuildATree
from iGenParams import iGenParams
import time


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start = time.time()
    print("start" + time.strftime("%b %d %Y %H:%M:%S", time.gmtime(start)))

    # read variables to Initialization
    iGenParams('RomeroInitData.json')

    # Init.DbFile comes from initialization variables read in ReadInit.GetInit
    # open the connection with the Database
    SqlAlchemy(iGenParams.db_root.format(iGenParams.DBFile), ['Nodes'])

    # Get all data needed from the database
    # InitVar.DBAArea also comes from initialization procedure
    db.GetData(iGenParams.DBAArea)
    datEnd = time.time()
    print("Reding data:" + time.strftime("%b %d %Y %H:%M:%S", time.gmtime(datEnd)))
    eTime = datEnd - start
    print("Reading data elapsed time " + str(eTime) + "seconds")

    # create the Tree of alternatives from the Inference engine algorithm
    NumNodes = 0
    NumNodes = BuildATree()
    # -- print elapsed time
    print("generated nodes: "+str(db.GlobalVar.LastNode))
    genEnd = time.time()
    print("Generation ending:" + time.strftime("%b %d %Y %H:%M:%S", time.gmtime(genEnd)))
    eTime = genEnd - datEnd
    print("generation elapsed time " + str(eTime) + "seconds")

    # Save results - the generated nodes - into the database
    wdb.InsertNewNodes()
    # -- print elapsed time
    insEnd = time.time()
    print("Insert ending:" + time.strftime("%b %d %Y %H:%M:%S", time.gmtime(insEnd)))
    eTime = insEnd - genEnd
    print("insert elapsed time " + str(eTime) + "seconds")
