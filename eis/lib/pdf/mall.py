# -*- coding: utf-8 -*- 
# $Id: mall.py 9 2015-06-30 06:34:46Z ahti $
"XMList PDFi genereerimine - katsetus"

from lxml import etree
from .pdfdoc import *

styles = getStyleSheet()
N = styles['Normal']
S = styles['Small']
H1 = styles['Heading1']
H2 = styles['Heading2']
H3 = styles['Heading3']                        

TB = TableStyle([('BOX',(0,0),(-1,-1), 1,colors.black),                         
                 ])

TS = TableStyle([('FONTSIZE',(0,0),(-1,-1), 8),
                 ('GRID',(0,0),(-1,-1), 0.5,colors.black),                         
                 ])        


def generate():
    fn = '/cygdrive/c/svn/eis/trunk/eis/lib/pdf/mall.xml'
    f = open(fn, 'r')
    sisu = f.read()
    f.close()
    sisu = '<root>%s</root>' % sisu
    tree = etree.XML(sisu)
    return _parse_element(tree)

def _parse_element(tree):
    story = []
    for elem in tree.iterchildren():
        if elem.tag == 'p':
            story.append(Paragraph(_inner_xml(elem) or '', S))
        elif elem.tag == 'table':
            tabledata = []
            for tr in elem.iterchildren('tr'):
                row = []
                for td in tr.iterchildren('td'):
                    cell = _parse_element(td)
                    row.append(cell)
                tabledata.append(row)
            story.append(Table(tabledata))
        else:
            assert Exception('Ootamatu element %s' % elem.tag)
    if not len(story):
        story.append(Paragraph(tree.text or '', S))
    return story

def _inner_xml(element):
    buf = etree.tostring(element, encoding=str, xml_declaration=False, method='xml')
    # eemaldame wrapper-elemendi
    buf = buf[buf.find('>')+1:buf.rfind('<')]
    #return buf.decode('utf-8').strip()
    return buf.strip()
