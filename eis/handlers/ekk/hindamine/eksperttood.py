import random
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class EksperttoodController(BaseResourceController):
    """Eksperthindamise vaates tööde loetelu vaatamine
    """
    _permission = 'eksperthindamine'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'ekk/hindamine/ekspert.tood.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/ekspert.tood_list.mako'
    _DEFAULT_SORT = 'sooritus.tahised' # vaikimisi sortimine

    def _query(self):
        self._calc_ekspertprotsent()
        self._get_h_kasutajad()

    def _search_default(self, q):
        # vaikimisi otsitakse pooleli eksperthindamisega töid
        self.c.probleem = 'pooleli'
        if self.c.user.id in [k[0] for k in self.c.opt_h_kasutajad]:
            # kui ise olen eksperthindaja, siis otsitakse vaikimisi minu eksperthindamisi
            self.c.h_kasutaja_id = self.c.user.id
        return self._search(q)

    def _search(self, q1):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        # nendel juhtudel loetletakse hindamisolekud eksperthindamistega
        self.c.list_holek = self._is_list_holek(self.c.probleem)

        if self.c.list_holek:
            # otsitakse eksperthindamisi
            q = model.SessionR.query(model.Sooritus, model.Hindamisolek, model.Hindamine)
            q = self._search_probleem(q, self.c.probleem)
        else:
            # otsitakse sooritusi
            q = model.SessionR.query(model.Sooritus, model.Vaie.staatus)
            q = self._search_probleem(q, self.c.probleem)

        if self.c.csv:
            return self._index_csv(q)

        q_cnt = model.SessionR.query(sa.func.count(model.Sooritus.id))
        if self.on_vaideaeg:
            self.c.cnt_vaided = self._search_probleem(q_cnt, 'vaided').scalar()
            self.c.cnt_lahendamata = self._search_probleem(q_cnt, 'lahendamata').scalar()
        else:
            self.c.cnt_erinevus = self._search_probleem(q_cnt, 'erinevus').scalar()
            self.c.cnt_pooleli = self._search_probleem(q_cnt, 'pooleli').scalar()
            self.c.cnt_ekspert = self._search_probleem(q_cnt, 'ekspert').scalar()

        return q

    def _is_list_holek(self, probleem):
        """Kas loetleda hindamisolekud või sooritused"""
        return probleem in ('pooleli','ekspert','erinevus')        

    def _search_probleem(self, q, probleem):
        """Probleemi järgi päringu koostamine"""

        q = (q.filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .join(model.Sooritus.sooritaja)
             .outerjoin(model.Sooritaja.vaie))

        if self.on_vaideaeg:
            # vaide korral hindamisel vaadeldakse töid, mis on tehtud või millel on vaie
            # saab vaidlustada ka sellise testi tulemust, millelt sooritaja on kõrvaldatud
            q = q.filter(sa.or_(model.Sooritus.staatus==const.S_STAATUS_TEHTUD,
                                model.Vaie.id!=None))
        else:
            # IV hindamine toimub ainult tehtud töödele
            q = q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)

        if self.c.tahised:
            q = q.filter(model.Sooritus.tahised.ilike(self.c.tahised))

        if self.c.kool_koht_id:
            q = q.filter(model.Sooritaja.kool_koht_id==self.c.kool_koht_id)

        if self._is_list_holek(probleem):
            # leitakse eksperthindamisega hindamisolekud või seda vajavad hindamisolekud

            q = q.join(model.Sooritus.hindamisolekud)

            f = []
            f.append(model.Hindamine.hindamisolek_id==model.Hindamisolek.id)
            f.append(model.Hindamine.liik==const.HINDAJA4)
            if self.c.h_kasutaja_id:
                f.append(model.Hindamine.hindaja_kasutaja_id==self.c.h_kasutaja_id)
            f = sa.and_(*f)
            
            if probleem == 'erinevus':
                # leia hindamisolekud, millel on III hindamine tehtud ja hindamisprobleem, 
                # aga eksperthindamist veel ei ole
                q = q.outerjoin((model.Hindamine, f))
                q = q.filter(model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_HINDAMISERINEVUS).\
                    filter(model.Hindamisolek.hindamistase==const.HINDAJA3)
            else:
                # eksperthindamise kirje peab olemas olema
                if probleem == 'pooleli':
                    f = sa.and_(f, model.Hindamine.staatus==const.H_STAATUS_POOLELI)
                q = q.join((model.Hindamine, f))
        else:
            # otsitakse soorituste kaupa

            if probleem == 'vaided':
                # otsitakse neid, millel on vaie olemas
                q = q.filter(model.Vaie.staatus>const.V_STAATUS_ESITATUD)

            elif probleem == 'lahendamata':
                # otsitakse, neid millel on otsustamata vaie
                q = q.filter(sa.and_(
                    model.Vaie.staatus>const.V_STAATUS_ESITATUD,
                    model.Vaie.staatus<const.V_STAATUS_OTSUSTATUD))

            if self.c.h_kasutaja_id:
                q = q.filter(model.Sooritus.hindamisolekud.any(\
                        model.Hindamisolek.hindamised.any(\
                            model.Hindamine.hindaja_kasutaja_id==self.c.h_kasutaja_id)))

        return q

    def _calc_ekspertprotsent(self):
        """Leitakse, mitmel protsendil tehtud sooritustest 
        on vähemalt üks hindamiskogum eksperdi poolt hindamisel olnud.
        """
        q = (model.Sooritus.query
             .filter_by(toimumisaeg_id=self.c.toimumisaeg.id)
             .filter_by(staatus=const.S_STAATUS_TEHTUD))
        total = q.count()
        if total == 0:
            self.c.ekspertprotsent = 0
        else:
            q = q.filter(model.Sooritus.hindamisolekud.any(
                model.Hindamisolek.hindamised.any(
                    sa.or_(model.Hindamine.liik==const.HINDAJA4,
                           model.Hindamine.liik==const.HINDAJA5))))
            expert = q.count()
            self.c.ekspertprotsent = expert * 100. / total
       
    def _get_h_kasutajad(self):
        q = (model.SessionR.query(model.Kasutaja.id, model.Kasutaja.nimi)
             .filter(model.Kasutaja.hindamised.any(
                 model.Hindamine.hindamisolek.has(
                     model.Hindamisolek.sooritus.has(
                         model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)))))
        q = q.order_by(model.Kasutaja.perenimi, model.Kasutaja.eesnimi)
        self.c.opt_h_kasutajad = [(r[0], r[1]) for r in q.all()]

    def create(self):
        """Kasutaja vajutas nupule "Vali juhuslikult", et hindajate kontrollimiseks
        mõnd juhuslikult valitud sooritust hindama hakata.
        """
        q = (model.Sooritus.query
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritus.pallid!=None)
             .filter(~ model.Sooritus.hindamisolekud.any(
                 model.Hindamisolek.hindamistase==const.HINDAJA4)))

        cnt = q.count()
        if cnt == 0:
            self.error(_("Pole hinnatud ja eksperthindamata töid, mille seast valida saaks"))
            return self._redirect(action='index')
        valik = int(random.random()*cnt)
        tos = q[valik]
        return HTTPFound(location=self.url('hindamine_ekspert_kogum', toimumisaeg_id=self.c.toimumisaeg.id, id=tos.id))

    def _prepare_header(self):
        header = [_("Testitöö tähis"),
                  _("Hindamise olek"),
                  _("Tulemus"),
                  ]
        return header

    def _prepare_item(self, rcd, n):
        tos = rcd[0]
        item = [tos.tahised,
                tos.hindamine_staatus_nimi,
                self.h.fstr(tos.pallid),
                ]
        return item

    def __before__(self):
        c = self.c
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.test = c.toimumisaeg.testiosa.test
        self.on_vaideaeg = c.toimumisaeg.tulemus_kinnitatud and c.test.testiliik_kood != const.TESTILIIK_RV
            
    def _perm_params(self):
        return {'obj': self.c.test}

