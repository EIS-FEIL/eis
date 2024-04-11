from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.sooritajateaadressid import SooritajateaadressidDoc
log = logging.getLogger(__name__)

class AadressidController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Testikoht
    _INDEX_TEMPLATE = '/ekk/korraldamine/aadressid.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/aadressid_list.mako'
    _DEFAULT_SORT = 'piirkond.nimi,sooritaja.perenimi,sooritaja.eesnimi'
    _ignore_default_params = ['pdf','csv']
    _no_paginate = True
    _UNIQUE_SORT = 'sooritaja.id'
    
    def _query(self):
        self.Oppurikoht = sa.orm.aliased(model.Koht)
        self.Lopetatudkoht = sa.orm.aliased(model.Koht)
        self.Soorituskoht = sa.orm.aliased(model.Koht, name='skoht')
        q = model.SessionR.query(model.Piirkond.nimi,
                                model.Kasutaja.isikukood,
                                model.Kasutaja.synnikpv,
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Aadress.tais_aadress,
                                model.Koht.normimata,
                                model.Koht.nimi,
                                model.Sooritaja.reg_markus,
                                self.Soorituskoht.nimi,
                                model.Sooritus.tahised)
        q = (q.join(model.Kasutaja.sooritajad)
             .filter(model.Sooritaja.testimiskord_id==self.c.toimumisaeg.testimiskord_id)
             .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
             .outerjoin((model.Koht,
                         sa.or_(model.Koht.id==model.Sooritaja.kool_koht_id,
                                sa.and_(model.Sooritaja.kool_koht_id==None,
                                        model.Koht.id==model.Kasutaja.kool_koht_id))))
             .outerjoin(model.Kasutaja.aadress)
             .outerjoin(model.Sooritaja.piirkond)
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .outerjoin(model.Sooritus.testikoht)
             .outerjoin((self.Soorituskoht, self.Soorituskoht.id==model.Testikoht.koht_id))
             )
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
        if self.c.lang:
            if isinstance(self.c.lang, (list, tuple)):
                q = q.filter(model.Sooritaja.lang.in_(self.c.lang))
            else:
                q = q.filter(model.Sooritaja.lang==self.c.lang)
        if self.c.kooliga and not self.c.koolita:
            q = q.filter(model.Sooritaja.kool_koht_id!=None)
        if self.c.koolita and not self.c.kooliga:
            q = q.filter(model.Sooritaja.kool_koht_id==None)

        if self.c.opibmujal:
            # õppimiskoht ja soorituskoht erinevad
            q = q.filter(model.Testikoht.koht_id!=model.Sooritaja.kool_koht_id)
            # leidub soorituskoht, mis asub tema õppimiskohas (et välistada need,
            # kes on meelega mujale suunatud, sest oma koolis testi ei toimu)
            KoolTestikoht = sa.orm.aliased(model.Testikoht)
            q = q.filter(sa.exists().where(sa.and_(
                KoolTestikoht.toimumisaeg_id==self.c.toimumisaeg.id,
                KoolTestikoht.koht_id==model.Sooritaja.kool_koht_id)
                ))
        if self.c.csv:
            return self._index_csv(q)
        self.c.prepare_header = self._prepare_header
        self.c.prepare_item = self._prepare_item
        return q

    def _order(self, q, sort=None):
        """Otsingu sorteerimine.
        """
        sort = sort or self.request.params.get('sort') or self._DEFAULT_SORT
        # kui on PDFi väljastamine, siis peab
        # alati olema sortimine piirkonna järgi
        if self.request.params.get('pdf'):
            if not sort.startswith('piirkond.nimi'):
                sort = 'piirkond.nimi,'+sort
        return BaseResourceController._order(self, q, sort)

    def _showlist(self):
        """Otsingu tulemuste kuvamine.
        """
        if self.request.params.get('pdf'):
            data, filename = self._render_pdf()
            mimetype = const.CONTENT_TYPE_PDF
            return utils.download(data, filename, mimetype)            

        if self.request.params.get('partial'):
            return self.render_to_response(self._LIST_TEMPLATE)
        else:
            return self.render_to_response(self._INDEX_TEMPLATE)

    def _prepare_header(self):
        "Loetelu päis"
        return (('piirkond.nimi', _("Soovitav piirkond")),
                ('kasutaja.isikukood', _("Isikukood")),
                ('sooritaja.eesnimi', _("Eesnimi")),
                ('sooritaja.perenimi', _("Perekonnanimi")),
                ('aadress.tais_aadress', _("Aadress")),
                ('koht.nimi', _("Õppeasutus")),
                ('sooritaja.reg_markus', _("Märkused")),
                ('skoht.nimi', _("Soorituskoht")),
                ('sooritus.tahised', _("Töö kood")),
                )

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        p_nimi, k_ik, k_synnikpv, eesnimi, perenimi, tais_aadress, normimata, koht_nimi, markus, sk_nimi, tahised = rcd
        return [p_nimi,
                k_ik or self.h.str_from_date(k_synnikpv),
                eesnimi,
                perenimi,
                '%s %s' % (tais_aadress or '', normimata or ''),
                koht_nimi,
                markus,
                sk_nimi,
                tahised]

    def _render_pdf(self):
        doc = SooritajateaadressidDoc(self.c.toimumisaeg, self.c.items)
        data = doc.generate()
        filename = 'sooritajate_aadressid_%s.pdf' % self.c.toimumisaeg.testimiskord.tahised
        return data, filename
    
    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
