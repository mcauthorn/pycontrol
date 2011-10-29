#!/bin/env python

"""
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


Pycontrol, version 2. Written by Matt Cauthorn for f5 Networks, Inc.
Contributors: Mohamed Lhrazi

This version of pycontrol and its improvements are possible because of the Suds
SOAP package, written and maintained by Jeff Ortel. Please see https://fedorahosted.org/suds/
for more information on Suds. We thank Jeff for his excellent work!
"""

import logging
from urllib import pathname2url
import platform
from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor
from suds.cache import ObjectCache

# For file:// uris, don't use the Suds https transport.
from suds.transport.http import HttpAuthenticated

# Fix missing imports. These can be global, as it applies to all f5 WSDLS.
IMP = Import('http://schemas.xmlsoap.org/soap/encoding/')
DOCTOR = ImportDoctor(IMP)
ICONTROL_URI = '/iControl/iControlPortal.cgi'
SESSION_WSDL = 'System.Session'

__version__ = '2.1'
__build__ = 'r3'


class BIGIP(object):

    """
    Wrap suds client object(s) and create a user-friendly class to use.
    """
    def __init__(self, hostname=None, username=None, password=None,
            wsdls=None, directory=None, fromurl=False, debug=False,
            proto='https',sessions=False,cache=None, **kwargs):

        self.hostname = hostname
        self.username = username
        self.password = password
        self.directory = directory
        self.sessions = sessions
        self.fromurl = fromurl
        self.proto = proto
        self.debug = debug
        self.kw = kwargs
        self.sessionisset = False

        # Setup the object cache
        if cache:
            self.cache = cache
        else:
            self.cache = ObjectCache(days=30)

        if self.debug == True:
            self._set_trace_logging()

        location = '%s://%s%s' % (self.proto,self.hostname, ICONTROL_URI)

        if self.sessions:
            '''This if block forces System.Session into index 0 in the wsdl list.'''
            if SESSION_WSDL in wsdls:
                self.wsdls = [x for x in wsdls if not x.startswith('System.Session')]
                self.wsdls.insert(0,SESSION_WSDL)
            else:
                self.wsdls = wsdls
                self.wsdls.insert(0,SESSION_WSDL)
        else:
            self.wsdls = wsdls

        self.clients = self._get_clients()

        for client in self.clients:
            self._set_module_attributes(client)
            self._set_interface_attributes(client)
            self._set_interface_sudsclient(client)
            self._set_type_factory(client)
            self._set_interface_methods(client)
            client.factory.separator('_')
            client.set_options(location=location, cache=self.cache)

            if self.sessions:
                if self.sessionisset:
                    pass
                else:
                    self.sessionid=self.get_sessionid()
                self.set_sessionid(self.sessionid.__str__(), client)

    #---------------------
    # Setters and getters.
    #---------------------

    def get_sessionid(self):
        '''Fetch a session identifier from a v11.x BigIP.'''
        mod = getattr(self, 'System')
        sessionid = getattr(mod, 'Session').get_session_identifier()
        self.sessionisset = True
        return sessionid

    def set_sessionid(self,sessionid,client):
        '''
        Sets the session header for a client.
        @sessionid (String) - session_id to add to the X-iControl-Session header.
        @client - client object.
        '''
        client.set_options(headers = {'X-iControl-Session': sessionid})

    def _get_clients(self):
            """ Get a suds client for the wsdls passed in."""
            clients = []
            for wsdl in self.wsdls:
                url = self._set_url(wsdl)
                sudsclient = self._get_suds_client(url,**self.kw)
                clients.append(sudsclient)
            return clients

    def _get_module_name(self, c):
        """ Returns the module name. Ex: 'LocalLB' """
        return c.sd[0].service.name.split('.')[0]

    def _get_module_object(self, c):
        """ Returns a module object (e.g. LocalLB) """
        return getattr(self, self._get_module_name(c))

    def _get_interface_name(self, c):
        """
        Returns the interface name. Ex: 'Pool' from 'LocalLB.Pool'
        """
        return c.sd[0].service.name.split('.')[1]

    def _get_interface_object(self, c, module):
        """
        Returns an interface object (e.g. Pool). Takes a client object and a module
        object as args.
        """
        return getattr(module, self._get_interface_name(c))

    def _get_methods(self, c):
        """ Get and return a list of methods for a specific iControl interface
        """
        methods = [method[0] for method in c.sd[0].ports[0][1]]
        return methods

    def _get_suds_client(self, url,**kw):
        """
        Make a suds client for a specifij WSDL (via url).
        Added new Suds cache features. Warning: These don't work on
        Windows. *nix should be fine. Also exposed general kwargs to pass
        down to Suds for advance users who don't want to deal with set_options().
        """

        if self.fromurl == False:
            # We're file:// access, so don't use https transport.
            t = HttpAuthenticated(username = self.username, password = self.password)
            c = Client(url, transport=t, doctor=DOCTOR,**kw)
        else:
            c = Client(url, username=self.username,
                    password=self.password,doctor=DOCTOR,**kw)
        return c

    def _set_url(self, wsdl):
        """
        Set the path of file-based wsdls for processing.If not file-based,
        return a fully qualified url to the WSDL
        """
        if self.fromurl == True:
            if wsdl.endswith('wsdl'):
                wsdl.replace('.wsdl','')
            qstring = '?WSDL=%s' % wsdl
            return 'https://%s%s' % (self.hostname, ICONTROL_URI + qstring)

        else:

            if wsdl.endswith('wsdl'):
                pass
            else:
                wsdl = wsdl + '.wsdl'

            # Check for windows and use goofy paths. Otherwise assume *nix
            if platform.system().lower() == 'windows':
                url = 'file:' + pathname2url(self.directory +'\\' + wsdl)
            else:
                url = 'file:' + pathname2url(self.directory + '/' + wsdl)
        return url

    def _set_module_attributes(self, c):
        """ Sets appropriate attributes for a Module. """

        module = self._get_module_name(c)
        if  hasattr(self, module):
            return
        else:
            setattr(self, module, ModuleInstance(module) )

    def _set_interface_sudsclient(self, c):
        """
        Set an attribute that points to the actual suds client. This
        will allow for power-users to get at suds client internals.
        """
        module = self._get_module_object(c)
        interface = self._get_interface_object(c, module)
        setattr(interface, 'suds', c)

    def _set_interface_attributes(self, c):
        """ Sets appropriate attributes for a Module. """

        module = self._get_module_object(c)
        interface = self._get_interface_name(c)
        setattr(module, interface, InterfaceInstance(interface))

    def _set_interface_methods(self, c):
        """
        Sets up methods as attributes for a particular iControl interface.
        Method keys (attrs) point to suds.service objects for the interface.
        """
        module = self._get_module_object(c)
        interface = self._get_interface_object(c, module)
        methods = self._get_methods(c)

        for method in methods:
            suds_method = getattr(c.service, method)
            method_params = method[1]
            setattr(interface, method, suds_method)
            m = getattr(interface, method)
            self._set_method_input_params(c, m, method)
            self._set_return_type(c, m, method)

    def _set_method_input_params(self, c, interface_method, method):
        """
        Set the method input argument attribute named 'params' for easy
        reference.
        """

        m = c.sd[0].ports[0][0].method(method)
        params = []
        for x in m.soap.input.body.parts:
            params.append((x.name, x.type[0]))
        setattr(interface_method, 'params', params)

    def _set_return_type(self, c, interface_method, method):
        """ Sets the return type in an attribute named response_type"""
        m = c.sd[0].ports[0][0].method(method)
        if len(m.soap.output.body.parts):
            res = m.soap.output.body.parts[0].type[0]
            setattr(interface_method, 'response_type', res)
        else:
            setattr(interface_method, 'response_type', None)


    def _set_type_factory(self, c):
        factory = getattr(c, 'factory')
        module = self._get_module_object(c)
        interface = self._get_interface_object(c, module)
        setattr(interface, 'typefactory', factory)

    def _set_trace_logging(self):
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)


class ModuleInstance(object):
    """ An iControl module object to set attributes against. """
    def __init__(self, name):
        self.name = name

class InterfaceInstance(object):
    """ An iControl interface object to set attributes against. """
    def __init__(self, name):
        self.name = name

def main():
    import sys
    if len(sys.argv) < 4:
        print "Usage: %s <hostname> <username> <password>"% sys.argv[0]
        sys.exit()

    a = sys.argv[1:]
    b = BIGIP(
            hostname = a[0],
            username = a[1],
            password = a[2],
            fromurl = True,
            wsdls = ['LocalLB.Pool'])

    pools = b.LocalLB.Pool.get_list()
    version = b.LocalLB.Pool.get_version()
    print "Version is: %s\n" % version
    print "Pools:"
    for x in pools:
        print "\t%s" % x

if __name__ == '__main__':
    main()
