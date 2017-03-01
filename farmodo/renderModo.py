#!/usr/bin/env python
import lx
import sqlite3
import os
import socket
from datetime import date, datetime
import platform
import modo
import constants
global renderJobId

jobsPending = True

def renderJob(job):    #render.animation this job
    debug = "0"
    # usage @modoRenderSubmit path/to/scene start end step output/path format -pass "comma,sep,text" -camera default -pattern default
    if job:
        renderJobId = job[JOBID]
    else:
        print "no job"
        return True


    # sys.stdout = open('/tmp/blt_renderLog.txt', 'a')



    lx.out("DEBUG LEVEL %s" % debug)
    lx.eval("log.toConsole true")
    lx.eval("log.toConsoleRolling true")
    lx.out("scenefile: %s " % job[SCENE])
    lx.out("start: %s " % job[JOBSTART])
    lx.out("end: %s " % job[JOBEND])
    lx.out("step: %s " % job[JOBSTEP])
    lx.out("camera: %s " % job[CAMERA])
    lx.out("initialPass: %s " % job[INITIAL_PASS])
    lx.out("passes: %s " % job[PASS])
    lx.out("passGroup: %s " % job[PASSGRP])
    lx.out("imageFile: %s " % job[IMAGEFILE])
    lx.out("imageFormat: %s " % job[IMAGEFORMAT])

    passGroup = job[PASSGRP]

    # # # # # #
    #scene open
    # # # # # #

    try:

        lx.eval("scene.open %s normal" % job[SCENE])
        scene = modo.Scene()
        #camera option
        renderCam = job[CAMERA]
        for camera in scene.cameras: # now search for it thoroughly, it may have been suffixed when imported as a reference
            if renderCam in camera.name:
                renderCam = camera.name
                lx.eval("render.camera {%s}" % renderCam)
                lx.out("render camera changed to %s" % renderCam)
                continue
        #intial pass setting - for multiple pass combos and multi node pass renders
        initialPassesPattern = ''
        initialList = job[6]
        if len(initialList):
            for eachInit in initialList.split(","):
                eachInitHalf = eachInit.split(":")
                initialRenderGroup = eachInitHalf[0]
                initialRenderPass = eachInitHalf[1]
                lx.out("intitial pass setting to %s" % initialRenderPass)
                if 'default' not in str(initialRenderPass) and len(initialRenderPass) > 0:
                    print 'not default or blank'
                    scene.item(initialRenderPass).active = True
                    initialPassesPattern += initialRenderPass + "_"
            print('initialPassesPattern is :%s' % initialPassesPattern)
        #pass option

        # # # # # #
        # set ouput pattern #replace <initialPass> marker with initial pass field
        # # # # # #
        outPat =  scene.items('polyRender')[0].channel('outPat').get()
        if "<initialPass>" in outPat:
            print "initial pass in output pattern"
            newOutPat = outPat.replace('<initialPass>',initialPassesPattern)
            if '__' in newOutPat:
                newOutPat = newOutPat.replace('__','_')
            scene.items('polyRender')[0].channel('outPat').set(newOutPat)
            lx.out("Output pattern changed to :%s " % (scene.items('polyRender')[0].channel('outPat').get()))



        lx.out("pass list specified %s" % job[7])
        #first switch everytning off
        n = lx.eval('query sceneservice actionItem.N ? ""')
        for x in range(n):  # enumerate ALL actionclips in scene
                eachPass = lx.eval("query sceneservice actionItem.name ? %d" % x)
                lx.eval("layer.enable {%s} off" % (eachPass))
                lx.out("switched off %s" % (eachPass))
        passDoList = job[7].split(",")
        renderPassGroup = job[8]
        if not renderPassGroup: #in case render pass group not given we can imply it from the pass
            for rpg in scene.renderPassGroups:
                for eachPass in rpg.passes:
                    if passDoList[0] == eachPass.name:
                        lx.out("Render pass group: %s implied from pass: %s" % (rpg.name,eachPass.name))
                        renderPassGroup = str(rpg.name)
        for eachPass in passDoList:
                lx.eval("layer.enable {%s} on" % (eachPass))
                lx.out("switched on %s" % (eachPass))

        # # # # # #
        #set start end
        # # # # # #

        lx.eval("select.item Render")
        lx.eval("item.channel first %s" % job[2])
        lx.eval("item.channel last %s" % job[3])
        lx.eval("item.channel step %s" % job[4])



        # # # # # #
        #render animation
        # # # # # #
        renderCmd = "render.animation filename:" + job[9] + " format:" + job[10]

        lx.out(renderCmd)
        if job[7] and (job[6] is not None):
            renderCmd += " group:{" + renderPassGroup + "}"

        if(debug == "0"):
            lx.out('Render Command: %s'% renderCmd)
            lx.eval(renderCmd)
            lx.eval ('!scene.close')
        if(debug == "1"):
            lx.out('Render Command: %s'% renderCmd)
        if(debug == "2"):
            lx.out('Saving scene only')
            lx.eval ('!scene.save')

        lx.out('Render Finshed For: %s'% job[1])
        markJobAsFinished(job[0],True)
        lx.eval('log.masterSave "/tmp/modoConsoleLog.txt"')
        return True
    except:
        print"******render Failed*******"
        print"Closing scene"
        lx.eval ('!scene.close')
        markJobAsFinished(job[0],False)
        return False




