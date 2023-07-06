from support.dbquery import SqlAlchemy
def iGenQueries(dbAArea:int, dfName)->str:
    sqlDic = {'dfParams': f"Select * from Parameter where AArea = {dbAArea} and Scope in ('iGen','All') ",
              'dfIntType': "Select * from InterventionType",
              'dfVar': "Select VariableId,Required,VarType,NoIntNodeUpdateRule,DisplayInHover from Variable where Scope = 'Node' ",
              'dfIniState': f"Select n.* from Nodes n inner join MgmUnit u on u.MgmUnitId = n.MgmUnit and u.AArea = {dbAArea} where n.PreviousNode = 0 ",
              'dfRules': f"Select * from Rule where RuleId in (select Rule from ValidRule where AArea = {dbAArea} )",
              'dfCond': f"Select * from RuleCondition where RuleId in (select Rule from ValidRule where AArea = {dbAArea} )",
              'dfNodes': f"Select n.* from Nodes n inner join MgmUnit u on u.MgmUnitId = n.MgmUnit and u.AArea = {dbAArea} ",
              }
    return sqlDic[dfName]
def getiGenDFs(dbAArea: int):
    dfParams = SqlAlchemy.getDataframeResultSet(iGenQueries(dbAArea,'dfParams'))
    dfIntType = SqlAlchemy.getDataframeResultSet(iGenQueries(dbAArea,'dfIntType'))
    dfVar = SqlAlchemy.getDataframeResultSet(iGenQueries(dbAArea,'dfVar'))
    dfIniState = SqlAlchemy.getDataframeResultSet(iGenQueries(dbAArea,'dfIniState'))
    dfRules = SqlAlchemy.getDataframeResultSet(iGenQueries(dbAArea,'dfRules'))
    dfCond = SqlAlchemy.getDataframeResultSet(iGenQueries(dbAArea,'dfCond'))
    dfNodes = SqlAlchemy.getDataframeResultSet(iGenQueries(dbAArea,'dfNodes'))
    return dfParams, dfIntType, dfVar, dfIniState, dfRules, dfCond, dfNodes

def iMathQueries(dbAArea:int, dfName)->str:
    sqlDic = {'dfParamsM': f"Select * from Parameter where AArea = {dbAArea} and Scope in ('iMath','All') ",
              'dfVar': "Select VariableId,Required,VarType,NoIntNodeUpdateRule,DisplayInHover from Variable where Scope = 'Node' ",
              'dfNodes': f"Select n.* from Nodes n inner join MgmUnit u on u.MgmUnitId = n.MgmUnit and u.AArea = {dbAArea} ",
              'dfAcctVar': "Select * from AcctVar",
              'dfRHSSet': "Select * from RHSSet",
              'dfRHSValue': "Select * from RHSValue",
              'dfModelBlock': "Select * from ModelBlock",
              'dfScenario': f"Select * from Scenario where AArea = {dbAArea}",
              'dfSceModel': f"Select m.* from ScenarioModel m inner join Scenario s on s.SceName = m.SceName and s.AArea = {dbAArea}"
              }
    return sqlDic[dfName]

def getiMathDFs(dbAArea:int):
    dfParamsM = SqlAlchemy.getDataframeResultSet(iMathQueries(dbAArea,'dfParamsM'))
    dfVar = SqlAlchemy.getDataframeResultSet(iMathQueries(dbAArea,'dfVar'))
    dfAcctVar = SqlAlchemy.getDataframeResultSet(iMathQueries(dbAArea,'dfAcctVar'))
    dfRHSSet =    SqlAlchemy.getDataframeResultSet(iMathQueries(dbAArea,'dfRHSSet'))
    dfRHSValue =  SqlAlchemy.getDataframeResultSet(iMathQueries(dbAArea,'dfRHSValue'))
    dfModelBlock = SqlAlchemy.getDataframeResultSet(iMathQueries(dbAArea,'dfModelBlock'))
    dfScenario =  SqlAlchemy.getDataframeResultSet(iMathQueries(dbAArea,'dfScenario'))
    dfSceModel =  SqlAlchemy.getDataframeResultSet(iMathQueries(dbAArea,'dfSceModel'))
    dfNodes = SqlAlchemy.getDataframeResultSet(iMathQueries(dbAArea,'dfNodes'))
    return dfParamsM, dfVar, dfAcctVar, dfRHSSet, dfRHSValue, dfModelBlock, dfScenario, dfSceModel, dfNodes

def getTheAArea(dbAArea:int)->str:
   qryGUI = f'Select AAreaDescription from AnalysisArea where AAreaId = {dbAArea}'
   dbAArea = SqlAlchemy.SelectFirst(qryGUI)
   return dbAArea[0]

