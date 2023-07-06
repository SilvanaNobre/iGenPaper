"""
Created on Mon April 04 2022
@author: Silvana R Nobre
"""

from support.dbquery import SqlAlchemy

class BaseClass(object):
    def __init__(self, classtype):
        self._type = classtype

def ClassFactory(name, AttrList, BaseClass=BaseClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # argnames variable is the one passed to the ClassFactory call
            if key not in AttrList:
                raise TypeError("Argument %s not valid for %s"
                                % (key, self.__class__.__name__))
            setattr(self, key, value)
        BaseClass.__init__(self, name[:-len("Class")])

    newclass = type(name, (BaseClass,), {"__init__": __init__})
    return newclass

class RuleClass(object):
    def __init__(self, LastIntervention : str, NextIntervention: str, StopGoing: bool):
        self.LastIntervention = LastIntervention
        self.NextIntervention = NextIntervention
        self.StopGoing = StopGoing

class RuleConditionClass(object):
    def __init__(self, RuleId, IfOrThen, RuleVar, RuleExpression):
        self.RuleId = RuleId
        self.IfOrThen = IfOrThen
        self.RuleVar = RuleVar
        self.RuleExpression = RuleExpression

class TableSearchParamsClass(object):
    def __init__(self, Table, Key, Return):
        self.Table = Table
        self.Key = Key
        self.Return = Return

class GlobalVar(object):
    class NodeClass:
        pass

    FirstNode = 1
    LastNode = 99
    ParamDic = {}
    IntTDic = {}
    NodeDic = {}
    RuleDic = {}
    UpdateVarDic = {}
    NodeAttributeDic = {}
    SearchTableDic = {}
    RuleConditionList = []
    NodeClassAttrNameList = []
    NodeClassAttrStr = ' '

# read General Parameters from the database
def GetGlobalVar(dbAnalysisArea) -> list:
    SqlString = "SELECT Variable, ParameterValue " + \
                "FROM Parameter " + \
                f"WHERE AArea = {dbAnalysisArea}"
    rows = SqlAlchemy.Select(SqlString)
    LocalDic = {}
    for row in rows:
        LocalDic[row[0]] = row[1]
    return LocalDic

def GetSearchTableParams(tbName) -> TableSearchParamsClass:
    tParams = TableSearchParamsClass(" ", " ", [])

    getTableInfoStr = 'pragma table_info(' + tbName + ')'
    fieldLst = SqlAlchemy.Select(getTableInfoStr)
    tbPrimaryKey =   [fields for fields in fieldLst if fields.pk > 0]
    tbReturnFields = [fields for fields in fieldLst if fields.pk == 0]

    tParams.Table = tbName
    tbPrimaryKey = [fields.name for fields in tbPrimaryKey]
    tParams.Key = ",".join(tbPrimaryKey)
    tParams.Return = [fields.name for fields in tbReturnFields]
    return tParams

# read the node variables with the update Rules
def GetVariables() -> dict:
    class ClassVar(object):
        def __init__(self, VarType, InitValue, UpdateRule, DisplayInHover, HoverFormat):
            self.VarType = VarType
            self.InitValue = InitValue
            self.UpdateRule = UpdateRule
            self.DisplayInHover = DisplayInHover
            self.HoverFormat = HoverFormat

    SqlString = "SELECT VariableId, VarType, NoIntNodeUpdateRule, " + \
                "DisplayInHover, HoverFormat " + \
                "FROM Variable " + \
                "WHERE Scope = 'Node' "
    rows = SqlAlchemy.Select(SqlString)
    LocalDic = {}
    for row in rows:
        if row[1][:3] == 'Int' or row[1][:3] == 'int':
            iV = 0
        elif row[1][:3] == 'Str' or row[1][:3] == 'str':
            iV = 'x'
        elif row[1][:3] == 'Dec' or row[1][:3] == 'dec':
            iV = 0.1
        else:
            iV = '0'
        LocalDic[row[0]] = ClassVar(VarType=row[1], InitValue=iV, UpdateRule=row[2],
                                    DisplayInHover=row[3], HoverFormat=row[4])
    return LocalDic

def GetClassAttrStr(VarDic) -> str:
    cAttr = "PreviousNode=-1, LiNode=-1"
    for k in VarDic.keys():
        cAttr = cAttr + ", " + k + "="
        if VarDic[k].VarType[:3] == 'Str' or VarDic[k].VarType[:3] == 'str':
            cAttr = cAttr + "'"
        cAttr = cAttr + str(VarDic[k].InitValue)
        if VarDic[k].VarType[:3] == 'Str' or VarDic[k].VarType[:3] == 'str':
            cAttr = cAttr + "'"
    return cAttr

def GetNameAttrList(VarDic) -> list:
    nList = []
    nList.append("PreviousNode")
    nList.append("LiNode")
    for k in VarDic.keys():
        nList.append(k)
    return nList

# read Nodes from the database
def GetInitialNodes(dbAnalysisArea) -> dict:
    FieldList = GlobalVar.NodeClassAttrNameList
    LastItem = len(FieldList)
    FieldStr = "n.NodeId"
    ClassStr = ""
    i = 1
    for f in FieldList:
        FieldStr = FieldStr + ", n." + f
        ClassStr += f + "=row[" + str(i) + "]"
        if i < LastItem:
            ClassStr += ","
        i += 1
    FieldStr = FieldStr + " "
    SqlString = f"SELECT {FieldStr} " \
                "FROM Nodes as n INNER JOIN MgmUnit mu on mu.MgmUnitId = n.MgmUnit " + \
                f"WHERE n.NodeType = 'Initial' and mu.AArea = {dbAnalysisArea}"
    rows = SqlAlchemy.Select(SqlString)
    LocalDic = {}
    for row in rows:
        LocalDic[row[0]] = eval("GlobalVar.NodeClass(" + ClassStr + ")")
    return LocalDic

def GetAllNodes(dbAnalysisArea) -> dict:
    GlobalVar.UpdateVarDic = GetVariables()
    GlobalVar.NodeClassAttrNameList = GetNameAttrList(GlobalVar.UpdateVarDic)
    GlobalVar.NodeClass = ClassFactory("NodeClass", GlobalVar.NodeClassAttrNameList)
    # this Str will be used whenever we need to instantiate a NodeClass variable
    GlobalVar.NodeClassAttrStr = GetClassAttrStr(GlobalVar.UpdateVarDic)

    FieldList = GlobalVar.NodeClassAttrNameList
    LastItem = len(FieldList)
    FieldStr = "n.NodeId"
    ClassStr = ""
    i = 1
    for f in FieldList:
        FieldStr = FieldStr + ", n." + f
        ClassStr += f + "=row[" + str(i) + "]"
        if i < LastItem:
            ClassStr += ","
        i += 1
    FieldStr = FieldStr + " "
    SqlString = "SELECT " + FieldStr + \
                "FROM Nodes as n INNER JOIN MgmUnit mu on mu.MgmUnitId = n.MgmUnit " + \
                f"WHERE mu.AArea = {dbAnalysisArea}"
    rows = SqlAlchemy.Select(SqlString)
    LocalDic = {}
    for row in rows:
        LocalDic[row[0]] = eval("GlobalVar.NodeClass(" + ClassStr + ")")
    return LocalDic

def GetDrawNodes(dbAnalysisArea, VarToShow, WhatToShow, drawHorizon) -> dict:
    FieldList = GlobalVar.NodeClassAttrNameList
    LastItem = len(FieldList)
    FieldStr = "n.NodeId"
    ClassStr = ""
    i = 1
    for f in FieldList:
        FieldStr = FieldStr + ", n." + f
        ClassStr += f + "=row[" + str(i) + "]"
        if i < LastItem:
            ClassStr += ","
        i += 1
    FieldStr = FieldStr + " "
    SqlString = "SELECT " + FieldStr + \
                "FROM Nodes as n INNER JOIN MgmUnit mu on mu.MgmUnitId = n.MgmUnit " + \
                f"WHERE mu.AArea = {dbAnalysisArea} and n.{VarToShow} = {WhatToShow} " + \
                f"  AND n.Period <= {drawHorizon} "
    rows = SqlAlchemy.Select(SqlString)
    LocalDic = {}
    for row in rows:
        LocalDic[row[0]] = eval("GlobalVar.NodeClass(" + ClassStr + ")")
    return LocalDic

# read the Intervention Types from the database
def GetInterventionTypes() -> dict:
    LocalDic = {}
    for row in SqlAlchemy.Select("SELECT IntTypeId, NodeColor FROM InterventionType"):
        LocalDic[row[0]] = row[1]
    return LocalDic

# read the rules from database
def GetRules(dbAnalysisArea) -> dict:
    SqlString = "SELECT r.RuleId, r.LastIntervention, r.NextIntervention, r.StopGoing " + \
                "FROM Rule r INNER JOIN ValidRule v on v.Rule = r.RuleId " + \
                f"WHERE v.AArea = {dbAnalysisArea}"
    rows = SqlAlchemy.Select(SqlString)
    LocalDic = {}
    for row in rows:
        if row[3] in ('F', 'False', 'false', 'falso', 'Falso', '0', 'N', 'n'):
            boolVar = False
        else:
            boolVar = True
        LocalDic[row[0]] = RuleClass(row[1], row[2], boolVar)
    return LocalDic

# read the rule conditions from database
def GetRuleConditions(dbAnalysisArea) -> list:
    SqlString = "SELECT r.RuleId, r.IfOrThen, r.RuleVar, r.RuleExpression " + \
                "FROM RuleCondition r INNER JOIN ValidRule v on v.Rule = r.RuleId " + \
                f"WHERE v.AArea = {dbAnalysisArea}"
    rows = SqlAlchemy.Select(SqlString)
    LocalList = []
    for row in rows:
        LocalList.append(RuleConditionClass(row[0], row[1], row[2], row[3]))
    return LocalList

# read Yield Tables or similar tables from database
def GetSearchTable() -> dict:
    TableDic = {}
    TableValueDic = {}

    tableStr = GlobalVar.ParamDic["SearchTable"]
    tables = tableStr.split(",")
    tables = [tName.strip() for tName in tables]

    for item in tables:
        tSearchParams = GetSearchTableParams(item)
        for returnField in tSearchParams.Return:
            ValueDic = {}
            SqlValueString = "SELECT " + tSearchParams.Key + " , " + returnField + " " + \
                              " FROM " + tSearchParams.Table
            values = SqlAlchemy.Select(SqlValueString)
            for rowv in values:
                KeyLength = len(rowv) - 1
                ExprToEvaluate = "("
                for i in range(0, KeyLength):
                    ExprToEvaluate = ExprToEvaluate + "rowv[" + str(i) + "]"
                    if i < KeyLength - 1:
                       ExprToEvaluate = ExprToEvaluate + ","
                ExprToEvaluate = ExprToEvaluate + ")"
                KeyValue = eval(ExprToEvaluate)
                ValueIndex = KeyLength
                Value = rowv[ValueIndex]
                ValueDic[KeyValue] = Value
            TableValueDicKey = tSearchParams.Table + "_" + returnField
            TableValueDic[TableValueDicKey] = ValueDic
    return TableValueDic

# main function that gets all data needed in Inference Engine
def GetData(dbAnalysisArea):
    GlobalVar.ParamDic = GetGlobalVar(dbAnalysisArea)
    GlobalVar.UpdateVarDic = GetVariables()
    GlobalVar.NodeClassAttrNameList = GetNameAttrList(GlobalVar.UpdateVarDic)
    GlobalVar.NodeClass = ClassFactory("NodeClass", GlobalVar.NodeClassAttrNameList)

    # this Str will be used whenever we need to instantiate a NodeClass variable
    GlobalVar.NodeClassAttrStr = GetClassAttrStr(GlobalVar.UpdateVarDic)

    GlobalVar.NodeDic = GetInitialNodes(dbAnalysisArea)
    GlobalVar.IntTDic = GetInterventionTypes()
    GlobalVar.RuleDic = GetRules(dbAnalysisArea)
    GlobalVar.RuleConditionList = GetRuleConditions(dbAnalysisArea)
    GlobalVar.SearchTableDic = GetSearchTable()

    # FirstNode
    GlobalVar.FirstNode = min(GlobalVar.NodeDic.keys())
    # LastNode
    GlobalVar.LastNode = max(GlobalVar.NodeDic.keys())
# end of def GetData(dbFileName,dbAnalysisArea):

# main function that gets all data needed just to draw a tree
def GetDataToDraw(dbAnalysisArea, UnitToShow):
    GlobalVar.UpdateVarDic = GetVariables()
    GlobalVar.NodeClassAttrNameList = GetNameAttrList(GlobalVar.UpdateVarDic)
    GlobalVar.NodeClass = ClassFactory("NodeClass", GlobalVar.NodeClassAttrNameList)

    # this Str will be used whenever we need to instantiate a NodeClass variable
    GlobalVar.NodeClassAttrStr = GetClassAttrStr(GlobalVar.UpdateVarDic)

    GlobalVar.ParamDic = GetGlobalVar(dbAnalysisArea)
    GlobalVar.NodeDic = GetDrawNodes(dbAnalysisArea, GlobalVar.ParamDic['DBVarToShow'], UnitToShow, GlobalVar.ParamDic['HorizonToDraw'])
    GlobalVar.IntTDic = GetInterventionTypes()







# end of def GetDataToDraw(dbFileName,dbAnalysisArea):
