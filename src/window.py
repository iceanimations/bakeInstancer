import site
site.addsitedir(r"R:/Python_Scripts")
from PyQt4.QtGui import *
import plugins.utilities as utils
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
        
        #variables
        self.instancers = []
        
    def switchSelectAll(self):
        select = True
        for inst in self.instancers:
            if inst.isChecked():
                pass
            else: select = False; break
        self.selectAllButton.setChecked(select)
        
    def selectAll(self):
        select = self.selectAllButton.isChecked()
        for inst in self.instancers:
            inst.setChecked(select)
        
    def listInstancers(self):
        pass
        
    def bake(self):
        startFrame = None
        endFrame = None
        step = None
        
    def refresh(self):
        pass