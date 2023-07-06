from taipy.gui import Gui, notify
import pandas as pd
import webbrowser
import os
import GUIReadDB as gdb

from iGenParams import iGenParams
from support.dbquery import SqlAlchemy
import ReadDB as db
from support import DrawATree
import WriteDB as wdb
from InferenceEngine import BuildATree

# pages definition
page_1 = """
<|navbar|>
<|layout|columns=1 8|
    <|
<|{logo}|image|height=75px|width=150px|on_action=image_action|>    
    |>
    <|
#Romero Multicriteria    
    |>
|>
<br/>
<|layout|columns=1 3 3|gap=40px|
    <|
<|{logoiGen}|image|height=125px|width=175px|>
<br/>
Available Databases:<br/> 
<|{dbName}|selector|lov={dbOptions}|dropdown|propagate=True|on_change=changeDB|>
<br/>
Analysis Area:<br/>
<|{dbAArea}|selector|lov={dbAAOptions}|dropdown|propagate=True|on_change=changeDBAArea|>
<br/><br/>
<|run iGen|button|height=125px|width=175px|on_action=iGen_action|>
<br/>
<|{iGenStatus}|><br/>
<|{iGenNodes}|>
<br/><br/>
    |>
    <|
##### Project : <|{st_ModelTitle}|>
General Parameters:<br/><br/>
<|{st_dfParams}|table|rebuild|editable[ParameterId]=False|editable[Variable]=False|on_edit=edit_action|page_size=10|width=100%|columns=ParameterId;ParameterDescription;Variable;ParameterValue|>
<|Refresh|button|id=st_dfParams|on_action=tableRefresh|>
    |>
    <|
Intervention Types:<br/><br/>
<|{st_dfIntType}|table|rebuild|editable[IntTypeId]=False|filter=True|on_edit=edit_action|page_size=10|width=80%|columns=IntTypeId;IntTypeDescription;NodeColor|>
<|Refresh|button|id=st_dfIntType|on_action=tableRefresh|>
<br/><br/>    
    |>        
|>
"""

page_2 = """
<|navbar|>
##### Project : <|{st_ModelTitle}|>
<|Variables|expandable|expanded=False|
<|{st_dfVar}|table|rebuild|filter=True|editable[VariableId]=False|editable[VarType]=False|on_edit=edit_action|page_size=20|width=90%|columns=VariableId;VarType;NoIntNodeUpdateRule;DisplayInHover|>
<|Refresh|button|id=st_dfVar|on_action=tableRefresh|>
|>

<|Initial State|expandable|expanded=False|
<|{st_dfIniState}|table|rebuild|filter=True|editable[NodeId]=False|editable[PreviousNode]=False|editable[LiNode]=False|on_edit=edit_action|page_size=20|width=90%|>
<|Refresh|button|id=st_dfIniState|on_action=tableRefresh|>
|>

<|Rules|expandable|expanded=False|
<|layout|columns= 2 3|
   <|
<|{st_dfRules}|table|rebuild|filter=True|editable[RuleId]=False|on_edit=edit_action|on_action=select_action|page_size=20|width=90%|columns=RuleId;LastIntervention;NextIntervention;RuleDescription;StopGoing|>
<|Refresh|button|id=st_dfRules|on_action=tableRefresh|>
   |>
   <|
<|{st_rFilter}|number|label=filter rule|on_change=ruleId_onchange|>
<br/>
<|{st_dfCondFiltered}|table|rebuild|editable[RuleId]=False|editable[IfOrThen]=False|editable[RuleVar]=False|on_edit=edit_action|page_size=20|width=90%|columns=RuleId;IfOrThen;RuleVar;RuleExpression|group_by[IfOrThen]|apply[RuleVar]=count|>
   |>
|>
|>
"""

