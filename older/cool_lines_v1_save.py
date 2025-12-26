import sys
import pprint
sys.path.append("INSTALLATION_PATH_REPLACE_STRING")

from importlib import reload
# reload()

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import shiboken2

from maya import cmds, mel
import maya.OpenMayaUI as omui

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from _widgets import cool_checkbox
reload(cool_checkbox)
from _widgets.cool_checkbox import CoolCheckbox

        
def mayaMainWindow():
    MainWindowPointer = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(MainWindowPointer), QWidget)


orange_theme= """
    QWidget {
        background-color: transparent;
        color: #fa901e;
        border: none;
    }
    QPushButton {
        background-color: #CD6C1B;
        border-radius: 10px;
        color: #F8D7BB;
        padding: 7px;
    }
    QPushButton:hover {
        background-color: #823F06;
    }
    QCheckBox {
        color: #fa901e;
    }
    QLineEdit {
        background-color: #462002;
        border: none;
        border-radius: 6px;
        color: #fa901e;
        padding: 3px;
    }
    QTextEdit {
        background-color: #4d4d4d;
        border: 1px solid #4d4d4d;
        color: #fa901e;
        padding: 3px;
    }
    QProgressBar {
        border: 1px solid #444444;
        border-radius: 7px;
        background-color: #2e2e2e;
        text-align: center;
        font-size: 10pt;
        color: white;
    }
    QProgressBar::chunk {
        background-color: #3a3a3a;
        width: 5px;
    }
    QScrollBar:vertical {
        border: none;
        background-color: #3a3a3a;
        width: 10px;
        margin: 16px 0 16px 0;
    }
    QScrollBar::handle:vertical {
        background-color: #fa901e;
        border-radius: 5px;
    }
    QScrollBar:horizontal {
        border: none;
        background-color: #fa901e;
        height: 10px;
        margin: 0px 16px 0 16px;
    }
    QScrollBar::handle:horizontal {
        background-color: #444444;
        border-radius: 5px;
    }
    QTabWidget {
        background-color: #2e2e2e;
        border: none;
    }
    QTabBar::tab {
        background-color: #2e2e2e;
        color: #fa901e;
        padding: 7px 7px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        border: none;
    }
 
    QTabBar::tab:selected, QTabBar::tab:hover {
        background-color: #fa901e;
        color: white;
    }

    QListWidget{
        border-radius: 10px;
        background-color: #462002;
    }

    QListView::item:selected{
        border-radius: 10px;
        background-color: #A3541A;
    }

    QMenu{
        background-color: #220E00;
    }

    QMenu::item:selected{
        background-color: #462002;
        color: #fa901e;
    }

    QMainWindow{
        background-color: #220E00;
    }"""

main_window_instance= None
paint_on_mesh= None
scene_lines_data= {}


def detectOrCreateShader():
    if cmds.objExists('outline_preview_shader'):
        pass
        #Get surface shader:
        sgq = cmds.listConnections("outline_preview_shader", d=True, et=True, t='shadingEngine')
        if sgq:
            shading_group= sgq[0]

    else:
        print('Preview Shader for outlines not found... Creating one.')
        shd = cmds.shadingNode('surfaceShader', name="outline_preview_shader", asShader=True)
        shdSG = cmds.sets(name='%sSG' % shd, empty=True, renderable=True, noSurfaceShader=True)
        cmds.connectAttr('%s.outColor' % shd, '%s.surfaceShader' % shdSG)
        shading_group = shdSG
    
    return shading_group



class DockableWindow(MayaQWidgetDockableMixin, QDialog):
    def __init__(self, parent=mayaMainWindow()): 
        super(DockableWindow, self).__init__(parent)

        self.setGeometry(100,100,200,200)

        #Making the window appear on top:
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Lines Utils')
        
        #Creating the tab widget:
        self.main_widget = mainWidget()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.main_widget)

        self.setStyleSheet(orange_theme)



class mainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        #Main Layout:
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.setStyleSheet('''font: 75 13pt "Microsoft YaHei UI"; ''')

        #####################################
        #Creation
        self.target_mesh_label = QLabel(self)
        self.target_mesh_label.setText('Target Mesh')
        
        self.set_target_mesh_hlayout = QHBoxLayout()

        self.set_target_mesh_lineedit = QLineEdit(self)
        self.set_target_mesh_button = QPushButton(self)
        self.set_target_mesh_button.setText('Set !')

        self.set_target_mesh_hlayout.addWidget(self.set_target_mesh_lineedit)
        self.set_target_mesh_hlayout.addWidget(self.set_target_mesh_button)


        self.create_paint_line_button = QPushButton(self)
        self.create_paint_line_button.setText('Line on Mesh')

        self.create_edge_line_button = QPushButton(self)
        self.create_edge_line_button.setText('Create Line from Edge')

        
        self.default_scale_lineedit = QLineEdit(self)
        validator = QRegExpValidator(QRegExp(r'[0-9]+.[0-9][0-9][0-9][0-9]'))
        self.default_scale_lineedit.setValidator(validator)
        self.default_scale_lineedit.setText('0.100')


        self.scene_content_label= QLabel(self)
        self.scene_content_label.setText("Scene Content")

        self.lines_list_widget = QListWidget(self)
        self.lines_list_widget.itemEntered.connect(self.selectTaperControlNode)

        
        #####################################
        #Organizing:
        self.main_layout.addWidget(self.target_mesh_label)
        self.main_layout.addLayout(self.set_target_mesh_hlayout)
        self.main_layout.addWidget(self.create_edge_line_button)

        self.main_layout.addWidget(self.create_paint_line_button)
        self.main_layout.addWidget(self.default_scale_lineedit)
        self.main_layout.addWidget(self.scene_content_label)
        self.main_layout.addWidget(self.lines_list_widget)

        self.main_layout.addStretch()


        #####################################
        #Connections:
        self.set_target_mesh_button.clicked.connect(self.setTargetMeshButtonClicked)
        self.create_edge_line_button.clicked.connect(self.createLineFromEdge)
        self.create_paint_line_button.clicked.connect(self.paintLineOnMesh)

        self.lines_list_widget.itemClicked.connect(self.selectTaperControlNode)

        #Creating the preview line shader:
        self.refreshList()

        
    def refreshList(self):
        
        self.lines_list_widget.clear()
        taper_control_nodes_list = cmds.ls(type='network')

        for current_taper_control_node in taper_control_nodes_list:

            if 'taper_control' in current_taper_control_node:
                print(f'Found : {current_taper_control_node}')
                current_title = current_taper_control_node.split('_')[0]
                print(current_title)

                # Exploring hierarchy to find mesh etc
                

            else:
                continue

            #Create item:
            current_line_item = QListWidgetItem()
            current_line_item.setData(1, current_taper_control_node)

            current_line_item_widget = lineListDisplayWidget(self, stroke_name= current_title)
            current_line_item.setSizeHint(current_line_item_widget.sizeHint())

            self.lines_list_widget.addItem(current_line_item)
            self.lines_list_widget.setItemWidget(current_line_item, current_line_item_widget)

            global scene_lines_data
            scene_lines_data[current_title]= {
                "taper_control_node": current_taper_control_node,

            }
            
        return

    
    def selectTaperControlNode(self, item):
        print(item)

        selected_taper_control_node = item.data(1)
        sweep_mesh_creator_node = cmds.listConnections(selected_taper_control_node + '.steps')[0]
        line_mesh_node = cmds.listConnections(sweep_mesh_creator_node + '.outMeshArray[0]')[0]

        print(sweep_mesh_creator_node)
        print(line_mesh_node)

        # Showing the "Selected !" Message on the selected mesh node
        cmds.headsUpMessage( 'Selected !', object=line_mesh_node )
        cmds.select(line_mesh_node, r=True)
        cmds.select(selected_taper_control_node, r=True)
   
        
    def setTargetMeshButtonClicked(self):
        
        global paint_on_mesh
        paint_on_mesh = cmds.ls(sl=True)[0]
        self.set_target_mesh_lineedit.setText(paint_on_mesh)


    def createLineFromEdge(self):

        polytocurve_result = cmds.polyToCurve(form=3,degree=1)
        polytocurve_curve = polytocurve_result[0]
        polytocurve_node = polytocurve_result[1]

        cmds.select(cl=True)
        cmds.select(polytocurve_curve)

        mel.eval('performSweepMesh 0;')

        #Finding the sweep mesh node:
        sweep_mesh_node = cmds.listConnections( polytocurve_curve + '.worldSpace[0]', d=True, s=False )[0]
        taper_control_node = createTaperController(sweep_mesh_node, start_scale_value= float(self.default_scale_lineedit.text()))

        cmds.addAttr(taper_control_node, at='enum', k=True, en = '______________', shortName='OPTIMIZATION', h=False)
        cmds.setAttr(taper_control_node + '.OPTIMIZATION', lock=True)

        cmds.addAttr(taper_control_node, at='bool', k=True, shortName='disable')


        cmds.select([polytocurve_curve, paint_on_mesh], r=True)
        print(cmds.CreateWrap())
        
        curve_shape = cmds.listRelatives(polytocurve_curve, s=True)[0]
        wrap_node = cmds.listConnections(curve_shape + '.create')[0]
        
        cmds.connectAttr(wrap_node + '.nodeState', sweep_mesh_node + '.nodeState')
        cmds.connectAttr(taper_control_node + '.disable', wrap_node + '.nodeState')

        cmds.delete(polytocurve_node)

        result_mesh = cmds.listConnections( sweep_mesh_node + '.outMeshArray[0]', d=True, s=False )[0]
        print(result_mesh, polytocurve_curve)
    
        cmds.group([result_mesh, polytocurve_curve], n='StrokeBundle')
        cmds.setAttr(polytocurve_curve + '.v', 0)

        
    def paintLineOnMesh(self):
        
        mel.eval("MakePaintable")
        mel.eval("PaintEffectsTool")
        
        # Help here ! https://www.regnareb.com/pro/2014/05/wait-for-user-input-in-maya/
        try:
            cmds.dynWireCtx("paintMesh")
        except RuntimeError:
            pass
        cmds.setToolTo("paintMesh")
        global paint_on_mesh
        paint_on_mesh = cmds.ls(sl=True)[0]
        cmds.scriptJob(runOnce=True, event=("SelectionChanged", f"executed_after_action({float(self.default_scale_lineedit.text())})"))



