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

renderPassLayout = QVBoxLayout()
renderJobLayout = QVBoxLayout()
renderPassLayout = QVBoxLayout()
cameraRadioButtonLayout = QVBoxLayout()
outPatternPreview = QTextBrowser()
imageNameEdit = QLineEdit()
imageFormatMenu = QComboBox()
imageFormatInternalName = ['']
imageFormatUserName = ['']
imageFormatSuffix = ['']
imagePathEdit = QLineEdit()
guiStart = 0
spinBoxStart = QSpinBox()
spinBoxEnd = QSpinBox()
spinBoxStep = QSpinBox()
jobsPerStep = QCheckBox('Job per Step')
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

                # cur.execute("INSERT INTO renderJobs(id,scenePath,start,end,step,camera,initialPass,passes,passGroup,imageFile,imageFormat,status,timeSubmitted,timeLimit,priority,application) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(newId,menuData[0],start,menuData[2],menuData[3],menuData[4],initialPass,menuData[5],menuData[6],imagePath,menuData[8],status,now,menuData[9],menuData[10],"modo"))
                # with open("/Users/jasonmayo/Desktop/sqlCmd.txt", "w") as text_file:
                #     text_file.write(sqlCmd)""
                # if cur.lastrowid:
                #     lx.out("job submitted with id %s" % (cur.lastrowid))
                #     newId = cur.lastrowid +1
    # try:
    #     for job in jobList:
    #         status = "pending"
    #         now = datetime.now().strftime('%c')
    #         minMachines = 1
    #         priority = 1
    #         initialPass = menuData[12] + ":" + job
    #         if (len(jobList)>1) and ("<initialPass>" not in outPat):
    #             imagePath = menuData[7] + "_" + job
    #         while machine < step:#assign a machine for each step
    #             cur.execute("INSERT INTO renderJobs(id,scenePath,start,end,step,camera,initialPass,passes,passGroup,imageFile,imageFormat,status,timeSubmitted,timeLimit,priority,application) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(newId,menuData[0],start,menuData[2],menuData[3],menuData[4],initialPass,menuData[5],menuData[6],imagePath,menuData[8],status,now,menuData[9],menuData[10],"modo"))
    #             if cur.lastrowid:
    #                 lx.out("job submitted with id %s" % (cur.lastrowid))
    #                 newId = cur.lastrowid +1
    #             start +=1
    #             machine +=1
    conn.commit()
    conn.close()
    # except lite.Error as er:
    #     modo.dialogs.alert("ERROR", er.message, dtype='info')



def frameRangesByStep(first,last,step):
    ranges=[]
    frames = (last+1) - first
    if step <1:
    	step =1
    if jobsPerStep.isChecked():
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
        start = (spinBoxStart.value())
    if not end:
        end = (spinBoxEnd.value())
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
    lx.out('Will Interpret Out pattern')
    scene = modo.Scene()
    imageNameList=''
    imageName = imageNameEdit.text()
    imageFormat = imageFormatInternalName[(imageFormatMenu.currentIndex())]
    LRCam = ''
    i=0
    j=1
    outPatList=''
    passList = layoutWidgetQuery(renderPassLayout)
    initialPass = layoutWidgetQuery(renderJobLayout)
    cameraList = layoutWidgetQuery(cameraRadioButtonLayout)
    for eachRange in frameRangesByStep(spinBoxStart.value(),spinBoxEnd.value(),spinBoxStep.value()):
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

def layoutWidgetQuery(layout):
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
    return {key:layers}

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

def renderJobQuery(layout):
    #query all the check boxes inside render job layer group
    scene = modo.Scene()
    layers=[]
    for i in range(layout.count()):
        widgetItem = layout.itemAt(i)
        if widgetItem.widget().isChecked():
            layers.append(scene.renderPassGroups[renderJobPopUp.currentIndex()].passes[i].name)
        return layers

def renderPassQuery(layout):
    #query all the check boxes inside render layer group
        layers=[]
        for i in range(layout.count()):
            widgetItem = layout.itemAt(i)
            if widgetItem.widget().isChecked():
                layers.append(scene.renderPassGroups[renderPassPopUp.currentIndex()].passes[i].name)
        return layers

def renderButtonClicked():
    #blt_module.renderToFarm(spinBoxStart.value())
    jobList = renderJobQuery(rjLayout)
    if not jobList:
        jobList = [""]
    list = []
    msgBox = QMessageBox()
    msgBox.setText("Scene not saved, nothing to submit.")
    if not (scene.filename):
        msgBox.exec_()
        return

    list.append(scene.filename)
    list.append(spinBoxStart.value())
    list.append(spinBoxEnd.value())
    list.append(spinBoxStep.value())
    for i in range(cameraRadioButtonLayout.count()):
        if((cameraRadioButtonLayout.itemAt(i).widget()).isChecked()):
            list.append(str((cameraRadioButtonLayout.itemAt(i).widget()).text()))
    #list.append(str(renderCamMenu.currentText()))
    list.append(",".join(renderPassQuery(renderPassLayout)))
    list.append(str(renderPassPopUp.currentText()))
    list.append((str(imagePathEdit.text()))+"/"+(str(imageNameEdit.text())))
    list.append(imageFormatInternalName[(imageFormatMenu.currentIndex())])
    list.append(timeLimit.value())
    list.append(priority.value())
    list.append(str(dbPathEdit.text()))
    list.append(str(renderJobPopUp.currentText()))
    list.append(",".join(renderJobQuery(rjLayout)))

    jobs = len(jobList)
    result = modo.dialogs.okCancel("submit",(str(jobs) + " jobs to submit"))
    if result == 'ok':
        blt_module.renderToFarm(list)

