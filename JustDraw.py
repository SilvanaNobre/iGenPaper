"""
Created on Mon April 06 2022
@author: Silvana R Nobre

--db_root "s --sqlite:///db/{0}" --fname scatter.html --web
"""
from support import DrawATree
from support.dbquery import SqlAlchemy
import ReadDB
from iGenParams import iGenParams
from ReadDB import GlobalVar
import time

if __name__ == '__main__':
    iGenParams('RomeroInitData.json')
    SqlAlchemy(iGenParams.db_root.format(iGenParams.DBFile), [])

    # Init.DbFile comes from initialization variables read in ReadInit.GetInit
    # open the connection with the Database
    ReadDB.GetDataToDraw(iGenParams.DBAArea, GlobalVar.ParamDic['DBToShow'])
    if GlobalVar.ParamDic['WhereToDraw'] == 'html':
        start = time.time()
        fig = DrawATree.DrawATreePlotly(Title=GlobalVar.ParamDic['ModelTitle'],
                                        SubTitle=GlobalVar.ParamDic['DBToShow'])
        print(time.time() - start)
        # get the database name
        # file name is projectName + MgmUnit Name
        fileName = 'Results/'+GlobalVar.ParamDic['ProjectName']+GlobalVar.ParamDic['DBToShow']+'.html'
        fig.write_html(fileName)
    else:
        start = time.time()
        DrawATree.DrawATreeMatplotlib()
        print(time.time() - start)
# end JustDraw
