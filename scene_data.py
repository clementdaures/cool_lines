import json
from maya import cmds
import pprint

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *


class GlobalSceneData(QObject):
    request_ui_sync = Signal()

    def __init__(self, *args, **kwargs):
        super(GlobalSceneData, self).__init__()

        self.global_lines_data= {}
        self.scene_data_node= None
        self.scene_data_node_default_name= 'CoolLines_SceneData'

        self.checkSceneDataNode()


    def checkSceneDataNode(self):

        if cmds.objExists(self.scene_data_node_default_name):
            print('SceneDataNode found!')
            self.scene_data_node= self.scene_data_node_default_name
            self.loadSceneData()
            return True
            
        else:
            print('Cant find data! Creating a new node so you can draw... :)')
            self.createSceneDataNode()
            return False
            

    def createSceneDataNode(self):
        # Create Node to store data. Data will be empty at first.
        self.scene_data_node= cmds.scriptNode( st=0, bs='', n=self.scene_data_node_default_name, stp='python')
    

    def addLineData(self, line_data):
        self.global_lines_data[line_data["name"]]= line_data
        self.request_ui_sync.emit()
        self.saveSceneData()


    def getGlobalLinesData(self):
        return self.global_lines_data


    def removeLineData(self, line_key):
        self.global_lines_data.pop(line_key)
        self.saveSceneData()
        self.request_ui_sync.emit()


    def updateLineData(self, line_key, new_line_data, update_name= False):

        print('*********')
        print('Updating Line Data:')

        if update_name:
            self.global_lines_data.pop(line_key)
            self.global_lines_data[new_line_data["name"]]= new_line_data
            pprint.pprint(self.global_lines_data[new_line_data["name"]])

        else:
            self.global_lines_data[line_key]= new_line_data
            pprint.pprint(self.global_lines_data[line_key])

        self.saveSceneData()
        self.request_ui_sync.emit()


    def saveSceneData(self):
        #Dump data to node:
        if self.scene_data_node:
            cmds.scriptNode(self.scene_data_node, e=True, bs=json.dumps(self.global_lines_data))
        else:
            cmds.error("Cannot save scene data because there is no scene data node..")


    def loadSceneData(self):
        #Attempt Loading data from node:
        if self.scene_data_node:
            scene_data_str= cmds.scriptNode(self.scene_data_node, q=True, bs=True)
        else:
            cmds.error("Cannot load scene data because there is no scene data node..")
            return

        
        if scene_data_str:
            scene_data= json.loads(scene_data_str)

            print('******************')
            print('Loaded Data:')
            print(scene_data)

            self.rebuildData(scene_data)
            self.request_ui_sync.emit()
        else:
            print("Skipping loading, data empty !")


    def rebuildData(self, scene_data):
        for current_line_name in list(scene_data.keys()):
            self.global_lines_data[current_line_name]= dict(scene_data[current_line_name])
        print('Data rebuilt successfull')