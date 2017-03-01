#!/usr/bin/env python
import modo
import time
import lx
import lxifc
import lxu.command
import PySide
from PySide.QtGui import *
from PySide.QtCore import *

import farmodo

class showSubmitterGUI(lxu.command.BasicCommand):
    #show GUI
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Execute(self, msg, flags):
        reload(farmodo)
        lx.eval('layout.createOrClose open:True cookie:farmodoSubmitterCookie layout:farmodoSubmitterLayout width:250 height:600 style:palette title:{Render Farm}')
        lx.eval('select.viewportInWindow cookie:farmodoSubmitterCookie')
        lx.eval('customview.view farmodo.submitterGUI')

lx.bless(showSubmitterGUI,'farmodo.showGUI')

class interpretOutPattern_CLS(lxu.command.BasicCommand):

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Execute(self, msg, flags):
        reload(farmodo)
        print'hello world'
        farmodo.interpretOutPattern()

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(interpretOutPattern_CLS,'farmodo.interpretOutPattern')



# To create our custom view, we subclass from lxifc.CustomView
class submitterGUI_Class(lxifc.CustomView):
    def customview_Init(self, pane):
        if pane is None:
            return False
        custPane = lx.object.CustomPane(pane)
        if not custPane.test():
            return False

        # get the parent object
        parent = custPane.GetParent()

        # convert to PySide QWidget
        widget = lx.getQWidget(parent)

        # Check that it succeeds
        if widget is not None:
            farmodo.buildSubmitterLayout(widget)
            return True

        return False

# Finally, register the new custom view server to Modo
if( not lx.service.Platform().IsHeadless() ):
    lx.bless(submitterGUI_Class, 'farmodo.submitterGUI')
