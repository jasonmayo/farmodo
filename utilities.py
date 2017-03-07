#!/usr/bin/env python
import time

import lxu.command
import lx,modo


START = 'first'
END = 'last'
STEP ='step'
SCENE ='scenePath'


def browseDB():
    inpath = modo.dialogs.customFile('fileOpen', 'Open File', ('text',), ('SQlite File',), ('*.db',))
    lx.eval("user.value farmodo_pathToDB %s" % inpath)

def browseValue(suffix,userValue):
    inpath = modo.dialogs.customFile('fileOpen', 'Open File', ('text',), ('Text File',), ('*.'+suffix,))
    lx.eval("user.value %s %s" % (userValue,inpath))
