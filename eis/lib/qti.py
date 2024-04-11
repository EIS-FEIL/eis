# -*- coding: utf-8 -*- 
import re
from lxml import etree, objectify

# Nimeruumid
XML = "http://www.w3.org/XML/1998/namespace"
XSI = "http://www.w3.org/2001/XMLSchema-instance"

# EISi oma nimeruum QTI-väliste asjade jaoks
EISNS = "http://eis.ekk.edu.ee/xsd/meta.xsd"

# QTI nimeruumid
IMSCP = "http://www.imsglobal.org/xsd/imscp_v1p1"
IMSMD = "http://www.imsglobal.org/xsd/imsmd_v1p2"
IMSQTI = "http://www.imsglobal.org/xsd/imsqti_v2p1"    
IMSQTI_2_0 = "http://www.imsglobal.org/xsd/imsqti_v2p0"    
MATH = "http://www.w3.org/1998/Math/MathML"

def outer_xml(element):
    """Nagu tostring, aga ilma nimeruumideta
    """
    #buf = etree.tostring(element, encoding='utf-8', xml_declaration=False, method='xml')
    buf = etree.tostring(element, encoding=str, xml_declaration=False, method='xml')
    # eemaldame nimeruumide kirjeldused
    buf = re.compile(' xmlns[:a-zA-Z0-9]*="[^"]*"').sub('', buf)
    # eemaldame nimeruumide prefiksid
    buf = re.compile('(</?)[a-zA-Z0-9]+:').sub(r'\1', buf)
    #log.info('OUTER_XML=%s' % buf)
    #return buf.decode('utf-8').strip()
    return buf.strip()

def inner_xml_without_ns(element):
    """Nagu tostring, aga ilma nimeruumideta
    """
    # eemaldame nimeruumid
    for elem in element.getiterator():
        if not hasattr(elem.tag, 'find'):
            continue  
        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i+1:]
    objectify.deannotate(element, cleanup_namespaces=True)
    buf = etree.tostring(element, encoding=str, xml_declaration=False, method='xml')

    # eemaldame wrapper-elemendi
    buf = buf[buf.find('>')+1:buf.rfind('<')]
    return buf.strip()

def inner_xml(element):
    """Nagu tostring, aga ilma wrapper-elemendita
    """
    buf = etree.tostring(element, encoding=str, xml_declaration=False, method='xml')
    # eemaldame wrapper-elemendi
    buf = buf[buf.find('>')+1:buf.rfind('<')]
    return buf.strip()

    ## see lisab ka QTI nimeruumid, mida me ei taha
    #return element.text + ''.join([etree.tostring(e) + e.tail for e in element.findall('*')])
