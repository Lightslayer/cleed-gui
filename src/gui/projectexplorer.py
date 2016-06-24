##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.m.deacon@gmail.com                                           #
#                                                                            #
# Copyright: Copyright (C) 2014-2015 Liam Deacon                             #
#                                                                            #
# License: MIT License                                                       #
#                                                                            #
# Permission is hereby granted, free of charge, to any person obtaining a    #
# copy of this software and associated documentation files (the "Software"), #
# to deal in the Software without restriction, including without limitation  #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,   #
# and/or sell copies of the Software, and to permit persons to whom the      #
# Software is furnished to do so, subject to the following conditions:       #
#                                                                            #
# The above copyright notice and this permission notice shall be included in #
# all copies or substantial portions of the Software.                        #
#                                                                            #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,   #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    #
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        #
# DEALINGS IN THE SOFTWARE.                                                  #
#                                                                            #
##############################################################################
'''

'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

from qtbackend import QtCore, QtGui

import os.path
try:
    import res_rc
except:
    pass

try:
    import core
except ImportError:
    import sys
    import os
    module_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, module_path)
    import core
finally:
    from core.model import Model, BulkModel, SurfaceModel, Atom

class ProjectTreeWidget(QtGui.QTreeWidget):
    default_dir = os.path.join(os.path.expanduser("~"), "CLEED", "models")
    examples_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                "..", "..", "res", "examples", "models")
    last_project_dir = default_dir
    
    def __init__(self, parent=None):
        super(ProjectTreeWidget, self).__init__(parent)
        
        self.setColumnCount(1)
        self.setHeaderLabel("Projects")
        
        # explorer actions       
        self.renameAction = QtGui.QAction(QtGui.QIcon(":/tag_stroke.svg"),
                                          "&Rename", self,
                                          triggered=self.rename)
        self.renameAction.setToolTip("Rename project...")
        
        self.refreshAction = QtGui.QAction(QtGui.QIcon(":/spin.svg"),
                                           "Refresh", self,
                                           triggered=self.refresh,
                                           shortcut="F5")
        self.refreshAction.setToolTip("Refresh")
         
        self.newProjectAction = QtGui.QAction(
                                      QtGui.QIcon(":/document_alt_stroke.svg"),
                                      "&New Project", self,
                                      triggered=self.newProject)
        self.newProjectAction.setToolTip("Create new project...")
        
        self.importProjectAction = QtGui.QAction(QtGui.QIcon(":/import.svg"),
                                                 "&Import Project", self,
                                                 triggered=self.importProject)
        self.importProjectAction.setToolTip("Import existing project...")    
        
        self.newModelAction = QtGui.QAction(QtGui.QIcon(":/atoms.svg"),
                                            "&New Model", self,
                                            triggered=self.newModel)
        self.newModelAction.setToolTip("Create new model...")
        
        self.importModelAction = QtGui.QAction(QtGui.QIcon(":/import.svg"),
                                               "&Import Model", self,
                                               triggered=self.importModel)
        self.importModelAction.setToolTip("Import existing model...") 
        
        self.removeProjectAction = QtGui.QAction(QtGui.QIcon(":/x.svg"),
                                                 "&Remove Project", self,
                                                 triggered=self.removeProject,
                                                 shortcut='Del')
        self.newProjectAction.setToolTip("Remove project")
        
        self.removeProjectAction = QtGui.QAction(
                                        QtGui.QIcon(":/folder_fill.svg"),
                                        "Open Project &Location", self,
                                        triggered=self.openProjectLocation)
        self.newProjectAction.setToolTip(
                                    "Opens project location in file explorer")
        
        # explorer menus
        self.explorerDefaultMenu = QtGui.QMenu()
        self.explorerDefaultMenu.addAction(self.newProjectAction)
        self.explorerDefaultMenu.addAction(self.importProjectAction)
        self.explorerDefaultMenu.addSeparator()
        #self.explorerDefaultMenu.addAction(self.copyAction)
        #self.explorerDefaultMenu.addAction(self.cutAction)
        #self.explorerDefaultMenu.addAction(self.pasteAction)
        self.explorerDefaultMenu.addAction(self.renameAction)
        self.explorerDefaultMenu.addSeparator()
        self.explorerDefaultMenu.addAction(self.refreshAction)
        
        self.explorerProjectMenu = QtGui.QMenu()
        self.explorerProjectMenu.addAction(self.newModelAction)
        self.explorerProjectMenu.addAction(self.importModelAction)
        #self.explorerProjectMenu.addSeparator()
        #self.explorerProjectMenu.addAction(self.copyAction)
        #self.explorerProjectMenu.addAction(self.cutAction)
        #self.explorerProjectMenu.addAction(self.pasteAction)
        self.explorerProjectMenu.addAction(self.renameAction)
        self.explorerProjectMenu.addAction(self.removeProjectAction)
        self.explorerProjectMenu.addSeparator()
        self.explorerProjectMenu.addAction(self.refreshAction)
        
        self.explorerFileMenu = QtGui.QMenu()
        #self.explorerFileMenu.addAction(self.newAction)
        self.explorerFileMenu.addAction(self.refreshAction) 
        
        #setup signals and slots
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.explorerPopupMenu)
        
        #recent projects
        self.recent_projects = []
    
    def openProjectLocation(self):
        ''' Opens the currently selected project's location '''
        import webbrowser
        filepath = self.currentItem()._path or self.default_dir
        webbrowser.open(filepath)
    
    def expandChildren(self, index):
        ''' Recursely expands all children for the given index node'''
        if not index.isValid():
            return

        childCount = index.model().rowCount(index)
        for i in range(childCount):
            child = index.child(i, 0)
            # Recursively call the function for each child node.
            self.expandChildren(child)

        if not self.view.expanded(index):
            self.view.expand(index)
    
    def explorerPopupMenu(self, point):
        ''' Handles popup menu for explorer widget '''
        index = self.indexAt(point)
        if index.isValid():
            location = self.viewport().mapToGlobal(point)
            # show custom menu for file type held at given index
            item = self.itemFromIndex(index)
            if self.indexOfTopLevelItem(item) > -1:
                # then its a top-level item
                self.selectionModel().setCurrentIndex(index, 
                                            QtGui.QItemSelectionModel.NoUpdate)
                self.explorerProjectMenu.popup(location)
            else:
                try:
                    self.currentItem().contextMenu.popup(location)
                    print('Handled right click of {} "{}"'
                          ''.format(self.currentItem(), self.currentItem().text(0)))
                except AttributeError:
                    print('Not handled right click of {} "{}"'
                          ''.format(self.currentItem(), self.currentItem().text(0)))
        else:
            # provide default menu
            self.explorerDefaultMenu.popup(
                        self.viewport().mapToGlobal(point))
    
    def currentProject(self):
        '''returns the currently selected project'''
        item = self.currentItem()
        
        # get root item
        while self.indexOfTopLevelItem(item) < 0:
            item = item.parent()

        return {'name': item.text(self.currentColumn()), 'item': item}
    
    def newProject(self, projectName=None):
        if not projectName:
            projectName = "Untitled_Project"
        
        # get storage location for project
        homePath = QtGui.QDesktopServices.storageLocation(
                                        QtGui.QDesktopServices.HomeLocation)
        projectDir = os.path.join(homePath, "CLEED", "models")
        if not os.path.exists(projectDir):
            projectDir = self.examples_dir
        folder = QtGui.QFileDialog.getExistingDirectory(parent=self, 
                            caption="Select Project Base Directory",
                            directory=projectDir, 
                            options=QtGui.QFileDialog.ShowDirsOnly | 
                                    QtGui.QFileDialog.DontResolveSymlinks)    
        if folder:
            # do stuff
            items = [self.parent().topLevelItem(i).Path for i 
                     in range(self.parent().topLevelItemCount())]
            if folder not in items:
                proj = ProjectItem(self.ui.parent(), path=folder)
            else:
                pass
                self.parent().setCurrentIndex(0, items.index(folder, ))
    
    def newModel(self, project, modelName=None):
        if not modelName:
            text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
                                              'Enter model name:')
            if not ok:
                return
            
            modelName = text
        
        try:
            index = self.selectedIndexes()[0]
            parent = self.itemFromIndex(index)
            path = os.path.join(parent.project_path, modelName)
             
            if not modelName:
                modelName = "New_Model"
                i = 1
                path = os.path.join(parent.Path, modelName)
                while os.path.isdir(modelName):
                    modelName = "New_Model%i" % i
                    path = os.path.join(parent.Path, modelName)
                    i += 1
            
            model = ModelGroupItem(path)
            #a = parent.addChild(model)
            if not os.path.exists(path):
                os.makedirs(path, 755)
                # add new input files
                
            else:
                pass
        
        except IndexError:
            # no index selected (or created?)
            pass    
    
    def importModel(self):
        '''Import model from text file'''
        pass
    
    def importProject(self):
        '''Import a project'''
        project = QtGui.QFileDialog.getExistingDirectory(parent=self, 
                            caption="Select CLEED project directory...")
        if os.path.isdir(project) and not project in self.projects:
            self.projects.append(project)
    
    def removeProject(self):
        print(self.currentItem().__dict__)
    
    def rename(self):
        '''Renames current project'''
        project = self.currentProject()
        old_name = project['name']
        new_name, ok = QtGui.QInputDialog.getText(self, 
                                                  self.tr("Rename Project"),
                                                  self.tr("New name:"), 
                                                  QtGui.QLineEdit.Normal,
                                                  old_name)
        if ok and new_name is not old_name:
            item = project['item']
            item.setText(self.currentColumn(), new_name) 
        
        
    def refresh(self):
        raise NotImplementedError('todo')
    
    def getChildItemsDict(self, obj):
        try:
            if isinstance(obj, QtGui.QTreeWidget):
                root = obj.invisibleRootItem()
            elif isinstance(obj, QtGui.QTreeWidgetItem):
                root = obj
            child_count = root.childCount()
            topLevelDict = {}
            for i in range(child_count):
                item = root.child(i)
                var = str(item.text(0))
                exec('%s = i' % var)
                topLevelDict.update({var: eval(var)})
            return topLevelDict
        except any as e:
            self.logger.error(e.msg)
            
    def getChildItemHandle(self, obj, name=str):
        if isinstance(obj, QtGui.QTreeWidget):
            root = obj.invisibleRootItem()
        elif isinstance(obj, QtGui.QTreeWidgetItem):
            root = obj
        
        if isinstance(name, int):
            return root.child(name)
        elif isinstance(name, str):
            for i in range(root.childCount()):
                item = root.child(i)
                if str(item.text(0)) == name:
                    return item


class BaseItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent=None):
        super(BaseItem, self).__init__(parent)
        
        self.editAction = QtGui.QAction(QtGui.QIcon(":/document_edit_24x32.png"),
                                        "&Edit", None)
        self.refreshAction = QtGui.QAction(QtGui.QIcon(":/spin.svg"),
                                           "&Refresh", None,
                                           triggered=self.refresh,
                                           shortcut="F5")
        self.refreshAction.setToolTip("Refresh")
        
        self.contextMenu = QtGui.QMenu()
        self.contextMenu.addAction(self.editAction)
        self.contextMenu.addAction(self.refreshAction)
    
    @classmethod
    def getChildren(cls, parent, recursive=True):
        ''' Get either immediate or all children of parent node ''' 
        children = []
        for i in range(parent.childCount()):
            child = parent.child(i)
            children += [child]
            if recursive:
                children += BaseItem.getChildren(child, recursive)
        return children
    
    def doubleClicked(self, index):
        """ Triggers doubleClick event """ 
        old_value = ''
        new_value, ok = QtGui.QInputDialog.getText(self, 
                                                  self.tr("Rename"),
                                                  self.tr("New value:"), 
                                                  QtGui.QLineEdit.Normal,
                                                  old_value)
        if ok and new_value is not old_value:
            item = self.parent.selectedIndexes()[0].model().itemFromIndex(index)
            item.setText(self.currentColumn(), new_value)
    
    def edit(self):
        ''' Edits the current item bringing up dialog if needed '''
        print("Edit of {}".format(self))
    
    def refresh(self):
        ''' Refreshes item and its children based on contained data '''
        print("Refresh of {}".format(self))
    

