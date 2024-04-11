import eis.model as model
from eis.model.usersession import _
from eis.model import const

from .pdfdoc import *
from .pages.pdfutils import *

log = logging.getLogger(__name__)

class TurvakotiaktDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, toimumisaeg, params):
        self.toimumisaeg = toimumisaeg
        self.piirkond_id = params.get('piirkond_id')
        self.testikoht_id = params.get('testikoht_id')
        self.params = params
        
    def gen_story(self):
        akt_ekk_kuller_t = self._load_template('akt_ekk_kuller')
        akt_kuller_maavalitsus_t = self._load_template('akt_kuller_maavalitsus')
        akt_maavalitsus_koolid_t = self._load_template('akt_maavalitsus_koolid')
        akt_kool_t = self._load_template('akt_kool')
        akt_maavalitsus_kuller_t = self._load_template('akt_maavalitsus_kuller')
        akt_kuller_ekk_t = self._load_template('akt_kuller_ekk')        

        if not self.is_loaded:
            self.error = _('Akti liik on valimata')
        elif not self.toimumisaeg.on_paketid:
            self.error = _("E-testis ei kasutata turvakotte")
        if self.error:
            return

        story = []

        # piirkondade päring
        q = model.SessionR.query(model.Piirkond.id, model.Piirkond.nimi)
        if self.piirkond_id:
            q = q.filter(model.Piirkond.id==self.piirkond_id)
        else:
            q = q.distinct().\
                join(model.Piirkond.kohad).\
                join(model.Koht.testikohad).\
                filter(model.Testikoht.toimumisaeg_id==self.toimumisaeg.id).\
                order_by(model.Piirkond.nimi)

        # maakonna testikohtade ja turvakottide päring
        q1 = model.SessionR.query(model.Turvakott.kotinr,
                                 model.Testipakett.lang,
                                 model.Koht.nimi,
                                 model.Ruum.tahis)
        q1 = q1.join(model.Turvakott.testipakett).\
            join(model.Testipakett.testikoht).\
            filter(model.Testikoht.toimumisaeg_id==self.toimumisaeg.id).\
            join(model.Testikoht.koht).\
            outerjoin(model.Testipakett.testiruum).\
            outerjoin(model.Testiruum.ruum)

        if self.testikoht_id:
            q1 = q1.filter(model.Testikoht.id==self.testikoht_id)

        # koolid
        q2 = model.SessionR.query(model.Testikoht).\
            filter(model.Testikoht.toimumisaeg_id==self.toimumisaeg.id).\
            join(model.Testikoht.koht)

        if self.testikoht_id:
            q2 = q2.filter(model.Testikoht.id==self.testikoht_id)
        
        # kooli turvakotid
        q3 = model.SessionR.query(model.Turvakott.kotinr).\
            join(model.Turvakott.testipakett)
            
        for rcd in q.all():
            piirkond_id, piirkond_nimi = rcd
            #log.debug('Piirkond %s: %s' % (piirkond_id, piirkond_nimi))

            # väljastus- ja tagastuskotid koos paketi keele ja kohanimega
            items_valja = q1.filter(model.Koht.piirkond_id==piirkond_id).\
                filter(model.Turvakott.suund==const.SUUND_VALJA).\
                order_by(model.Testipakett.lang, model.Koht.nimi, model.Turvakott.kotinr).\
                all()
            items_tagasi = q1.filter(model.Koht.piirkond_id==piirkond_id).\
                filter(model.Turvakott.suund==const.SUUND_TAGASI).\
                order_by(model.Testipakett.lang,model.Koht.nimi,model.Turvakott.kotinr).\
                all()
            

            # eksamikeskuselt kullerile
            # (väljastuskotid, iga piirkonna kohta 1 akt 2 eksemplaris)
            if akt_ekk_kuller_t:
                for n in range(0, int(self.params.get('akt_ekk_kuller_kogus') or 1)):
                    akt_ekk_kuller_t.generate(story, self.toimumisaeg, piirkond_nimi, items_valja)

            # kullerilt maavalitsusele
            # (väljastuskotid, iga piirkonna kohta 1 akt 2 eksemplaris)
            if akt_kuller_maavalitsus_t:
                for n in range(0, int(self.params.get('akt_kuller_maavalitsus_kogus') or 1)):
                    akt_kuller_maavalitsus_t.generate(story, self.toimumisaeg, piirkond_nimi, items_valja)

            # akt, kuhu maavalitsus kogub koolide allkirjad 
            # (väljastuskotid, iga piirkonna kohta 1)
            if akt_maavalitsus_koolid_t:
                for n in range(0, int(self.params.get('akt_maavalitsus_koolid_kogus') or 1)):
                    akt_maavalitsus_koolid_t.generate(story, self.toimumisaeg, piirkond_nimi, items_valja)

            # akt iga kooli kohta, millele kirjutavad alla välisvaatleja ja direktor
            # (väljastuskotid ja tagastuskotid)
            if akt_kool_t:
                for testikoht in q2.filter(model.Koht.piirkond_id==piirkond_id).\
                        order_by(model.Koht.nimi).all():
                    # kõik selle testikoha keeled
                    for testipakett in testikoht.testipaketid:
                        # leiame selle testikoha ja selle keele väljastuskottide numbrid
                        valjastuskotid = q3.filter(model.Testipakett.id==testipakett.id).\
                            filter(model.Turvakott.suund==const.SUUND_VALJA).\
                            order_by(model.Turvakott.kotinr).all()
                        valja_nr = [r[0] or '..........' for r in valjastuskotid]

                        # leiame selle testikoha ja selle keele tagastuskottide numbrid
                        tagastuskotid = q3.filter(model.Testipakett.id==testipakett.id).\
                            filter(model.Turvakott.suund==const.SUUND_TAGASI).\
                            order_by(model.Turvakott.kotinr).all()
                        tagasi_nr = [r[0] or '..........' for r in tagastuskotid]

                        # genereerime kooli akti
                        for n in range(0, int(self.params.get('akt_kool_kogus') or 1)):
                            akt_kool_t.generate(story, self.toimumisaeg, piirkond_nimi, testikoht, testipakett, valja_nr, tagasi_nr)


            # kullerilt eksamikeskusele
            # (tagastuskotid, iga piirkonna kohta 1 akt 2 eksemplaris)
            if akt_maavalitsus_kuller_t:
                for n in range(0, int(self.params.get('akt_maavalitsus_kuller_kogus') or 1)):
                    akt_maavalitsus_kuller_t.generate(story, self.toimumisaeg, piirkond_nimi, items_tagasi)

            # maavalitsuselt kullerile
            # (tagastuskotid, iga piirkonna kohta 1 akt 2 eksemplaris)
            if akt_kuller_ekk_t:
                for n in range(0, int(self.params.get('akt_kuller_ekk_kogus') or 1)):
                    akt_kuller_ekk_t.generate(story, self.toimumisaeg, piirkond_nimi, items_tagasi)

        return story

    def _first_page(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 8)

        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1)
        p = canvas.beginPath()
        p.moveTo(15*mm, 14*mm)
        p.lineTo(150*mm, 14*mm)
        canvas.drawPath(p, stroke=1)

        canvas.drawString(15*mm, 11*mm, 'Märkus. Juhul, kui esineb erinevusi akti ja tegelikkuse vahel või kui turvakotid on lahti võetud või muul viisil rikutud,')
        canvas.drawString(15*mm, 8*mm, 'teatada sellest viivitamatult Haridus- ja Noorteametile tel 7350566 ja koostada seletuskiri lehe pöördele.')
        canvas.restoreState()

    def _later_pages(self, canvas, doc):
        return self._first_page(canvas, doc)
