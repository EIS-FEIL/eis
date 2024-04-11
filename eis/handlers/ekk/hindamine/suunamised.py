from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class SuunamisedController(BaseResourceController):
    _permission = 'hindajamaaramine'
    _MODEL = model.Hindamine
    _INDEX_TEMPLATE = 'ekk/hindamine/maaramine.suunamised.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/maaramine.suunamised_list.mako'
    _DEFAULT_SORT = 'hindamine_1.id' # vaikimisi sortimine
    _UNIQUE_SORT = 'hindamine_1.id'
    
    def _query(self):
        testiosa = self.c.toimumisaeg.testiosa
        self.c.hindamiskogumid_opt = [(r.id, r.tahis) \
                                      for r in testiosa.hindamiskogumid \
                                      if r.staatus]
        self.c.hindajad_opt = self._get_hindajad_opt()

        self.Hindamine_vana = sa.orm.aliased(model.Hindamine) # hindamine_1
        self.Hindamine_uus = sa.orm.aliased(model.Hindamine) # hindamine_2        
        q = (model.SessionR.query(model.Sooritus,
                                 model.Hindamisolek,
                                 self.Hindamine_vana,
                                 self.Hindamine_uus,
                                 model.Hindamiskogum.tahis,
                                 model.Sooritaja.lang,
                                 model.Kasutaja.nimi)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritus.hindamisolekud)
             .filter(model.Hindamisolek.puudus==False)
             .join(model.Hindamisolek.hindamiskogum)
             .join((self.Hindamine_vana, 
                    sa.and_(self.Hindamine_vana.sisestus==1,
                            self.Hindamine_vana.hindamisolek_id==model.Hindamisolek.id)))
             .outerjoin(self.Hindamine_vana.hindaja_kasutaja)
             .outerjoin((self.Hindamine_uus, 
                         sa.and_(self.Hindamine_uus.sisestus==1,
                                 self.Hindamine_uus.id==self.Hindamine_vana.uus_hindamine_id)))
             )

        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.hindamiskogum_id:
            hindamiskogum_id = int(self.c.hindamiskogum_id)
            q = q.filter(model.Hindamisolek.hindamiskogum_id==hindamiskogum_id)

        if self.c.hindaja_id:
            hindaja_id = int(self.c.hindaja_id)
            q = q.filter(self.Hindamine_vana.hindaja_kasutaja_id==hindaja_id)

        if self.c.lykatud or self.c.uusmaaramata:
            q = q.filter(self.Hindamine_vana.staatus==const.H_STAATUS_LYKATUD)
            if self.c.uusmaaramata:
                q = q.filter(self.Hindamine_vana.uus_hindamine_id==None)

        if self.c.probleem:
            q = q.filter(model.Hindamisolek.hindamisprobleem==int(self.c.probleem))

        if self.c.csv:
            return self._index_csv(q)
        return q

    def _get_hindajad_opt(self):
        qh = model.SessionR.query(model.Kasutaja.id, model.Kasutaja.nimi).\
            filter(model.Kasutaja.labiviijad.any(\
                sa.and_(model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id,
                        model.Labiviija.liik!=None))).\
            order_by(model.Kasutaja.nimi)
        return [(k[0],k[1]) for k in qh.all()] 

    def _index_otsihindaja(self):
        """Dialoogiakna avamine uue hindaja lisamise alustamiseks: valitakse
        olemasolevate hindajate seast
        """
        q = (model.SessionR.query(model.Labiviija.id, model.Kasutaja.nimi, model.Hindamiskogum.tahis)
             .filter(model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id)
             .join(model.Labiviija.kasutaja)
             .join(model.Labiviija.hindamiskogum)
             )
        self.c.liik = self.request.params.get('liik')
        if self.c.liik:
            q = q.filter(model.Labiviija.liik==int(self.c.liik))

        eesnimi = self.request.params.get('eesnimi')
        perenimi = self.request.params.get('perenimi')
        if eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(eesnimi))
        if perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(perenimi))
        q = q.order_by(model.Kasutaja.nimi)
        self.c.items = q.all()
        # jätame meelde soorituste loetelu sortimistingimused,
        # et peale suunamist samamoodi sortida
        self.c.list_url = self.request.params.get('list_url')

        return self.render_to_response('/ekk/hindamine/maaramine.suunahindaja.mako')

    def _create_otsihindaja(self):
        """Labiviija on valitud, salvestame uue hindaja.
        Vana hindamise kirje jääb alles ja saab tyhistatud.
        Uuele hindajale tehakse uus hindamise kirje.
        """
        hindamised_id = self.request.params.get('hindamised_id').split(',')

        for key in self.request.params:
            prefix = 'lv_'
            if key.startswith(prefix):
                lv_id = int(key[len(prefix):])
                lv = model.Labiviija.get(lv_id)
                assert lv.toimumisaeg_id == self.c.toimumisaeg.id, _("Vale toimumisaeg")
                break        
            
        for hindamine_id in hindamised_id:
            if not hindamine_id:
                continue

            hindamine1 = model.Hindamine.get(hindamine_id)
            holek = hindamine1.hindamisolek
            tos = holek.sooritus

            hindamine_uus = hindamine1.uus_hindamine
            if hindamine_uus:
                self.error(_("Sooritus {s} on juba edasi suunatud").format(s=tos.tahised))
                return self._after_update(None)
            
            for hindamine2 in holek.hindamised:
                if hindamine2.hindaja_kasutaja_id == lv.kasutaja_id and not hindamine2.tyhistatud:
                    self.error(_("{s1} juba on soorituse {s2} hindaja").format(
                        s1=lv.kasutaja.nimi, s2=tos.tahised))
                    return self._after_update(None)

            if hindamine1.labiviija == lv:
                if hindamine1.tyhistatud:
                    # suunamine tyhistatud, suuname tyhistajale tagasi
                    hindamine_uus = hindamine1
                    hindamine1 = holek.get_hindamine(hindamine1.liik)
                else:
                    self.error(_("Sooritust {s1} ei saa suunata hindajale {s2}, kuna ta juba on selle soorituse hindaja").format(
                        s1=tos.tahised, s2=lv.kasutaja.nimi))
                    return self._after_update(None)
        
            assert tos.toimumisaeg_id == self.c.toimumisaeg.id, _("Vale toimumisaeg")

            if holek.hindamiskogum_id != lv.hindamiskogum_id:
                self.error(_("Hindamiskogum {s1} ei klapi hindaja hindamiskogumiga ({s2})").format(
                    s1=holek.hindamiskogum.tahis, s2=lv.hindamiskogum.tahis))
                return self._after_update(None)                

            if tos.sooritaja.lang != lv.lang:
                self.error(_("Soorituse {s1} keel ({s2}) ei klapi hindaja keelega ({s3})").format(
                    s1=tos.tahised, s2=tos.sooritaja.lang, s3=lv.lang))
                return self._after_update(None)
            
            if hindamine1 and hindamine1.staatus == const.H_STAATUS_HINNATUD:
                # kui on juba hinnatud, siis saab edasi suunata juhul, kui on
                # hindamiserinevus
                if holek.hindamisprobleem == const.H_PROBLEEM_HINDAMISERINEVUS \
                        and holek.hindamistase == const.HINDAJA2 and hindamine1.liik < const.HINDAJA3:
                    # kontrollime, et sama protokollirühma ei hinda keegi teine
                    q = model.SessionR.query(model.Hindamine.labiviija_id).distinct().\
                        filter(model.Hindamine.liik==const.HINDAJA3).\
                        filter(model.Hindamine.tyhistatud==False).\
                        join(model.Hindamine.hindamisolek).\
                        filter(model.Hindamisolek.hindamiskogum_id==holek.hindamiskogum_id).\
                        join(model.Hindamisolek.sooritus).\
                        filter(model.Sooritus.testiprotokoll_id==tos.testiprotokoll_id)
                    for lv2_id, in q.all():
                        if lv2_id != lv.id:
                            lv2 = model.Labiviija.get(lv2_id)
                            self.error(_("Sooritust {s1} ei saa suunata hindajale {s2}, kuna protokollirühma {s3} hindab {s4}").format(
                                s1=tos.tahised, s2=lv.kasutaja.nimi, s3=tos.testiprotokoll.tahised, s4=lv2.kasutaja.nimi))
                            continue
                    # loome kolmanda hindamise kirje
                    hindamine3 = holek.give_hindamine(const.HINDAJA3)
                    hindamine3.labiviija = lv
                    hindamine3.hindaja_kasutaja_id = lv.kasutaja_id
                else:
                    self.error(_("Sooritus {s} on juba hinnatud").format(s=tos.tahised))
            else:
                # kui hindamine ei ole veel hinnatud, siis see tühistatakse
                if hindamine1:
                    hindamine1.staatus = const.H_STAATUS_SUUNATUD
                    hindamine1.tyhistatud = True
                    model.Session.flush()
                if not hindamine_uus:
                    hindamine_uus = holek.give_hindamine(hindamine1.liik, labiviija_id=lv.id)
                    hindamine_uus.hindamisprotokoll = hindamine1.hindamisprotokoll
                    hindamine1.uus_hindamine = hindamine_uus
                if hindamine_uus.staatus == const.H_STAATUS_HINNATUD:
                    self.error(_("Soorituse {s} hindamine on juba kinnitatud").format(s=tos.tahised))
                    return self._after_update(None)
                
                hindamine_uus.hindaja_kasutaja_id = lv.kasutaja_id
                hindamine_uus.labiviija = lv
                hindamine_uus.uus_hindamine = None
                
                # kui on kolmanda hindamise kahekordne sisestamine, siis tuleb teise sisestuse kirjet ka muuta
                # kuna kolmanda hindamise korral on kirje loodud konkreetse hindaja jaoks
                if hindamine1 and hindamine1.liik == const.HINDAJA3:
                    hindamine1_2 = holek.get_hindamine(hindamine1.liik, sisestus=2)
                    if hindamine1_2:
                        hindamine1_2.hindaja_kasutaja_id = lv.kasutaja_id
                        hindamine1_2.labiviija = lv
            model.Session.flush()
            
        model.Session.commit()
        return self._after_update(None)

    def _create_suunatagasi(self):
        """Suuname tööd lükanud hindajale tagasi.
        """
        hindamised_id = self.request.params.getall('hindamine1_id')

        for hindamine_id in hindamised_id:
            if not hindamine_id:
                continue
            hindamine1 = model.Hindamine.get(hindamine_id)
            hindamine1.staatus = const.H_STAATUS_HINDAMATA
            if hindamine1.tyhistatud:
                holek = hindamine1.hindamisolek
                hindamine2 = holek.get_hindamine(hindamine1.liik)
                if hindamine2:
                    if hindamine2.sisestatud:
                        #staatus == const.H_STAATUS_HINNATUD:
                        tos = holek.sooritus
                        k2 = hindamine2.hindaja_kasutaja
                        k2_nimi = k2 and k2.nimi or ''
                        self.error(_("Tööd {s} ei saa tagasi suunata, sest {s2} on selle juba hinnanud").format(s=tos.tahised, s2=k2_nimi))
                        model.Session.rollback()
                        return self._after_update(None)
                    hindamine2.tyhistatud = True
                    hindamine1.tyhistatud = False
                hindamine1.uus_hindamine = None
        model.Session.commit()
        return self._after_update(None)

    def _after_update(self, id):
        # kui sortimistingimused ja pagineerimis-lk on meeles, siis kasutame samu 
        list_url = self.request.params.get('list_url')
        if list_url:
            return HTTPFound(location=list_url)
        else:
            return self._redirect('index')

    def _prepare_header(self):
        header = [_("Test"),
                  _("Hindamiskogum"),
                  _("Keel"),
                  _("Hindaja"),
                  _("Liik"),
                  _("Olek"),
                  _("Probleem"),
                  _("Määratud uus hindaja"),
                  ]
        return header
    
    def _prepare_item(self, rcd, n):
        tos, holek, hindamine_vana, hindamine_uus, hk_tahis, j_lang, vana_k_nimi = rcd
        k_uus = hindamine_uus and hindamine_uus.hindaja_kasutaja or None

        item = [tos.tahised,
                hk_tahis,
                model.Klrida.get_lang_nimi(j_lang),
                vana_k_nimi,
                hindamine_vana.liik_nimi,
                self.c.opt.H_STAATUS.get(hindamine_vana.staatus),
                holek.selgitus or holek.hindamisprobleem_nimi,
                k_uus and k_uus.nimi or '',
                ]
        return item

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.testimiskord = self.c.toimumisaeg.testimiskord
        self.c.test = self.c.testimiskord.test
        self.c.on_suunamine = True
            
    def _perm_params(self):
        return {'obj':self.c.test}
