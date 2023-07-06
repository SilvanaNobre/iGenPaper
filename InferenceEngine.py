"""
Created on Mon April 04 2022

@author: Silvana R Nobre
"""
import ReadDB
from ReadDB import GlobalVar
import ExtFunctions as exf
import math



# -------------------------------------------------------------------------------------------------
# Creation of an Intervention Node based on a Rule Base
# the InterventionNodeId will be key of that new node
# the NothingNodeId is the node where we are when some rule matched
# the PreviousNodeId is the previousNode of the NothingNode we were and the one we are creating now
# the LINodeId is the last intervention node that happened before this node we are creating now
# Period is the Period we are creating the node at
# Rule is the RuleId fo the match rule - the Match function processed the if's of the rule
# and now we are going to process the then's of the Match rule

def SearchTable(TableName, TableKey, ReturnValue):
    TableValueDicKey = TableName + "_" + ReturnValue
    #print('TableName='+TableName+'  TableKey='+str(TableKey)+'  ReturnValue='+ReturnValue)
    Value = GlobalVar.SearchTableDic[TableValueDicKey][TableKey]
    return Value

def CreateIntNode(InterventionNodeId, NoInterventionNodeId, PreviousNodeId, LINodeId, Period, Rule):
    # Rule is a list, the element[0] is the RuleId, [1]LastIntervention, [2]NextIntervention
    # Period when we are creating the IntNode
    # LiNodeId is the last Intervention Node
    # PreviousNodeId is the previous Node of both:
    #                              the one we are creating now, and the NoInt node (our reference)
    # InterventionNodeId is the one we are creating just now
    # ---------------------------------------------------------------------------------------------
    niNode = GlobalVar.NodeDic[NoInterventionNodeId]
    intNode = eval("GlobalVar.NodeClass(" + GlobalVar.NodeClassAttrStr + ")")
    # ---------------------------------------------------------------------------------------------
    # we use here the gv.RuleConditionList that has the following fields:
    # RuleId, IfOrThen, RuleVar, RuleExpression
    # first we filter the list for the rule we are working with here
    # ----------------------------------------------------------------------------------------------
    ThenStatements = []
    thenItem = ReadDB.RuleConditionClass(0, 'Then', 'var', '=')
    ThenStatements = [thenItem for thenItem in GlobalVar.RuleConditionList if
                      (thenItem.RuleId == Rule[0] and thenItem.IfOrThen == 'Then')]
    # ----------------------------------------------------------------------------------------------
    # our reference node for calculation now is the NoInterventionNode -> noNode
    # we are replacing the var name for noNode.var
    # gv.UpdateVarDic is a dic of all node variables we can use in "Then" and "Update" statements
    # because users can use other variables in a Statement, we have to surch for all of them
    # ----------------------------------------------------------------------------------------------
    for thenItem in ThenStatements:
        ThenStatement = thenItem.RuleExpression
        ThenVar = thenItem.RuleVar
        for k in [keys for keys in GlobalVar.UpdateVarDic.keys()]:
            ThenStatement = ThenStatement.replace(":" + k, "niNode." + k)
        ExprToExec = "intNode." + ThenVar + " " + ThenStatement
        exec(ExprToExec)
    # complete intNode data
    intNode.PreviousNode = PreviousNodeId
    intNode.LiNode = LINodeId
    intNode.Period = Period
    intNode.Intervention = Rule[1].NextIntervention
    GlobalVar.NodeDic[InterventionNodeId] = intNode


# end def CreateIntNode(NodeId,PreviousNode,Period):

# --------------------------------------------------------------------------------------------------
# this function tests if the variable values of the NothingNode of the NothingNodeId we are analysing
# matches the entire set of "if's" of an specific Rule
def Match(Rule, NoInterventionNodeId) -> bool:
    # Rule is a list, the element[0] is the RuleId
    # The NoInterventionNodeId is the reference node where the variables have the values we need here
    # ---------------------------------------------------------------------------------------------
    noNode = GlobalVar.NodeDic[NoInterventionNodeId]
    # ---------------------------------------------------------------------------------------------
    # we use here the gv.RuleConditionList that has the following fields:
    # RuleId, IfOrThen, RuleVar, RuleExpression
    # first we filter the list for the rule we are going to test the match here
    # ---------------------------------------------------------------------------------------------
    MatchConditions = []
    ifItem = ReadDB.RuleConditionClass(0, 'If', 'var', '==')
    MatchConditions = [ifItem for ifItem in GlobalVar.RuleConditionList if
                       (ifItem.RuleId == Rule[0] and ifItem.IfOrThen == 'If')]
    MatchResult = True
    # -------------------------------------------------------------------------------------------------
    # for each "if" of the MatchCondition we replace the var name by noNode.var
    # because our reference now is the noNode that has the same var values of a node we could create
    # if any condition fails, it means this rule does not match
    # -------------------------------------------------------------------------------------------------
    for ifItem in MatchConditions:
        IfVar = ifItem.RuleVar
        IfRule = ifItem.RuleExpression
        for k in [keys for keys in GlobalVar.UpdateVarDic.keys()]:
            IfRule = IfRule.replace(":" + k, "noNode." + k)
        IfResult = eval(IfRule)
        if not IfResult:
            MatchResult = False
    return MatchResult


# end def Match(Rule,NodeId):