def clearLayout(layout):
    if layout != None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())



def getImageFolder():

    imageDir = QFileDialog.getExistingDirectory(None,("Open Directory"),("~/Pictures"),QFileDialog.ShowDirsOnly);
    imagePathEdit.setText(imageDir)

def makeRenderJobCheckboxes(index):
    layout = renderJobLayout
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
            checkBox.stateChanged.connect(updateOutPatternPreview)
    updateOutPatternPreview()

def makeRenderPassCheckboxes(index):
    layout = renderPassLayout
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
            checkBox.stateChanged.connect(updateOutPatternPreview)
    updateOutPatternPreview()



def buildSubmitterLayout(widget):

    # try:
    #     cssString = QString('')
    # except:
    #     QString = type("")
    #     cssString = QString("")
    #
    # with open((os.path.split(__file__)[0] + '/style.css'), 'r') as cssFile:
    #     cssString = QString(cssFile.read())

    #widget.setStyleSheet(cssString)

    widget.setStyleSheet("QGroupBox {border-image: none; border-style: solid; border-radius : 6px;border-width: 1px ; border-color: #353535}")
    scene = modo.Scene()
    renderItem = scene.renderItem
    #frame range buttons
    spinBoxStart.setFont(BIG_FONT)
    spinBoxStart.setRange(-999999, 999999)
    spinBoxStart.setValue(renderItem.channel('first').get())
    spinBoxStart.editingFinished.connect(updateOutPatternPreview)
    spinBoxEnd.setFont(BIG_FONT)
    spinBoxEnd.setRange(-999999, 999999)
    spinBoxEnd.setValue(renderItem.channel('last').get())
    spinBoxEnd.editingFinished.connect(updateOutPatternPreview)
    spinBoxStep.setFont(BIG_FONT)
    spinBoxStep.setRange(0, 999999)
    spinBoxStep.setValue(renderItem.channel('step').get())
    spinBoxStep.editingFinished.connect(updateOutPatternPreview)
    stepFormLayout = QFormLayout()
    jobsPerStep.setChecked(True)
    jobsPerStep.clicked.connect(updateOutPatternPreview)
    stepFormLayout.addRow(spinBoxStep,jobsPerStep)

    #render camera buttons
    cameraBox = QGroupBox('Render Camera')
    for camera in scene.cameras:
        camRadioButton = QCheckBox(str(camera.name))
        cameraRadioButtonLayout.addWidget(camRadioButton)
        camRadioButton.toggled.connect(updateOutPatternPreview)
    (cameraRadioButtonLayout.itemAt(scene.renderCamera.index).widget()).setChecked(True)
    cameraBox.setLayout(cameraRadioButtonLayout)

    #make frame range form layout
    frameRangeOutline = QGroupBox('Frame Range')
    frameRangeLayout = QFormLayout()
    frameRangeLayout.addRow('First',spinBoxStart)
    frameRangeLayout.addRow('Last',spinBoxEnd)
    frameRangeLayout.addRow('Step',stepFormLayout)
    frameRangeOutline.setLayout(frameRangeLayout)


    #outline render pass job category
    renderJobOutline = QGroupBox('Render Jobs (each scene initialised with "initial pass")')
    #make a vertical box layout
    # renderJobLayout = QVBoxLayout()
    #make a combo box of all render jobs from passes
    renderJobPopUp = QComboBox()
    #check if there are any render pass groups
    renderJobList = ["-Single Job-"]+([rpg.name for rpg in scene.renderPassGroups])
    renderJobPopUp.addItems(renderJobList)
    renderJobLayout.addWidget(renderJobPopUp)
    i=0
    renderJobPopUp.setCurrentIndex(0)
    #connecting refresh on rj change
    renderJobPopUp.currentIndexChanged.connect(makeRenderJobCheckboxes)
    #add outline to layout
    renderJobOutline.setLayout(renderJobLayout)

    #outline render pass job category
    renderPassOutline = QGroupBox('Render Passes (pass list or each Render Job)')
    #make a combo box of all render jobs from passes
    renderPassPopUp = QComboBox()
    #make a vertical box layout
    # renderPassLayout = QVBoxLayout()
    #check if there are any render pass groups

    renderPassList = ["-None-"]+[rpg.name for rpg in scene.renderPassGroups]
    renderPassPopUp.addItems(renderPassList)
    renderPassLayout.addWidget(renderPassPopUp)
    i=0
    renderPassPopUp.setCurrentIndex(i)
    for rpg in scene.renderPassGroups:
        if lx.eval('group.current ? pass') == rpg.id:
            makeRenderPassCheckboxes(i+1)
            renderPassPopUp.setCurrentIndex(i+1)
        i+=1

    renderPassPopUp.currentIndexChanged.connect(makeRenderPassCheckboxes)
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



    generalLayout.addWidget(renderButton)

    widget.setLayout(masterLayout)
    updateOutPatternPreview()


if __name__ == '__main__':
    print "This only executes when is executed rather than imported"
