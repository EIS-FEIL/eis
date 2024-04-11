# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
from eis.lib.xtee import ehis
import json
_ = i18n._

log = logging.getLogger(__name__)

class HindajaymbrikudController(BaseResourceController):
    """Tagastusymbriku väljastamine hindajale
    """
    _permission = 'sisestamine'
    _MODEL = model.Tagastusymbrik
    _INDEX_TEMPLATE = 'ekk/sisestamine/hindajaymbrikud.mako'
    _LIST_TEMPLATE = 'ekk/sisestamine/hindajaymbrikud_list.mako'
    _DEFAULT_SORT = 'tagastusymbrik.valjastatud' # vaikimisi sortimine
    _no_paginate = True

    def _index_d(self):
        q = self._query()
        q = self._order(q)
        self.c.items = self._paginate(q)
        return self.response_dict
    
    def _query(self):
        q = model.Tagastusymbrik.query.\
            filter(model.Tagastusymbrik.labiviija_id==self.c.hindaja1.id)
        return q

    def create(self):
        sub = self._get_sub()
        if sub:
            return eval('self._create_%s' % sub)()

        ymbrik, msg = self._leia_ymbrik()
        if ymbrik:
            err, msg = self._valjasta(ymbrik)
            if not err:
                model.Session.commit()
                msg = _('Ümbrik {s1} on väljastatud ').format(s1=ymbrik.tahised) +\
                      _(' ja selles olevad tööd määratud hindajale hindamiseks. ') + (msg or '')
        else:
            err = True
            
        if err:
            body = ''
        else:
            body = self.render(self._LIST_TEMPLATE, self._index_d())
        return Response(json_body=[err, msg, body])

    def update(self):
        """Arvuta uuesti
        """
        id = self.request.matchdict.get('id')
        ymbrik = model.Tagastusymbrik.get(id)
        if ymbrik and ymbrik.labiviija_id == self.c.hindaja1.id:
            if self._valjasta(ymbrik):
                model.Session.commit()
                self.success(_('Ümbriku väljastamine on üle kontrollitud ja uuesti arvutatud'))
        return self._redirect(action='index')           

    def _create_amet(self):
        _("Hindajate ametikohtade uuendamine - vaatame EHISest, millises koolis hindaja töötab")
        d = datetime.now()

        kasutajad = [self.c.hindaja1.kasutaja]
        if self.c.hindaja2:
            kasutajad.append(self.c.hindaja2.kasutaja)

        for k in kasutajad:
            k.ametikoht_proovitud = d

        params = [k.isikukood for k in kasutajad]
        reg = ehis.Ehis(handler=self)
        message, ametikohad = reg.ametikohad(params)
    
        if message:
            self.error(message)
        else:
            for k in kasutajad:
                k_ametikohad = [a for a in ametikohad if str(a.isikukood) == k.isikukood]
                if k.update_pedagoogid(k_ametikohad):
                    xtee.uuenda_rr_pohiandmed(self, k)                    

        model.Session.commit()
        return self._redirect(action='index')

    def _leia_ymbrik(self):
        self.c.tahised = self.request.params.get('tahised')
        if not self.c.tahised:
            return None, _('Sisesta ümbriku tähis')

        self.c.tahised = self.c.tahised.replace('+', '-').upper()
        li = self.c.tahised.split('-')
        if len(li) != 6:
            return None, _('Sisesta ümbriku tähis kujul: TEST-TESTIOSA-TESTIMISKORD-TESTIKOHT-PROTOKOLLIRÜHM-ÜMBRIKULIIK')

        (tpr_tahised, yliik_tahis) = self.c.tahised.rsplit('-', 1)
        ymbrik = model.Tagastusymbrik.query.filter_by(tahised=self.c.tahised).first()
        if not ymbrik:
            return None, _('Sisestatud tähisega {s} ümbrikut ei ole olemas').format(s=self.c.tahised)
        tpr = ymbrik.testiprotokoll
        
        toimumisprotokoll = tpr.testipakett.toimumisprotokoll
        if not toimumisprotokoll:
            return None, _('Testi toimumise protokoll puudub!')
        elif toimumisprotokoll.staatus not in (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD):
            return None, _('Testi toimumise protokoll on kinnitamata')

        toimumisaeg_id = tpr.testipakett.testikoht.toimumisaeg_id
        ymbrikuliik = ymbrik.tagastusymbrikuliik
        if not ymbrikuliik:
            return None, _('Sisestatud tähisega {s} ümbrikut ei ole olemas').format(s=self.c.tahised)

        if toimumisaeg_id != self.c.toimumisaeg.id:
            return None, _('Ümbrikus {s} ei ole selle testi toimumisaja tööd').format(s=self.c.tahised)

        if ymbrik.labiviija_id:
            # ymbrik on kellelegi teisele suunatud
            return None, _('Ümbrik {s1} on väljastatud hindajale {s2}').format(s1=self.c.tahised, s2=ymbrik.labiviija.kasutaja.nimi)

        return ymbrik, None

    def _valjasta(self, ymbrik):    
        "Ymbriku väljastamine hindajale"
        err, msg = self._check_hindaja(self.c.hindaja1, ymbrik)
        if err:
            return err, msg
        if self.c.hindaja2:
            err, msg = self._check_hindaja(self.c.hindaja2, ymbrik)
            if err:
                return err, msg

        ymbrik.staatus = const.M_STAATUS_HINDAJA
        if ymbrik.labiviija != self.c.hindaja1:
            # hindajale väljastamise aja märgime siis,
            # kui toimub väljastamine, mitte uuesti arvutamine
            ymbrik.valjastatud = datetime.now()
        ymbrik.labiviija = self.c.hindaja1
        hindamiskogum = self.c.hindaja1.hindamiskogum
        testiosa = self.c.toimumisaeg.testiosa
        tpr = ymbrik.testiprotokoll
        tpr2 = ymbrik.testiprotokoll2
        sooritused = list(tpr.sooritused)
        if tpr2:
            sooritused.extend(list(tpr2.sooritused))
        for tos in sooritused:
            if tos.staatus != const.S_STAATUS_TEHTUD:
                # puudujaid ei hinda
                # kontrollime, ega pole varasemast tekkinud hindamise kirjeid
                holek = tos.get_hindamisolek(hindamiskogum)
                if holek:
                    for hindamine in holek.hindamised:
                        if hindamine.liik == self.c.hindaja1.liik or \
                               self.c.hindaja2 and hindamine.liik == self.c.hindaja2.liik:
                            if len(hindamine.ylesandehinded) == 0:
                                hindamine.delete()
                            else:
                                hindamine.tyhistatud = True
                continue

            holek = tos.give_hindamisolek(hindamiskogum)
            holek.puudus = tos.check_hk_puudus(hindamiskogum, testiosa, not tos.toimumisaeg_id)
            if holek.puudus:
                continue

            # hindamist väärt sooritus
            # tyhistame teised hindamised, kui on
            for hindaja in (self.c.hindaja1, self.c.hindaja2):
                if hindaja:
                    found = False
                    for hindamine in holek.hindamised:
                        if hindamine.liik == hindaja.liik and hindamine.sisestus == 1:
                            if hindamine.hindaja_kasutaja_id == hindaja.kasutaja_id:
                                # juba on suunatud
                                hindamine.tyhistatud = False
                                hindamine.labiviija = hindaja
                                found = True
                            else:
                                # varasemast on olemas sama liigi hindamine kellegi teise poolt
                                if len(hindamine.ylesandehinded) == 0 and hindamine.staatus <= const.H_STAATUS_POOLELI:
                                    hindamine.delete()
                                else:
                                    hindamine.tyhistatud = True
                                model.Session.flush()
                    if not found:
                        # loome hindajale hindamise kirje
                        hindamine = holek.give_hindamine(hindaja.liik,
                                                         hindaja_kasutaja_id=hindaja.kasutaja_id)
                        hindamine.labiviija = hindaja

        self.c.hindaja1.calc_toode_arv()
        if self.c.hindaja2:
            self.c.hindaja2.calc_toode_arv()

        return err, msg

    def _check_hindaja(self, hindaja, ymbrik):
        msg = None

        # kontrollime, et ymbrikus on hindaja hindamiskogumi ylesanded
        on_hk = oige_hk = False
        tagastusymbrikuliik = ymbrik.tagastusymbrikuliik
        for hk in tagastusymbrikuliik.hindamiskogumid:
            on_hk = True
            if hk.id == hindaja.hindamiskogum_id:
                oige_hk = True
                break
        if on_hk and not oige_hk:
            hk = hindaja.hindamiskogum
            return True, _('Hindajale on määratud hindamiskogum {s}, aga ümbrikus selle hindamiskogumi töid ei ole').format(s=hk.tahis)

        # kontrollime, et piirkonnas oleks hindajal lubatud hinnata
        if self.c.toimumisaeg.oma_prk_hindamine:
            lubatud_piirkonnad_id = hindaja.kasutaja.get_kasutaja_piirkonnad_id()
            ymbrik_piirkond_id = ymbrik.testiprotokoll.testipakett.testikoht.koht.piirkond_id
            if ymbrik_piirkond_id not in lubatud_piirkonnad_id:
                return True, _('Soorituskoht ei asu hindaja piirkonnas, kuid lubatud on hinnata ainult oma piirkonnas')
        
        # kontrollime, et hindaja oma kooli õpilasi liiga suures koguses ei hindaks
        if not self.c.toimumisaeg.oma_kooli_hindamine:
            # ei ole üldse oma kooli õpilasi lubatud hinnata
            q = model.Sooritus.query.\
                filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id).\
                join(model.Sooritus.sooritaja).\
                join((model.Pedagoog, model.Pedagoog.koht_id==model.Sooritaja.kool_koht_id)).\
                filter(model.Pedagoog.kasutaja_id==hindaja.kasutaja_id)

            # q on päring antud toimumisaja sooritustest, kes õpivad pedagoogi koolis
            # leiame antud ymbrikus olevate pedagoogi kooli soorituste arvu
            cnt = q.filter(model.Sooritus.testiprotokoll_id==ymbrik.testiprotokoll_id).\
                filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD).\
                count()
            if cnt > 0:
                return True, _('Ümbrikus {s1} olevate tööde testisooritajad õpivad samas õppeasutuses, kus töötab hindaja {s2}').format(
                       s1=ymbrik.tahised, s2=hindaja.kasutaja.nimi)

        if self.c.toimumisaeg.sama_kooli_hinnatavaid:

            # leiame ymbrikus olevate tööde sooritajate arvud koolide kaupa
            q = model.SessionR.query(model.Sooritaja.kool_koht_id, 
                                    sa.func.count(model.Sooritus.id)).\
                filter(model.Sooritaja.kool_koht_id!=None).\
                join(model.Sooritaja.sooritused).\
                filter(model.Sooritus.testiprotokoll_id==ymbrik.testiprotokoll_id).\
                filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD).\
                group_by(model.Sooritaja.kool_koht_id)

            for rcd in q.all():
                kool_koht_id, ymbrik_cnt = rcd
                # leiame hindajale juba varem määratud sooritajate arvu samast koolist,
                # aga jätame välja need õpilased, kes on ümbrikus, et neid topelt ei loeks
                hindaja_cnt = model.SessionR.query(sa.func.count(model.Sooritus.id)).\
                    filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id).\
                    join(model.Sooritus.sooritaja).\
                    filter(model.Sooritaja.kool_koht_id==kool_koht_id).\
                    join(model.Sooritus.hindamisolekud).\
                    join(model.Hindamisolek.hindamised).\
                    filter(model.Hindamine.labiviija_id==hindaja.id).\
                    filter(model.Sooritus.testiprotokoll_id!=ymbrik.testiprotokoll_id).\
                    scalar()
                if hindaja_cnt + ymbrik_cnt > self.c.toimumisaeg.sama_kooli_hinnatavaid:
                    koht = model.Koht.get(kool_koht_id)
                    return True, _('Ümbrikus {s1} on {d1} tööd sooritajatelt, kelle kool on {n1}. Hindajal on juba {s2} sama kooli õpilase tööd. Hindaja ei tohi hinnata rohkem kui {s3} sama kooli õpilase tööd.').format(
                                    s1=ymbrik.tahised,
                                    d1=ymbrik_cnt, 
                                    n1=koht.nimi, 
                                    s2=hindaja_cnt, 
                                    s3=self.c.toimumisaeg.sama_kooli_hinnatavaid)

        # kontrollime, et ymbrik on hindaja hindamiskeeles
        testipakett = ymbrik.testiprotokoll.testipakett
        if testipakett.lang != hindaja.lang:
            return True, _('Ümbrikus {s1} olevate tööde soorituskeel ({s2}) ei kattu hindaja keelega ({s3})').format(
                   s1=ymbrik.tahised, s2=testipakett.lang_nimi, s3=hindaja.lang_nimi)

        # kontrollime, et plaanitud tööde arvu ei ületata
        if hindaja.planeeritud_toode_arv:
            # leiame hindajale juba varem antud tööde arvu, 
            # välja arvatud need sooritajad, kes on selles ymbrikus
            cnt = model.SessionR.query(sa.func.count(model.Sooritus.id)).\
                filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id).\
                filter(model.Sooritus.testiprotokoll_id!=ymbrik.testiprotokoll_id).\
                join(model.Sooritus.hindamisolekud).\
                join(model.Hindamisolek.hindamised).\
                filter(model.Hindamine.labiviija_id==hindaja.id).\
                scalar()
            # lisame ymbrikus olevad sooritused
            cnt += ymbrik.testiprotokoll.tehtud_toodearv
            if cnt > hindaja.planeeritud_toode_arv:
                msg = _('Hindamiseks antud tööde arv {d1} ületab plaanitud hinnatavate tööde arvu {d2}!').format(d1=cnt, d2=hindaja.planeeritud_toode_arv)

        return False, msg

    def _delete(self, ymbrik):
        """Ümbriku hindajale väljastamise tühistamine
        """
        q = model.Hindamine.query.\
            filter(model.Hindamine.hindamisolek.has(\
                sa.and_(model.Hindamisolek.hindamiskogum_id==self.c.hindaja1.hindamiskogum_id,
                        model.Hindamisolek.sooritus.has(\
                            model.Sooritus.testiprotokoll_id==ymbrik.testiprotokoll_id))
                ))

        q1 = q.filter(model.Hindamine.labiviija==self.c.hindaja1)
        alustatud = q1.filter(model.Hindamine.staatus!=const.H_STAATUS_HINDAMATA).count()
        if alustatud > 0:
            self.error('Selle ümbriku väljastamist ei saa tühistada, sest {s1} on juba ümbrikus olevate tööde hindamist alustanud').format(s1=self.c.hindaja1.kasutaja.nimi)
            model.Session.rollback()
            return
        for hindamine in list(q1.all()):
            hindamine.delete()

        if self.c.hindaja2:
            q2 = q.filter(model.Hindamine.labiviija==self.c.hindaja2)
            alustatud = q2.filter(model.Hindamine.staatus!=const.H_STAATUS_HINDAMATA).count()
            if alustatud > 0:
                self.error(_('Selle ümbriku väljastamist ei saa tühistada, sest {s1} on juba ümbrikus olevate tööde hindamist alustanud').format(s1=self.c.hindaja2.kasutaja.nimi))
                model.Session.rollback()
                return
            for hindamine in list(q2.all()):
                hindamine.delete()
   
        ymbrik.staatus = const.M_STAATUS_TAGASTATUD
        ymbrik.labiviija = None

        self.c.hindaja1.calc_toode_arv()
        if self.c.hindaja2:
            self.c.hindaja2.calc_toode_arv()

        model.Session.commit()
        self.success(_('Ümbriku väljastamine on tühistatud'))
            
    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.hindaja1 = model.Labiviija.get(self.request.matchdict.get('hindaja_id'))
        self.c.hindaja2 = self.c.hindaja1.get_hindaja2()

