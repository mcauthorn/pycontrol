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

'''
Example of how to pull a pool list from pycontrol v.2. This example passes in
the  'fromurl' keyword as True (default is False), which tells pycontrol
to fetch the WSDL from the remote BigIP.
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

pools = b.LocalLB.Pool.get_list()
version = b.LocalLB.Pool.get_version()

print "Version is: %s\n" % version
print "Pools:"

# Note that pools.item represents the pool list. Return
# Structures from pycontrol2 are VERY different from the original.
for x in pools:
    print "\t%s" % x