def jobAssignedToThisNode():
    #get job assigned to this node, there can only be one
    jobD={}
    conn = sqlite3.connect(lx.eval("user.value farmodo_pathToDB ?"))
    lx.out("Retrieving assigned job")
    username = socket.gethostname()
    cur = conn.cursor()
    cur.execute('PRAGMA table_info (renderJobs)')
    pragma =cur.fetchall()
    cur.execute('SELECT * FROM renderJobs WHERE username = "%s" AND status = "%s" '  % (username,"rendering"))
    job=cur.fetchone()
    conn.close()
    for i in range(len(job)):
	    jobD[pragma[i][1]]=job[i]
    return jobD




    #mark th job as finished
def markJobAsFinished(renderJobId,success):
    #get job assigned to this node, there can only be one
    conn = sqlite3.connect(lx.eval("user.value farmodo_pathToDB ?"))
    cur = conn.cursor()
    lx.out("Finishing assigned job: id %d" % renderJobId)
    if success:
        cur.execute('UPDATE renderJobs SET status="----finished----" WHERE id=%d' % renderJobId)
    else:
        cur.execute('UPDATE renderJobs SET status="****ERROR****" WHERE id=%d' % renderJobId)
    conn.commit()
    conn.close()

    #now check to see if there is another job
        #if there is another job then renderAssigned Job
        #else mark the iAmFreeTag to Free and app.quit modo


def doIStillHaveAJob():
    conn = sqlite3.connect(lx.eval("user.value farmodo_pathToDB ?"))
    print "Looking for another job"
    username = socket.gethostname()
    cur = conn.cursor()
    cur.execute('SELECT id,scenePath FROM renderJobs WHERE status LIKE "pending" ORDER BY id ASC' ):
    job = cur.fetchone()
        if job:
            print("Job  %s found to render %s" %(job[0],job[1]))
            #assign node to this job
            cur.execute('UPDATE renderJobs SET status="rendering", username="%s" WHERE id=%d' % (username,job[0]))
            print("Rendering assigned to:" + username)
            conn.commit()
            print"commit"
            conn.close()
            return True
    conn.close()
    return False



if __name__ == "__main__":
    print("renderModo script")
    while(jobsPending):
        renderJob(jobAssignedToThisNode())
        jobsPending = doIStillHaveAJob()

    try:
        os.system('rm ' + blt_farm.tagFileName)
    except:
        print "Error trying to delete tmp file"
    #quit modo and nap
    lx.eval('app.quit')
