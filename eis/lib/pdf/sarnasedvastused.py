import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import sarnasedvastused

class SarnasedvastusedDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, toimumisaeg, items, max_index, alatest_index):
        self.toimumisaeg = toimumisaeg
        self.items = items
        self.max_index = max_index
        self.alatest_index = alatest_index

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output,
                                 pagesize=landscape(A4),
                                 topMargin=10*mm, bottomMargin=10*mm, 
                                 rightMargin=10*mm, leftMargin=10*mm)
    def gen_story(self):
        story = []
        sarnasedvastused.generate(story, self.toimumisaeg, self.items, self.max_index, self.alatest_index)
        return story

