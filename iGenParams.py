"""
Created on Mon April 04 2022
@author: Silvana R Nobre
"""

import json


class iGenParams(object):
    DBFile = 'xx'
    DBAArea = 1
    db_root = 'sqlite:///db/{0}'

    def __init__(self, JasonFileName):
        with open(JasonFileName, "r") as f:
            jsonContent = f.read()
        RomeroInicialization = json.loads(jsonContent)
        iGenParams.DBFile = RomeroInicialization['DBFile']
        iGenParams.DBAArea = int(RomeroInicialization['DBAArea'])
        iGenParams.db_root = RomeroInicialization['db_root']

    @classmethod
    def Update(cls, JasonFileName):
        x = {"DBFile": cls.DBFile,
             "DBAArea": str(cls.DBAArea),
             "db_root": cls.db_root}
        with open(JasonFileName, "w") as f:
            f.write(json.dumps(x, indent=4))
