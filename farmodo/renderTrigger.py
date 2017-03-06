#!/usr/bin/env python
from datetime import date, datetime
import sqlite3
import settings
import socket


""" this script is called by each render node periodically from outside of Modo to check database for new jobs,
if a job is found a chain reaction is started and subsequent jobs are grabbed using a sister script in
renderModo"""

def openModo():
    """"open up modo_cl and run a script to pick up the job we just allocated to this node"""


def thereIsAJob():
    conn = sqlite3.connect(settings.pathToDB)
    print "Looking for a job"
    username = socket.gethostname()
    cur = conn.cursor()
    cur.execute('SELECT id,scenePath FROM renderJobs WHERE status LIKE "pending" ORDER BY id ASC' )
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
    print("Farmodo trigger script")
    # check database for pending render jobs
    if thereIsAJob():
        openModo