def getAAreaId(dbAArea:str)->int:
   qryGUI = f"Select AAreaId from AnalysisArea where AAreaDescription = '{dbAArea}'"
   dbAArea = SqlAlchemy.SelectFirst(qryGUI)
   return dbAArea[0]

def getAAreas()->list:
   qryGUI = 'Select AAreaDescription from AnalysisArea'
   dbAAreasLst = []
   dbAAreas = SqlAlchemy.Select(qryGUI)
   for row in dbAAreas:
       dbAAreasLst.append(row[0])
   return dbAAreasLst

def getRules():
   qryGui = 'Select min(RuleId) MinRule, max(RuleId) MaxRule from RuleCondition'
   lstRange = SqlAlchemy.SelectFirst(qryGui)
   return lstRange[0], lstRange[1]

def getMinUnit():
   qryGui = 'Select min(MgmUnitId) MinUnit from MgmUnit'
   lstRange = SqlAlchemy.SelectFirst(qryGui)
   return lstRange[0]

def getRHSMin():
   qryGui = 'Select min(RHSSetName) RHSMin from RHSSet'
   lstRange = SqlAlchemy.SelectFirst(qryGui)
   return lstRange[0]

def getSceMin():
    qryGui = 'Select min(SceName) SceMin from Scenario'
    lstRange = SqlAlchemy.SelectFirst(qryGui)
    return lstRange[0]
def getRHSValueFiltered(valName):
    sqlStr = "Select * from RHSValue where RHSName = '" + valName + "'"
    df = SqlAlchemy.getDataframeResultSet(sqlStr)
    return df

def getSceModelFiltered(dbAArea, valName):
    sqlStr = f"Select m.* from ScenarioModel m inner join Scenario s on s.SceName = m.SceName where s.AArea = {dbAArea} and m.SceName = '{valName}' "
    df = SqlAlchemy.getDataframeResultSet(sqlStr)
    return df

def getRuleCond(dbAArea, ruleId):
    sqlStr = f"Select * from RuleCondition where RuleId in (select Rule from ValidRule where AArea = {dbAArea} ) and RuleId = {ruleId} "
    df = SqlAlchemy.getDataframeResultSet(sqlStr)
    return df

def SingleRowUpdate(table, idNames, ids, column, value):
    qryGui = f"update {table} set {column} = "
    if type(value) == str:
        ValuePart = value
        NewValue = ''
        while ValuePart.find("'") > -1:
           index = ValuePart.find("'") + 1
           NewValue = NewValue + ValuePart[:index] + "'"
           ValuePart = ValuePart[index:]
        NewValue = NewValue + ValuePart
        qryGui = qryGui + "'" + NewValue + "' where "
    else:
        qryGui = qryGui + f"{value} where "

    idl = len(idNames)
    for ix in range(0, idl):
        if ix > 0:
           qryGui = qryGui + ' and '
        if type(ids[ix]) == str:
           qryGui = qryGui + idNames[ix] + " = '" + ids[ix] + "'"
        else:
           qryGui = qryGui + f"{idNames[ix]} = {ids[ix]} "

    print(qryGui)
    SqlAlchemy.RunSql(qryGui)

def SingleRowInsert(table, colNames, colValues):
    columns = ', '.join(colNames)
    qryGui = f"insert into {table} set ({[columns]}) values ( "
    concatValues = ""
    numCol =len(colValues)
    countCol = 0
    for value in colValues:
        countCol += 1
        if type(value) == str:
           NewValue = "''"+value+"''"
        else:
            NewValue = str(value)
    concatValues += NewValue
    if countCol < numCol:
        concatValues =+ ", "

    qryGui = qryGui + concatValues + ")"
    print(qryGui)
    SqlAlchemy.RunSql(qryGui)

def getSqlFormulation(Formulation:str, dbAnalysisArea:int, Horizon:int) ->str:
    if Formulation == 'N':
       sqlString = "Select pn.MgmUnit, pn.nodeId previous, nn.NodeId next "+\
                "  from nodes pn "+\
                "       inner join nodes nn "+\
                "          on nn.PreviousNode = pn.NodeId "+\
                "       inner join MgmUnit u "+\
                "          on u.MgmUnitId = pn.MgmUnit "+\
                f" where u.AArea = {dbAnalysisArea}" +\
                "  order by pn.nodeId, nn.NodeId "
    elif Formulation == '1':
       sqlString = "Select pn.MgmUnit, pn.NodeId previous, nn.NodeId next "+\
                   "  from nodes pn "+\
                   f"       inner join MgmUnit u on u.MgmUnitId = pn.MgmUnit and u.AArea = {dbAnalysisArea} "+\
                   f"       inner join Nodes nn on nn.MgmUnit = pn.MgmUnit and nn.Period = {Horizon} "+\
                   " where pn.PreviousNode = 0 "+\
                   " order by pn.MgmUnit, pn.NodeId "
    elif Formulation == '2':
       sqlString = "select pn.MgmUnit, pn.NodeId, nn.NodeId "+\
                   "  from nodes pn "+\
                   f" inner join MgmUnit u on u.MgmUnitId = pn.MgmUnit and u.AArea = {dbAnalysisArea} "+\
                   " inner join nodes nn "+\
                   "    on nn.linode = pn.nodeid and "+\
                   f"      (nn.intervention <> 'ni' or (nn.intervention ='ni' and nn.period = {Horizon})) "
    return sqlString

