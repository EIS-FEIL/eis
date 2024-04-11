import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import eksamistatistika_pk, eksamistatistika_r, eksamistatistika_rvoork

class EksamistatistikaDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, test, qry):
        self.test = test
        self.qry = qry
        voorkeeled = (const.AINE_EN, const.AINE_FR, const.AINE_DE, const.AINE_RU)
        if test.testiliik_kood in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            if test.aine_kood in voorkeeled:
                # riigieksamid, võõrkeeled
                self.page_template = eksamistatistika_rvoork
                self.pagesize = A4
            else:
                # riigieksamid, mitte-võõrkeeled
                self.page_template = eksamistatistika_r
                self.pagesize = A4
        else:
            # test.testiliik_kood == const.TESTILIIK_POHIKOOL 
            # test.testiliik_kood == const.TESTILIIK_TASEMETOO
            # põhikooli lõpueksamid, tasemetööd
            self.page_template = eksamistatistika_pk
            self.pagesize = landscape(A4)
        
    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        # vähendame ääri
        return SimpleDocTemplate(output,
                                 pagesize=self.pagesize,
                                 topMargin=24*mm, bottomMargin=21*mm, 
                                 rightMargin=16*mm, leftMargin=16*mm)

    def _get_NumberedCanvas(self):
        class NumberedCanvas25(NumberedCanvas):
            x_border = 26 * mm
        return NumberedCanvas25
        
    def gen_story(self):
        story = []
        self.page_template.generate(story, self.test, self.qry)
        return story


