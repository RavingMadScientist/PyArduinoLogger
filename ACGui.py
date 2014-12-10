# -*- coding: utf-8 -*-
"""
Created on Sun Nov 23 00:37:20 2014

@author: legitz3
"""

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtCore import pyqtSlot
import numpy as np
import sys, os
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
# Qt4Agg backend-dependent FigureCanvas.
#Provides the object onto which the figure is drawn
# It also inherits from QWidget
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# import the NavigationToolbar Qt4Agg widget
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.backend_bases import FigureManagerBase, key_press_handler

#make into if loop (too lazy rite now)
sys.path.append("/home/legitz3/pyreal/SpectrumImporter")
sys.path.append("/home/legitz3/pyreal/ArduinoSerial/ArduinoConnGUI")

import basicembed
import ACGuiLib

#from SpectrumImporter import basicembed
#from SpectrumImporter import ParserGreeter

def main():

    qApp = QtGui.QApplication(sys.argv)
    print 'hello'
   # aw = ApplicationWindow()
   # print 'hello2'
   # aw.show()

    ArConn=basicembed.ComAppWindow(ManNumHeaders=4, stringMode=True)
#    ArConn=ParserGreeter.ParserGreeter()
#    ArConn=basicembed.ApplicationWindow()
    
    ArConn.show()
   
    sys.exit(qApp.exec_())
if __name__ == '__main__':
    main()       