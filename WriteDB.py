"""
Created on Mon April 06 2022
@author: Silvana R Nobre
"""

from ReadDB import GlobalVar
from support.dbquery import SqlAlchemy

# delete all the nodes that were created by InferenceEngine
def DeleteNodes():
    SqlAlchemy.RunSql("Delete from Nodes where PreviousNode <> 0")


# insert all the nodes that were created by InferenceEngine
def InsertNewNodes():
    DeleteNodes()
    Nodes2Add = []
    Insert = {}
    for NodeId, NodeData in GlobalVar.NodeDic.items():
        if NodeData.PreviousNode != 0:
            del NodeData.__dict__['_type']
            for attr, value in NodeData.__dict__.items():
                Insert[attr] = value
            Node = SqlAlchemy.Base.classes.Nodes(**Insert)
            Node.NodeId = NodeId
            Nodes2Add.append(Node)
    SqlAlchemy.Session.add_all(Nodes2Add)
    SqlAlchemy.Session.commit()

