import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import meeldetuletus

class MeeldetuletusDoc(PdfDoc):
    "Meeldetuletus riigieksamil osalemise tasu maksmiseks"

    def __init__(self, sooritaja):
        self.sooritaja = sooritaja
        self.page_template = meeldetuletus
        
    def gen_story(self):
        story = []
        self.page_template.generate(story, self.sooritaja)
        return story


