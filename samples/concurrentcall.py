#!/bin/env python

'''
----------------------------------------------------------------------------
The contents of this file are subject to the "END USER LICENSE AGREEMENT FOR F5
Software Development Kit for iControl"; you may not use this file except in
compliance with the License. The License is included in the iControl
Software Development Kit.

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
the License for the specific language governing rights and limitations
under the License.

The Original Code is iControl Code and related documentation
distributed by F5.

The Initial Developer of the Original Code is F5 Networks,
Inc. Seattle, WA, USA. Portions created by F5 are Copyright (C) 1996-2004 F5 Networks,
Inc. All Rights Reserved.  iControl (TM) is a registered trademark of F5 Networks, Inc.

Alternatively, the contents of this file may be used under the terms
of the GNU General Public License (the "GPL"), in which case the
provisions of GPL are applicable instead of those above.  If you wish
to allow use of your version of this file only under the terms of the
GPL and not to allow others to use your version of this file under the
License, indicate your decision by deleting the provisions above and
replace them with the notice and other provisions required by the GPL.
If you do not delete the provisions above, a recipient may use your
version of this file under either the License or the GPL.
----------------------------------------------------------------------------
'''
# *** NOTE *** 
# There appears to be a python 2.6 issue that will throw a 'maxiumum recursion'
# warnings with the Suds clone() method. This isn't a fatal error and 
# the script should still work.

import sys
import pycontrol.pycontrol as pc
import threading
import Queue
import time
'''
Example of threaded calls with pycontrol v.2. Almost all 
of this code was taken and then tweaked from:
http://www.ibm.com/developerworks/aix/library/au-threadingpython/ 

See this link for other good ideas on using threads with Python.

WARNING!!: timouts aren't accounted for here: if you have a zombie 
system it'll block and won't exit (on Windows, at least). You'll need
to account for this on your own!
'''
q = Queue.Queue()

if len(sys.argv) < 2:
    print "Usage: %s [bip1] [bip2]" % sys.argv[0]
    sys.exit()

if pc.__version__ == '2.0':
    pass
else:
    print "Requires pycontrol version 2.x!"
    sys.exit()


# The list of BigIP systems you want to query in parallel.
bigips = sys.argv[1:]

# Pick one and create a 'main' object. It's literally only a 
# Parent object that we'll clone multiple times for each system.
b = pc.BIGIP( hostname = bigips[0],
            username = 'admin', #change to match your env.
            password = 'admin', #change to match your env.
            directory = 'c:\\tmp\\', #Change this to a local dir on your system.
            wsdls = ['LocalLB.Pool'])
 
queue = Queue.Queue()

class ConcurrentCall(threading.Thread):
    """Threaded BigIP calls to multiple systems"""
    def __init__(self, queue, b):
        threading.Thread.__init__(self)
        self.queue = queue
        self.b = b

    def run(self):
        while True:
            #grab a BigIP host from queue
            host = self.queue.get()
            c = b.LocalLB.Pool.suds.clone()

            # Set the new location. Note how set_options() is used here. Handy!
            url = 'https://' + host + '/iControl/iControlPortal.cgi'
            c.set_options(location = url)

            # The get_version() call is now a pure Suds library call.
            # Once we clone(), we're working with pure Suds, not pycontrol.
            # With suds, we call methods against the service attribute (see
            # below).
            res = c.service.get_version()
            print "%s is %s" % (host.rjust(16), res.rjust(5))

            #signals to queue job is done
            self.queue.task_done()

start = time.time()
def main():
    
    # spawn a pool of threads, and pass them the queue instance 
    print "\n"
    for i in bigips:
        t = ConcurrentCall(queue, b)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for host in bigips:
        queue.put(host)
    
    # wait on the queue until everything has been processed
    queue.join()
main()
print "\n Elapsed Time: %s" % (time.time() - start)

