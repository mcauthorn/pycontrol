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

#######################################################################################
# Example of how to create a virtual server from pycontrol v.2. This example passes in
# the  'fromurl' keyword as True (default is False), which tells pycontrol
# to fetch the WSDL from the remote BigIP. This script creates an http VS 
# with oneconnect (see profile setup/sequence section).
#######################################################################################

if pc.__version__ == '2.0':
    pass
else:
    print "Requires pycontrol version 2.x!"
    sys.exit()

if len(sys.argv) < 4:
    print "Usage %s ip_address username password" % sys.argv[0]
    sys.exit()

a = sys.argv[1:]

b = pc.BIGIP(
        hostname = a[0],
        username = a[1],
        password = a[2],
        fromurl = True,
        wsdls = ['LocalLB.VirtualServer'])


# Setup a shortcut
v = b.LocalLB.VirtualServer

# create() takes four params:
# definitions, a Common.VirtualServerSequence,
# wildmasks, a Common.IPAddressSequence,
# resources, a LocalLB.VirtualServer.VirtualServerResourceSequence,
# profiles, a LocalLB.VirtualServer.VirtualServerProfileSequenceSequence

name = 'PC2' + str(int(time.time())) # the name of our vs.ww

# Setup types.
vs_def = v.typefactory.create('Common.VirtualServerDefinition')

vs_def.name = name
vs_def.address = '10.100.100.92'
vs_def.port = 8888

proto = v.typefactory.create('Common.ProtocolType')
vs_def.protocol = proto.PROTOCOL_TCP

vs_def_seq = v.typefactory.create('Common.VirtualServerSequence')
vs_def_seq.item = [vs_def]

# Resource has a 'type' attribute, which must point to a 'VirtualServerType'
# object, so let's create that.
vs_type = v.typefactory.create('LocalLB.VirtualServer.VirtualServerType')
resource = v.typefactory.create('LocalLB.VirtualServer.VirtualServerResource')

resource.type = vs_type.RESOURCE_TYPE_POOL
resource.default_pool_name = 'dummyServer' # Change to whatever pool you want 

# A resource sequence we can add the resource to.
resource_seq = v.typefactory.create(
        'LocalLB.VirtualServer.VirtualServerResourceSequence'
        )
resource_seq.item = [resource]


context = v.typefactory.create('LocalLB.ProfileContextType')
prof = v.typefactory.create('LocalLB.VirtualServer.VirtualServerProfile')
prof.profile_context = context.PROFILE_CONTEXT_TYPE_ALL
prof.profile_name = 'tcp'

prof_http = v.typefactory.create('LocalLB.VirtualServer.VirtualServerProfile')
prof_http.profile_name = 'http'

prof_oneconn = v.typefactory.create('LocalLB.VirtualServer.VirtualServerProfile')
prof_oneconn.profile_name = 'oneconnect'

# We need to create a 'profile sequence' to add this profile to...
prof_seq = v.typefactory.create(
        'LocalLB.VirtualServer.VirtualServerProfileSequence'
        )

prof_seq.item = [prof, prof_http, prof_oneconn]
try:
    v.create(
            definitions = vs_def_seq,
            wildmasks=['255.255.255.255'],
            resources=resource_seq,
            profiles=[prof_seq]
            )
except Exception, e:
    print "Error creating virtual server %s" % name
    print e

# To see the useful exceptions we now get, try running this script again.
# You'll see a message come back from the BigIP:

#################################################################################################
# Error creating virtual server PC21260800310
# Server raised fault: 'Exception caught in LocalLB::urn:iControl:LocalLB/VirtualServer::create()
# Exception: Common::OperationFailed
#        primary_error_code   : 17236787 (0x01070333)
#        secondary_error_code : 0
#        error_string         : 01070333:3: Virtual Server PC21260800310 illegally shares both
#        address and vlan with Virtual Server PC21260765845.'
#################################################################################################
