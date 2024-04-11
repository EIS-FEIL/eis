from eis.lib.baseresource import *
_ = i18n._

from eis.lib.pdf.hindamisprotokoll3 import Hindamisprotokoll3Doc        

log = logging.getLogger(__name__)

class SooritusedController(BaseResourceController):
    """I,II või III hindajale antud testitööde loetelu vaatamine ja
    III hindajale testitööde suunamine
    """

    _permission = 'hindajamaaramine'
    _MODEL = model.Hindamine
    _INDEX_TEMPLATE = 'ekk/hindamine/maaramine.sooritused.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/maaramine.sooritused_list.mako'
    _DEFAULT_SORT = 'hindamine.id' # vaikimisi sortimine
    _get_is_readonly = False

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.staatus:
            q = q.filter(model.Hindamine.staatus == self.c.staatus)
        if self.request.params.get('arvutauuesti'):
            # arvutame uuesti hindaja tööde arvu
            self.c.hindaja.calc_toode_arv()
            model.Session.commit()
        return q

    def _search_default(self, q):
        return self._search(q)

    def _query(self):
        # leiame sooritused, mis on kas hindajale hindamiseks antud ümbrikus või mida hindaja on hinnanud
        q = (model.SessionR.query(model.Sooritus, model.Hindamisolek, model.Hindamine, model.Koht.nimi)
             .join(model.Sooritus.hindamisolekud)
             .filter(model.Hindamisolek.hindamiskogum_id==self.c.hindaja.hindamiskogum_id)
             .filter(model.Hindamisolek.puudus==False)
             .join(model.Sooritus.testikoht)
             .join(model.Testikoht.koht)
             .join(model.Sooritus.sooritaja)
             )
        if self.c.hindaja.liik == const.HINDAJA3:
            q = q.join((model.Hindamine, 
                        sa.and_(model.Hindamisolek.id==model.Hindamine.hindamisolek_id,
                                model.Hindamine.labiviija_id==self.c.hindaja.id,
                                model.Hindamine.sisestus==1)))
        else:
            q = q.filter(sa.or_(
                model.Sooritus.testiprotokoll.has(\
                        model.Testiprotokoll.tagastusymbrikud.any(\
                                model.Tagastusymbrik.labiviija_id==self.c.hindaja.id)),
                model.Hindamine.id!=None))
            q = q.outerjoin((model.Hindamine, 
                             sa.and_(model.Hindamisolek.id==model.Hindamine.hindamisolek_id,
                                 sa.or_(model.Hindamine.labiviija_id==self.c.hindaja.id,
                                        model.Hindamine.kontroll_labiviija_id==self.c.hindaja.id),
                                 model.Hindamine.sisestus==1)))
            
        return q

    def create(self):
        """Antakse tööd kolmandale hindajale
        """
        assert self.c.hindaja.liik == const.HINDAJA3, _("Vale hindaja liik")
        if self.c.hindaja.planeeritud_toode_arv and self.c.hindaja.toode_arv:
            if self.c.hindaja.planeeritud_toode_arv <= self.c.hindaja.toode_arv:
                self.error(_("Labiviija planeeritud tööde arv on täis"))
                return self._redirect('index')

        sisestamisega = self.c.toimumisaeg.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP)

        # leitame soorituste hindamisolekud, 
        # mis on antud hindaja hindamiskogumi kohta
        # ja milles on hindamiserinevus ning kolmandat hindajat pole määratud
        q = (model.Hindamisolek.query
             .filter(sa.or_(
                 # kas on I ja II hindamise erinevus
                 sa.and_(model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_HINDAMISERINEVUS,
                         model.Hindamisolek.hindamistase==const.HINDAJA2),
                 # või on peetud vajalikuks III hindamist, kuid hindajat veel pole määratud
                 sa.and_(model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_SISESTAMATA,
                         model.Hindamisolek.hindamistase==const.HINDAJA3,
                         ~ model.Hindamisolek.hindamised.any(sa.and_(
                             model.Hindamine.liik==const.HINDAJA3,
                             model.Hindamine.staatus!=const.H_STAATUS_LYKATUD,
                             model.Hindamine.labiviija_id!=None))
                         )
                 ))
             .filter(model.Hindamisolek.hindamiskogum_id==self.c.hindaja.hindamiskogum_id)
             .join(model.Hindamisolek.sooritus)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.lang==self.c.hindaja.lang)
             )
        
        # kolmandat hindajat vajavate tööde arv kokku hindaja keeles
        n_vaja3 = q.count()
        #model.log_query(q)
        if not self.c.toimumisaeg.oma_kooli_hindamine:
            # oma kooli õpilaste hindamine pole lubatud
            # leiame hindaja oma koolid
            q_omakoolid = model.SessionR.query(model.Pedagoog.koht_id).\
                          filter(model.Pedagoog.kasutaja_id==self.c.hindaja.kasutaja_id)
            omakoolid = [r[0] for r in q_omakoolid.all()]
            if len(omakoolid) > 0:
                # jätame välja hindaja oma kooli tööd
                q = q.filter(sa.or_(~ model.Sooritaja.kool_koht_id.in_(omakoolid),
                                    model.Sooritaja.kool_koht_id==None))

            # kolmandat hindamist vajavate tööde arv, mis pole hindaja oma kooli õpilaste tööd
            n_vaja3_teinekool = q.count()
        else:
            n_vaja3_teinekool = n_vaja3
            
        # leiame protokollid, mille töid hindaja juba hindab
        q_prot = model.SessionR.query(model.Sooritus.testiprotokoll_id).distinct().\
                 join(model.Sooritus.hindamisolekud).\
                 join(model.Hindamisolek.hindamised).\
                 filter(model.Hindamisolek.hindamiskogum_id==self.c.hindaja.hindamiskogum_id).\
                 filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id).\
                 filter(model.Hindamine.liik==self.c.hindaja.liik).\
                 filter(model.Hindamine.labiviija_id==self.c.hindaja.id)
        omaprot = [r[0] for r in q_prot.all()]

        n = 0
        rc = 0
        if len(omaprot):
            # esmalt otsime hindaja oma protokollirühmadest töid
            q0 = q.filter(model.Sooritus.testiprotokoll_id.in_(omaprot))
            q0 = q0.order_by(model.Sooritus.testiprotokoll_id)
            for rcd in q0.all():
                rc = self._jagasooritus(rcd, n, sisestamisega)
                if rc == -1:
                    break
                else:
                    n += rc

        if rc >= 0:
            # edasi otsime suvalistest protokollirühmadest töid
            q0 = q.order_by(model.Sooritus.testiprotokoll_id)
            for rcd in q0.all():
                rc = self._jagasooritus(rcd, n, sisestamisega)
                if rc == -1:
                    break
                else:
                    n += rc

        if n > 0:
            self.c.hindaja.calc_toode_arv()
            # self.c.hindaja.toode_arv = model.Hindamine.query.\
            #     filter(model.Hindamine.labiviija_id==self.c.hindaja.id).\
            #     filter(model.Hindamine.sisestus==1).\
            #     count()

            model.Session.commit()
            self.success(_("Lisatud {n} töö hindamine").format(n=n))
        elif n_vaja3 == 0:
            self.notice(_("Hindamiskogumis {s} ei leitud kolmandat hindamist vajavaid töid").format(
                s=self.c.hindaja.hindamiskogum.tahis))
        elif n_vaja3_teinekool == 0:
            self.notice(_("Hindamiskogumis {s} ei leitud kolmandat hindamist vajavaid töid, mis poleks hindaja oma kooli õpilaste omad").format(
                s=self.c.hindaja.hindamiskogum.tahis))            
        else:
            self.notice(_("Hindamiskogumis {s} ei leitud kolmandat hindamist vajavaid töid, mida saaks sellele hindajale määrata").format(
                s=self.c.hindaja.hindamiskogum.tahis))

        return self._redirect('index')

    def _delete(self, item):
        "Töö eemaldamine hindajalt (kui hindamine on veel alustamata)"
        if item.staatus == const.H_STAATUS_HINDAMATA:
            # leiame hindamise teise sisestuse
            q = (model.Session.query(model.Hindamine)
                 .filter_by(hindamisolek_id=item.hindamisolek_id)
                 .filter_by(labiviija_id=item.labiviija_id)
                 .filter_by(sisestus=2))
            item2 = q.first()
            if item2:
                if item2.staatus != const.H_STAATUS_HINDAMATA:
                    self.error(_("Hindamist on juba alustatud, enam ei saa eemaldada"))
                    return
                # eemaldame hindamise teise sisestuse
                item2.delete()

            # eemaldame hindamise
            item.delete()
            model.Session.flush()
            self.c.hindaja.calc_toode_arv()
            model.Session.commit()
        else:
            self.error(_("Hindamist on juba alustatud, enam ei saa eemaldada"))
    
    def _jagasooritus(self, rcd, n, sisestamisega):
        """Kirje jagatakse sooritamiseks
        Kui rohkem pole vaja jagada, tagastab -1
        Kui seda kirjet ei saa jagada, tagastab 0
        Kui jagas ära, tagastab 1
        """
        if self.c.hindaja.planeeritud_toode_arv:
            toode_arv = (self.c.hindaja.toode_arv or 0) + n + 1
            if self.c.hindaja.planeeritud_toode_arv < toode_arv:
                # selle hindaja plaan on täis
                return -1

        # kontrollime, et see hindaja ei ole ise 
        # seda sooritust juba I või II hindajana hinnanud
        for he in rcd.hindamised:
            if he.hindaja_kasutaja_id == self.c.hindaja.kasutaja_id and not he.tyhistatud:
                # kasutaja juba on selle töö hindaja
                log.debug(_("Hindaja kasutaja {s} on juba seda tööd hinnanud").format(s=self.c.hindaja.kasutaja_id))
                return 0

        testiosa = self.c.toimumisaeg.testiosa
        if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
            # jätame välja need hindamisolekud, mille sooritaja kuulub sellisesse
            # protokolirühma, mille mõnda tööd juba hindab keegi teine kolmas hindaja
            q1 = model.SessionR.query(model.Hindamine.labiviija_id).distinct().\
                 filter(model.Hindamine.liik==const.HINDAJA3).\
                 filter(model.Hindamine.tyhistatud==False).\
                 join(model.Hindamine.hindamisolek).\
                 filter(model.Hindamisolek.hindamiskogum_id==self.c.hindaja.hindamiskogum_id).\
                 join(model.Hindamisolek.sooritus).\
                 filter(model.Sooritus.testiprotokoll_id==rcd.sooritus.testiprotokoll_id)
            for lv2_id, in q1.all():
                if lv2_id != self.c.hindaja.id:
                    # keegi teine on kolmas hindaja samas testiprotokollirühmas
                    log.debug(_("Protokolli {s1} hindab juba hindaja {s2}").format(s1=rcd.sooritus.testiprotokoll_id, s2=lv2_id))
                    return 0

        rcd.give_hindamine3(self.c.hindaja.kasutaja_id, self.c.hindaja.id, sisestamisega)

        return 1

    def _index_protokoll(self):
        "Hindamisprotokollide väljastamine"
        doc = Hindamisprotokoll3Doc(self.c.toimumisaeg, self.c.hindaja)
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            self.c.nosub = True
            return self.index()
        else:
            fn = 'hindamisprotokoll.pdf'
            return utils.download(data, fn, 'application/pdf')

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.hindaja = model.Labiviija.get(self.request.matchdict.get('hindaja_id'))
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
        
    def _perm_params(self):
        return {'obj': self.c.test}
