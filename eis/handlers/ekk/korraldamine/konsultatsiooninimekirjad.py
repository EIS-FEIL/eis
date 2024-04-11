# -*- coding: utf-8 -*- 
# $Id: konsultatsiooninimekirjad.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
from eis.lib.pdf import pages_loader
from eis.lib.pdf.konsnimekiri import KonsnimekiriDoc

log = logging.getLogger(__name__)

class KonsultatsiooninimekirjadController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Piirkond
    _INDEX_TEMPLATE = '/ekk/korraldamine/konsultatsiooninimekirjad.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/konsultatsiooninimekirjad_list.mako'
    _EDIT_TEMPLATE = '/ekk/korraldamine/konsultatsiooninimekiri.mako'
    _DEFAULT_SORT = 'piirkond.nimi'
    _ignore_default_params = ['materjal']

    def _query(self):
        self.c.pdf_templates = pages_loader.get_templates_opt_dict()
        # ainele kehtiv vaikimisi valik
        self.c.pdf_default = model.Ainepdf.get_default_dict(self.c.toimumisaeg.testiosa.test.aine_kood)

        q = (model.Session.query(sa.func.count(model.Sooritaja.id), model.Sooritaja.piirkond_id)
             .filter(model.Sooritaja.soovib_konsultatsiooni==True)
             .filter(model.Sooritaja.staatus > const.S_STAATUS_REGAMATA)
             .join((model.Testikonsultatsioon,
                    sa.and_(model.Testikonsultatsioon.eksam_testimiskord_id==model.Sooritaja.testimiskord_id,
                            model.Testikonsultatsioon.kons_testimiskord_id==self.c.toimumisaeg.testimiskord_id)))
             )
        # leiame kasutajale lubatud piirkondade loetelu
        piirkonnad_id = self.c.user.get_kasutaja().get_piirkonnad_id('korraldamine', const.BT_SHOW)
        # kas pole õigust kõigi piirkondade korraldamiseks?
        if None not in piirkonnad_id:
            # piirkondlik korraldaja ei või kõiki kohti vaadata, 
            # talle kuvatakse ainult nende piirkondade koolid, mis talle on lubatud
            q = q.filter(model.Koht.piirkond_id.in_(piirkonnad_id))

        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        if self.c.piirkond_id:
            f = []
            self.c.piirkond = prk = model.Piirkond.get(self.c.piirkond_id)
            for prk_id in prk.get_alamad_id():
                f.append(model.Sooritaja.piirkond_id==prk_id)
            q = q.filter(sa.or_(*f))

        q = q.group_by(model.Sooritaja.piirkond_id)

        data = {}
        total = {}
        self.c.cnt_total = 0
        for cnt, piirkond_id in q.all():
            data[piirkond_id] = cnt
            self.c.cnt_total += cnt

            # liidame ylematele piirkondadele
            if piirkond_id:
                prk = model.Piirkond.get(piirkond_id)
                for ylem_id in prk.get_ylemad_id():
                    if ylem_id not in total:
                        total[ylem_id] = 0
                    total[ylem_id] += cnt
            else:
                # piirkonnata sooritajad
                total[None] = cnt

        self.c.sooritajad_piirkonniti = data
        self.c.sooritajad_ylempiirkonniti = total

    def _show(self, item):
        "Ühe piirkonna sooritajate nimekirja kuvamine"
        q = (model.Session.query(model.Sooritaja.eesnimi, 
                                 model.Sooritaja.perenimi, 
                                 model.Kasutaja.isikukood,
                                 model.Test.nimi)
             .filter(model.Sooritaja.soovib_konsultatsiooni==True)
             .filter(model.Sooritaja.staatus > const.S_STAATUS_REGAMATA)
             .filter(model.Sooritaja.piirkond_id==item.id)
             .join((model.Testikonsultatsioon,
                    sa.and_(model.Testikonsultatsioon.eksam_testimiskord_id==model.Sooritaja.testimiskord_id,
                            model.Testikonsultatsioon.kons_testimiskord_id==self.c.toimumisaeg.testimiskord_id)))
             .join(model.Sooritaja.kasutaja)
             .join(model.Sooritaja.test)
             )
        self.c.items = q.all()

    def _get_sub(self):
        if self.c.nosub:
            return
        if self.request.params.get('materjal'):
            return 'materjal'

    def _index_materjal(self):
        self._validate_pdf()
        doc = KonsnimekiriDoc(self.c.toimumisaeg, 
                              self.form.data)
        return self._gen_pdf(doc, 'kons_materjalid.pdf')

    def _validate_pdf(self):
        self.form = Form(self.request, schema=forms.ekk.korraldamine.ValjastusPDFForm)
        self.form.validate()
        self._copy_search_params(self.form.data)

    def _gen_pdf(self, doc, fn):
        """Väljatrükid
        """
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            
            self.c.nosub = True
            self.form = False
            return self.index()
        else:
            return utils.download(data, fn, 'application/pdf')

    def _perm_params(self):
        return {'obj':self.c.toimumisaeg.testiosa.test}
    
    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