def GetCoABlock(dbAnalysisArea:int,Horizon:int,ModelIndexes:str,NodeDic:dict,Formulation) ->(list,dict):

    def VarSequence(nId,Formulation) ->list:
        Node = nId
        VarSeqLst = []
        if Formulation == '1':
           while True:
               pvNode = NodeDic[Node].PreviousNode
               if pvNode > 0:
                  VarSeqLst.append(Node)
                  Node = pvNode
               else:
                  break
        elif Formulation == '2':
           while True:
               pvNode = NodeDic[Node].PreviousNode
               liNode = NodeDic[Node].LiNode
               if pvNode != liNode:
                  VarSeqLst.append(Node)
                  Node = pvNode
               else:
                  VarSeqLst.append(Node)
                  break
        elif Formulation == 'N':
            VarSeqLst.append(Node)
        return VarSeqLst

    def VarIndexes(nId) ->list:
        iList = []
        iList.append(nId)
        iStr = 'x['+str(nId)
        for item in IndexesList:
            strToEval = 'NodeDic[nId].'+item
            xEval = NodeDic[1].MgmUnit
            xEval = eval(strToEval)
            iList.append(xEval)
            iStr += ','+str(xEval)
        iStr += ']'
        return iList, iStr

    VarSeqDic = {}
    IndexesList = [x.strip() for x in ModelIndexes.split(",")]
    SqlString = getSqlFormulation(Formulation, dbAnalysisArea, Horizon)
    rows = SqlAlchemy.Select(SqlString)
    # rowList Elements=['MgmUnit', 'PreviousNode', 'pnIndexes', 'NextNodesStr', 'NextNodesLst', 'nnIndexes', 'ModelRowStr'])
    LocalList = []
    RowList = []
    ModelRow = -1
    PreviousNode = -1
    NextNodesList = []
    NextNodesStr: str = ' '
    for row in rows:
        # row[1] previousNode - if changed
        if PreviousNode != row[1]:
            if ModelRow > -1:
               pnIdxList, pnIdxStr = VarIndexes(PreviousNode)
               pnIdxStr += ' >= '
               # -----------------------pnIndexes
               RowList.append(pnIdxList)
               NextNodesStr = '(' + ','.join(str(x) for x in NextNodesList) + ')'
               # -----------------------NextNodesStr
               RowList.append(NextNodesStr)
               # -----------------------NextNodesLst
               RowList.append(NextNodesList)
               # -----------------------nnIndexes and ModelLine
               ModelRowStr = pnIdxStr
               nnIndexes = []
               ixCount = 0
               ixLen = len(NextNodesList)
               for nnIdx in NextNodesList:
                   nnIdxList, nnIdxStr = VarIndexes(nnIdx)
                   nnIndexes.append(nnIdxList)
                   ModelRowStr += str(nnIdxStr)
                   ixCount += 1
                   if ixCount < ixLen:
                       ModelRowStr += ' + '
               RowList.append(nnIndexes)
               RowList.append(ModelRowStr)

               LocalList.append(RowList)

            NextNodesList = []
            ModelRow += 1
            PreviousNode = row[1]
            RowList = []
            #-----------------------MgmUnit
            RowList.append(row[0])
            #-----------------------PreviousNode
            RowList.append(row[1])
            NextNodesList.append(row[2])
        else:
            NextNodesList.append(row[2])
        VarSeqDic[(row[0],row[2])] = VarSequence(row[2],Formulation)
        pass
    pass
    return LocalList, VarSeqDic

def VarSeqLst(VarSeqDic:dict)->list:
    SeqVarLst = []
    for keyVar, SeqLst in VarSeqDic.items():
        keyVarStr = ",".join(str(x) for x in keyVar)
        SeqLstStr = ",".join(str(x) for x in SeqLst)
        SeqVarLst.append([keyVarStr,SeqLstStr])
    return SeqVarLst


