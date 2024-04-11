"Helper functions"

from lxml import etree
from lxml.builder import ElementMaker
from datetime import datetime, date
import os
import re
import stat
import binascii
import shutil
from datetime import datetime

import logging
log = logging.getLogger(__name__)

class NS(object):
    "Namespace constants"
    XSD = "http://www.w3.org/2001/XMLSchema"
    XSI = "http://www.w3.org/2001/XMLSchema-instance"
    _XSI = '{%s}' % XSI
    SOAPENC = 'http://schemas.xmlsoap.org/soap/encoding/'
    _SOAPENC = '{%s}' % SOAPENC
    SOAP11 = 'http://schemas.xmlsoap.org/soap/envelope/'
    _SOAP11 = '{%s}' % SOAP11
    SOAP12 = 'http://www.w3.org/2003/05/soap-env'
    SOAPENV = 'http://schemas.xmlsoap.org/soap/envelope/'
    _SOAPENV = '{' + SOAPENV + '}'
    
    XROAD3 = 'http://x-road.ee/xsd/x-road.xsd'
    _XROAD3 = '{%s}' % XROAD3
    XROAD4 = 'http://x-road.eu/xsd/xroad.xsd'
    _XROAD4 = '{%s}' % XROAD4
    XROAD4ID = 'http://x-road.eu/xsd/identifiers'

class SoapFault(RuntimeError):
    def __init__(self, faultcode, faultstring, detail=None):
        self.faultcode = faultcode
        self.faultstring = faultstring
        self.detail = detail       

# XML element maker which ignores child elements with None value
class NilElementMaker(ElementMaker):
    def __call__(self, tag, *children, **attrib):
        non_null_children = [c for c in children if c is not None]
        return ElementMaker.__call__(self, tag, *non_null_children, **attrib)

# XML creation helper functions:
# define typemap in order to use non-strings as parameters for E
# which will be transformed to strings
def add_date(elem, item):
    elem.text = item.strftime('%Y-%m-%d')
def add_datetime(elem, item):
    elem.text = item.strftime('%Y-%m-%dT%H:%M:%S')
def add_str(elem, item):
    elem.text = str(item)
def add_bool(elem, item):
    elem.text = item and 'true' or 'false'

# XML element maker instance
E = NilElementMaker(typemap={date: add_date,
                             datetime: add_datetime,
                             int: add_str,
                             float: add_str,
                             bool: add_bool})

# Functions for reading parameter values from input message 
# request - parsed XML object
def get_text(request, key, maxlen=None):
    "Get text value of a XML element"
    node = request.find(key)
    if node is not None:
        value = node.text
        if value:
           value = value.strip()
        if value and maxlen:
            value = value[:maxlen]
        return value

def get_int(request, key):
    "Get integer value of a XML element"
    value = get_text(request, key)
    try:
        return int(value)
    except:
        pass

def get_float(request, key):
    "Get float value of a XML element"
    value = get_text(request, key)
    try:
        return float(value)
    except:
        pass

def get_boolean(request, key):
    "Get boolean value of a XML element"
    value = get_text(request, key)
    if value in ('true', '1'):
        return True
    elif value in ('false', '0'):
        return False

def get_date(request, key):
    "Get date value of a XML element"
    value = get_text(request, key)
    return date_from_iso(value)

def get_datetime(request, key):
    "Get datetime value of a XML element"
    value = get_text(request, key)
    return datetime_from_iso(value)

def date_from_iso(value):
    if value:
        return date(*map(int, re.split('[^\d]', value)[:3]))    

def datetime_from_iso(value):
    if value:
        # "2008-09-03T20:56:35.450686Z"
        return datetime(*map(int, re.split('[^\d]', value)[:-1]))

def outer_xml(element, xml_declaration=False):
    "Convert XML object into string"
    buf = etree.tostring(element, xml_declaration=xml_declaration, method='xml', pretty_print=True, encoding='UTF-8')
    return buf.strip().decode('utf-8')

class Xresult(object):
    "Response object"
    def __init__(self, **attrs):
        self.addattrs(**attrs)

    def addattrs(self, **attrs):
        for key in attrs:
            setattr(self, key, attrs[key])
            
    def __getattr__(self, name):
        # avoid exceptions when attribute does not exist
        if name in self.__dict__:
            return self.__dict__[name]
        return None

    def __getitem__(self, name):
        # make it subscriptable
        return getattr(self, name)

    def asdict(self):
        def scalarvalue(value):
            if isinstance(value, Xresult):
                return value.asdict()
            elif isinstance(value, list):
                return [scalarvalue(r) for r in value]
            else:
                return value
        d = {}
        for key, value in list(self.__dict__.items()):
            d[key] = scalarvalue(value)
        return d
    
    def __repr__(self):
        return repr(self.asdict())

    def find(self, keys):
        """Traverse tree of children, format of keys is:
        attr1/subattr2/subsubattr3/.../subattrN
        """
        item = self
        for key in keys.split('/'):
            if not item:
                return None
            item = getattr(item, key)
        return item
    
def tree_to_xresult(root, path='', list_path=[]):
    """Convert XML object into dict 
    - path - path of current element
    - list_path - list of pathes to elements which should be converted as list
      (because element may occur more than once)
    """
    res = Xresult()
    for node in root.getchildren():
        try:
            tag = node.tag.split('}')[-1]
        except:
            # maybe Comment
            pass
        else:
            subpath = path + '/' + tag
            subresult = tree_to_xresult(node, subpath, list_path)
            if list_path and subpath in list_path:
                # is list
                if getattr(res, tag) is None:
                    setattr(res, tag, [])
                getattr(res, tag).append(subresult)
            else:
                if getattr(res, tag) is not None:
                    log.error('Element occurs multiple times but not defined as a list: ' + subpath)
                setattr(res, tag, subresult)
    if not res.__dict__:
        # simpletype
        res = root.text
        if res:
            res = res.strip()
    return res

def make_log_day_path(log_dir, user=None):
    "Create directory for logging the messages"
    if log_dir:
        dt = datetime.now()
        sday = dt.strftime('%y%m%d')
        stime = dt.strftime('%y%m%d.%H%M%S.%f')
        path = '%s/%s' % (log_dir, sday)
        if not os.path.exists(path):
            os.makedirs(path)
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IXOTH | stat.S_IROTH)
            if user:
                try:
                    shutil.chown(path, user)
                except:
                    pass
        prefix = '%s/%s' % (path, stime)
        return prefix
