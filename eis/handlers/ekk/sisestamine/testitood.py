from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TestitoodController(BaseResourceController):
    """Kirjalike testisoorituste otsimine vastuste sisestamiseks
    """
    _permission = 'sisestamine'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'ekk/sisestamine/testitood.otsing.mako'
    _LIST_TEMPLATE = 'ekk/sisestamine/testitood.otsing_list.mako'
    _DEFAULT_SORT = 'sooritus.tahised'
    _get_is_readonly = False

    def _index_optsk(self):
        "Sisestuskogumite valiku värskendamine peale toimumisaja tähise käsitsi sisestamist"
        ta_tahised = self.request.params.get('ta_tahised')
        ta, err = self._get_toimumisaeg_by_tahis(ta_tahised)
        if ta:
            li = self._get_opt_sisestuskogum(ta)
            data = [{'id':a[0],'value':a[1]} for a in li]
        else:
            data = []
        return Response(json_body=data)
        
    def _query(self):
        self.c.opt_sessioon = self.c.opt.testsessioon
        q = model.SessionR.query(model.Sooritus, 
                                model.Sisestusolek, 
                                model.Testiprotokoll.tahised,
                                model.Koht.nimi)
        q = q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD).\
            join(model.Sooritus.sooritaja).\
            join((model.Sisestuskogum, 
                  model.Sisestuskogum.testiosa_id==model.Sooritus.testiosa_id))

        q = q.outerjoin((model.Sisestusolek, 
                         sa.and_(model.Sisestusolek.sooritus_id==model.Sooritus.id,
                                 model.Sisestusolek.sisestuskogum_id==model.Sisestuskogum.id,
                                 model.Sisestusolek.liik==const.VASTUSTESISESTUS))).\
            outerjoin(model.Sooritus.testiprotokoll)       
        q = q.join(model.Sooritus.testikoht).\
            join(model.Testikoht.koht)

        # jätame välja need sooritajad, kes pole osalenud ühelgi selle sisestuskogumi alatestil
        q = q.filter(sa.exists().where(sa.and_(\
            model.Hindamisolek.puudus==False,
            model.Hindamisolek.sooritus_id==model.Sooritus.id,
            model.Hindamisolek.hindamiskogum_id==model.Hindamiskogum.id,
            model.Hindamiskogum.sisestuskogum_id==model.Sisestuskogum.id)))
        return q

    def _search_default(self, q):
        return self._search(q)

    def _get_toimumisaeg_by_tahis(self, ta_tahised):
        self.c.ta_tahised = ta_tahised.strip().replace('+','-').upper()
        li_ta = self.c.ta_tahised.split('-')
        if len(li_ta) != 3:
            return None, _('Sisesta toimumisaja tähis 3-osalisena')
        else:
            ta = model.Toimumisaeg.query.filter_by(tahised=self.c.ta_tahised).first()
            if not ta:
                return None, _('Sellise tähisega toimumisaega ei leitud')
            else:
                return ta, None

    def _get_opt_sisestuskogum(self, ta):
        skogumid = [sk for sk in ta.testiosa.sisestuskogumid if sk.on_vastused]
        return [(sk.id, '%s - %s' % (sk.tahis, sk.nimi)) for sk in skogumid]
    
    def _search(self, q):
        on_parandamine = self.request.params.get('sisestus') == 'p'

        if self.c.ta_tahised and (self.c.otsi or self.c.sisesta):
            # on antud toimumisaja tähis ja vajutati nupule Otsi või Sisesta
            # või sisestusvormil Järgmine
            # (mitte ei valitud loetelust toimumisaega)
            ta, err = self._get_toimumisaeg_by_tahis(self.c.ta_tahised)
            if ta:
                self.c.toimumisaeg_id = ta.id
            else:
                self.error(err)

        ta = None
        if self.c.toimumisaeg_id:
            # toimumisaeg on valitud - kas valikust või tähisega
            ta = model.Toimumisaeg.get(self.c.toimumisaeg_id)
            if ta:
                self.c.ta_tahised = ta.tahised
                self.c.opt_sisestuskogum = self._get_opt_sisestuskogum(ta)
                if not self.c.sisestuskogum_id and len(self.c.opt_sisestuskogum):
                    self.c.sisestuskogum_id = self.c.opt_sisestuskogum[0][0]
                if not self.c.sessioon_id:
                    self.c.sessioon_id = ta.testimiskord.testsessioon_id
                q = q.filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg_id) 

        on_tpr = False
        if self.c.tpr_tahised:
            # on antud testiprotokolli tähis kahekohaliselt KOHT-PROTOKOLL
            li_tpr = self.c.tpr_tahised.split('-')
            if not self.c.toimumisaeg_id:
                self.error(_('Sisesta toimumisaja tähis ka'))
            elif len(li_tpr) != 2:
                self.error(_('Sisesta protokollirühma tähis 2-osalisena (KOHT-PROTOKOLL)'))
            else:
                on_tpr = True
                tkoht_tahis, tpr_tahis = li_tpr
                q = q.filter(model.Testikoht.tahis==tkoht_tahis).\
                    filter(model.Testiprotokoll.tahis==tpr_tahis)

        if self.c.sisestuskogum_id:
            q = q.filter(model.Sisestuskogum.id==self.c.sisestuskogum_id)

        if self.c.tahised:
            q = q.filter(model.Sooritus.tahised==self.c.tahised)

        sisestus_isikukoodiga = ta and ta.testimiskord.sisestus_isikukoodiga
        if sisestus_isikukoodiga:
            # lisame kasutaja tabeli, et saaks isikukoodi järgi sortida
            q = q.join(model.Sooritaja.kasutaja)

        if self.c.isikukood:
            if sisestus_isikukoodiga:
                usp = validators.IsikukoodP(self.c.isikukood)
                q = q.filter(usp.filter(model.Kasutaja))                
            elif ta:
                self.error(_('Valitud testimiskorral pole isikukoodiga sisestamine lubatud'))
                return

        #model.log_query(q)
        if self.c.sisesta and on_parandamine:
            # kasutaja vajutas parandamise vormil nupule "Järgmine"
            if not self.c.ta_tahised:
                self.error(_('Palun sisesta toimumisaja tähis'))
            elif not self.c.sisestuskogum_id:
                self.error(_('Palun vali sisestuskogum'))
            else:
                # otsime neid, millel on sisestuserinevus
                q = q.filter(model.Sisestusolek.staatus==const.H_STAATUS_POOLELI).\
                    filter(model.Sisestusolek.staatus1==const.H_STAATUS_HINNATUD).\
                    filter(model.Sisestusolek.staatus2==const.H_STAATUS_HINNATUD).\
                    order_by(model.Testiprotokoll.tahised, model.Sooritus.tahised)
                rcd = q.first()
                tos = rcd and rcd[0] or None
                if not tos:
                    self.error(_('Ei ole sisestuserinevustega testitöid, mille mõlemad sisestused on kinnitatud'))
                elif not tos.testiprotokoll_id:
                    self.error(_('Testisooritaja ei kuulu ühtegi protokollirühma'))
                else:
                    sisestuskogum = model.Sisestuskogum.get(self.c.sisestuskogum_id)
                    return HTTPFound(location=self.url('sisestamine_vastused', 
                                                       sooritus_id=tos.id,
                                                       sisestus='p',
                                                       sisestuskogum_id=sisestuskogum.id,
                                                       eelmine_id=self.c.eelmine_id))

        elif self.c.sisesta:
            # kasutaja vajutas nupule "Sisesta" või sisestusvormil nupule "Järgmine" ja soovib kohe sisestama asuda
            if not self.c.ta_tahised:
                self.error(_('Palun sisesta toimumisaja tähis'))
            elif not self.c.sisestuskogum_id:
                self.error(_('Palun vali sisestuskogum'))
            elif not self.c.tpr_tahised and not self.c.isikukood and sisestus_isikukoodiga:
                self.error(_('Palun sisesta protokollirühma tähis või isikukood'))
            elif not self.c.tpr_tahised and not sisestus_isikukoodiga:
                self.error(_('Palun sisesta protokollirühma tähis'))
            elif not self.c.tahised and not self.c.isikukood and sisestus_isikukoodiga:
                self.error(_('Palun sisesta testitöö tähis või isikukood'))
            elif not self.c.tahised and not sisestus_isikukoodiga:
                self.error(_('Palun sisesta testitöö tähis'))
            else:
                # otsime tähise järgi
                rcd = q.first()
                tos = rcd and rcd[0] or None
                if not tos:
                    if self.c.tahised:
                        self.error(_('Sellise tähisega testisooritust ei ole'))
                    else:
                        self.error(_('Sellist testisooritust ei ole'))
                elif not tos.testiprotokoll_id:
                    self.error(_('Testisooritaja ei kuulu ühtegi protokollirühma'))
                else:
                    sisestuskogum = model.Sisestuskogum.get(self.c.sisestuskogum_id)
                    if not on_parandamine:
                        sisestus = self._get_sisestus(tos, sisestuskogum)
                    else:
                        sisestus = 'p'
                    if sisestus:
                        return HTTPFound(location=self.url('sisestamine_vastused', 
                                                           sooritus_id=tos.id,
                                                           sisestus=sisestus,
                                                           sisestuskogum_id=sisestuskogum.id,
                                                           eelmine_id=self.c.eelmine_id))

            
        if self.c.sessioon_id:
            self.c.opt_toimumisaeg = model.Toimumisaeg.get_opt(self.c.sessioon_id, 
                                                               vastvorm_kood=const.VASTVORM_KP)
        if ta:
            liigid = self.c.user.get_testiliigid(self._permission)
            if None not in liigid:
                if ta.testiosa.test.testiliik_kood not in liigid:
                    self.error(_('Toimumisaeg {s} kuulub sellisele testile, mille testiliigi sisestamine pole kasutajale lubatud').format(s=ta.tahised))
                    return
                
            self.c.toimumisaeg = ta
            if sisestus_isikukoodiga:
                if self.c.testikoht_id:
                    q = q.filter(model.Testikoht.id==self.c.testikoht_id)
                self.c.opt_testikoht = [(r.id, r.koht.nimi) for r in ta.testikohad if r.staatus]

            return q

    def _get_sisestus(self, tos, sisestuskogum):
        """Leitakse sisestus
        """
        if self.c.sisestus == 'p' and \
                self.c.user.has_permission('parandamine', const.BT_UPDATE):            
            # kasutaja soovis just parandama hakata
            return 'p'

        # tuleb valida sisestus 1 või 2
        solek = tos.get_sisestusolek(sisestuskogum.id, const.VASTUSTESISESTUS)
        if not solek:
            # olen esimene või teine sisestaja ja seda sisestust veel ei ole alustatud
            # loome sisestusoleku kirje ja seome selle sisestaja kasutajaga
            solek = tos.give_sisestusolek(sisestuskogum, const.VASTUSTESISESTUS)
        sisestus = None
        if solek.sisestaja1_kasutaja_id == self.c.user.id:
            # sisestus 1 on minu oma
            sisestus = 1
        elif solek.sisestaja2_kasutaja_id == self.c.user.id:
            # sisestus 2 on minu oma
            sisestus = 2
        elif not solek.sisestaja1_kasutaja_id:
            solek.sisestaja1_kasutaja_id = self.c.user.id
            solek.sisestaja1_algus = datetime.now()            
            sisestus = 1
        elif not solek.sisestaja2_kasutaja_id:
            solek.sisestaja2_kasutaja_id = self.c.user.id
            solek.sisestaja2_algus = datetime.now()                        
            sisestus = 2

        if sisestus == 2:
            if solek.staatus2 == const.H_STAATUS_HINDAMATA:
                solek.staatus2 = const.H_STAATUS_POOLELI
        elif sisestus == 1:
            if solek.staatus1 == const.H_STAATUS_HINDAMATA:
                solek.staatus1 = const.H_STAATUS_POOLELI
                
        model.Session.commit()
        if sisestus:
            # sobiv sisestus on leitud
            return sisestus

        if self.c.user.has_permission('parandamine', const.BT_UPDATE):
            # olen parandaja
            return 'p'

        self.error(_('Mõlema sisestusega on juba alustatud'))
