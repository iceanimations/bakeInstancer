import site
site.addsitedir(r"R:/Python_Scripts")
from PyQt4.QtGui import *
import plugins.utilities as utils
import bake_particle_instancer as bpi
from PyQt4 import uic
import os
osp = os.path
import sys

selfPath = sys.modules[__name__].__file__
rootPath = osp.dirname(osp.dirname(selfPath))
uiPath = osp.join(rootPath, 'ui')

Form, Base = uic.loadUiType(osp.join(uiPath, 'window.ui'))
class Window(Form, Base):
    def __init__(self, parent= utils.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        
        # bindings
        self.bakeButton.clicked.connect(self.bake)
        self.refreshButton.clicked.connect(self.refresh)
        self.selectAllButton.clicked.connect(self.selectAll)
        self.resetButton.clicked.connect(self.resetWindow())
        
        #variables
        self.instancers = []
        
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
            btn.clicked.connect(self.switchSelectAll)
            self.instancersLayout.addWidget(btn)
            self.instancers.append(btn)
        
    def bake(self):
        startFrame = None
        endFrame = None
        step = None
        
        
    def refresh(self):
        self.clearInstancers()
        self.listInstancers()