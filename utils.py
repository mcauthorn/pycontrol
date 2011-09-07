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

from logging import getLogger
log = getLogger(__name__)
from datetime import datetime

import os
import sys
import glob
import sgmllib
from logging import getLogger
import urllib2
from urllib2 import URLError
from tempfile import gettempdir

log = getLogger(__name__)
ICONTROL_URI = "/iControl/iControlPortal.cgi"

def longest_common_prefix(strings):
    """ 
    Taken from: http://boredzo.org/blog/archives/2007-01-06/longest-common-prefix-in-python-2
    This function returns the longest common prefix of one or more sequences. Raises an exception when zero sequences are provided.
    """
    assert strings, 'Longest common prefix of no strings requested. Such behavior is highly irrational and is not tolerated by this program.' 
    
    if len(strings) == 1: return strings[0] 
    
    strings = [pair[1] for pair in sorted((len(fi), fi) for fi in strings)]
    
    for i, comparison_ch in enumerate(strings[0]): 
        for fi in strings[1:]: 
            ch = fi[i] 
            if ch != comparison_ch: 
                return fi[:i] 
    return strings[0]

def setupHTTPAuth(url, username, password):
    """ Setup authentication if we're pulling from BigIP iControlPortal.cgi"""

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url, username, password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)

def get_wsdls(options):
    """ fetch the wsdls from BigIP and save them off in options.wsdl_dir"""
    wsdl_names = []
    setupHTTPAuth(options.bigip_url,options.username,options.password)
    log.info("Getting list of WSDLs on BigIP: %s..." % options.bigip_url)

    try:
        wsdl_list_url = "%s%s?WSDL" % (options.bigip_url,ICONTROL_URI)
        wsdl_index_page = urllib2.urlopen(wsdl_list_url).read()
        parser = WebParser()
        parser.parse(wsdl_index_page)
        links = parser.get_hyperlinks()
        wsdl_names = [x[x.find('=')+1:] for x in links]
    except URLError,e:
        log.error("Error getting list of WSDLs on BigIP: %s" % wsdl_list_url)
        raise

    log.info("Done. Found %d WSDLs" % len(wsdl_names))
    log.info("Downloading required WSDLs...")
    
    n = 0
    for wsdl_name in wsdl_names:
        #if options.setup_demo and not wsdl_name=="LocalLB.Pool": 
        #    continue
        #if not is_matching_wsdl(wsdl_name, options.setup_wsdl_patterns):
        #    continue
        wsdl_url = "%s%s?WSDL=%s" % (options.bigip_url, ICONTROL_URI, wsdl_name)
        wsdl_file_name = os.path.join(options.wsdl_dir,"%s.wsdl" % (wsdl_name))
        print "WSDL FILE NAME is: %s" % wsdl_file_name

        if options.setup_force or not os.path.exists(wsdl_file_name):
            log.debug("Downloading %s..." % (wsdl_file_name))
            wsdl_text = urllib2.urlopen(wsdl_url).read()
            wsdl_file = open(wsdl_file_name,"w+")
            wsdl_file.write(wsdl_text)
            wsdl_file.close()
            n+=1

    log.info("Done. Downloaded %d missing and required WSDLs." % n)
    return True

def empty_wsdl_dir(wsdl_dir):
    """ delete the wsdl files """

    for filename in glob.glob(os.path.join(wsdl_dir,"*.wsdl")):
        os.remove(filename)

def rebuild_wsdl_dir(options, empty):
    if empty: empty_wsdl_dir(options.wsdl_dir)
    get_wsdls(options)


class WebParser(sgmllib.SGMLParser):
    """A simple parser class."""

    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)
        self.close()
    
    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."
        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []

    def start_a(self, attributes):
        "Process a hyperlink and its 'attributes'."
        for name, value in attributes:
            if name == "href":
                self.hyperlinks.append(value)

    def get_hyperlinks(self):
        "Return the list of hyperlinks."
        return self.hyperlinks

def is_matching_wsdl(wsdl_name, wsdls_list):
    #log.debug("Testing wsdl_name %s against list: %s"%(wsdl_name,wsdls_list))
    if wsdls_list:
        module_name,interface_name = wsdl_name.split('.')
        wsdls_list = [x.split(".") for x in wsdls_list]
        for m,i in wsdls_list:
            if (m == "*" or m.upper() == module_name.upper()) and (i == "*" or i.upper() == interface_name.upper()):
                #log.debug("Testing wsdl_name %s MATCHED: %s.%s"%(wsdl_name,m,i))
                return True
    #log.debug("Testing wsdl_name %s NO MATCH"%(wsdl_name))
    return False


class UsefulU64(object):
    """
    A port of this Java class to Python:
    http://devcentral.f5.com/Default.aspx?tabid=63&articleType=ArticleView&articleId=78
    
    Makes dealing with the "ULong64 type returned in statistics calls from the iControl API" easier.
    """
    def __init__(self,ulong):
        self.ulong=ulong
        self.value=0
        high=ulong.high
        low=ulong.low
        rollOver = 0x7fffffff
        rollOver += 1
        tmpVal=0
        if(high >=0):
            tmpVal = high << 32 & 0xffff0000 
        else:
            tmpVal = ((high & 0x7fffffff) << 32) + (0x80000000 << 32)     
        if(low >=0):
            tmpVal = tmpVal + low 
        else:
            tmpVal = tmpVal + (low & 0x7fffffff) + rollOver

        self.value=tmpVal
        
    def __str__(self):
        size = ""
        value=self.value
        if(value / 1024 >= 1.0):
            size = "K"
            value = value / 1024 
        if(value / 1024 >= 1.0): 
            size = "M"
            value = value / 1024 
        if(value / 1024 >= 1.0): 
            size = "G"
            value = value / 1024 
        return "%.2f%s"%(value,size)
    def __call__(self):
        return self.__str__()

class Options(object):
    pass

if __name__ == '__main__':
    
    if len(sys.argv) < 4:
        print "Usage: %s <hostname> <username> <password>"% sys.argv[0]
        sys.exit()

    host,username,password = sys.argv[1:]
    o = Options()
    o.wsdl_dir = gettempdir()
    o.bigip_url = 'https://%s' % host
    o.username = username
    o.password = password
    o.setup_demo = False
    o.setup_wsdl_patterns = False
    o.setup_force = True
    get_wsdls(o)

