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
# Or, pass in debug=True to the pycontrol constructor.

'''
Example of how to create a partition from pycontrol v.2. This example passes in
the  'fromurl' keyword as True (default is False), which tells pycontrol
to fetch the WSDL from the remote BigIP. 

This script will create a partition named pycontrol2.

This example is also a good starting point for learning how to handle types in
pycontrol2! 
'''

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
p = pc.BIGIP(
        hostname = a[0],
        username = a[1],
        password = a[2],
        fromurl = True,
        wsdls = ['Management.Partition'])


# Output from printing "b.Management.Partition.create_partition.params" is:
# (partitions, u'Management.Partition.AuthZPartitionSequence'),
# so we know we'll need to create an object  of
# Management.Partition.AuthZPartition, set its parameters, then pass it in
# as a sequence (python list).

# Generate the object via typefactory.
part = p.Management.Partition.typefactory.create('Management.Partition.AuthZPartition')

# Modify the attributes.
part.partition_name = 'pycontrol2'
part.description = 'Made via pycontrol2!'

# Now create it. It's as simple as:
p.Management.Partition.create_partition(partitions = [part])

# Let's check and see if our partition is in the list now.
res = p.Management.Partition.get_partition_list()

for x in res:
    if 'pycontrol2' in x.partition_name[0]:
        print "Created partition %s, with description: %s" % (x.partition_name[0], x.description[0])


# Now, if we run this again, we'll get an informative(!) exception:

#suds.WebFault: Server raised fault: 'Exception caught in Management::urn:iContro l:Management/Partition::create_partition()
#Exception: Common::OperationFailed
#        primary_error_code   : 16908343 (0x01020037)
#        secondary_error_code : 0
#        error_string         : 01020037:3: The requested partition (pycontrol2) #already exists.'
