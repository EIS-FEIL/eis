import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import vaideotsus, vaideotsus_te

class VaideotsusDoc(PdfDoc):

    kasutaja = None
    pagenumbers = True

    def _get_NumberedCanvas(self):
        return VaideotsusNumberedCanvas
    
    def __init__(self, handler, vaie, allkirjastajad):
        self.handler = handler
        self.vaie = vaie
        self.allkirjastajad = allkirjastajad
        if vaie.sooritaja.test.testiliik_kood == const.TESTILIIK_TASE:
            self.page_template = vaideotsus_te
        else:
            self.page_template = vaideotsus
        self._register_arialnarrow_font()

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output,
                                 pagesize=A4,
                                 topMargin=20*mm, bottomMargin=20*mm, 
                                 rightMargin=20*mm, leftMargin=28*mm)

        
    def gen_story(self):
        story = []
        self.page_template.generate(story, self.vaie, self.allkirjastajad)
        return story

class VaideotsusNumberedCanvas(NumberedCanvas):
    "Max lehekülgede arvu näitamiseks kasutatav kangas"

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 7)
        try:
            doctemplate = self._doctemplate
        except AttributeError:
            # ainult 1 lk
            return

        if self._pageNumber == 1:
            # esimesel lehekyljel ei kuva numbrit
            return

        x = 36 * mm
        y = 8 * mm

        grey = colors.HexColor('#b5b2aa')
        self.setFillColor(grey) # font color        
        buf = '%d (%d)' % (self._pageNumber, page_count)
        self.drawRightString(x, y, buf)

