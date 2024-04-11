from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class OtsikohadController(BaseResourceController):
    """Soorituskoha otsimine dialoogiaknas, 
    et yhe või mitme koha kõik sooritajad sinna ümber suunata
    """
    _permission = 'korraldamine'
    _MODEL = model.Testiruum
    _INDEX_TEMPLATE = 'ekk/korraldamine/otsikohad.mako'
    _DEFAULT_SORT = 'koht.nimi' # vaikimisi sortimine
    _no_paginate = True

    def _query(self):
        q = (model.SessionR.query(model.Testiruum, model.Koht, model.Ruum)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.koht)
             .outerjoin(model.Testiruum.ruum)
             .outerjoin(model.Koht.aadress)
             .filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id))
        return q
             
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c

        test = c.toimumisaeg.testiosa.test
        testiliik = test.testiliik_kood
        kasutaja = c.user.get_kasutaja()
        piirkonnad_id = kasutaja.get_piirkonnad_id('korraldamine', const.BT_SHOW, testiliik=testiliik)
        if None not in piirkonnad_id:
            c.piirkond_filtered = piirkonnad_id
            # piirkondlik korraldaja ei või kõiki kohti vaadata, 
            # talle kuvatakse ainult nende piirkondade koolid, mis talle on lubatud
            q = q.filter(model.Koht.piirkond_id.in_(piirkonnad_id))
        else:
            c.piirkond_filtered = None
            
        if c.vabukohti:
            q = q.filter(model.Testiruum.kohti>=model.Testiruum.sooritajate_arv+int(c.vabukohti))
        if c.piirkond_id:
            piirkonnad_id = model.Piirkond.get(c.piirkond_id).get_alamad_id()
            q = q.filter(model.Koht.piirkond_id.in_(piirkonnad_id))
        if c.maakond_kood:
            tase, kood = c.maakond_kood.split('.')
            q = q.filter(model.Aadress.kood1==kood)

        if not c.tr_id:
            return
        elif isinstance(c.tr_id, list):
            q = q.filter(~model.Testiruum.id.in_(c.tr_id))
            c.suunatavad_tr_id = c.tr_id
        else:
            q = q.filter(model.Testiruum.id!=c.tr_id)
            c.suunatavad_tr_id = [c.tr_id]

        q_arv = model.SessionR.query(sa.func.sum(model.Testiruum.sooritajate_arv)).\
            filter(model.Testiruum.id.in_(c.suunatavad_tr_id))
        c.suunatavate_arv = q_arv.scalar()
        return q

    def _search_default(self, q):
        # seatakse c.suunatavad_tr_id
        self._search(q) 
        #self.c.vabukohti = self.c.suunatavate_arv 
        # otsingut ennast ei toimu
        return None 

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
