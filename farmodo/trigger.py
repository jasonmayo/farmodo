


def doIStillHaveAJob():
    if (debug == 2):
        exit()
    conn = sqlite3.connect(lx.eval("user.value farmodo_pathToDB ?"))
    print "Looking for another job"
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
