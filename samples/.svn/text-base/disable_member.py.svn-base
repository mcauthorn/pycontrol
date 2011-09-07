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


# A basic example of how to disable a pool member from pycontrol v.2. This example passes in
#the  'fromurl' keyword as True (default is False), which tells pycontrol
#to fetch the WSDL from the remote BigIP. If you don't pass 'fromurl', you'll
#need to pass in a full path to your local WSDL store on-disk.

POOL = 'test2' # Change this to your pool
members = ['1.2.3.4:80','1.2.3.4:81'] # members to disable

if pc.__version__ == '2.0':
    pass
else:
    print "Requires pycontrol version 2.x!"
    sys.exit()

if len(sys.argv) < 4:
    print "Usage %s ip_address username password" % sys.argv[0]
    sys.exit()

a = sys.argv[1:]

# The constructor is similar to the original pyControl.
# Note the change from wsdl_files to wsdls, which makes more sense.
b = pc.BIGIP(
        hostname = a[0],
        username = a[1],
        password = a[2],
        fromurl = True,
        wsdls = ['LocalLB.PoolMember'])

# According to the API, we need to pass in a type of
# 'LocalLB.PoolMember.MemberSessionStateSequenceSequence' into this
# method's "session_states" keyword argument. So the flow will go like:
# 
#  1) Create a pool member object (Common.IPPortDefinition).
#  2) Create a session state object (LocalLB.PoolMember.MemberSessionState)
#  3) Add that to a 'sequence'
#
# We'll use the 'typefactory' to create these types to pass in.


# --------- helper methods below ---------- #

def member_factory(b, member):
    ''' 
    Produces a Common.IPPortDefinition object per member ip:port combination
    object per member ip:port combination. Add these to Common.IPPortDefinitionSequence.

    args: a pycontrol LocalLB.PoolMember object and an ip:port
    combination that you'd like to add.
    '''

    ip,port = member.split(':')
    pmem = b.LocalLB.PoolMember.typefactory.create('Common.IPPortDefinition')
    pmem.address = ip
    pmem.port = int(port)
    return pmem

def session_state_factory(b, members):
    ''' 
    Returns session state objects. Returns a list of session state objects with associated
    members.
    '''
    session_states = []

    # create a type of: 'LocalLB.PoolMember.MemberSessionState'
    # Inside of this type, you'll see that it expects a pool member as an
    # attribute. Let's create that, set our attributes (address, port), and add it to sstate
    # above.

    for x in members:
        sstate = b.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberSessionState')
        sstate.member = member_factory(b,x) 
        sstate.session_state = 'STATE_DISABLED'
        session_states.append(sstate)
    return session_states


# The session state sequence object. Takes a list of 'member session state'
# objects.Wrap the members in a LocalLB.PoolMember.MemberSessionStateSequence
sstate_seq = b.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberSessionStateSequence')

# 'item' is an attribute that maps to a list of 'Common.IPPortDefinition' objects.
sstate_seq.item = session_state_factory(b, members)


def disable_member(b, session_objects):
    """
    Disable our members in the of session state
    objects.
    """
    try:
        b.LocalLB.PoolMember.set_session_enabled_state(pool_names =
                [POOL], session_states = [sstate_seq])
    
    except Exception, e:
        print e

def enable_member(b, session_objects):
    """
    Enable our members in the of session state
    objects.
    """
    #Note how easy it is to simply 'toggle' the session state now that
    #we are dealing with object attributes.
    for x in sstate_seq.item:
        x.session_state = 'STATE_ENABLED'
    try:
        b.LocalLB.PoolMember.set_session_enabled_state(pool_names = [POOL],
                session_states = [sstate_seq])
    except Exception, e:
        print e


# ----- Now let's run it all. ---- #

# Create a list of members.
session_objects = session_state_factory(b,members)

# Disable them.
disable_member(b, session_objects)

# Let's confirm it's disabled.

res = b.LocalLB.PoolMember.get_session_enabled_state(pool_names = [POOL])
print "States: %s" % res

# Now let's confirm our session state.
enable_member(b, session_objects)
res = b.LocalLB.PoolMember.get_session_enabled_state(pool_names = [POOL])

print "States: %s" % res
