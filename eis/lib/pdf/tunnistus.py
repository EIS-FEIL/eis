# -*- coding: utf-8 -*- 
# $Id: tunnistus.py 345 2016-02-10 12:20:20Z ahti $

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *

class TunnistusDoc(PdfDoc):

    kasutaja = None # tunnistuse omanik
    tunnistusenr = None # tunnistus.tunnistusenr
    nimi = None # omaniku nimi
    oppeaasta = None # tunnistus.oppeaasta

    def __init__(self, testiliik, sessioon, t_name):
        self.sessioon = sessioon
        t_type = 'tunnistus_%s' % testiliik
        self.page_template = pages_loader.get_template(t_type, t_name)
        
    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        try:
            # kui mallil on oma DocTemplate
            doc = self.page_template.get_doctemplate(output)
        except AttributeError:
            # vaikimisi DocTemplate
            doc = SimpleDocTemplate(output, 
                                    leftMargin=14*mm,
                                    rightMargin=14*mm,
                                    topMargin=0*mm,
                                    bottomMargin=1*mm)
        doc.title = 'Tunnistus'
        return doc
    
    def set_data(self, tunnistusenr, nimi, valjastamisaeg, oppeaasta, kasutaja, q_sooritajad, sooritaja):
        self.tunnistusenr = tunnistusenr
        self.nimi = nimi
        self.valjastamisaeg = valjastamisaeg # page_template.first_page loeb seda
        self.oppeaasta = oppeaasta # page_template.first_page loeb seda
        self.kasutaja = kasutaja
        self.q_sooritajad = q_sooritajad
        self.sooritaja = sooritaja

    def gen_story(self):
        story = []
        self.page_template.generate(story, 
                                    self.tunnistusenr, 
                                    self.valjastamisaeg,
                                    self.nimi,
                                    self.kasutaja, 
                                    self.sessioon, 
                                    self.q_sooritajad,
                                    self.sooritaja)
        return story