class ProjectItem(BaseItem):
    projects = []
    
    '''class for project items'''
    def __init__(self, parent=None, path=None, name=None):
        super(ProjectItem, self).__init__(parent)
        self.name = name or "New_Project{}".format(len(self.projects))
        self.setIcon(0, QtGui.QIcon(":/folder_fill.svg"))
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        self.setToolTip(0, "LEED-IV Project")
        self.setProjectPath(path)
        
        self.models = []
        
        #add children
        self._init_children()
        
        ProjectItem.projects.append(self)
    
    def _init_children(self):
        self.models.append(ModelGroupItem(self))
        
    def __del__(self):
        try:
            ProjectItem.projects.remove(self)
        except:
            pass
    
    @classmethod
    def load(cls, directory):
        pass
    
    @property
    def project_path(self):
        if not hasattr(self, "_path"): 
            self._path = None
        return self._path or os.path.join(ProjectTreeWidget.default_dir,
                                          self.name)
    
    @project_path.setter
    def project_path(self, path):
        self._path = path or ProjectTreeWidget.default_dir
    
    def setProjectPath(self, path):
        self.project_path = path 
        self.setText(0, self.name)
        self.setToolTip(0, 'LEED-IV Project: "{}"'.format(os.path.join(self.project_path, self.name)))
        
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
    
        
class ModelGroupItem(BaseItem):
    '''class for project items'''
    def __init__(self, parent=None, path=None):
        super(ModelGroupItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/blocks.svg"))
        self.setText(0, "New_Model")
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        self.setToolTip(0, "Model belonging to project")
        #self.setModelName(path)
        
        # init items
        self.surface = SurfaceModelItem(self)
        self.bulk = BulkModelItem(self)
        self.iv_groups = IVGroupItem(self)
    
    def setModelName(self, path):
        self.Path = path
        self.Name = QtCore.QFileInfo(path).baseName()
        self.setText(0, self.Name)
        self.setToolTip(0, path)
        
    def addGroup(self, group=None):
        if group is None:
            # create default group
            group = IVGroupItem()
        
        if isinstance(group, IVGroupItem):
            self.addChild(group)
        
class ModelItem(BaseItem):
    ''' common class for both bulk and surface model items '''
    MODEL_CLASS = core.model.BaseModel
    __tooltip__ = "Model"
    __description__ = ""
    
    def __init__(self, parent=None, model=None):
        super(BaseItem, self).__init__(parent)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

        self.model = model
    
    @QtCore.Slot()
    def modelChanged(self, model):
        """ Actions to undertake once model has changed """
        print(self.__tooltip__ + " changed")
    
    def setModel(self, model):
        ''' sets the model '''
        if isinstance(model, basestring):
            # attempt to load model assuming filepath
            model = self.MODEL_CLASS().load(model)
        elif model == None:
            model = self.MODEL_CLASS()
        else:
            try:
                self.MODEL_CLASS(**model)
            except:
                raise ValueError("{} is not a supported model type".format(model))
        self._model = model
        
    def getModel(self):
        ''' gets the model '''
        return self._model
    
    def refresh(self):
        ''' Updates QTreeWidgetItem '''
        try:
            filename = self.model
            self.setToolTip(0, self.__tooltip__ + 
                            ' ({})\n\n'.format(filename) + self.__description__)
        except:
            self.setToolTip(0, self.__tooltip__ + '\n' + self.__description__)
            
        print("TODO: clear all children")
        if self.model:
            atoms = [AtomItem(atom=a) for a in self.model.atoms]
    
    model = property(fset=setModel, fget=getModel)

class SurfaceModelItem(ModelItem):
    MODEL_CLASS = SurfaceModel
    __tooltip__ = "Surface Model"
    __description__ = "Contains input parameters that are changed during geometry optimisation"
    
    '''class for project items'''
    def __init__(self, parent=None, surface_model=None):
        super(self.__class__, self).__init__(parent, model=surface_model)
        self.setIcon(0, QtGui.QIcon(":/minus.svg"))
        self.setText(0, 'Surface_Model')
        
      
class BulkModelItem(ModelItem):
    '''class for project items'''
    
    MODEL_CLASS = BulkModel
    __tooltip__ = 'Bulk Model'
    __description__ = "Contains bulk parameters that do not change"
    
    def __init__(self, parent=None, bulk_model=None):
        super(self.__class__, self).__init__(parent, model=bulk_model)
        self.setIcon(0, QtGui.QIcon(":/layers.svg"))
        self.setText(0, "Bulk_Model")
        
            
        
class SearchItem(BaseItem):
    '''class for LEED-IV control items'''
    def __init__(self, parent=None, path=None):
        #super(InputItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/cog.svg"))
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)


