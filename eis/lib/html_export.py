import sys
import os
import zipfile
import tempfile
import shutil
import re

import eis.lib.helpers as h
from eis.lib.base import *
from eis.lib.block import BlockController
from eis.lib.blockview import BlockView

import weasyprint

log = logging.getLogger(__name__)

def export_test_zip(komplekt, lang, parent_ctrl):
    return HtmlExport(komplekt, lang, parent_ctrl).export()

def export_test_html(komplekt, lang, parent_ctrl):
    return HtmlExport(komplekt, lang, parent_ctrl).create_test()

def export_zip(ylesanne, lang, parent_ctrl):
    # koostame failid ja pakime zipiks
    return HtmlExport(ylesanne, lang, parent_ctrl).export()

def export_html(ylesanne, lang, parent_ctrl):
    return HtmlExport(ylesanne, lang, parent_ctrl).create_assessment()

def export_test_pdf(komplekt, lang, parent_ctrl):
    return HtmlExport(komplekt, lang, parent_ctrl).create_test_pdf()
    
class HtmlExport(object):
    """Ülesande eksportimine
    """
    tempdir = None
    
    def __init__(self, item, lang, parent_ctrl):
        self.parent_ctrl = parent_ctrl
        if parent_ctrl:
            parent_ctrl.c.url_no_sp = True
        self.ylesanne = None
        self.komplekt = None
        if isinstance(item, model.Komplekt):
            self.komplekt = item
            fn = 'test.zip'
            test = self.komplekt.komplektivalik.testiosa.test
            #if lang not in test.get_keeled() or lang == test.lang:
            #    lang = None
        else:
            self.ylesanne = item
            fn = 'ylesanne.zip'
            if lang not in self.ylesanne.keeled or lang == self.ylesanne.lang:
                lang = None

        self.dirname = tempfile.mkdtemp() # ajutiste failide koht
        self.fn = os.path.join(self.dirname, fn)
        self.zf = zipfile.ZipFile(self.fn, "w")
        self.files = []
        self.lang = lang
        
    def export(self):
        # loome zip-faili
        if self.komplekt:
            self.create_zip_test()
        else:
            self.create_zip_ylesanne()
        # paneme selle kinni
        self.zf.close()

        # loeme tehtud zipi sisu
        f = open(self.fn, 'r')
        data = f.read()
        f.close()

        # kustutame kõik failid
        shutil.rmtree(self.dirname)
        
        # tagastame zipi sisu
        return data

    def create_zip_ylesanne(self):
        self.fn_resource = 'ylesanne-%s.html' % (self.ylesanne.id)            
        self.files.append(self.fn_resource)
        self.add_file(self.fn_resource, self.create_assessment())

    def create_zip_test(self):
        self.fn_resource = 'komplekt-%s.html' % (self.komplekt.id)
        self.files.append(self.fn_resource)
        self.add_file(self.fn_resource, self.create_test())

    def create_test_pdf(self):
        html_data = self.create_test()
        self.zf.close()
        
        doc = weasyprint.HTML(string=html_data, base_url=self.dirname)

        # stiil:
        # - kiri Arial 10pt
        # - lehekyljenumbrid 
        # - checkbox/radio nähtavaks
        style = """
        @page {
          @bottom-center {
            content: counter(page) "/" counter(pages);
            font-family: Arial;
            font-size: 8pt;
          }
        }
        input[type="checkbox"] {
          border: 1px solid black;
          width: 10px;
          height: 10px;
        }
        input[type="radio"] {
          border: 1px solid black;
          border-radius: 5px;
          width: 10px;
          height: 10px;
        }
        input[type="checkbox"]:checked, input[type="radio"]:checked {
          background-color: #222;
        }
        """
        stylesheets = [weasyprint.CSS(string=style)]
        filedata = doc.write_pdf(stylesheets=stylesheets)
        # kustutame kõik failid
        shutil.rmtree(self.dirname)
        return filedata
        
    def add_file(self, fn, data, is_raw=False):
        fn_full = os.path.join(self.dirname, fn)
        #log.debug('WRITE %s' % fn_full)
        _write_file(fn_full, data)
        self.zf.write(fn_full, fn, zipfile.ZIP_DEFLATED)
        
    def export_obj(self, obj):
        """Kutsutakse block.py seest
        faili lisamiseks 
        """
        if obj and not obj.fileurl:
            if isinstance(obj, model.Sisuobjekt):
                ylesanne_id = obj.sisuplokk.ylesanne_id
                sisuplokk_id = obj.sisuplokk_id
                filedata = obj.tran(self.lang).filedata
                if filedata:
                    fn = obj.get_url(self.lang, True, encode=False)
                    self.add_file(fn, filedata, True)

    def export_hotspots(self, obj):
        if obj and not obj.fileurl:
            filedata = obj.tran(self.lang).filedata
            if filedata:
                valikud = obj.sisuplokk.kysimus.valikud
                filedata, mimetype = BlockView.draw_hotspots(obj, filedata, valikud)
                fn = obj.get_url(self.lang, True, with_hotspots=True, encode=False)
                self.add_file(fn, filedata, True)

        
    def create_assessment(self):
        buf = h.literal("<!DOCTYPE html><html>\n<head>\n" + \
            '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n')
        buf += h.literal(_css())
        buf += h.literal("<title>") + self.ylesanne.tran(self.lang).nimi + \
            h.literal("</title>\n")
        buf += h.literal("</head>\n<body>\n") + \
            self.assessment_view(self.ylesanne) +\
            h.literal("\n</body>\n</html>")
        return buf

    def assessment_view(self, ylesanne, seq=None):
        item_html = ''
        nimi = 'Ülesanne'
        if seq:
            nimi += ' %s' % seq
        item_html += h.literal('<b><h4>%s</h4></b>' % nimi)

        for block in ylesanne.sisuplokid:      
            # loome igale plokile oma kontrolleri
            ctrl = BlockController.get(block, ylesanne, self.parent_ctrl)
            # keel
            ctrl.lang = self.lang
            # genereerime HTMLi
            block_html = ctrl.view_print(self)
            # paneme ploki oma kohale
            item_html = BlockView.replace_placeholder(item_html, block_html)

        return item_html

    def create_test(self):
        buf = h.literal("<html>\n<head>\n" + \
            '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n')
        buf += h.literal(_css())
        buf += h.literal("<title>") + self.komplekt.komplektivalik.testiosa.test.nimi + \
            h.literal("</title>\n")
        buf += h.literal("</head>\n<body>\n") + \
            self.test_view() +\
            h.literal("\n</body>\n</html>")
        return buf

    def test_view(self):
        testiosa = self.komplekt.komplektivalik.testiosa
        test = testiosa.test
        buf = h.literal('<h1>' + test.nimi + '</h1>\n')
        buf += h.literal('<h1>' + (testiosa.nimi or '')+ '</h1>\n')
        if testiosa.sooritajajuhend:
            buf += h.literal('<b>%s</b>' % testiosa.sooritajajuhend)
        buf += h.literal('<h2>Komplekt %s</h2>' % self.komplekt.tahis)

        has_alatest = False
        for alatest in self.komplekt.komplektivalik.alatestid:
            has_alatest = True
            has_testiplokk = False
            buf += h.literal('<h2>' + alatest.nimi + '</h2>')
            if alatest.sooritajajuhend:
                buf += h.literal('<b>%s</b>' % alatest.sooritajajuhend)

            for testiplokk in alatest.testiplokid:
                has_testiplokk = True
                buf += h.literal('<h3>' + testiplokk.nimi + '</h3>')
                for testiylesanne in testiplokk.testiylesanded:
                    seq = '%s.%s.%s' % (alatest.seq, testiplokk.seq, testiylesanne.seq)
                    buf += self.testiylesanne_view(testiylesanne, seq)
            if not has_testiplokk:
                for testiylesanne in alatest.testiylesanded:
                    seq = '%s.%s' % (alatest.seq, testiylesanne.seq)
                    buf += self.testiylesanne_view(testiylesanne, seq)
        if not has_alatest:
            for testiylesanne in testiosa.testiylesanded:
                seq = testiylesanne.seq
                buf += self.testiylesanne_view(testiylesanne, seq)
        return buf

    def testiylesanne_view(self, testiylesanne, seq):
        buf = ''
        for vy in testiylesanne.valitudylesanded:
            if vy.komplekt == self.komplekt:
                if not vy.ylesanne:
                    buf += h.literal('<p>%s. ÜLESANNE PUUDUB</p>' % seq)
                else:
                    buf += self.assessment_view(vy.ylesanne, seq)
        return buf

##########################################################
# Abifunktsioonid

def _unique_fn(fn, n):
    p = fn.rfind('.')
    extra = '-%s' % n
    if p == -1:
        fn_new = fn + extra
    else:
        fn_new = fn[:p-1] + extra + fn[p:]
    return fn_new

def _write_file(fn, data):
    path = os.path.dirname(fn)
    if not os.path.exists(path):
        os.makedirs(path)
    f = open(fn, 'wb')
    f.write(data)
    f.close()

def _css():
    return """
<style type="text/css">
body, body td, div {    
    font-family: "Roboto",-apple-system,blinkmacsystemfont,"Segoe UI",roboto,"Helvetica Neue",arial;
    font-size: 1rem;
    line-height: 1.5;
}
.inputlines {
line-height:25px;
}

.hottext {
background-color:#FEC0C0;
text-decoration: underline; 
} 

.border-sortable {
    border: 1px #B22F16 dashed;
    padding: 5px;
}

.border-draggable {
    border: 1px #B22F16 dotted;
    padding: 5px;
}
</style>
"""