class lineListDisplayWidget(QWidget):
    def __init__(self, parent_dialog, stroke_name, *args,**kwargs):
        QWidget.__init__(self,*args,**kwargs)

        self.parent_dialog = parent_dialog


        self.main_layout = QHBoxLayout()
        self.main_layout.setSizeConstraint(QLayout.SetFixedSize) #Mandatory to scale correctly the widget
        self.setLayout(self.main_layout)

        self.asset_name_label = QLabel(self)
        
        self.line_name_label = QLabel(self)
        self.line_name_label.setText(stroke_name)

        
        self.disable_line_checkbox = CoolCheckbox(self)
        self.disable_line_checkbox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.disable_line_checkbox.setMinimumSize(30,15)
        self.disable_line_checkbox.setMaximumSize(30,15)
        self.disable_line_checkbox.setupAnimations(animation_curve=QEasingCurve.OutBounce, animation_duration=300, start_checked=True)


        self.main_layout.addWidget(self.line_name_label)
        self.main_layout.addWidget(self.disable_line_checkbox)
        

        self.setStyleSheet('''font: 75 10pt "Microsoft YaHei UI";''')
        


def executed_after_action(start_scale):

    cmds.headsUpMessage( 'Please Wait!', time=3.0 )
    cmds.setToolTo( 'moveSuperContext' )
    shape = cmds.listRelatives( cmds.ls(sl=True), fullPath=False, shapes=True)

    if cmds.objectType(shape) == 'stroke':
        print ("Stroke Done! Converting...")
        mel.eval("PaintEffectsToCurve;")

        print(shape)
        stroke_shape = shape[0]
        
        #Getting the converted curve:
        converted_curve_shape_node = cmds.listConnections(stroke_shape + '.outMainCurves[0]', d=True, s=False )[0]


        cmds.select(converted_curve_shape_node)
        mel.eval('rebuildCurve -ch 1 -rpo 1 -rt 0 -end 1 -kr 0 -kcp 0 -kep 1 -kt 0 -s 10 -d 3 -tol 0.0001;')
        mel.eval('performSweepMesh 0;')
        
        sweep_mesh_node = cmds.listConnections( converted_curve_shape_node + '.worldSpace[0]', d=True, s=False )[0]
        taper_control_node = createTaperController(sweep_mesh_node, paint_mode=True, start_scale_value=start_scale)

        cmds.addAttr(at='enum', k=True, en = '______________', shortName='OPTIMIZATION', h=False)
        cmds.setAttr(taper_control_node + '.OPTIMIZATION', lock=True)

        cmds.addAttr(at='bool', k=True, shortName='disable')


        result_mesh = cmds.listConnections( sweep_mesh_node + '.outMeshArray[0]', d=True, s=False )[0]
        

        #Organizing(Grouping elements):
        first_group = cmds.listRelatives(converted_curve_shape_node, p=True)[0]
        root_converted_curve_group = cmds.listRelatives(first_group, p=True)[0]

        stroke_transform = cmds.listRelatives(stroke_shape, p=True)[0]
        cmds.setAttr(stroke_transform + '.v', 0)
        cmds.setAttr(root_converted_curve_group + '.v', 0)

        cmds.group([result_mesh, root_converted_curve_group, stroke_transform], n='StrokeBundle')


        #Baking:
        stroke_transform = cmds.listRelatives(stroke_shape, p=True)[0]
        cmds.delete(stroke_shape)
        cmds.delete(stroke_transform)


        #Wrapping:
        cmds.select([converted_curve_shape_node, paint_on_mesh], r=True)
        print(cmds.CreateWrap())

        curve_shape = cmds.listRelatives(converted_curve_shape_node, s=True)[0]
        wrap_node = cmds.listConnections(curve_shape + '.create')[0]
        
        cmds.connectAttr(wrap_node + '.nodeState', sweep_mesh_node + '.nodeState')
        cmds.connectAttr(taper_control_node + '.disable', wrap_node + '.nodeState')

        global main_window_instance
        main_window_instance.main_widget.refreshList()