class SettingsItem(BaseItem):
    '''class for local settings'''
    def __init__(self, parent=None, path=None):
        super(self.__class__, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/wrench.svg"))
        self.setText(0, "Settings")
        self.setToolTip(0, "Defines settings for project")


class AtomItem(BaseItem):
    ''' Class for handling atoms '''
    def __init__(self, parent=None, atom=None):
        super(self.__class__, self).__init__(parent)
        
        self.atom = atom or self.newAtom()
        self.refresh()
        
    @QtCore.Slot()
    def atomChanged(self, atom):
        pass
        
    def newAtom(self, element='C', **kwargs):
        return Atom(element, **kwargs)
    
    def refresh(self):
        self.setIcon(0, QtGui.QIcon(":/atom.svg"))
        self.setText(0, self.atom.symbol)
        self.setToolTip(0, "{} atom\n{}".format(self.atom.name, str(self.atom)))
        
        for i,j in enumerate(["x", "y", "z"]):
            eval("self.{} = QtGui.QTreeWidgetItem(self)".format(j))
            eval('self.{}.setText(0, "{} = {}")'.format(j, j, self.atom.coordinates[i]))
            eval('self.{}.setToolTip(0, "{}-coordinate for atom"'.format(j, j.upper()))
        
        # valence
        self.valence = QtGui.QTreeWidgetItem(self)
        self.valence.setText(0, "valence = {}".format(self.atom.valence))
        self.valence.setToopTip(0, "Specifies the valency (charge) of the atom (or ion) e.g. +2")
        
        # fractional occupancy
        self.occupancy = QtGui.QTreeWidgetItem(self)
        self.occupancy.setText(0, "occupancy = {}".format(self.atom.occupancy))
        self.occupancy.setToolTip(0, "Specifies the fractional occupancy "
                                  "of the atomic site.\nThis is useful if "
                                  "sites (e.g. on the surface) are known to \n"
                                  "contain vacancies or the structure is an alloy")
        # minimum radius
        self.radius = QtGui.QTreeWidgetItem(self)
        self.radius.setText(0, "r_{min} = {}".format(self.atom.radius))
        self.radius.setToolTip(0, "Specifies the muffin-tin radius of "
                               "the atom or ion.\nThis radius is the smallest "
                               "interatomic distance before \na penalty is "
                               "invoked during geometry optimisation")
        
        
class IVGroupItem(BaseItem):
    '''class for handling LEED-IV curves'''
    def __init__(self, parent=None, path=None, ivs=[]):
        super(IVGroupItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/list.svg"))
        self.setText(0, 'IV_Group')
        
        # initialise actions
        self.iv_pairs = [IVInfoItem(self)]
        
        # initialise other aspects
        self.theta = QtGui.QTreeWidgetItem(self)
        self.theta.setText(0, 'Theta')
        self.theta.setIcon(0, QtGui.QIcon(':/theta.svg'))
        self.theta.setToolTip(0, "Angle of incidence, \u03B8")
        
        self.phi = QtGui.QTreeWidgetItem(self)
        self.phi.setText(0, 'Phi')
        self.phi.setIcon(0, QtGui.QIcon(':/phi.svg'))
        self.phi.setToolTip(0, "Azimuth for angle of incidence, \u03C6")
        
        self.enabled = QtGui.QTreeWidgetItem(self)
        self.enabled.setText(0, 'Enabled')
        self.enabled.setIcon(0, QtGui.QIcon(':/check.svg'))
        self.enabled.setToolTip(0, "Specifies whether this IV group is used")
        
        self.rfactor = QtGui.QTreeWidgetItem(self)
        self.rfactor.setText(0, 'Rfactor')
        self.rfactor.setIcon(0, QtGui.QIcon(':/heart_fill.svg'))
        self.rfactor.setToolTip(0, "The R-Factor for the IV group")
        
    @classmethod
    def readControlFile(cls, ctr):
        pass
    
    def _createActions(self):
        self.generateControlAction = QtGui.QAction(
                                    QtGui.QIcon(":/document_edit_24x32.png"),
                                    "&Edit ctr file...", 
                                    self,
                                    triggered=self.viewControl,
                                    shortcut='Ctrl+E')
        self.generateControlAction.setToolTip("Edit LEED control file...")

    def viewControl(self):
        pass

class IVInfoItem(BaseItem):
    def __init__(self, parent=None, iv_pair=None):
        super(IVInfoItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/index.svg"))
        self.setText(0, '(h, k)')
        
        self.expt = ExperimentalIVCurveItem(self)
        self.theory = TheoreticalIVCurveItem(self)

        self.id = QtGui.QTreeWidgetItem(self)
        self.id.setText(0, 'ID')
        self.id.setIcon(0, QtGui.QIcon(":/id.svg"))

        self.weight = QtGui.QTreeWidgetItem(self)
        self.weight.setText(0, 'Weight')
        self.weight.setIcon(0, QtGui.QIcon(":/eject.svg"))
                  
        self.rfactor = QtGui.QTreeWidgetItem(self)
        self.rfactor.setText(0, 'Rfactor')
        self.rfactor.setIcon(0, QtGui.QIcon(":/heart_fill.svg"))
        try:
            if isinstance(iv_pair, core.iv.IVCurvePair):
                self.load(iv_pair)
        except:
            pass
            
        def load(self, iv_pair):
            pass


class IVCurveItem(BaseItem):
    """ IVCurveItem for handling a generic IV curve """
    def __init__(self, parent=None, path=None):
        super(IVCurveItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/graph_dash.svg"))
        self.setText(0, "IV curve")
        self.setToolTip(0, "IV curve")
        
        self.path = path
    
    @QtCore.Slot()
    def dataChanged(self):
        pass
    
    @property
    def path(self):
        return self._path
        
    @path.setter
    def path(self, path):
        try:
            self._path = os.path.abspath(os.path.expanduser(path))
        except:
            self._path = None


class ExperimentalIVCurveItem(IVCurveItem):
    def __init__(self, parent=None, path=None):
        super(ExperimentalIVCurveItem, self).__init__(parent, path)
        self.setIcon(0, QtGui.QIcon(":/iv_expt.svg"))
        self.setText(0, "Experimental IV")
        self.setToolTip(0, "Experimental IV")


class TheoreticalIVCurveItem(IVCurveItem):
    def __init__(self, parent=None, path=None):
        super(TheoreticalIVCurveItem, self).__init__(parent, path)
        self.setIcon(0, QtGui.QIcon(":/iv_theory.svg"))
        self.setText(0, "Theoretical IV")
        self.setToolTip(0, "Theoretical IV")
    
    def contextMenu(self):
        pass


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    explorer = ProjectTreeWidget()
    
    project = ProjectItem()
    #pro2 = ProjectItem()
    explorer.addTopLevelItem(project)
    for child in project.getChildren(project):
        child.setExpanded(True)
    #explorer.addTopLevelItem(pro2)
    
    explorer.show()
    app.exec_()
