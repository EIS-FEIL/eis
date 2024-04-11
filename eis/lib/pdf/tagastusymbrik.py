"Tagastusümbrike PDF dokument"

from reportlab.platypus import *
import sqlalchemy as sa
import math
import eis.model as model       
from eis.model.usersession import _
from .pdfdoc import PdfDoc, SimpleDocTemplate, C4, mm, PdfGenException

class TagastusymbrikDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, toimumisaeg, params, order_by):
        self.toimumisaeg = toimumisaeg
        self.order_by = ','.join(order_by)
        self.piirkond_id = params.get('piirkond_id')
        self.testikoht_id = params.get('testikoht_id')
        self.params = params
        self._register_barcode_font()

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output, pagesize=C4, topMargin=10*mm, bottomMargin=10*mm)

    def gen_story(self):
        tagastusymbrik_t = self._load_template('tagastusymbrik') or []
        tyhjadeymbrik_t = self._load_template('tyhjadeymbrik')
        protokollideymbrik_t = self._load_template('protokollideymbrik')

        # tagastusymbrike liigid
        tliigid_id = [liik_t['liik_id'] for liik_t in tagastusymbrik_t]

        if not self.is_loaded:
            self.error = _('Ümbrikuliik on valimata')
        elif not self.toimumisaeg.on_paketid:
            self.error = _("E-testis ei kasutata ümbrikke")
        if self.error:
            return

        story = []
        q = model.Session.query(model.Testikoht, model.Testipakett).\
            filter(model.Testikoht.toimumisaeg_id==self.toimumisaeg.id).\
            join(model.Testikoht.testipaketid).\
            join(model.Testikoht.koht).\
            outerjoin(model.Koht.piirkond).\
            outerjoin(model.Testipakett.testiruum)

        if self.testikoht_id:
            # soovitakse ainult antud testikoha väljatrükki
            q = q.filter(model.Testikoht.id==int(self.testikoht_id))
        elif self.piirkond_id:
            q = q.filter(model.Koht.piirkond_id==self.piirkond_id)

        q = q.order_by(sa.text(self.order_by + ',testiruum.tahis'))

        for rcd in q.all():
            testikoht, testipakett = rcd

            if self.params.get('protokollideymbrik'):
                protokollideymbrik_t.generate(story, self.toimumisaeg, testikoht, testipakett)

            if len(tliigid_id):
                q1 = model.Session.query(model.Tagastusymbrik, 
                                         model.Testiprotokoll, 
                                         model.Tagastusymbrikuliik)
                q1 = q1.filter(model.Testiprotokoll.testipakett_id==testipakett.id).\
                    filter(model.Tagastusymbrik.tagastusymbrikuliik_id.in_(tliigid_id)).\
                    join(model.Tagastusymbrik.testiprotokoll).\
                    join(model.Tagastusymbrik.tagastusymbrikuliik).\
                    order_by(model.Testiprotokoll.tahis,
                             model.Tagastusymbrikuliik.tahis,
                             model.Testiprotokoll.kursus_kood)
                for rcd1 in q1.all():
                    ymbrik, tpr, ymbrikuliik = rcd1
                    # otsime selle ymbrikuliigi malli
                    liik_id = ymbrikuliik.id
                    liik_t = [l for l in tagastusymbrik_t if l['liik_id'] == liik_id][0]
                    template = liik_t['template']
                    sisukohta = model.Tagastusymbrikuliik.SISUKOHTA_TPR

                    # vaatame, kas on protokolliga seotud ümbrik või paketiga seotud
                    try:
                        paketiymbrik = template.paketiymbrik
                        sisukohta = model.Tagastusymbrikuliik.SISUKOHTA_PAKETT
                    except AttributeError:
                        paketiymbrik = False

                    try:
                        ruumiymbrik = template.ruumiymbrik
                        sisukohta = model.Tagastusymbrikuliik.SISUKOHTA_TPR2
                    except AttributeError:
                        ruumiymbrik = False

                    if ymbrikuliik.sisukohta != sisukohta:
                        raise PdfGenException('Ümbrikuliigi {s} sisu ei vasta valitud mallile'.format(s=ymbrikuliik.tahis))
                        
                    if paketiymbrik:
                        # valitud mall on seotud paketiga, mitte protokollirühmaga,
                        # mistõttu tuleb genereerida korraga kogu paketile,
                        # mitte kirjega seotud protokollirühmale
                        toodearv = testipakett.toodearv
                        maht = ymbrikuliik.maht or 20
                        ymbrikearv = ymbrik.ymbrikearv
                        for n_y in range(ymbrikearv):
                            y_toodearv = min(maht, toodearv - n_y * maht)
                            template.generate(story, self.toimumisaeg, testikoht, testipakett, ymbrikuliik, y_toodearv, n_y + 1, ymbrikearv)

                    elif ruumiymbrik:
                        # valitud mall on mõeldud sama ruumi kuni kahe protokollirühma jaoks
                        tpr2 = ymbrik.testiprotokoll2
                        for n_y in range(ymbrik.ymbrikearv):
                            template.generate(story, self.toimumisaeg, testikoht, testipakett, tpr, ymbrikuliik, tpr2)
                    else:
                        # see mall on seotud protokollirühmaga ja vastab andmebaasis olevale ümbriku kirjele
                        # ymbrikearv kordi trykime sama ymbrikku
                        for y_cnt in range(ymbrik.ymbrikearv):
                            template.generate(story, self.toimumisaeg, testikoht, testipakett, tpr, ymbrikuliik)
                            
            if tyhjadeymbrik_t:
                aine = self.toimumisaeg.testiosa.test.aine_kood
                kursused = [model.Klrida.get_str('KURSUS', k, ylem_kood=aine) \
                            for k in testipakett.get_kursused()] or [None]

                # igast väljastusymbrikuliigist trykime yhe ymbriku tyhjade tööde tagastamiseks
                for ymbrikuliik in self.toimumisaeg.valjastusymbrikuliigid:
                    for liik_t in tyhjadeymbrik_t:
                        if ymbrikuliik.id == liik_t['liik_id']:
                            for kursus_nimi in kursused:
                                # tyhjade tagastamise ymbrik on yhine kõigile kursustele
                                liik_t['template'].generate(story, self.toimumisaeg, testikoht, testipakett, ymbrikuliik, '')
                                break

        return story