def createTaperController(sweep_mesh_node, paint_mode = False, start_scale_value = 1):
        
    #Create Default taper curve:
    taper_control_node = cmds.createNode('network', n=f'{sweep_mesh_node}_taper_control')

    cmds.addAttr(at='enum', k=True, en = '______________', shortName='GLOBAL', h=False)
    cmds.setAttr(taper_control_node + '.GLOBAL', lock=True)
    cmds.addAttr(at='float', k=True, min=0, shortName='scale_profile')

    cmds.addAttr(at='long', k=True, shortName='rotate_profile')
    cmds.setAttr(taper_control_node + '.rotate_profile', 0)

    cmds.addAttr(at='long', k=True, shortName='resolution')
    cmds.setAttr(taper_control_node + '.resolution', 4)

    cmds.setAttr(sweep_mesh_node + '.interpolationMode', 1)

    cmds.addAttr(at='long', k=True, shortName='steps')
    cmds.setAttr(taper_control_node + '.steps', 15)
    
    cmds.connectAttr(taper_control_node + '.steps', sweep_mesh_node + '.interpolationSteps')
    

    cmds.addAttr(at='enum', k=True, en = '______________', shortName='POINTS', h=False)
    cmds.setAttr(taper_control_node + '.POINTS', lock=True)
    cmds.addAttr(at='float', k=True, shortName='START_position')
    cmds.addAttr(at='float', k=True, min=0, shortName='START_value')
    cmds.addAttr(at='float', k=True, shortName='point1_position')
    cmds.addAttr(at='float', k=True, min=0, shortName='point1_value')
    cmds.addAttr(at='enum', k=True, en = 'None:Linear:Smooth:Spline', shortName='point1_interp')
    cmds.addAttr(at='float', k=True, shortName='point2_position')
    cmds.addAttr(at='float', k=True, min=0, shortName='point2_value')
    cmds.addAttr(at='enum', k=True, en = 'None:Linear:Smooth:Spline', shortName='point2_interp')
    cmds.addAttr(at='float', k=True, shortName='point3_position')
    cmds.addAttr(at='float', k=True, min=0, shortName='point3_value')       
    cmds.addAttr(at='enum', k=True, en = 'None:Linear:Smooth:Spline', shortName='point3_interp')    
    cmds.addAttr(at='float', k=True, min=0, shortName='END_position') 
    cmds.addAttr(at='float', k=True, min=0, shortName='END_value')
    


    cmds.setAttr(taper_control_node + '.scale_profile', 1)

    cmds.setAttr(taper_control_node + '.END_position', 1)
    cmds.setAttr(taper_control_node + '.point1_position', 0.2)
    cmds.setAttr(taper_control_node + '.point2_position', 0.5)
    cmds.setAttr(taper_control_node + '.point3_position', 0.8)

    cmds.setAttr(taper_control_node + '.point1_value', 1)
    cmds.setAttr(taper_control_node + '.point2_value', 1)
    cmds.setAttr(taper_control_node + '.point3_value', 1)

    cmds.setAttr(taper_control_node + '.point1_interp', 1)
    cmds.setAttr(taper_control_node + '.point2_interp', 1)
    cmds.setAttr(taper_control_node + '.point3_interp', 1)


    cmds.connectAttr(taper_control_node + '.scale_profile', sweep_mesh_node + '.scaleProfileX')
    cmds.connectAttr(taper_control_node + '.rotate_profile', sweep_mesh_node + '.rotateProfile')
    cmds.connectAttr(taper_control_node + '.resolution', sweep_mesh_node + '.profilePolySides')

    cmds.connectAttr(taper_control_node + '.START_position', sweep_mesh_node + '.taperCurve[0].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.START_value', sweep_mesh_node + '.taperCurve[0].taperCurve_FloatValue')

    cmds.connectAttr(taper_control_node + '.END_position', sweep_mesh_node + '.taperCurve[1].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.END_value', sweep_mesh_node + '.taperCurve[1].taperCurve_FloatValue')

    cmds.connectAttr(taper_control_node + '.point1_position', sweep_mesh_node + '.taperCurve[2].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.point1_interp', sweep_mesh_node + '.taperCurve[2].taperCurve_Interp')
    cmds.connectAttr(taper_control_node + '.point1_value', sweep_mesh_node + '.taperCurve[2].taperCurve_FloatValue')

    cmds.connectAttr(taper_control_node + '.point2_position', sweep_mesh_node + '.taperCurve[3].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.point2_interp', sweep_mesh_node + '.taperCurve[3].taperCurve_Interp')
    cmds.connectAttr(taper_control_node + '.point2_value', sweep_mesh_node + '.taperCurve[3].taperCurve_FloatValue')

    cmds.connectAttr(taper_control_node + '.point3_position', sweep_mesh_node + '.taperCurve[4].taperCurve_Position')
    cmds.connectAttr(taper_control_node + '.point3_interp', sweep_mesh_node + '.taperCurve[4].taperCurve_Interp')
    cmds.connectAttr(taper_control_node + '.point3_value', sweep_mesh_node + '.taperCurve[4].taperCurve_FloatValue')

    #Set mesh optimization for the sweep mesh :
    if paint_mode:
        cmds.setAttr(sweep_mesh_node + '.interpolationOptimize', 0)
    else:
        cmds.setAttr(sweep_mesh_node + '.interpolationOptimize', 1)

    #Setting the start scale value :
    cmds.setAttr(taper_control_node + '.scale_profile', start_scale_value)

    return taper_control_node


def toggleLineVisibility(line_name):
    pass


if __name__ == '__main__':

    main_window_instance= DockableWindow()
    main_window_instance.show(dockable=True)