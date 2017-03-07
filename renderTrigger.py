#!/usr/bin/env python
from datetime import date, datetime
import sqlite3
import settings
import socket
import os
import platform
from settings import *
import subprocess

# #!/usr/bin/env python
#
# import sqlite3
# import sys
# import os
# import socket
# from datetime import date, datetime
# import platform
# import blt_settings
# import datetime


""" this script is called by each render node periodically from outside of Modo to check database for new jobs,
if a job is found a chain reaction is started and subsequent jobs are grabbed using a sister script in
renderModo"""

def openModo():
    """"open up modo_cl and run a script to pick up the job we just allocated to this node"""


def thereIsAJobDoIt():
    conn = sqlite3.connect(settings.pathToDB)
    print "Looking for a job"
    username = socket.gethostname()
    cur = conn.cursor()
    cur.execute('SELECT id,application FROM renderJobs WHERE status LIKE "pending" ORDER BY id ASC' )
    job = cur.fetchone()
    if job:
        #assign node to render this job
        print("Job  %s found to render %s" %(job[0],job[1]))
        if job[1] == 'modo':
            pid = renderModo()#collect process number so we can kill it if we need to
        cur.execute('UPDATE renderJobs SET status="assigned", username="%s",process = "%s" WHERE id=%d' % (username,pid,job[0]))
        print("Rendering assigned to:" + username)
        conn.commit()
        print"commit"
        conn.close()
        return True
    conn.close()
    return False







tagFile = ""


def modoApp():
    if platform.system() == 'Linux':
        print "Linux platform"
        return linuxModo
    elif platform.system() == 'Darwin':
        print"OSX platform"
        return OSXModo
    else:
        return "Windows? Currently this is *nix only, sorry"

#check that I'm free
def freeToRender():
    #this file is created when a node is rendering and deleted after
    if os.path.isfile(tagFileName):
        # TO DO:check to see if this tag is stale (passed its timeout time)
        return False
    else:
        return True


def renderModo():
    renderArgs = []
    renderArgs.append(modoApp())
    renderCmd = modoApp()
    renderArgs.append('-cmd:@' + rootDir + '/renderModo.py')#command to run when Modo starts up
    renderArgs.append('-path:content='+ contentPath )
    renderArgs.append('-config:' + modoConfig)
    renderArgs.append('-dbon:noconfig')
    renderArgs.append('-dblog:/tmp/farmmodolog.txt')
    renderArgs.append('-debug:normal')
    # renderArgs.append(' > /tmp/modo_render_log ')
    print renderArgs
    print renderCmd
    # os.system(renderCmd)
    process = subprocess.Popen(renderArgs,shell = False)
    return process.pid


def tellThemImBusy():
    try:
        print"Creating busy tagfile"
        file=open(tagFileName,'a')
        # TO DO:timestamp this file with nowtime plus timeout time
    except:
        print"Error trying to create tmp file"


if __name__ == "__main__":
    print("Farmodo trigger script")
    # check database for pending render jobs
    if not (freeToRender()):
        print("Modo process already running")
    elif thereIsAJobDoIt():
        tellThemImBusy()
        # renderModo()# which is now assigned to this node
    else:
        print"No Jobs"
