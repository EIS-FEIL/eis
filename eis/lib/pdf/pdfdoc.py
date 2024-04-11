import logging
import io
import sys
import os
import re
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import *
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.doctemplate import LayoutError
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import *
from reportlab.lib.fonts import addMapping 
from reportlab.lib import colors
import _thread
thread_lock = _thread.allocate_lock()

from . import pages_loader

log = logging.getLogger(__name__)

# triipkoodi fondi failinimi
FN_BARCODE_FONT = '/srv/eis/ttf/barcode_font.ttf'
FN_ARIALNARROW_FONT = '/srv/eis/ttf/arial-narrow.ttf'
FN_ARIALNARROWBOLD_FONT = '/srv/eis/ttf/arial-narrow-bold.ttf'

# kirillitsat sisaldavad fondid (reportlabi vaikimisi font ei sisalda kirillitsat)
FN_TIMES_FONT = '/srv/eis/ttf/times.ttf'
FN_TIMESBD_FONT = '/srv/eis/ttf/timesbd.ttf'
FN_TIMESI_FONT = '/srv/eis/ttf/timesi.ttf'

# ymbrikute suurus
#C4 = (229*mm, 324*mm)
C4 = (324*mm, 229*mm) # C4 landscape

class PdfDoc(object):
    settings = None
    error = None # veateade
    is_loaded = False # kas mingi mall on kasutusel
    page_template = None # PDF malli moodul kataloogist pages
    pages_loader = pages_loader
    pagenumbers = False
    is_cyrillic = True
    
    def generate(self, **kw):
        "PDFi genereerimine ja selle sisu väljastamine"
        if self.is_cyrillic:
            self._register_times_font()

        output = io.BytesIO()
        try:
            self.generate_into_threadsafe(output, **kw)
            data = output.getvalue()
        except LayoutError as ex:
            self.error = 'Andmed ei mahu PDF leheküljele '
            log.error('%s (%s) %s' % (self.error, self.__class__.__name__, str(ex)))
            return
        finally:
            output.close()
        if not self.error and not data:
            self.error = 'Dokument on tühi '
        return data

    def generate_into_threadsafe(self, output, **kw):
        """ReportLab ei ole lõimekindel, mistõttu tekivad vead.
        Vigadest hoidumiseks toimub iga dokumendi genereerimine atomaarselt.
        """
        thread_lock.acquire()
        try:
            self.generate_into(output, None, **kw)
        finally:
            thread_lock.release()
               
    def generate_from_story(self, story):
        "PDFi genereerimine ja selle sisu väljastamine, kui sisujutt on juba olemas"
        output = io.BytesIO()
        try:
            self.generate_into(output, story)
            data = output.getvalue()
        except LayoutError:
            self.error = 'Lehe mõõdud on dokumendimalli jaoks liiga väiksed'
            return
        finally:
            output.close()
        if not self.error and not data:
            self.error = 'Dokument on tühi'
        return data

    def generate_into(self, output, story, **kw):
        "PDFi genereerimine etteantud voogu"
        doc = self._doctemplate(output)
        # mõnikord võib dokumendi sisu juba eelnevalt valmis olla
        if story is None:
            # aga yldjuhul genereeritakse dokumendi sisu siin
            story = self.gen_story(**kw)
        if story:
            if self.pagenumbers:
                # lehekyljenumbritega dokument
                doc.multiBuild(story,
                               onFirstPage=self._first_page,
                               onLaterPages=self._later_pages,
                               canvasmaker=self._get_NumberedCanvas())
            else:
                # lehekyljenumbriteta dokument
                doc.multiBuild(story,
                               onFirstPage=self._first_page,
                               onLaterPages=self._later_pages)
            doc.creator = 'EIS'
            doc.author = 'Haridus- ja Noorteamet'

    def _get_NumberedCanvas(self):
        return NumberedCanvas
    
    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output)

    def gen_story(self):
        "PDFi sisu jaoks andmete pärimine ja PDFi sisu genereerimine - üle kirjutada"
        story = []
        return story

    def _first_page(self, canvas, doc):
        if self.page_template:
            try:
                f = self.page_template.first_page
            except AttributeError:
                return
            else:
                f(canvas, doc, self)

    def _later_pages(self, canvas, doc):
        if self.page_template:
            try:
                f = self.page_template.later_pages
            except AttributeError:
                return
            else:
                f(canvas, doc, self)

    def _register_barcode_font(self):
        pdfmetrics.registerFont(TTFont('Barcode', FN_BARCODE_FONT))

    def _register_arialnarrow_font(self):
        pdfmetrics.registerFont(TTFont('Arial-Narrow', FN_ARIALNARROW_FONT))
        pdfmetrics.registerFont(TTFont('Arial-Narrow-Bold', FN_ARIALNARROWBOLD_FONT))
        addMapping('Arial-Narrow', 1, 0, 'Arial-Narrow-Bold')
        
    def _register_times_font(self):
        # kirjutame vaikimisi fondifaili yle selleks, 
        # et saada läti tähti, mida vaikimisi font ei paku
        pdfmetrics.registerFont(TTFont('Times-Roman', FN_TIMES_FONT))
        pdfmetrics.registerFont(TTFont('Times-Bold', FN_TIMESBD_FONT))
        pdfmetrics.registerFont(TTFont('Times-Italic', FN_TIMESI_FONT))
        addMapping('Times-Roman', 0, 0, 'Times-Roman') #normal
        addMapping('Times-Roman', 0, 1, 'Times-Italic') #italic
        addMapping('Times-Roman', 1, 0, 'Times-Bold') #bold
        #addMapping('Times-Roman', 1, 1, 'Times-BoldItalic') #italic and bold 

    def _load_template(self, t_type):
        """Imporditakse lehekylje malli moodul, kui soovitakse selle trykkimist.
        Parameeter on malli tyybi nimi.
        Postitatud parameetrite seas (self.params) eeldatakse olevat parameetrit,
        mille nimi on malli tyybi nimi koos sufiksiga _t. Selle väärtusest loetakse malli nimi.
        Malli failinimi on kujul TYYP_NIMI.py, kus TYYP on t_type.
        """
        param = self.params.get(t_type)
        if param:
            n_liik = self.params.get('n_liik') # testiliik
            if n_liik:
                t_type_n_liik = '%s_%s' % (t_type, n_liik)
            else:
                t_type_n_liik = t_type

            if isinstance(param, list):
                # antud on ymbrikuliik, iga liigi kohta on eraldi valitud mall
                ret = []
                for liik_t in param:
                    if liik_t.get('ttype'):
                        # vajatakse
                        t_name = liik_t.get('tname')
                        template = self._load_single_template(t_type_n_liik, t_name)
                        if template:
                            liik_t['template'] = template
                            ret.append(liik_t)
                        else:
                            return
                return ret
            else:
                t_name = self.params.get('%s_t' % t_type)
                template = self._load_single_template(t_type_n_liik, t_name)
                return template

    def _load_single_template(self, t_type, t_name):
        if not t_name:
            self.error = 'Mall %s on valimata' % t_type
            return
        m = self.pages_loader.get_template(t_type, t_name)
        if not m:
            self.error = 'Mall %s_%s puudub või pole kasutatav' % (t_type, t_name)
            return
        self.is_loaded = True
        return m

