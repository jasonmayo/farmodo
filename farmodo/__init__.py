#!/usr/bin/env python
import lx
import lxu.command
import modo
import PySide
from PySide.QtGui import *
import farmodo
import os

BIG_FONT = QFont("Helvetica", 18,QFont.Bold)
MEDIUM_FONT = QFont("Helvetica", 12,QFont.Bold)
FIRST = 'Start'
LAST='End'
STEP ='Step'

renderPassLayout = QVBoxLayout()
renderJobLayout = QVBoxLayout()
renderPassLayout = QVBoxLayout()
outPatternPreview = QTextBrowser()
imageNameEdit = QLineEdit()
imageFormatMenu = QComboBox()
imageFormatInternalName = ['']
imageFormatUserName = ['']
imageFormatSuffix = ['']

from submitter import *
from utilities import *

def updateOutPatternPreview():
    print'Update out pattern preview'
    lx.out('Will Interpret Out pattern')
    scene = modo.Scene()
    imageNameList=''
    imageName = imageNameEdit.text()
    imageFormat = imageFormatInternalName[(imageFormatMenu.currentIndex())]
    frame = '0001'
    LRCam = ''
    i=0
    outPatList=''
    for eachJob in layoutWidgetQuery(renderJobLayout):
        for eachPass in layoutWidgetQuery(renderPassLayout):
            currentPat =imageName + scene.renderItem.channel('outPat').get()
            renderOutput =  scene.items('renderOutput')[i].name
            currentPat = currentPat.replace('[<pass>]',eachPass)
            currentPat = currentPat.replace('[<initialPass>]',eachJob)
            currentPat = currentPat.replace('<FFFF>',frame)
            currentPat = currentPat.replace('[<output>]',renderOutput)
            currentPat = currentPat.replace('[<LR>]',LRCam)
            currentPat = currentPat.replace('<none>','')
            currentPat  += imageFormatSuffix[(imageFormatMenu.currentIndex())]
            currentPat += '\n'
            outPatList += currentPat
    print outPatList
    outPatternPreview.setText(outPatList)

def layoutWidgetQuery(layout):
    scene = modo.Scene()
    layers=[]
    print(layout.count())
    for i in range(layout.count()):
        widgetItem = layout.itemAt(i)
        try:
            if widgetItem.widget().isChecked():
                print widgetItem.widget().text()
                layers.append(str(widgetItem.widget().text()))
        except:
            print'ignored widget'
    if not len(layers):
        layers.append('')
    print layers
    return layers




def submitToDB(paras):
    print 'first:' + str(paras['first'])
    print 'step:' + str(paras['step'])

def HLine():
                toto = QFrame()
                toto.setFrameShape(QFrame.HLine)
                toto.setFrameShadow(QFrame.Sunken)
                return toto

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
    for i in range(radioLayout.count()):
        if((radioLayout.itemAt(i).widget()).isChecked()):
            list.append(str((radioLayout.itemAt(i).widget()).text()))
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


    #
    # def getRootPath():
    #     os.path.split(__file__)[0]
    #
    #

    try:
        cssString = QString('')
    except:
        QString = type("")
        cssString = QString("")

    with open((os.path.split(__file__)[0] + '/style.css'), 'r') as cssFile:
        cssString = QString(cssFile.read())

    #widget.setStyleSheet(cssString)

    widget.setStyleSheet("QGroupBox {border-image: none; border-style: solid; border-radius : 6px;border-width: 1px ; border-color: #353535}")
    scene = modo.Scene()
    renderItem = scene.renderItem
    #frame range buttons

    spinBoxStart = QSpinBox()
    spinBoxStart.setFont(BIG_FONT)
    spinBoxStart.setRange(-999999, 999999)
    spinBoxStart.setValue(renderItem.channel('first').get())
    spinBoxEnd = QSpinBox()
    spinBoxEnd.setFont(BIG_FONT)
    spinBoxEnd.setRange(-999999, 999999)
    spinBoxEnd.setValue(renderItem.channel('last').get())
    spinBoxStep = QSpinBox()
    spinBoxStep.setFont(BIG_FONT)
    spinBoxStep.setRange(0, 999999)
    spinBoxStep.setValue(renderItem.channel('step').get())

    #render camera buttons
    cameraBox = QGroupBox('Render Camera')
    radioLayout = QVBoxLayout()
    for camera in scene.cameras:
        radioLayout.addWidget(QRadioButton(camera.name))
    (radioLayout.itemAt(scene.renderCamera.index).widget()).setChecked(True)
    cameraBox.setLayout(radioLayout)


    #make frame range form layout
    frameRangeOutline = QGroupBox('Frame Range')
    frameRangeLayout = QFormLayout()
    frameRangeLayout.setAlignment(kjh)
    frameRangeLayout.addRow(FIRST,spinBoxStart)
    frameRangeLayout.addRow(LAST,spinBoxEnd)
    frameRangeLayout.addRow(STEP,spinBoxStep)
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
    imagePathEdit = QLineEdit()
    imagePathEdit.setText(defaultPath)
    imagePathBrowse = QPushButton("browse image folder")
    imagePathBrowse.clicked.connect(farmodo.getImageFolder)

    imageFormLayout.addRow('Image Base Name',imageNameEdit)
    imageFormLayout.addRow(imagePathBrowse,imagePathEdit)
    imageFormLayout.addRow('Image Format',imageFormatMenu)


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
    # This connects the "clicked" signal of the submit button to the function above
    renderButton.clicked.connect(farmodo.renderButtonClicked)

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
    generalLayout.addWidget(outPatternPreview)




    masterLayout.addWidget(renderButton)

    widget.setLayout(masterLayout)
    updateOutPatternPreview()