# -------------------------------------------------------------------------------------------------
# Now we are creating a NothingNode from a PreviosNode
# We are creating this NothingNode in this Period
# we always save the Last Intervention Node (LiNodeId) that comes before this NothingNode
def CreateNoInterventionNode(NoInterventionNodeId, PreviousNodeId, LiNodeId, Period):

    # ---------------------------------------------------------------------------------------------
    pvNode = GlobalVar.NodeDic[PreviousNodeId]
    niNode = eval("GlobalVar.NodeClass(" + GlobalVar.NodeClassAttrStr + ")")
    # ---------------------------------------------------------------------------------------------
    # Users can use any node variable in the update rules
    # Here we are substituting all variables by a pvNode.var
    # because the rules refers to values of the previous node
    # gv.UpdateVarDic is a dic of all node variables we can use in "Then" and "Update" statements
    # ---------------------------------------------------------------------------------------------
    for k1 in [keys for keys in GlobalVar.UpdateVarDic.keys()]:
        # replace all variables, not only the key one
        NewUpdateRule = GlobalVar.UpdateVarDic[k1].UpdateRule
        for k2 in [keys for keys in GlobalVar.UpdateVarDic.keys()]:
            NewUpdateRule = NewUpdateRule.replace(":" + k2, "pvNode." + k2)
        # and then we execute the rule to calculate the new values for the node we are inserting now
        ExecStr = "niNode." + k1 + " " + NewUpdateRule
        exec(ExecStr)
    # complete the information of the niNode
    niNode.PreviousNode = PreviousNodeId
    niNode.LiNode = LiNodeId
    GlobalVar.NodeDic[NoInterventionNodeId] = niNode


# end  CreateNoInterventionNode(NothingNodeId, PreviousNodeId, LiNodeId, Period):

# -------------------------------------------------------------------------------------------------
# from one InterventionNode (LiNodeId) we now open it into other nodes
# we filter the rules that can be applied to this node
# first, we create a NothingNode and update the variables
# then, with these values we use the Match function for each valid rule
# we test each rule to see if they Match the variables we have just calculated
# when there is a match, we create an intervention Node.
# -------------------------------------------------------------------------------------------------
def OpenNode(LiNodeId):
    # ---------------------------------------------------------------------------------------------
    LastIntervention = GlobalVar.NodeDic[LiNodeId].Intervention
    LiPeriod = GlobalVar.NodeDic[LiNodeId].Period
    # filter RuleList by Intervention
    LiRuleList = list(GlobalVar.RuleDic.items())
    LiRuleList = [rItem for rItem in LiRuleList if rItem[1].LastIntervention == LastIntervention]

    Period = LiPeriod
    PreviousNodeId = LiNodeId
    GenNodesCount = 0
    NoInterventionNodeId = 0
    InterventionNodeId = 0
    KeepGoing = True

    while True:
        Period = Period + 1

        if Period <= int(GlobalVar.ParamDic['Horizon']):
            NoInterventionNodeId = GlobalVar.LastNode + 1
            GlobalVar.LastNode = NoInterventionNodeId
            # Create a Nothing Node linked to this Node
            # The new node comes with updated values
            # ---------------------------------------------------------------------------------
            CreateNoInterventionNode(NoInterventionNodeId, PreviousNodeId, LiNodeId, Period)
            # ---------------------------------------------------------------------------------
            if Period > 0:
                for Rule in LiRuleList:
                    # if Match...
                    if Match(Rule, NoInterventionNodeId):
                        InterventionNodeId = GlobalVar.LastNode + 1
                        GlobalVar.LastNode = InterventionNodeId
                        # Create a intervention Node linked to Previous Node
                        # The new node comes with updated values
                        # -------------------------------------------------------------------------
                        CreateIntNode(InterventionNodeId, NoInterventionNodeId, PreviousNodeId, LiNodeId,
                                      Period, Rule)
                        GenNodesCount = GenNodesCount + 1
                        # Verify if this is a rule that asks to stop
                        if Rule[1].StopGoing:
                            KeepGoing = False
                    # end if Mach
                # end for Rule in LiRuleList:
            # if Period > 0:
            if KeepGoing:
               PreviousNodeId = NoInterventionNodeId
            else:
               del GlobalVar.NodeDic[NoInterventionNodeId]
               break
        else:
            break
    print("NoInterventionNodeId=",NoInterventionNodeId)
    print("InterventionNodeId=",InterventionNodeId)
    #print("LiNodeId=",LiNodeId)
    return GenNodesCount


# end def OpenNode(NodeId):

# Create a Tree is the main algorithm of the Inference Engine
# From a set of Initial Nodes, creates a tree of alternatives
# This algorithm aims to open nodes until it is no longer possible
# Every opened node, it sets as 'Opened'
# When it finds a node that cannot be open, it sets this node as 'Final'.
# ---------------------------------------------------------------------------------------------
def BuildATree():
    # ---------------------------------------------------------------------------------------------
    NodesToOpen = []
    while True:
        NodesToOpen = []
        # transform NodeDic into a List of tuples
        NodesToOpen = [(nKey, nItem) for nKey, nItem in GlobalVar.NodeDic.items() if nItem.NodeType in ('Initial', 'Middle')]
        NodesToOpenCount = len(NodesToOpen)

        if NodesToOpenCount > 0:
            for Node in NodesToOpen:
                # call the OpenNode procedure
                GenNodesCount = OpenNode(Node[0])
                if GenNodesCount == 0:
                    # if no intervention nodes can be generated from this node, it is a final one
                    # update the global Nodes dictionary
                    GlobalVar.NodeDic[Node[0]].NodeType = 'Final'
                else:
                    GlobalVar.NodeDic[Node[0]].NodeType = 'Opened'
                    # end for Node in NodesToOpen:
        else:
            break
    pass
            # break where there is no nodes in the list, NoOfNodesToOpen = 0
    # end while True:
    return GlobalVar.LastNode
# end of BuildATree()
