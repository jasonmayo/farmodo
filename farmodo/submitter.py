#!/usr/bin/env python
import lx
import lxu.command
import modo
import PySide
from PySide.QtGui import *
import farmodo
import os

BIG_FONT = QFont("Helvetica", 24,QFont.Bold)
MEDIUM_FONT = QFont("Helvetica", 18,QFont.Bold) 


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
        layers=[]
        for i in range(layout.count()):
            widgetItem = layout.itemAt(i)
            if widgetItem.widget().isChecked():
                layers.append(scene.renderPassGroups[rjMenu.currentIndex()].passes[i].name)
        return layers

def renderPassQuery(layout):
    #query all the check boxes inside render layer group
        layers=[]
        for i in range(layout.count()):
            widgetItem = layout.itemAt(i)
            if widgetItem.widget().isChecked():
                layers.append(scene.renderPassGroups[rpgMenu.currentIndex()].passes[i].name)
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
    list.append(",".join(renderPassQuery(rpgLayout)))
    list.append(str(rpgMenu.currentText()))
    list.append((str(imagePathEdit.text()))+"/"+(str(imageNameEdit.text())))
    list.append(imageFormatInternalName[(imageFormatMenu.currentIndex())])
    list.append(timeLimit.value())
    list.append(priority.value())
    list.append(str(dbPathEdit.text()))              
    list.append(str(rjMenu.currentText()))
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
    

    
def buildSubmitterLayout(widget):
    
    def makeRenderPassCheckboxes(index):
        if rpgLayout is not None:
            clearLayout(rpgLayout)
        for renderPass in modo.Scene().renderPassGroups[index].passes:
            renderLayerBox = QCheckBox(str(renderPass.name))
            renderLayerBox.setChecked(renderPass.enabled)
            rpgLayout.addWidget(renderLayerBox)
            
    def makeRenderJobCheckboxes(index):
        if rjLayout is not None:
            clearLayout(rjLayout)
        for renderPass in modo.Scene().renderPassGroups[index].passes:
            renderJobBox = QCheckBox(str(renderPass.name))
            renderJobBox.setChecked(renderPass.enabled)
            rjLayout.addWidget(renderJobBox)
            
    def getRootPath():
        os.path.split(__file__)[0]

    
    


    try:
        cssString = QString('')
    except:
        QString = type("")
        cssString = QString("")
        
    with open((os.path.split(__file__)[0] + '/style.css'), 'r') as cssFile:
        cssString = QString(cssFile.read())

    #widget.setStyleSheet(cssString)

           
    
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
    radioLayout = QVBoxLayout()
    for camera in scene.cameras:
        radioLayout.addWidget(QRadioButton(camera.name))
    (radioLayout.itemAt(scene.renderCamera.index).widget()).setChecked(True)
    
    #make frame range form layout
    frameRangeBox = QGroupBox('Frame Range')

    frameRangeLayout = QFormLayout()
    frameRangeLayout.addRow("Start",spinBoxStart)
    frameRangeLayout.addRow("End",spinBoxEnd)
    frameRangeLayout.addRow("Step",spinBoxStep)
    frameRangeBox.setLayout(frameRangeLayout)
    frameRangeBox.setStyleSheet("QGroupBox {border-image: none; border-style: solid; border-radius : 6px;border-width: 1px ; border-color: #353535;padding-top:20px; min-height:100px}") 


    #make a combo box of all render pass jobs
    rjMenu = QComboBox()
    rjList = [""]
    #make a layout to contain passes
    rjLayout = PySide.QtGui.QVBoxLayout()
    #check if there are any render pass groups                   
    rjList = ([rpg.name for rpg in scene.renderPassGroups])
    rjList.append("-Single Job-")
    rjMenu.addItems(rjList)
    #make pass check boxes for current rpg
    i=0
    rjMenu.setCurrentIndex(len(rjList)-1)
    
    #connecting refresh on rj change
    #rjMenu.currentIndexChanged.connect(farmodo.makeRenderJobCheckboxes)
    rjMenu.currentIndexChanged.connect(makeRenderJobCheckboxes)
    
    #make a combo box of all render pass groups
    rpgMenu = QComboBox()
    rpgList = [""]
    #make a layout to contain passes
    rpgLayout = PySide.QtGui.QVBoxLayout()
    #check if there are any render pass groups
    if scene.renderPassGroups:                
        rpgList = ([rpg.name for rpg in scene.renderPassGroups])
        rpgList.append("-None-")
        rpgMenu.addItems(rpgList)
        #make pass check boxes for current rpg
        i=0
        for rpg in scene.renderPassGroups:
            if lx.eval('group.current ? pass') == rpg.id:
                rpgMenu.setCurrentIndex(i)
                makeRenderPassCheckboxes(i)
            i+=1
    else:
        rpgList = ["-None-"]
        rpgMenu.addItems(rpgList)
    #connecting refresh on rpg change
    rpgMenu.currentIndexChanged.connect(makeRenderPassCheckboxes)
    
    #make imagename box using scene name as default
    imageNameEdit = QLineEdit()
    imageNameEdit.setText((scene.name).rsplit( ".", 1 )[ 0 ] )
    
    #make image path browser layout
    proj = lx.service.File()
    try:
     defaultPath= (proj.FileSystemPath(lx.symbol.sSYSTEM_PATH_PROJECT))
     defaultPath += "/Renders/Frames/"
    except:
     defaultPath ='Set Project Directory'
    imagePathLayout = PySide.QtGui.QHBoxLayout()
    imagePathEdit = QLineEdit()
    imagePathEdit.setText(defaultPath)
    imagePathLayout.addWidget(imagePathEdit)
    imagePathBrowse = QPushButton("browse")
    imagePathBrowse.clicked.connect(farmodo.getImageFolder)
    imagePathLayout.addWidget(imagePathBrowse)
    
    #make image format menu
    imageFormatMenu = QComboBox()
    imageFormatList = farmodo.get_imagesavers()
    imageFormatInternalName = []
    imageFormatUserName = []
    for tpl in imageFormatList:
     imageFormatInternalName.append(tpl[0])                
     imageFormatUserName.append(tpl[1])
    imageFormatMenu.addItems(imageFormatUserName)
    imageFormatMenu.setCurrentIndex(6)
    
    # create main layout
    layout = PySide.QtGui.QVBoxLayout()
    renderButton = QPushButton("Submit")
    # This connects the "clicked" signal of the submit button to the function above
    renderButton.clicked.connect(farmodo.renderButtonClicked)
    
    #making tabbed widget
    tabwidget = QTabWidget()
    layout.addWidget(tabwidget)
    
    generalTabWidget = PySide.QtGui.QWidget()
    tabwidget.addTab(generalTabWidget, 'General')
    

    generalLayout = QVBoxLayout(generalTabWidget)
    generalLayout.addWidget(frameRangeBox)

    #testWidget = QFrame()
    #testWidget.setFixedSize(100,100)
    #testWidget.setObjectName("myWidget")
    #testWidget.setStyleSheet("#myWidget {background-color:red;}")
    #testWidget.setLayout(generalLayout)

    # make range box
    #rangeBox = QToolBar()
    #rangeBox.setStyleSheet("QFrame { border: 1px solid black }")
    #rangeBox.addWidget(QLabel('Frame Range'))
    

    #make camera box
    cameraBox = QVBoxLayout()
    renCamLabel = QLabel(('Render Camera'))
    cameraBox.addWidget(renCamLabel)
    cameraBox.addLayout(radioLayout)
    generalLayout.addLayout(cameraBox)
    
    
    generalLayout.addWidget(QLabel('Render Pass Jobs (initial pass)'))
    generalLayout.addWidget(rjMenu)
    generalLayout.addLayout(rjLayout)
    
    generalLayout.addWidget(QLabel('Render Passes (per Job)'))
    generalLayout.addWidget(rpgMenu)
    generalLayout.addLayout(rpgLayout)
    
    generalLayout.addWidget(farmodo.HLine())
    
    generalLayout.addWidget(QLabel('Image Name'))
    generalLayout.addWidget(imageNameEdit)
    generalLayout.addWidget(QLabel('Image Folder'))
    generalLayout.addLayout(imagePathLayout)
    generalLayout.addWidget(QLabel('Image Format'))
    generalLayout.addWidget(imageFormatMenu)
    
    layout.setContentsMargins(2, 2, 2, 2)
    layout.addStretch()
    layout.addWidget(renderButton)
    
    widget.setLayout(layout)