class NumberedCanvas(canvas.Canvas):
    "Max lehekülgede arvu näitamiseks kasutatav kangas"

    x_border = None
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        #self._gen_time = datetime.now().strftime('%d.%m.%Y %H.%M')
        
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 7)
        try:
            doctemplate = self._doctemplate
        except AttributeError:
            # ainult 1 lk
            return

        width = doctemplate.width / mm
        height = doctemplate.height / mm
        #x_time = None
        if width > 273 and height > 208:
            # C4 printeri äär on suurem
            # tagastusymbrik C4, 273.2x209
            # (väljastusymbrik C4, 273.2x178 ?)
            x = 25 * mm
            y = 20 * mm
        elif width < 101:
            # kleeps, 100x47
            x = 10 * mm
            y = 5 * mm
        else:
            # A4, 189x277
            x = 20 * mm
            y = 5 * mm
            #x_time = width * mm

        grey = colors.HexColor('#b5b2aa')
        self.setFillColor(grey) # font color        

        if self.x_border:
            x = self.x_border

        buf = '%d (%d)' % (self._pageNumber, page_count)
        self.drawRightString(x, y, buf)

class PdfGenException(Exception):
    pass
        
if __name__ == '__main__':
    from eis.lib.pdf.pages.pdfutils import *
    from eis.lib.pdf.pages.stylesheet import *
    story = []
    story.append(Paragraph('Hello', N))
    data = PdfDoc().generate_from_story(story)
    print(len(data))