page_3 = """
<|navbar|>
##### Project : <|{st_ModelTitle}|>
<|layout|columns=1 6|
   <|
<br/>
Filter<|{st_uFilter}|number|label=Unit|on_change=Unit_onchange|>
<br/><br/>
<|Draw the Tree Graph|button|height=125px|width=175px|on_action=drawgraph_action|>
<br/>
<|{drawStatus}|>
<br/><br/>
<|Show the Tree Graph|button|height=125px|width=175px|on_action=graph_action|>
   |>
   <|
<|{st_dfNodesFiltered}|table|page_size=20|width=100%|filter=True|size=small|>
<|Refresh|button|id=st_dfNodesFiltered|on_action=tableRefresh|>
   |>
|>
"""

class gvGUI(object):
   # variables definition
   dfParams = pd.DataFrame()
   dfIntType = pd.DataFrame()
   dfRules = pd.DataFrame()
   dfCond = pd.DataFrame()
   dfVar = pd.DataFrame()
   dfIniState = pd.DataFrame()
   dfNodes = pd.DataFrame()
   dfCondFiltered = pd.DataFrame()
   dfNodesFiltered = pd.DataFrame()
   RuleMin: int = 1
   RuleMax: int = 10
   RuleFilter: int = 1
   UnitMin: int = 1
   UnitFilter: int = 1
   gParams= {}
   GraphName: str ='xxx'
   GraphFileName: str = 'xxx'

def image_action(state):
    webbrowser.open("http://www.romeromulticriteria.com/")

def setUPiGenGUI(dbAArea:int):
   # read what we need from database
   gvGUI.dfParams, gvGUI.dfIntType, gvGUI.dfVar, gvGUI.dfIniState, gvGUI.dfRules, gvGUI.dfCond, gvGUI.dfNodes = gdb.getiGenDFs(dbAArea)
   gvGUI.RuleMin, gvGUI.RuleMax = gdb.getRules()
   gvGUI.MinUnit = gdb.getMinUnit()
   gvGUI.gParams = db.GetGlobalVar(1)

   gvGUI.RuleFilter = gvGUI.RuleMin
   gvGUI.dfCondFiltered = gdb.getRuleCond(dbAArea,gvGUI.RuleMin)

   gvGUI.UnitFilter = gvGUI.MinUnit
   NodesFilter = (gvGUI.dfNodes['MgmUnit'] == gvGUI.UnitFilter)
   gvGUI.dfNodesFiltered = gvGUI.dfNodes[NodesFilter]

   gvGUI.GraphName = os.path.join(cDir, gvGUI.gParams['ProjectName'])
   gvGUI.GraphFileName = gvGUI.GraphName + str(gvGUI.UnitFilter) + '.html'

def changeDB(state, var_name, value):
   CompleteDbName = iGenParams.db_root.format(value)
   SqlAlchemy(CompleteDbName, ['Nodes'])
   setUPiGenGUI(state.st_dbAArea)
   state.st_rFilter = gvGUI.RuleFilter
   state.st_uFilter = gvGUI.UnitFilter

   state.st_dfParams = gvGUI.dfParams
   state.st_dfIntType = gvGUI.dfIntType
   state.st_dfVar = gvGUI.dfVar
   state.st_dfIniState = gvGUI.dfIniState
   state.st_dfRules = gvGUI.dfRules
   state.st_dfCond = gvGUI.dfCond
   state.st_dfCondFiltered = gvGUI.dfCondFiltered
   state.st_dfNodes = gvGUI.dfNodes
   state.st_dfNodesFiltered = gvGUI.dfNodesFiltered
   state.st_ModelTitle = gvGUI.gParams['ModelTitle']
   state.st_ProjectName = gvGUI.gParams['ProjectName']
   state.st_GraphName = gvGUI.GraphName
   state.st_GraphFileName = gvGUI.GraphFileName
   state.iGenStatus = '.'
   state.iGenNodes = '.'

def changeDBAArea(state, var_name, value):
   state.st_dbAArea = gdb.getAAreaId(value)
   state.st_dfParams = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea, 'dfParams'))
   state.st_dfIniState = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea, 'dfIniState'))
   state.st_dfRules = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea, 'dfRules'))
   state.st_dfCond = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea, 'dfCond'))
   state.st_dfCondFiltered = filter_by_ruleId(state.st_dbAArea, state.st_rFilter)
   state.st_dfNodes = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea, 'dfNodes'))
   state.st_dfNodesFiltered = filter_by_Unit(state.st_dfNodes, state.st_uFilter)

