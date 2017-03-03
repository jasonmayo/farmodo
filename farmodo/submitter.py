#!/usr/bin/env python

import lx
import lxu.command
import modo
import PySide
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtSql import *
import farmodo
import os
import re
from datetime import date, datetime
import sqlite3 as lite

BIG_FONT = QFont("Helvetica", 18,QFont.Bold)
MEDIUM_FONT = QFont("Helvetica", 12,QFont.Bold)

scene = modo.Scene()

guiBuilt = False

outPatternPreview = QTextBrowser()
imageNameEdit = QLineEdit()
imageFormatMenu = QComboBox()
imageFormatInternalName = ['']
imageFormatUserName = ['']
imageFormatSuffix = ['']
imagePathEdit = QLineEdit()

guiSettings = {'start':scene.renderItem.channel('first').get(),'end':scene.renderItem.channel('last').get(), 'step':scene.renderItem.channel('step').get()}

passList = {}
initialPass = {}
cameraList = {}

# passList = {'colour':('red','black','blue')}
# initialPass = {'wheels':('steel')}


def dict2Text(dict):
	return str(dict).replace('{','').replace('}','').replace("'","").replace("(","").replace(")","").replace(" ","").replace("[","").replace("]","")

def submitToDB():
    newId = 0
    #message
    lx.out("submitting current scene farm database")
    #sqlite_file = '/Users/jasonmayo/Documents/qt/renderFarm/blottoFarmDB.db'
    sqlite_file = lx.eval("user.value farmodo_pathToDB ?")
    conn = lite.connect(sqlite_file)
    cur = conn.cursor()
    newId = cur.lastrowid
    job={}
    passList = layoutWidgetQuery(renderPassLayout)
    initialPass = layoutWidgetQuery(renderJobLayout)
    cameraList = layoutWidgetQuery(cameraRadioButtonLayout)
    imageFile = str(imagePathEdit.text()) + "/"+ str(imageNameEdit.text())
    for eachRange in frameRangesByStep(spinBoxStart.value(),spinBoxEnd.value(),spinBoxStep.value()):
        for eachCamera in cameraList[cameraList.keys()[0]]:
            for eachJob in initialPass[initialPass.keys()[0]]:
                idNum = newId
                first = eachRange.split('-')[0]
                last = eachRange.split('-')[1]
                step = str(spinBoxStep.value())
                scene = modo.Scene().filename
                status = "pending"
                now = datetime.now().strftime('%c')
                priority = '1'
                initialPassString = str(initialPass.keys()[0])+":"+eachJob
                passListString = dict2Text(passList)
                imageFormat = imageFormatSuffix[(imageFormatMenu.currentIndex())]
                timeLimit = '200'

                application = 'modo'
                camera = eachCamera
                cur.execute("INSERT INTO renderJobs(id,scenePath,start,end,step,camera,initialPass,passes,imageFile,imageFormat,status,timeSubmitted,timeLimit,priority,application) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(idNum,scene,first,last,step,camera,initialPassString,passListString,imageFile,imageFormat,status,now,timeLimit,priority,application))
                if cur.lastrowid:
                    lx.out("job submitted with id %s" % (cur.lastrowid))
                    newId = cur.lastrowid +1

    conn.commit()
    conn.close()


def frameRangesByStep(first,last,step):
    ranges=[]
    frames = (last+1) - first
    if step <1:
    	step =1
    if jobsPerStep:
        for i in range(step):
        	print first + i
        	ranges.append(str(first + i) + '-' + str(frames-((last)-(first+i))%step))
    else:
        ranges.append(str(first)+ '-' +str(last))
    return ranges
def replaceFsWithFrameRange(outPat,start,end):
    endPad = ''
    scene = modo.Scene()
    found = re.search('<F*.>',outPat)
    if not found:
        return outPat
    if not start:
        start = guiSettings['start']
    if not end:
        end = guiSettings['end']
    startPad = str(start)
    endPad = str(end)
    # end = str(scene.renderItem.channel('first').get())
    while len(startPad)<(len(found.group(0))-2):
        startPad = '0' + startPad
    if start == end:
        return outPat.replace(found.group(0),startPad)
    else:
        while len(endPad)<(len(found.group(0))-2):
            endPad = '0' + endPad
        return outPat.replace(found.group(0),(startPad + '-' + endPad))

    # return outPat.replace(r.group(0),startPad)


def updateOutPatternPreview():
    print'Update out pattern preview'
    print str(guiSettings)
    scene = modo.Scene()
    imageNameList=''
    imageName = imageNameEdit.text()
    imageFormat = imageFormatInternalName[(imageFormatMenu.currentIndex())]
    LRCam = ''
    i=0
    j=1
    outPatList=''
    passList = guiSettings.get('passList',None)
    initialPass = guiSettings.get('initialPass',None)
    cameraList = guiSettings.get('cameraList',None)

    for eachRange in frameRangesByStep(guiSettings['start'],guiSettings['end'],guiSettings['step']):
        for eachCamera in cameraList[cameraList.keys()[0]]:
            for eachJob in initialPass[initialPass.keys()[0]]:
                outPatList += 'job#'+ str(j) +'\n'
                j+=1
                for eachPass in passList[passList.keys()[0]]:
                    for eachOutput in renderOutputQuery(True):
                        currentPat = imageName + scene.renderItem.channel('outPat').get()
                        currentPat = replaceFsWithFrameRange(currentPat, eachRange.split('-')[0],eachRange.split('-')[1])
                        renderOutput =  eachOutput
                        currentPat = currentPat.replace('[','')
                        currentPat = currentPat.replace(']','')
                        currentPat = currentPat.replace('<pass>',eachPass)
                        currentPat = currentPat.replace('<initialPass>',eachJob)
                        currentPat = currentPat.replace('<output>',renderOutput)
                        currentPat = currentPat.replace('<LR>',LRCam)
                        currentPat = currentPat.replace('<camera>',eachCamera)
                        currentPat = currentPat.replace('<none>','')
                        currentPat  += '.' + imageFormatSuffix[(imageFormatMenu.currentIndex())]
                        currentPat += '\n'
                        outPatList += currentPat
    print outPatList
    outPatternPreview.setText(outPatList)

def renderOutputQuery(noAlpha):
    scene= modo.Scene()
    outputList =[]
    for output in scene.items(itype = 'renderOutput'):
        if not (output.channel('enable').get()):
            continue
        elif noAlpha and (output.channel('effect').get() != 'shade.alpha'):
            outputList.append(output.name)
        elif not noAlpha:
            outputList.append(output.name)
    return(outputList)

def layoutWidgetQuery(layout,guiSettingKey):
    """adds a dict to guiSettings dict, containing another dict with a single
    key to a list of controls representing passes usually"""
    scene = modo.Scene()
    layers=[]
    key = ''
    print(layout.count())
    for i in range(layout.count()):
        widgetItem = layout.itemAt(i)
        widgetClass = str(widgetItem.widget().__class__)
        if 'QComboBox' in widgetClass:
            key = str(widgetItem.widget().currentText())
        elif 'QCheckBox' in widgetClass:
            if widgetItem.widget().isChecked():
                print widgetItem.widget().text()
                layers.append(str(widgetItem.widget().text()))
    if not len(layers):
        layers.append('')
    print 'dict'+str( {key:layers})
    guiSettings[guiSettingKey] = {key:layers}
    # refresh output pattern preview
    print'should i update preview now?'
    if guiBuilt:
        updateOutPatternPreview()

def selectedCamera():
    for i in range(cameraRadioButtonLayout.count()):
        if((cameraRadioButtonLayout.itemAt(i).widget()).isChecked()):
            return (str((cameraRadioButtonLayout.itemAt(i).widget()).text()))


def get_imagesavers():
#""" Returns a list of available image savers. Each entry in the returned list
    #    is a tuple made up of the format's internal name, it's username and it's
    #    DOS type (extension).
    #
    #"""
    host_svc = lx.service.Host()
    savers = []
    for x in range(host_svc.NumServers('saver')):
        saver = host_svc.ServerByIndex('saver', x)
        out_class = saver.InfoTag(lx.symbol.sSAV_OUTCLASS)
        if  (out_class == 'image' or out_class == 'layeredimage'):
            name = saver.Name()
            uname = saver.UserName()
            try:
                dostype = saver.InfoTag(lx.symbol.sSAV_DOSTYPE)
            except:
                dostype = ''
            savers.append((name, uname, dostype,))
    return savers


def getImageFolder():

    imageDir = QFileDialog.getExistingDirectory(None,("Open Directory"),("~/Pictures"),QFileDialog.ShowDirsOnly);
    imagePathEdit.setText(imageDir)

def makeRenderJobCheckboxes(index,layout):
    print 'index: '+ str(index)
    print 'layout count: ' + str(layout.count())
    if layout is not None:
        while layout.count()>1:
            #delete all but the first popup item -single job-
            widget = layout.takeAt(1).widget()
            widget.deleteLater()
    #create check boxes for each render pass
    if index > 0:
        for renderPass in modo.Scene().renderPassGroups[index-1].passes:
            checkBox = QCheckBox(str(renderPass.name))
            checkBox.setChecked(renderPass.enabled)
            layout.addWidget(checkBox)
            checkBox.stateChanged.connect(lambda:layoutWidgetQuery(layout,'initialPass'))
    layoutWidgetQuery(layout,'initialPass')


def makeRenderPassCheckboxes(index,layout):
    print'makeRenderPassCheckboxes'
    print 'index: '+ str(index)
    print 'layout count: ' + str(layout.count())
    if layout is not None:
        while layout.count()>1:
            #delete all but the first popup item -single job-
            widget = layout.takeAt(1).widget()
            widget.deleteLater()
    #create check boxes for each render pass
    if index > 0:
        for renderPass in modo.Scene().renderPassGroups[index-1].passes:
            checkBox = QCheckBox(str(renderPass.name))
            checkBox.setChecked(renderPass.enabled)
            layout.addWidget(checkBox)
            checkBox.stateChanged.connect(lambda:layoutWidgetQuery(layout,'passList'))
    layoutWidgetQuery(layout,'passList')

def storeGuiSettings(widget,key):
	if 'QSpinBox' in  str(widget.__class__):
		guiSettings[key] = widget.value()
	elif 'QCheckBox' in str(widget.__class__):
		guiSettings[key] = bool(widget.checkState())
	print guiSettings[key]


def buildSubmitterLayout(widget):
    """Build a QtGUi view to prepare for submission to render farm"""

    widget.setStyleSheet("QGroupBox {border-image: none; border-style: solid; border-radius : 6px;border-width: 1px ; border-color: #353535}")
    scene = modo.Scene()
    renderItem = scene.renderItem
    #frame range buttons
    spinBoxStart = QSpinBox()
    spinBoxEnd = QSpinBox()
    stepFormLayout = QFormLayout()
    spinBoxStep = QSpinBox()


    spinBoxStart.setFont(BIG_FONT)
    spinBoxStart.setRange(-999999, 999999)
    spinBoxStart.setValue(guiSettings['start'])

    spinBoxStart.editingFinished.connect(lambda:storeGuiSettings(spinBoxStart,"start"))


    spinBoxEnd.setFont(BIG_FONT)
    spinBoxEnd.setRange(-999999, 999999)
    spinBoxEnd.setValue(guiSettings['end'])
    spinBoxEnd.editingFinished.connect(lambda:storeGuiSettings(spinBoxEnd,"end"))
    spinBoxStep.setFont(BIG_FONT)
    spinBoxStep.setRange(1, 999999)
    spinBoxStep.setValue(guiSettings['step'])
    spinBoxEnd.editingFinished.connect(lambda:storeGuiSettings(spinBoxStep,"step"))
    jobsPerStep = QCheckBox('Job per Step')
    jobsPerStep.setChecked(True)
    jobsPerStep.clicked.connect(lambda:storeGuiSettings(jobsPerStep,"jobsPerStep"))
    stepFormLayout.addRow(spinBoxStep,jobsPerStep)


    #render camera buttons
    cameraBox = QGroupBox('Render Camera')
    cameraRadioButtonLayout = QVBoxLayout()
    for camera in scene.cameras:
        camRadioButton = QCheckBox(str(camera.name))
        cameraRadioButtonLayout.addWidget(camRadioButton)
        if scene.renderCamera.id==camera.id:
            camRadioButton.setChecked(True)
        camRadioButton.toggled.connect(lambda :layoutWidgetQuery(cameraRadioButtonLayout,'cameraList'))
    #(cameraRadioButtonLayout.itemAt(scene.renderCamera.index).widget()).setChecked(True)
    cameraBox.setLayout(cameraRadioButtonLayout)


    #make frame range form layout
    frameRangeOutline = QGroupBox('Frame Range')
    frameRangeLayout = QFormLayout()
    frameRangeLayout.addRow('First',spinBoxStart)
    frameRangeLayout.addRow('Last',spinBoxEnd)
    frameRangeLayout.addRow('Step',stepFormLayout)
    frameRangeOutline.setLayout(frameRangeLayout)


    #outline render pass job category
    renderJobOutline = QGroupBox('Render Jobs (job initialised with pass)')
    #make a vertical box layout
    renderJobLayout = QVBoxLayout()
    #make a combo box of all render jobs from passes
    renderJobPopUp = QComboBox()
    #check if there are any render pass groups
    renderJobList = ["-Single Job-"]+([rpg.name for rpg in scene.renderPassGroups])
    renderJobPopUp.addItems(renderJobList)
    renderJobLayout.addWidget(renderJobPopUp)
    i=0
    renderJobPopUp.setCurrentIndex(0)
    #connecting refresh on rj change
    renderJobPopUp.currentIndexChanged.connect(lambda x:makeRenderJobCheckboxes(x,renderJobLayout))
    #add outline to layout
    renderJobOutline.setLayout(renderJobLayout)


    #outline render pass job category
    renderPassOutline = QGroupBox('Render Passes (pass list for job)')
    #make a combo box of all render jobs from passes
    renderPassPopUp = QComboBox()
    #make a vertical box layout
    renderPassLayout = QVBoxLayout()
    #check if there are any render pass groups
    renderPassList = ["-None-"]+[rpg.name for rpg in scene.renderPassGroups]
    renderPassPopUp.addItems(renderPassList)
    renderPassLayout.addWidget(renderPassPopUp)
    i=0
    renderPassPopUp.setCurrentIndex(i)
    for rpg in scene.renderPassGroups:
        if lx.eval('group.current ? pass') == rpg.id:
            makeRenderPassCheckboxes(i+1,renderPassLayout)
            renderPassPopUp.setCurrentIndex(i+1)
        i+=1
    renderPassPopUp.currentIndexChanged.connect(lambda x: makeRenderPassCheckboxes(x,renderPassLayout))
    renderPassOutline.setLayout(renderPassLayout)


    #make imagename box using scene name as default
    imageNameOutline = QGroupBox('Image Name')
    imageNameLayout = QVBoxLayout()
    imageFormLayout = QFormLayout()
    imageNameOutline.setLayout(imageFormLayout)
    # imageNameOutline.setLayout(imageNameLayout)
    imageNameEdit.setText((scene.name).rsplit( ".", 1 )[ 0 ])
    #make image path browser layout
    proj = lx.service.File()
    try:
        defaultPath= (proj.FileSystemPath(lx.symbol.sSYSTEM_PATH_PROJECT))
        defaultPath += "/Renders/Frames/"
    except:
        defaultPath =''

    imagePathEdit.setText(defaultPath)
    imagePathBrowse = QPushButton("browse")
    imagePathBrowse.clicked.connect(farmodo.getImageFolder)

    imageFormLayout.addRow('Base Name',imageNameEdit)
    imageBrowseFormLayout=QFormLayout()
    imageBrowseFormLayout.addRow(imagePathBrowse,imagePathEdit)
    imageFormLayout.addRow("Folder",imageBrowseFormLayout)
    imageFormLayout.addRow('Format',imageFormatMenu)


    #make image format menu
    imageFormatList = farmodo.get_imagesavers()
    for tpl in imageFormatList:
        imageFormatInternalName.append(tpl[0])
        imageFormatUserName.append(tpl[1])
        imageFormatSuffix.append(tpl[2])
    imageFormatMenu.addItems(imageFormatUserName)
    imageFormatMenu.currentIndexChanged.connect(updateOutPatternPreview)
    imageFormatMenu.setCurrentIndex(7)

    imageNameEdit.textChanged.connect(updateOutPatternPreview)
    
    # create main layout
    masterLayout = PySide.QtGui.QVBoxLayout()
    renderButton = QPushButton("Submit")
    renderButton.setStyleSheet("QPushButton { background-color: #f89a2b; color: black; font-size:24px}")
    # This connects the "clicked" signal of the submit button to the function above
    renderButton.clicked.connect(farmodo.submitToDB)

    #making tabbed widget

    tabwidget = QTabWidget()
    masterLayout.addWidget(tabwidget)

    generalTabWidget = PySide.QtGui.QWidget()
    tabwidget.addTab(generalTabWidget, 'Submit')
    generalLayout = QVBoxLayout(generalTabWidget)

    generalLayout.addWidget(frameRangeOutline)
    generalLayout.addWidget(cameraBox)
    generalLayout.addWidget(renderJobOutline)
    generalLayout.addWidget(renderPassOutline)
    generalLayout.addWidget(imageNameOutline)
    outPatternRefresh= QPushButton('Preview Image Name')
    outPatternRefresh.clicked.connect(updateOutPatternPreview)
    generalLayout.addWidget(outPatternRefresh)
    generalLayout.addWidget(outPatternPreview)

    # finally initilise guiSettings dictionary from gui layout
    layoutWidgetQuery(renderJobLayout,'initialPass')
    layoutWidgetQuery(renderPassLayout,'passList')
    layoutWidgetQuery(cameraRadioButtonLayout,'cameraList')
    
    
    generalLayout.addWidget(renderButton)

    widget.setLayout(masterLayout)
    print'**GUI BUILT***'
    global guiBuilt
    guiBuilt = True

if __name__ == '__main__':
    print "This only executes when is executed rather than imported"
