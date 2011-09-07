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
import re
import suds
from xml.sax import SAXParseException

# Project info

class F5Error(Exception):
    def __init__(self, e):
        self.exception=e
        self.msg=str(e)
        
        if isinstance(e,suds.WebFault):
            try:
                parts=e.fault.faultstring.split('\n')
                e_source=parts[0].replace("Exception caught in ","")
                e_type=parts[1].replace("Exception: ","")
                e_msg=re.sub("\serror_string\s*:\s*","",parts[4])
                self.msg="%s: %s"%(e_type,e_msg)
            except IndexError:
                self.msg=e.fault.faultstring
        if isinstance(e,SAXParseException):
            self.msg="Unexpected server response. %s"%e.message
    def __str__(self):
        return self.msg
 