def iGen_action(state):
   state.iGenStatus = 'I am running... wait'
   db.GetData(1)
   NumNodes = BuildATree()
   state.iGenNodes = str(NumNodes) + ' nodes generated'
   wdb.InsertNewNodes()
   state.st_dfNodes = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea,'dfNodes'))
   state.st_dfNodesFiltered = filter_by_Unit(state.st_dfNodes, state.st_uFilter)
   state.iGenStatus = 'I finished!!!'

def select_action(state, var_name, action, payload):
    # the keys of payload dict are 'action', 'index', 'args'
    if var_name == 'st_dfRules' and action == 'select_action':
       RuleId = state.st_dfRules.loc[payload['index'], 'RuleId']
       state.st_rFilter = str(RuleId)
       state.st_dfCondFiltered = filter_by_ruleId(state.st_dbAArea, state.st_rFilter)

def tableRefresh(state, id, action):
    if id == 'st_dfParams':
       state.st_dfParams = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea,'dfParams'))
    elif id == 'st_dfIntType':
       state.st_dfIntType = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea,'dfIntType'))
    elif id == 'st_dfVar':
       state.st_dfVar = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea,'dfVar'))
    elif id == 'st_dfIniState':
       state.st_dfIniState = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea,'dfIniState'))
    elif id == 'st_dfRules':
       state.st_dfRules = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea,'dfRules'))
       state.st_dfCond = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea,'dfCond'))
       state.st_dfCondFiltered = filter_by_ruleId(state.st_dbAArea,state.st_rFilter)
    elif id == 'st_dfNodesFiltered':
       state.st_dfNodes = SqlAlchemy.getDataframeResultSet(gdb.iGenQueries(state.st_dbAArea,'dfNodes'))
       state.st_dfNodesFiltered = filter_by_Unit(state.st_dfNodes, state.st_uFilter)

def edit_action(state, var_name, action, payload):
    #print(payload)
    if var_name == 'st_dfParams':
       state.st_dfParams.at[payload['index'],payload['col']] = payload['value']
       state.st_dfParams = state.st_dfParams
       ParameterId = state.st_dfParams.at[payload['index'],'ParameterId']
       gdb.SingleRowUpdate('Parameter', ['ParameterId'], [ParameterId], payload['col'], payload['value'])
    elif var_name == 'st_dfIntType':
       state.st_dfIntType.at[payload['index'],payload['col']] = payload['value']
       state.st_dfIntType = state.st_dfIntType
       IntTypeId = state.st_dfIntType.at[payload['index'],'IntTypeId']
       gdb.SingleRowUpdate('InterventionType',['IntTypeId'], [IntTypeId], payload['col'], payload['value'])
    elif var_name == 'st_dfVar':
       state.st_dfVar.at[payload['index'],payload['col']] = payload['value']
       state.st_dfVar = state.st_dfVar
       VariableId = state.st_dfVar.at[payload['index'],'VariableId']
       gdb.SingleRowUpdate('Variable',['VariableId'], [VariableId], payload['col'], payload['value'])
    elif var_name == 'st_dfIniState':
       state.st_dfIniState.at[payload['index'],payload['col']] = payload['value']
       state.st_dfIniState = state.st_dfIniState
       NodeId = state.st_dfIniState.at[payload['index'],'NodeId']
       gdb.SingleRowUpdate('Nodes',['NodeId'], [NodeId], payload['col'], payload['value'])
    elif var_name == 'st_dfRules':
       state.st_dfRules.at[payload['index'],payload['col']] = payload['value']
       state.st_dfRules = state.st_dfRules
       RuleId = state.st_dfRules.at[payload['index'],'RuleId']
       gdb.SingleRowUpdate('Rule',['RuleId'], [RuleId], payload['col'], payload['value'])
    elif var_name == 'st_dfCondFiltered':
       state.st_dfCondFiltered.at[payload['index'],payload['col']] = payload['value']
       state.st_dfCondFiltered = state.st_dfCondFiltered
       RuleId = state.st_dfCondFiltered.at[payload['index'],'RuleId']
       IfOrThen = state.st_dfCondFiltered.at[payload['index'],'IfOrThen']
       RuleVar = state.st_dfCondFiltered.at[payload['index'],'RuleVar']
       gdb.SingleRowUpdate('RuleCondition',['RuleId','IfOrThen','RuleVar'], [RuleId,IfOrThen,RuleVar], payload['col'], payload['value'])

