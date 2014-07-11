import site
site.addsitedir(r"R:/Pipe_Repo/Users/Qurban/Utilities")
try:
    from uiContainer import uic
except:
    from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import qtify_maya_window as qtfy
import bake_particle_instancer as bpi
import os
osp = os.path
import sys
import time

selfPath = sys.modules[__name__].__file__
rootPath = osp.dirname(osp.dirname(selfPath))
uiPath = osp.join(rootPath, 'ui')

Form, Base = uic.loadUiType(osp.join(uiPath, 'window.ui'))
class Window(Form, Base):
    def __init__(self, parent= qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        
        # instance variables
        self.instancers = []
        
        # bindings
        self.bakeButton.clicked.connect(self.bake)
        self.refreshButton.clicked.connect(self.refresh)
        self.selectAllButton.clicked.connect(self.selectAll)
        self.resetButton.clicked.connect(self.resetWindow)
        
        # widgets' settings
        validator = QIntValidator(self)
        validator.setBottom(0)
        self.startBox.setValidator(validator)
        self.endBox.setValidator(validator)
        self.listInstancers()
        
        # update the database, how many times this app is used
        site.addsitedir(r'r:/pipe_repo/users/qurban')
        import appUsageApp
        appUsageApp.updateDatabase('bakeInstancer')
        
    def switchSelectAll(self):
        """checks the selectAllButton if users checks all
        the instancers on window"""
        select = True
        for inst in self.instancers:
            if inst.isChecked():
                pass
            else: select = False; break
        self.selectAllButton.setChecked(select)

    def selectAll(self):
        """checks all the instancers when the user checks
        selectAllButton"""
        select = self.selectAllButton.isChecked()
        for inst in self.instancers:
            inst.setChecked(select)

    def clearInstancers(self):
        for inst in self.instancers:
            inst.deleteLater()
        self.instancers[:] = []
        self.selectAllButton.setChecked(False)

    def resetWindow(self):
        self.clearInstancers()
        self.timeSliderButton.setChecked(True)
        self.startBox.clear()
        self.endBox.clear()
        self.stepBox.setValue(1.00)
        self.listInstancers()

    def listInstancers(self):
        """Lists instancers on window"""
        instancers = bpi.instancers()
        for inst in instancers:
            name = inst.split(":")[-1]
            btn = QCheckBox(inst, self)
            btn.setObjectName(inst)
            btn.clicked.connect(self.switchSelectAll)
            self.instancersLayout.addWidget(btn)
            self.instancers.append(btn)
        
    def bake(self):
        startFrame = None
        endFrame = None
        if self.startEndButton.isChecked():
            startText = self.startBox.text()
            endText = self.endBox.text()
            if not startText:
                self.makeWidgetBlink(self.startBox)
                return
            if not endText:
                self.makeWidgetBlink(self.endBox)
                return
            startFrame = int(str(startText))
            endFrame = int(str(endText))
            if startFrame >= endFrame:
                self.makeWidgetBlink(self.endBox)
                return
        step = self.stepBox.value()
        instancers = []
        for inst in self.instancers:
            if inst.isChecked():
                instancers.append(str(inst.objectName()))
        if not instancers:
            self.makeWidgetBlink(self.scrollArea)
            return
        for instancer in instancers:
            bpi.bake_particle_inst(instancer, step, startFrame, endFrame)
        
    def refresh(self):
        self.clearInstancers()
        self.listInstancers()
        
    def makeWidgetBlink(self, widget):
        """Makes the given widget blink with red color"""
        ss = widget.styleSheet()
        for i in range(3):
            widget.setStyleSheet("border: 1px solid red;")
            widget.repaint()
            time.sleep(0.1)
            widget.setStyleSheet("border: None")
            widget.repaint()
            time.sleep(0.1)
        widget.setStyleSheet(ss)