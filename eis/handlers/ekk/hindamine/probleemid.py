from eis.lib.baseresource import *
_ = i18n._
from eis.lib.resultentry import ResultEntry

log = logging.getLogger(__name__)

class ProbleemidController(BaseResourceController):

    _permission = 'hindamisanalyys'
    _MODEL = model.Hindamisolek
    _INDEX_TEMPLATE = 'ekk/hindamine/analyys.probleemid.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/analyys.probleemid_list.mako'
    _DEFAULT_SORT = 'koht.nimi,hindamiskogum.tahis sooritaja.valimis,sooritus.tahised' # vaikimisi sortimine 

    def _query(self):
        fields = [model.Sooritus,
                  model.Hindamisolek,
                  model.Koht,
                  model.Sooritaja,
                  ]
        q = (model.Session.query(*fields)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .join(model.Sooritus.hindamisolekud)
             .join(model.Hindamisolek.hindamiskogum)
             .join(model.Sooritus.testikoht)
             .join(model.Testikoht.koht)
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .join(model.Sooritus.sooritaja)
             )
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.hindamiskogum_id:
            q = q.filter(model.Hindamisolek.hindamiskogum_id==int(c.hindamiskogum_id))
        if c.probleem:
            q = q.filter(model.Hindamisolek.hindamisprobleem==int(c.probleem))
        else:
            q = q.filter(model.Hindamisolek.hindamisprobleem != 0)
        if c.hindamistase:
            q = q.filter(model.Hindamisolek.hindamistase==int(c.hindamistase))
        if c.valim == '0':
            q = q.filter(model.Sooritaja.valimis==False)
        elif c.valim == '1':
            q = q.filter(model.Sooritaja.valimis==True)

        if c.xls:
            fields = [model.Sooritus,
                      model.Hindamisolek,
                      model.Koht,
                      model.Sooritaja,
                      model.Hindamine.liik,
                      model.Hindamine.staatus,
                      model.Hindamine.sisestatud,
                      model.Kasutaja.nimi,
                      model.Kasutaja.epost,
                      ]
            q = (q.with_entities(*fields)
                 .outerjoin((model.Hindamine,
                             sa.and_(model.Hindamine.hindamisolek_id==model.Hindamisolek.id,
                                     model.Hindamine.tyhistatud==False,
                                     model.Hindamine.staatus!=const.H_STAATUS_HINNATUD)
                             ))
                 .outerjoin(model.Hindamine.hindaja_kasutaja)
                 )
            return self._index_xls(q)

        c.prepare_header = self._prepare_header
        c.prepare_item = self._prepare_item
        return q

    def create(self):
        params = self.request.params
        testiosa = self.c.toimumisaeg.testiosa
        test = testiosa.test
        resultentry = ResultEntry(self, None, test, testiosa)
        for key in params:
            if key.startswith('probleem_'):
                holek_id = key[9:]
                holek = model.Hindamisolek.get(holek_id)
                probleem = int(params[key])
                if probleem != holek.hindamisprobleem:
                    holek.hindamisprobleem = probleem
                    sooritus = holek.sooritus
                    h_staatus, pallid, min_probleemne_tase = resultentry.get_h_staatus(sooritus)
                    sooritus.hindamine_staatus = h_staatus
                            
        model.Session.commit()
        self.success()
        return self._redirect('index')

    def _prepare_header(self):
        if self.c.xls:
            header = [('koht.nimi', _("Soorituskoht")),
                      ('sooritus.tahised', _("Testisooritus")),
                      ('hindamiskogum.tahis sooritaja.valimis', _("Hindamiskogum")),
                      ('hindamisolek.hindamisprobleem hindamisolek.selgitus', _("Probleem")),
                      (None, _("Hindamise olek")),
                      (None, _("Hindamise liik")),
                      (None, _("Hindaja")),
                      (None, _("Hindaja e-post")),
                      ('koht.epost', _("Soorituskoha e-post")),
                      ]
        else:
            header = [('koht.nimi', _("Soorituskoht")),
                      ('sooritus.tahised', _("Testisooritus")),
                      ('hindamiskogum.tahis sooritaja.valimis', _("Hindamiskogum")),
                      ('hindamisolek.hindamisprobleem hindamisolek.selgitus', _("Probleem")),
                      ]
        return header
    
    def _prepare_item(self, rcd, n):
        tos, holek, koht, sooritaja = rcd[:4]
            
        hk = holek.hindamiskogum
        hk_tahis = hk.tahis or '-'
        koht_nimi = koht.nimi
        k_epost = koht.epost
        valimis = sooritaja.valimis
        if valimis:
            hk_tahis = '%s (%s)' % (hk_tahis, _("valim"))

        if self.c.xls:
            liik, hstaatus, sisestatud, h_nimi, h_epost = rcd[4:]

            if hstaatus is None:
                hstaatus_nimi = _("Hindaja määramata")
            elif hstaatus == const.H_STAATUS_POOLELI and sisestatud:
                hstaatus_nimi = _("Kinnitamata")
            else:
                hstaatus_nimi = self.c.opt.H_STAATUS.get(hstaatus)

            if hstaatus is None and holek.hindamisprobleem == const.H_PROBLEEM_SISESTAMATA:
                # hindajat pole määratud - leiame võimalikud hindajad
                li = self._get_maaramata_hindajad(tos, holek, hk, sooritaja, koht.piirkond_id)
                if li:
                    sep = self.c.xls and '; ' or '<br/>'
                    h_nimi = sep.join([k.nimi for k in li[:3]])
                    h_epost = sep.join([k.epost or '' for k in li[:3] if k.epost])
                    if len(li) > 3:
                        h_nimi += sep + ' ...'
                        h_epost += sep + ' ...'
            
            item = [koht_nimi,
                    tos.tahised,
                    hk_tahis,
                    holek.hindamisprobleem_nimi,
                    hstaatus_nimi,
                    liik,
                    h_nimi,
                    h_epost,
                    k_epost,
                    ]
            ix_prob = 3
            return item
        else:
            item = [koht_nimi,
                    tos.tahised,
                    hk_tahis,
                    holek.hindamisprobleem_nimi,
                    ]
            url_sis = self._url_sisestama(tos, hk)
            ix_prob = 3
            return item, url_sis, ix_prob

    def _url_sisestama(self, tos, hk):
        "Sisestamise URL p-testi korral"
        c = self.c
        h = self.h
        url_sis = None
        if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
            # p-testi korral teeme lingi sisestamisele
            if hk.on_hindamisprotokoll == False:
                # vastuste sisestamine
                url_sis = h.url('sisestamine_vastused', sooritus_id=tos.id,
                                sisestuskogum_id=hk.sisestuskogum_id, sisestus='p')
            else:
                # hindamisprotokolli sisestamine
                testikoht = tos.testikoht
                sisestuskogum = hk.sisestuskogum
                sk_tahis = sisestuskogum and sisestuskogum.tahis or ''
                tpr = tos.testiprotokoll
                hpr_tahis = '%s-%s-%s' % (testikoht.tahis, tpr.tahis, sk_tahis)
                if c.testiosa.vastvorm_kood == const.VASTVORM_KP:
                    url_sis = h.url('sisestamine_kirjalikud',
                                    sessioon_id=c.testimiskord.testsessioon_id, 
                                    toimumisaeg_id=c.toimumisaeg.id, tahis=hpr_tahis)
                elif c.testiosa.vastvorm_kood == const.VASTVORM_SP:
                    url_sis = h.url('sisestamine_suulised',
                                    sessioon_id=c.testimiskord.testsessioon_id, 
                                    toimumisaeg_id=c.toimumisaeg.id, tahis=hpr_tahis)
        return url_sis

    def _get_maaramata_hindajad(self, tos, holek, hk, sooritaja, piirkond_id):
        """Leitakse võimalikud hindajad, kes saaksid hinnata tööd, millele hindajat pole määratud"""
        hk_id = hk.id
        liik = holek.hindamistase
        if holek.hindamistase == const.HINDAJA2 and \
               holek.hindamisprobleem == const.H_PROBLEEM_SISESTAMATA:
            # puudu võib olla kas hindaja 1 või 2
            q = (model.Session.query(model.Hindamine.liik)
                 .filter(model.Hindamine.hindamisolek_id==holek.id)
                 .filter(model.Hindamine.tyhistatud==False))
            olemas = [r for r, in q.all()]
            if const.HINDAJA1 not in olemas:
                liik = const.HINDAJA1

        valimis = sooritaja.valimis
        lang = sooritaja.lang
        klass = sooritaja.klass
        paralleel = sooritaja.paralleel or ''
        holek_id = holek.id
        testikoht_id = tos.testikoht_id
        
        if self.c.toimumisaeg.muu_koha_hindamine(valimis, liik):
            # muu koha hindamise korral ei leia hindajaid,
            # selleks oleks vaja eelnevalt arvutada iga kooli kohta
            # kooli sooritajate arv ja kooli hindajate tööde koguarv,
            # et mitte kuvada hindajaid, kelle kooli tööde arv on täis
            return []

        if valimis:
            kkh = hk.kahekordne_hindamine_valim
        else:
            kkh = hk.kahekordne_hindamine
        
        if kkh and hk.paarishindamine and holek.hindamistase == const.HINDAJA2:
            # kas paariline on hinnanud?
            q = (model.Session.query(model.Labiviija)
                 .join(model.Labiviija.hindamised)
                 .filter(model.Hindamine.hindamisolek_id==holek.id)
                 .filter(model.Hindamine.tyhistatud==False)
                 .filter(model.Hindamine.liik.in_((const.HINDAJA1, const.HINDAJA2)))
                 )
            lv = q.first()
            if lv:
                # leiame määratud hindaja paarilise
                for p in lv.paarishindajad:
                    if p.id != lv.id:
                        return [p.kasutaja]

        # hindajate päring
        q = (model.Session.query(model.Kasutaja)
             .join(model.Kasutaja.labiviijad)
             .filter(model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id)
             .filter(model.Labiviija.liik==liik)
             .filter(model.Labiviija.hindamiskogum_id==hk_id)
             .filter(model.Labiviija.lang==lang)
             .filter(model.Labiviija.valimis==valimis)
             .filter(sa.or_(model.Labiviija.planeeritud_toode_arv==None,
                            model.Labiviija.toode_arv==None,
                            model.Labiviija.toode_arv<model.Labiviija.planeeritud_toode_arv))
             )

        # EKK hindajad või oma kooli hindajad
        q = (q.filter(sa.or_(model.Labiviija.testikoht_id==None,
                             model.Labiviija.testikoht_id==testikoht_id))
             .filter(sa.or_(~ model.Labiviija.labiviijaklassid.any(),
                            model.Labiviija.labiviijaklassid.any(
                                sa.and_(
                                    sa.func.coalesce(model.Labiviijaklass.klass,'')==klass,
                                    sa.func.coalesce(model.Labiviijaklass.paralleel,'')==paralleel)
                                )
                            ))
             )
        
        if self.c.toimumisaeg.oma_prk_hindamine:
            # hindaja peab olema samast piirkonnast
            q = q.filter(sa.exists().where(
                sa.and_(model.Kasutajapiirkond.kasutaja_id==model.Labiviija.kasutaja_id,
                        model.Kasutajapiirkond.piirkond_id==piirkond_id))
                         )
                
        # jätame välja hindajad, kes on töö tagasi lykanud või on muud liiki hindajana hinnanud
        q = q.filter(~ sa.exists().where(
            sa.and_(model.Hindamine.hindamisolek_id==holek_id,
                    model.Hindamine.hindaja_kasutaja_id==model.Labiviija.kasutaja_id)
            ))
        return list(q.limit(4).all())

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.testimiskord = self.c.toimumisaeg.testimiskord
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
        
    def _perm_params(self):
        return {'obj': self.c.test}
        
