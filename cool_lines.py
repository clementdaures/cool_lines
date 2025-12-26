import sys
import pprint
sys.path.append("INSTALLATION_PATH_REPLACE_STRING")

from importlib import reload
from pathlib import Path

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import shiboken2

from maya import cmds, mel
import maya.OpenMayaUI as omui

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import scene_data
reload(scene_data)

from _widgets import cool_checkbox, cool_name_display, cool_img_button
reload(cool_checkbox)
reload(cool_name_display)
reload(cool_img_button)

from _widgets.cool_checkbox import CoolCheckbox
from _widgets.cool_name_display import CoolNameDisplay
from _widgets.cool_img_button import CoolImgButton

        
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
        background-color: #220E00;
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
        background-color: transparent;
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
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px; 
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
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
        background-color: #220E00;
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

    QDialog{
        background-color: #462002;
    }"""

# light brown #462002
# dark brown #220E00

main_window_instance= None
paint_on_mesh= None
scene_lines_data= {}
global_scene_data_obj= scene_data.GlobalSceneData()
cool_lines_shader= None

# Installing script job to refresh file on opened
cmds.scriptJob(event=["SceneOpened", global_scene_data_obj.detectSceneChange])



def detectOrCreateShader():

    global cool_lines_shader
    if cmds.objExists('CoolLinesShader'):
        cool_lines_shader= 'CoolLinesShader'

    else:
        print('Preview Shader for outlines not found... Creating one.')
        cool_lines_shader= cmds.createNode('surfaceShader', name="CoolLinesShader")


class DockableWindow(MayaQWidgetDockableMixin, QDialog):
    def __init__(self, parent=mayaMainWindow()): 
        super(DockableWindow, self).__init__(parent)

        self.setGeometry(200,200,200,600)

        #Making the window appear on top:
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Cool Lines!')
        
        #Creating the tab widget:
        self.main_widget = mainWidget()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.main_widget)

        #Adding menu bar:
        #Creating the Tool Bar:
        menu_bar = QMenuBar(self)
        self.main_layout.setMenuBar(menu_bar)
        file_menu = menu_bar.addMenu("File")
        
        refresh_file_action = QAction("Manual Refesh", self)
        refresh_file_action.triggered.connect(global_scene_data_obj.detectSceneChange)
        refresh_file_action.setShortcut(QKeySequence("Alt+R"))
        file_menu.addAction(refresh_file_action)

        self.setStyleSheet(orange_theme)



class mainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        #Main Layout:
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.setStyleSheet('''font: 75 13pt "Microsoft YaHei UI";''')

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


        self.paint_options_buttons_hlayout= QHBoxLayout()

        brush_icon_path= Path(scene_data.__file__).parent / './_icons/brush_icon.png'
        self.create_paint_line_button= CoolImgButton(img_path=brush_icon_path.as_posix(), btn_size= QSize(80, 80), img_size=QSize(70,70),
                                          bg_color= QColor("#CD6C1B"))
        self.create_paint_line_button.setToolTip("Draw a line on the target mesh !")
        
        edge_line_icon_path= Path(scene_data.__file__).parent / './_icons/edge_line_icon.png'
        self.create_edge_line_button= CoolImgButton(img_path=edge_line_icon_path.as_posix(), btn_size= QSize(80, 80), img_size=QSize(70,70),
                                          bg_color= QColor("#CD6C1B"))
        self.create_edge_line_button.setToolTip("Use an edge of the target mesh to generate a line !")
        
        paint_bucket_icon_path= Path(scene_data.__file__).parent / './_icons/paint_bucket_icon.png'
        self.assign_shader_button= CoolImgButton(img_path=paint_bucket_icon_path.as_posix(), btn_size= QSize(80, 80), img_size=QSize(70,70),
                                          bg_color= QColor("#CD6C1B"))
        self.assign_shader_button.setToolTip("Assign default line shader to selected strokes !")
        
        self.paint_options_buttons_hlayout.addStretch()
        self.paint_options_buttons_hlayout.addWidget(self.create_paint_line_button)
        self.paint_options_buttons_hlayout.addWidget(self.create_edge_line_button)
        self.paint_options_buttons_hlayout.addWidget(self.assign_shader_button)
        self.paint_options_buttons_hlayout.addStretch()


        self.default_scale_title_label= QLabel(self)
        self.default_scale_title_label.setText("Default Scale")


        self.default_scale_lineedit = QLineEdit(self)
        validator = QRegExpValidator(QRegExp(r'[0-9]+.[0-9][0-9][0-9][0-9]'))
        self.default_scale_lineedit.setValidator(validator)
        self.default_scale_lineedit.setText('0.100')


        self.scene_content_label= QLabel(self)
        self.scene_content_label.setText("Scene Content")

        self.lines_list_widget = QListWidget(self)
        self.lines_list_widget.setFocusPolicy(Qt.NoFocus)
        self.lines_list_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.lines_list_widget.viewport().installEventFilter(self)

        self.credits_label= QLabel(self)
        self.credits_label.setText("Credits (Hover)")
        self.credits_label.setToolTip("Dev: Victor Schenck / Sources: Beranger Roussel's website / Icons: icons8.com")
        self.credits_label.setStyleSheet("""font: 75 8pt "Microsoft YaHei UI";""")

        
        #####################################
        #Organizing:
        self.main_layout.addWidget(self.target_mesh_label)
        self.main_layout.addLayout(self.set_target_mesh_hlayout)

        self.main_layout.addLayout(self.paint_options_buttons_hlayout)

        self.main_layout.addWidget(self.default_scale_title_label)
        self.main_layout.addWidget(self.default_scale_lineedit)

        self.main_layout.addWidget(self.scene_content_label)
        self.main_layout.addWidget(self.lines_list_widget)

        self.main_layout.addWidget(self.credits_label)


        #####################################
        #Connections:

        global_scene_data_obj.request_ui_sync.connect(self.refreshList)
        global_scene_data_obj.request_ui_clear.connect(self.lines_list_widget.clear)

        self.set_target_mesh_button.clicked.connect(self.setTargetMeshButtonClicked)
        self.create_edge_line_button.clicked.connect(self.createLineFromEdge)
        self.create_paint_line_button.clicked.connect(self.paintLineOnMesh)
        self.assign_shader_button.clicked.connect(self.assignPreviewShader)

        self.lines_list_widget.itemClicked.connect(self.selectLineInMaya)

        self.refreshList()

        # extra
        self.target_mesh=None


    def eventFilter(self, source, event):
        # Deselect item when nothing clicked
        if source == self.lines_list_widget.viewport() and event.type() == QEvent.MouseButtonPress:
            
            item = self.lines_list_widget.itemAt(event.pos())
            if not item:
                self.lines_list_widget.clearSelection()
        
        # Always return the parent's result so we don't break default behavior
        return super().eventFilter(source, event)

        
    def refreshList(self):
        
        self.lines_list_widget.clear()
        global_scene_data= global_scene_data_obj.getGlobalLinesData()

        for current_line_name in list(global_scene_data.keys()):

            current_line_data= dict(global_scene_data[current_line_name])

            # UI
            current_line_item = QListWidgetItem()
            current_line_item.setData(Qt.UserRole, current_line_data)

            current_line_item_widget = lineListDisplayWidget(current_line_data, current_line_item)
            current_line_item.setSizeHint(current_line_item_widget.sizeHint())

            self.lines_list_widget.addItem(current_line_item)
            self.lines_list_widget.setItemWidget(current_line_item, current_line_item_widget)
            current_line_item_widget.delete_line_item.connect(self.deleteLineItem)
            
        return


    def deleteLineItem(self, current_widget):
        self.lines_list_widget.takeItem(self.lines_list_widget.currentRow())
        global_scene_data_obj.removeLineData(current_widget.line_data["name"])
        self.deleteLineInMaya(current_widget.line_data)



    
    # Maya Interactions:
    def deleteLineInMaya(self, line_data):
        cmds.delete(line_data["group"])


    def selectLineInMaya(self, item):

        line_data= item.data(Qt.UserRole)

        # Showing the "Selected !" Message on the selecteds mesh node
        cmds.headsUpMessage( 'Selected !', object= line_data["mesh"] )
        cmds.select([line_data["mesh"], line_data["taper_ctrl_node"]], r=True)
   

    def setTargetMeshButtonClicked(self):
        user_selection= cmds.ls(sl=True)[0]

        if "|" in user_selection: # Means obj is not unique !!!
            QMessageBox.warning(self, "Can't paint :(", "This object's name is not unique !")
            return
        
        global paint_on_mesh
        paint_on_mesh = user_selection
        self.set_target_mesh_lineedit.setText(paint_on_mesh)


    def createLineFromEdge(self):

        stroke_id= len(list(global_scene_data_obj.getGlobalLinesData().keys()))

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

        result_mesh = cmds.listConnections( sweep_mesh_node + '.outMeshArray[0]', d=True, s=False )[0]
        cmds.setAttr(polytocurve_curve + '.v', 0)

        stroke_group= cmds.group([result_mesh, polytocurve_curve], n=f'Stroke_{stroke_id}_grp')
        
        # Node State Connections!!
        # Connect vis to taper ctrl node to reverse to wrap & sweep nodestate
        reverse_state_node= cmds.createNode('reverse')
        cmds.connectAttr(stroke_group + '.v', taper_control_node + '.disable')
        cmds.connectAttr(taper_control_node + '.disable', reverse_state_node + '.inputX')
        cmds.connectAttr(reverse_state_node + '.outputX', wrap_node + '.nodeState')
        cmds.connectAttr(reverse_state_node + '.outputX', sweep_mesh_node + '.nodeState')

        cmds.delete(polytocurve_node)

        


        # Formatting w stroke name
        line_name= f"Stroke_{stroke_id}"
        result_mesh= cmds.rename(result_mesh, f"Stroke_{stroke_id}_msh")
        sweep_mesh_node= cmds.rename(sweep_mesh_node, f"Stroke_{stroke_id}_sweep")
        wrap_node= cmds.rename(wrap_node, f"Stroke_{stroke_id}_wrap")
        converted_curve_shape= cmds.rename(polytocurve_curve, f"Stroke_{stroke_id}_OGcurve")
        taper_control_node= cmds.rename(taper_control_node, f"edit_Stroke_{stroke_id}")
        reverse_state_node= cmds.rename(reverse_state_node, f"reverse_state_Stroke_{stroke_id}")


        line_data= {"name": line_name,
                    "type": "edge",
                    "group": stroke_group,
                    "mesh": result_mesh,
                    "curve": converted_curve_shape,
                    "sweep_msh_node" : sweep_mesh_node,
                    "taper_ctrl_node": taper_control_node,
                    "wrap_node": wrap_node,
                    "root_convert_grp": None,
                    "converted_curve_grp": None,
                    "reverse_state_node": reverse_state_node
                    }
        


        global_scene_data_obj.addLineData(line_data)

        
    def paintLineOnMesh(self):
        
        global paint_on_mesh
        if not paint_on_mesh:
            QMessageBox.warning(self, "Can't paint :(", "Please set a target mesh to paint on it !")
            return

        cmds.select(paint_on_mesh)
        mel.eval("MakePaintable")
        mel.eval("PaintEffectsTool")
        
        # Help here ! https://www.regnareb.com/pro/2014/05/wait-for-user-input-in-maya/
        try:
            cmds.dynWireCtx("paintMesh")
        except RuntimeError:
            pass
        cmds.setToolTo("paintMesh")
        # global paint_on_mesh
        # paint_on_mesh = cmds.ls(sl=True)[0]
        cmds.scriptJob(runOnce=True, event=("SelectionChanged", f"executed_after_action({float(self.default_scale_lineedit.text())})"))


    def assignPreviewShader(self):
        global cool_lines_shader
        print("Shader:")
        print(cool_lines_shader)

        maya_selection= True

        # Checking if selected from UI or in maya
        user_selection= cmds.ls(sl=True)
        if len(user_selection) == 2:
            for current_item in user_selection:
                if cmds.nodeType(current_item) == "network":
                    maya_selection= False
                else:
                    continue
        
        if not maya_selection:
            cmds.select(self.lines_list_widget.currentItem().data(Qt.UserRole)["mesh"])
        
        if cool_lines_shader:
            cmds.hyperShade(assign= cool_lines_shader)
        else:
            detectOrCreateShader()
            cmds.hyperShade(assign= cool_lines_shader)



class lineListDisplayWidget(QWidget):
    delete_line_item= Signal(QWidget)

    def __init__(self, line_data :dict, list_item :QListWidgetItem, *args,**kwargs):
        QWidget.__init__(self,*args,**kwargs)

        self.line_data= line_data
        self.list_item= list_item

        self.main_layout = QHBoxLayout()
        self.main_layout.setSizeConstraint(QLayout.SetFixedSize) #Mandatory to scale correctly the widget
        self.setLayout(self.main_layout)

        
        self.line_name_widget= CoolNameDisplay(line_data)

        self.line_type_label= QLabel(self)
        self.line_type_label.setText(self.line_data["type"])
        self.line_type_label.setStyleSheet('''font: 75 7pt "Microsoft YaHei UI";''')

        # Query initial line grp vis!
        current_line_grp_vis= cmds.getAttr(self.line_data["group"] + '.v')
        current_line_grp_vis= bool(current_line_grp_vis)
        
        self.disable_line_checkbox= CoolCheckbox(self)
        self.disable_line_checkbox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.disable_line_checkbox.setMinimumSize(30,15)
        self.disable_line_checkbox.setMaximumSize(30,15)
        self.disable_line_checkbox.setupAnimations(animation_curve=QEasingCurve.OutBounce, animation_duration=300, start_checked= current_line_grp_vis)
        
        trash_icon_path= Path(scene_data.__file__).parent / './_icons/trash_icon.png'
        self.delete_button= CoolImgButton(img_path=trash_icon_path.as_posix(), btn_size= QSize(30, 30), img_size=QSize(20,20),
                                          bg_color= QColor("#CD6C1B"))

        self.main_layout.addWidget(self.line_name_widget)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.disable_line_checkbox)
        self.main_layout.addWidget(self.delete_button)
        self.main_layout.addWidget(self.line_type_label)
        
        self.setStyleSheet('''font: 75 10pt "Microsoft YaHei UI";''')

        # Connections:
        self.line_name_widget.name_changed.connect(self.changeLineNameWrapper)
        self.disable_line_checkbox.stateChanged.connect(self.toggleLineVisibility)
        self.delete_button.clicked.connect(self.requestDelete)


    def changeLineNameWrapper(self, new_name :str):
        
        print(f'New Name: {new_name}')
        if new_name== self.line_data["name"]:
            print("Same name.")
            return
        
        else:
            line_key= self.line_data["name"]
            self.line_data["name"]= new_name #updating the line_data
                   
            # Shared types data rename:
            stroke_group= cmds.rename(self.line_data["group"], f'{new_name}_grp')
            result_mesh= cmds.rename(self.line_data["mesh"], f"{new_name}_msh")
            sweep_mesh_node= cmds.rename(self.line_data["sweep_msh_node"], f"{new_name}_sweep")
            wrap_node= cmds.rename(self.line_data["wrap_node"], f"{new_name}_wrap")
            converted_curve_shape_node= cmds.rename(self.line_data["curve"], f"{new_name}_OGcurve")
            taper_control_node= cmds.rename(self.line_data["taper_ctrl_node"], f"edit_Stroke_{new_name}")
            reverse_state_node= cmds.rename(self.line_data["reverse_state_node"], f"reverse_state_Stroke_{new_name}")

            new_data= {"name": new_name,
                       "type": self.line_data.get("type"),
                        "group": stroke_group,
                        "mesh": result_mesh,
                        "curve": converted_curve_shape_node,
                        "sweep_msh_node" : sweep_mesh_node,
                        "taper_ctrl_node": taper_control_node,
                        "wrap_node": wrap_node,
                        "root_convert_grp": None,
                        "converted_curve_grp": None,
                        "reverse_state_node": reverse_state_node
                        }

            # Unique type data rename:
            if self.line_data["type"] == "paint":

                root_converted_curve_group= cmds.rename(self.line_data["root_convert_grp"], f"{new_name}_keep_grp")
                converted_curve_grp= cmds.rename(self.line_data["converted_curve_grp"], f"{new_name}_OGCuve_grp")

                paint_unique_data={"converted_curve_grp": root_converted_curve_group,
                                   "root_convert_grp": converted_curve_grp,
                                   }
                
                new_data.update(paint_unique_data)
            
            global_scene_data_obj.updateLineData(line_key, dict(new_data), update_name=True)


    def toggleLineVisibility(self):
        current_vis= cmds.getAttr(self.line_data["group"] + '.v')
        cmds.setAttr(self.line_data["group"] + '.v', (not current_vis))


    def requestDelete(self):
        self.list_item.listWidget().setCurrentItem(self.list_item)
        self.delete_line_item.emit(self)



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

        stroke_id= len(list(global_scene_data_obj.getGlobalLinesData().keys()))

        first_group = cmds.listRelatives(converted_curve_shape_node, p=True)[0]
        root_converted_curve_group = cmds.listRelatives(first_group, p=True)[0]

        stroke_transform = cmds.listRelatives(stroke_shape, p=True)[0]
        cmds.setAttr(stroke_transform + '.v', 0)
        cmds.setAttr(root_converted_curve_group + '.v', 0)

        stroke_group= cmds.group([result_mesh, root_converted_curve_group, stroke_transform], n=f'Stroke_{stroke_id}_grp')

        #Baking:
        stroke_transform = cmds.listRelatives(stroke_shape, p=True)[0]
        cmds.delete(stroke_shape)
        cmds.delete(stroke_transform)


        #Wrapping:
        cmds.select([converted_curve_shape_node, paint_on_mesh], r=True)
        print(cmds.CreateWrap())

        curve_shape = cmds.listRelatives(converted_curve_shape_node, s=True)[0]
        wrap_node = cmds.listConnections(curve_shape + '.create')[0]
        

        # Node State Connections!!
        # Connect vis to taper ctrl node to reverse to wrap & sweep nodestate
        reverse_state_node= cmds.createNode('reverse')
        cmds.connectAttr(stroke_group + '.v', taper_control_node + '.disable')
        cmds.connectAttr(taper_control_node + '.disable', reverse_state_node + '.inputX')
        cmds.connectAttr(reverse_state_node + '.outputX', wrap_node + '.nodeState')
        cmds.connectAttr(reverse_state_node + '.outputX', sweep_mesh_node + '.nodeState')

        converted_curve_grp= cmds.listRelatives(converted_curve_shape_node, p=True)[0]
        cmds.select(cl=True)

        # Formatting w stroke name
        line_name= f"Stroke_{stroke_id}"
        result_mesh= cmds.rename(result_mesh, f"Stroke_{stroke_id}_msh")
        sweep_mesh_node= cmds.rename(sweep_mesh_node, f"Stroke_{stroke_id}_sweep")
        wrap_node= cmds.rename(wrap_node, f"Stroke_{stroke_id}_wrap")
        root_converted_curve_group= cmds.rename(root_converted_curve_group, f"Stroke_{stroke_id}_keep_grp")
        converted_curve_shape_node= cmds.rename(converted_curve_shape_node, f"Stroke_{stroke_id}_OGcurve")
        converted_curve_grp= cmds.rename(converted_curve_grp, f"Stroke_{stroke_id}_OGCuve_grp")
        taper_control_node= cmds.rename(taper_control_node, f"edit_Stroke_{stroke_id}")
        reverse_state_node= cmds.rename(reverse_state_node, f"reverse_state_Stroke_{stroke_id}")


        line_data= {"name": line_name,
                    "type": "paint",
                    "group": stroke_group,
                    "mesh": result_mesh,
                    "curve": converted_curve_shape_node,
                    "sweep_msh_node" : sweep_mesh_node,
                    "taper_ctrl_node": taper_control_node,
                    "wrap_node": wrap_node,
                    "root_convert_grp": root_converted_curve_group,
                    "converted_curve_grp": converted_curve_grp,
                    "reverse_state_node": reverse_state_node
                    }
        


        global_scene_data_obj.addLineData(line_data)


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



if __name__ == '__main__':

    main_window_instance= DockableWindow()
    main_window_instance.show(dockable=True)