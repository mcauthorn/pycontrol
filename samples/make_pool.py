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
import sys
import pycontrol.pycontrol as pc
import time

#Uncomment below to see how to log with pycontrol2/suds

#import logging
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)


'''
Example of how to create a pool from pycontrol v.2. This example passes in
the  'fromurl' keyword as True (default is False), which tells pycontrol
to fetch the WSDL from the remote BigIP.

This script will create a pool named from localtime, fetch members, then delete
the pool.

This example is also a good starting point for learning how to handle types in
pycontrol2!
'''

if len(sys.argv) < 4:
    print "Usage %s ip_address username password" % sys.argv[0]
    sys.exit()

a = sys.argv[1:]

if pc.__version__ == '2.0':
    pass
else:
    print "Requires pycontrol version 2.x!"
    sys.exit()

# The constructor is similar to the original pyControl.
# Note the change from wsdl_files to wsdls, which makes more sense.
b = pc.BIGIP(
        hostname = a[0],
        username = a[1],
        password = a[2],
        fromurl = True,
        wsdls = ['LocalLB.Pool'])



# We'll call the create() method, which takes three params:
# pool_names, lb_methods, and members. Note how we create objects for the more
# complicated stuff.


# we'll create an LB Method object. Its attributes look like
# "lbmeth.LB_METHOD_ROUND_ROBIN", etc.
lbmeth = b.LocalLB.Pool.typefactory.create('LocalLB.LBMethod')

# This is basically a stub holder of member items that we need to wrap up.
mem_sequence = b.LocalLB.Pool.typefactory.create('Common.IPPortDefinitionSequence')

# Now we'll create some pool members.
mem1 = b.LocalLB.Pool.typefactory.create('Common.IPPortDefinition')
mem2 = b.LocalLB.Pool.typefactory.create('Common.IPPortDefinition')

# Note how this is 'pythonic' now. We set attributes agains the objects, then
# pass them in.
mem1.address = '1.2.3.4'
mem1.port = 80

mem2.address = '1.2.3.4'
mem2.port = 81

# Create a 'sequence' of pool members.
mem_sequence.item = [mem1, mem2]

# Let's create our pool.
name = 'PC2' + str(int(time.time()))

b.LocalLB.Pool.create(pool_names = [name], lb_methods = \
        [lbmeth.LB_METHOD_ROUND_ROBIN], members = [mem_sequence])

# This method returns our members from the new pool.
members = b.LocalLB.Pool.get_member(pool_names = [name])

print "Created pool %s with members:" % name
for x in members:
    for y in x:
        print "%s:%s" % (y.address, y.port)
       


#Voila!