def filter_by_ruleId(dbAArea, rFilter):
   dfFiltered = gdb.getRuleCond(dbAArea, rFilter)
   return dfFiltered
def ruleId_onchange(state, var_name, value):
   state.st_rFilter = int(value)
   state.st_dfCondFiltered = filter_by_ruleId(state.st_dbAArea, state.st_rFilter)

def filter_by_Unit(df, uFilter):
   NodesFilter = (df['MgmUnit'] == uFilter)
   dfFiltered = df[NodesFilter]
   return dfFiltered
def Unit_onchange(state, var_name, value):
   state.st_uFilter = int(value)
   state.st_dfNodesFiltered = filter_by_Unit(state.st_dfNodes, state.st_uFilter)

def graph_action(state):
   gvGUI.GraphFileName = gvGUI.GraphName + str(state.st_uFilter) + '.html'
   state.st_GraphFileName = gvGUI.GraphFileName
   webbrowser.open(state.st_GraphFileName)
def drawgraph_action(state):
   gvGUI.GraphFileName = gvGUI.GraphName + str(state.st_uFilter) + '.html'
   state.st_GraphFileName = gvGUI.GraphFileName
   state.drawStatus = 'I am drawing... wait... '
   db.GetDataToDraw(1, state.st_uFilter)
   fig = DrawATree.DrawATreePlotly(Title=gvGUI.gParams['ModelTitle'],
                                   SubTitle=state.st_uFilter)
   fig.write_html(state.st_GraphFileName)
   state.drawStatus = 'I finished drawing this unit.'


if __name__ == '__main__':
   pages = {
      "General_Parameters": page_1,
      "Forest_Definition": page_2,
      "Alternatives": page_3
   }

   # where is everything: images, graphs, database
   logo = 'images/ROMERO_Simbolo.png'
   logoiGen = 'images/iGen_logo.png'
   cDir = os.getcwd()
   GraphDir = "Results\\"
   cDir = os.path.join(cDir, GraphDir)
   drawStatus = '.'
   iGenStatus = '.'
   iGenNodes = '.'

   # available databases
   dbOptions = ['Pulp.db','American.db']

   #connect to the json database
   iGenParams('RomeroInitData.json')
   dbName = iGenParams.DBFile
   CompleteDbName = iGenParams.db_root.format(dbName)
   SqlAlchemy(CompleteDbName,['Nodes'])
   setUPiGenGUI(iGenParams.DBAArea)
   dbAArea = gdb.getTheAArea(iGenParams.DBAArea)
   dbAAOptions = gdb.getAAreas()

   st_rFilter = gvGUI.RuleFilter
   st_uFilter = gvGUI.UnitFilter

   st_dfParams = gvGUI.dfParams
   st_dfIntType = gvGUI.dfIntType
   st_dfVar = gvGUI.dfVar
   st_dfIniState = gvGUI.dfIniState
   st_dfRules = gvGUI.dfRules
   st_dfCond = gvGUI.dfCond
   st_dfCondFiltered = gvGUI.dfCondFiltered
   st_dfNodes = gvGUI.dfNodes
   st_dfNodesFiltered = gvGUI.dfNodesFiltered
   st_ModelTitle = gvGUI.gParams['ModelTitle']
   st_ProjectName = gvGUI.gParams['ProjectName']
   st_dbAArea = iGenParams.DBAArea
   st_GraphName = gvGUI.GraphName
   st_GraphFileName = gvGUI.GraphFileName

   gui = Gui(pages = pages)
   gui.run(dark_mode=False)

