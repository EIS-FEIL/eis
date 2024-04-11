from eis.lib.baseresource import *
from eis.lib.blockview import BlockView
from eis.lib.resultentry import ResultEntry
_ = i18n._

log = logging.getLogger(__name__)

class VastusedController(BaseResourceController):
    """Kirjaliku p-testi testitöö vastuste sisestamine
    """
    _permission = 'sisestamine'
    _INDEX_TEMPLATE = 'ekk/sisestamine/vastused.mako'
    _ITEM_FORM = forms.ekk.sisestamine.VastusedForm
    _get_is_readonly = False
    _index_after_create = True

    def _index_d(self):
        c = self.c
        if not c.sooritus:
            self.error(_('Testiosasooritust ei ole'))
            raise self._back_to_index()

        c.protokoll = c.sooritus.testiprotokoll 
        if not c.protokoll:
            self.error(_('Sooritaja ei kuulu protokollirühma'))
            raise self._back_to_index()

        if sisestaja_soorituskoht(c.user.id, c.sooritus.testikoht_id):
            self.error(_("Ümbriku kontroll. Palun edasta ümbrik korraldusspetsialistile."))
            raise self._back_to_index()

        c.assessment_entry = BlockView.assessment_entry

        c.solek = self._give_sisestusolek()
        if not c.solek:
            self.error(_('Ei saa sisestada'))
            raise self._back_to_index()

        if not c.focus:
            # fookus võidakse määrata create sees vigade kuvamisel samuti
            c.focus = self.request.params.get('focus')
            
        c.komplekt, c.komplekt_id1, c.komplekt_id2 = self._get_komplekt()

        # eelmiselt vormilt järgmisele minnes on kaasas 
        # eelmisena sisestatud soorituse id, et selle pealt võtta hindajad;
        # kui tööd võetakse samast ymbrikust (mis tavaliselt tähendab, et samas protokollis), 
        # siis on yldiselt ka sama hindaja
        eelmine_id = self.request.params.get('eelmine_id')
        if eelmine_id:
            tos = model.Sooritus.get(eelmine_id)
            if tos and tos.testiprotokoll_id == c.sooritus.testiprotokoll_id:
                c.eelmine_sooritus = tos

        return self.response_dict

    def _give_sisestusolek(self):
        c = self.c
        solek = c.sooritus.get_sisestusolek(c.sisestuskogum.id, const.VASTUSTESISESTUS)
        if not solek:
            solek = c.sooritus.give_sisestusolek(c.sisestuskogum, const.VASTUSTESISESTUS)
        if c.sisestus == 1 and solek.can_sis1(c.user.id):
            if solek.sisestaja1_kasutaja_id != c.user.id:
                solek.sisestaja1_kasutaja_id = c.user.id
                if not solek.sisestaja1_algus:
                    solek.sisestaja1_algus = datetime.now()
                model.Session.commit()
            return solek
        elif c.sisestus == 2 and solek.can_sis2(c.user.id):
            if solek.sisestaja2_kasutaja_id != c.user.id:
                solek.sisestaja2_kasutaja_id = c.user.id
                if not solek.sisestaja2_algus:
                    solek.sisestaja2_algus = datetime.now()
                model.Session.commit()
            return solek
        elif c.sisestus == 'p':
            return solek

    def _get_komplekt(self):
        """Leitakse sisestatud komplektivalik
        """
        komplekt_id1 = komplekt_id2 = None

        # sisestuskogumi kõigil hindamiskogumitel on üks ja sama komplektivalik
        for hkogum in self.c.sisestuskogum.hindamiskogumid:
            self.c.opt_komplekt = hkogum.get_komplektivalik().get_opt_komplektid(self.c.toimumisaeg)
            break
        
        # vaatame andmebaasist, mis komplektid on sisestatud
        # ja kuna vastuste sisestamisel on yksainus komplekti sisestamise väli
        # kõigi hindamise kirjete jaoks,
        # siis peaks sama sisestamise kõigis hindamise kirjetes olema sama komplekt_id
        # võtame esimese ettejuhtuva
        sisestus = self.c.sisestus == 'p' and 1 or self.c.sisestus

        for sisestus in (1,2):
            rcd = model.SessionR.query(model.Hindamine.komplekt_id).\
                  join(model.Hindamine.hindamisolek).\
                  filter(model.Hindamisolek.sooritus_id==self.c.sooritus.id).\
                  filter(model.Hindamine.komplekt_id!=None).\
                  filter(model.Hindamine.liik==self.c.hindamine_liik).\
                  filter(model.Hindamine.sisestus==sisestus).\
                  join(model.Hindamisolek.hindamiskogum).\
                  filter(model.Hindamiskogum.sisestuskogum_id==self.c.sisestuskogum.id).\
                  first()
            k_id = rcd and rcd[0] or None
            if sisestus == 1:
                komplekt_id1 = k_id
            elif sisestus == 2:
                komplekt_id2 = k_id
                
        if self.c.sisestus == 2:
            komplekt_id1, komplekt_id2 = komplekt_id2, komplekt_id1

        # kui kasutaja just valis komplekti, siis see on parameetris
        komplekt = None
        komplekt_id = self.request.params.get('komplekt_id') or komplekt_id1
        if komplekt_id:
            # komplekti valik on sisestatud
            komplekt = model.Komplekt.get(komplekt_id)
        elif len(self.c.opt_komplekt) == 1:
            # kui komplekti valik pole sisestatud, aga ainult yks valida oligi,
            # siis võtame selle
            komplekt = model.Komplekt.get(self.c.opt_komplekt[0][0])

        komplekt_id2 = self.request.params.get('komplekt_id2') or komplekt_id2

        # tagastame praegu sisestatava komplekti ja juba sisestatud komplektide id
        return komplekt, komplekt_id1, komplekt_id2

    def index(self):
        self._index_d()
        return self.render_to_response(self._INDEX_TEMPLATE)

    def _create(self):

        tpr = self.c.sooritus.testiprotokoll
        sisestus = self.c.sisestus == 'p' and 1 or int(self.c.sisestus)

        test = self.c.testiosa.test
        resultentry = ResultEntry(self, None, test, self.c.testiosa)
        sooritaja = self.c.sooritus.sooritaja
        if sisestus == 1 and not self.c.kahekordne_sisestamine:
            # valimi yhekordsel sisestamisel leiame mittevalimi soorituse
            # ja mittevalimi protokolli vormi
            # (andmed jäetakse meelde resultentry objektis)
            mv_tos_id = get_mittevalim_sooritus_id(sooritaja, self.c.sooritus)
            # praegu sisestatud hindamised meelde jätta hiljem mittevalimiga võrdlemiseks
            v_items = []
        else:
            mv_tos_id = None
            
        lopeta = self.request.params.get('kinnita') or self.c.sisestus == 'p'

        komplekt_id = self.form.data.get('komplekt_id')
        komplekt = model.Komplekt.get(komplekt_id)
        if komplekt:
            komplektivalik_id = komplekt.komplektivalik_id
            sk = ExamSaga(self).give_soorituskomplekt(self.c.sooritus.id, komplektivalik_id)
            sk.komplekt_id = komplekt.id
            TestSaga(self).komplekt_set_lukus_tk(komplekt, self.c.testimiskord)
        else:
            sk = None
            
        staatus1 = const.H_STAATUS_HINNATUD
        staatus2 = const.H_STAATUS_HINNATUD

        sisestuserinevus = False
        # kas mõlemad sisestused on olemas ja hinnatud
        molemad = True
        # kas võrrelda sisestatut teise sisestusega
        compare2 = self.c.sisestus != 'p' and self.c.kahekordne_sisestamine
        hindajad_id = set()
        sk_pallid = sk_toorpunktid = 0
        for hk_n, hk in enumerate(self.form.data.get('hk')):
            # yhe hindamiskogumi hinnete salvestamine (kõik sooritused)
            hindamiskogum = model.Hindamiskogum.get(hk.get('hindamiskogum_id'))

            # leitakse soorituse hindamisoleku kirje antud hindamiskogumi kohta
            holek = self.c.sooritus.give_hindamisolek(hindamiskogum)
            rcd = hk.get('hmine')
            if rcd:
                # rcd on yhe soorituse yhe hindamiskogumi yhele hindamisele vastav kirje
                # leitakse hindamisolekule vastav hindamise kirje antud sisestuse kohta
                hindamine = holek.give_hindamine(self.c.hindamine_liik, sisestus)
                # update_sooritus() pole esimese hindaja puhul vaja teha juhul,
                # kui salvestame kahekordse sisestamise parandamist
                # ja teise hindaja juures seda niikuinii teeme
                is_update_sooritus = self.c.sisestus != 'p' or not self.c.kahekordne_sisestamine
                prefix = 'hk-%d.hmine' % (hk_n)
                resultentry.save_sisestamine(sooritaja, rcd, lopeta, prefix, self.c.sooritus, holek,
                                             self.c.testiosa, hindamine, komplekt, sk, compare2, is_update_sooritus)
                staatus1 = min(staatus1, hindamine.staatus)
                hindajad_id.add(hindamine.labiviija_id)
                hindajad_id.add(hindamine.kontroll_labiviija_id)
                sk_pallid += holek.pallid or 0
                sk_toorpunktid += holek.toorpunktid or 0
                if not hindamine.sisestaja_kasutaja_id:
                    hindamine.sisestaja_kasutaja_id = self.c.user.id

                if self.c.sisestus != 'p':
                    if hindamine.sisestuserinevus:
                        sisestuserinevus = True
                    if not hindamine.sisestatud:
                        molemad = False

                if mv_tos_id:
                    # jätame sisestatud hindamise meelde, et võrrelda hiljem mittevalimiga
                    v_items.append((prefix, rcd))

            if self.c.sisestus == 'p' and self.c.kahekordne_sisestamine:
                resultentry.sisestuserinevus = False # kas on erinevusi teise sisestusega
                resultentry.molemad = True # kas mõlemad sisestused on sisestatud
                sisestus2 = 2
                rcd = hk.get('hmine2')
                if rcd:
                    # rcd on yhe soorituse sama hindamiskogumi teisele sisestamisele vastav kirje
                    # leitakse hindamisolekule vastav hindamise kirje antud sisestuse kohta
                    hindamine2 = holek.give_hindamine(self.c.hindamine_liik, sisestus2)
                    resultentry.save_sisestamine(sooritaja, rcd, lopeta, 'hk-%d.hmine2' % (hk_n), self.c.sooritus, holek, self.c.testiosa, hindamine2, komplekt, sk, True)
                    staatus2 = min(staatus2, hindamine2.staatus)                    
                    if hindamine2.sisestuserinevus:
                        sisestuserinevus = True
                    if not hindamine2.sisestatud:
                        molemad = False

        if resultentry.errors:
            raise ValidationError(self, resultentry.errors)

        if lopeta:
            if resultentry.error_lopeta:
                # sisestamise lõpetamist takistav viga
                self.error(resultentry.error_lopeta)
                lopeta = False

        solek = self.c.sooritus.give_sisestusolek(self.c.sisestuskogum, const.VASTUSTESISESTUS)

        if self.c.sisestus != 'p':
            if not lopeta:
                # vajutati "Loobu"
                staatus1 = const.H_STAATUS_LYKATUD
            if self.c.sisestus == 1:
                solek.staatus1 = staatus1
                if solek.staatus2 != const.H_STAATUS_HINNATUD:
                    molemad = False
            elif self.c.sisestus == 2:
                solek.staatus2 = staatus1
                if solek.staatus1 != const.H_STAATUS_HINNATUD:
                    molemad = False

        else:
            # parandamine
            if not self.c.kahekordne_sisestamine:
                solek.staatus1 = const.H_STAATUS_HINNATUD
            elif not sisestuserinevus and molemad:
                solek.staatus1 = solek.staatus2 = const.H_STAATUS_HINNATUD

        if solek.staatus1 == const.H_STAATUS_HINNATUD and \
                not self.c.kahekordne_sisestamine:
            solek.staatus = const.H_STAATUS_HINNATUD
        elif solek.staatus1 == const.H_STAATUS_HINNATUD and \
                solek.staatus2 == const.H_STAATUS_HINNATUD and \
                not sisestuserinevus:
            solek.staatus = const.H_STAATUS_HINNATUD
        else:
            solek.staatus = const.H_STAATUS_POOLELI

        if solek.staatus == const.H_STAATUS_HINNATUD:
            solek.pallid = sk_pallid
            solek.toorpunktid = sk_toorpunktid
        else:
            solek.pallid = solek.toorpunktid = None
            
        model.Session.commit()
        
        self.c.lisatud_labiviijad_id = list()
        # arvutame hindajate hinnatud tööde arvu kokku
        for lv_id in hindajad_id:
            if lv_id:
                lv = model.Labiviija.get(lv_id)
                lv.calc_toode_arv()
                if lv in resultentry.neg_labiviijad:
                    # äsja siin lõime läbiviija kirje negatiivsest id-st
                    self.c.lisatud_labiviijad_id.append(lv.id)
        model.Session.commit()

        mv_err = None
        if mv_tos_id:
            # valimi sisestamisel võrrelda testiosa tulemust mittevalimi tulemusega
            mv_err = cmp_mittevalim(self, resultentry, v_items, self.c.sooritus, mv_tos_id)

        if mv_err or resultentry.warnings:
            if lopeta:
                err = _('Sisestamine on kinnitatud, kuid ei lange kokku teise sisestamisega. ')
            else:
                err = _('Andmed on salvestatud, kuid ei lange kokku teise sisestamisega. Palun kontrolli märgitud andmeväljad üle.')
            if mv_err:
                err += mv_err
            if resultentry.warnings:
                log.debug(resultentry.warnings)
                err += _('Palun kontrolli märgitud andmeväljad üle. ')                
            raise ValidationError(self, resultentry.warnings, message=err)

        if lopeta:
            self.success(_('Sisestamine on kinnitatud!'))
        else:
            self.success()
        return self.c.sooritus

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """   
        # lisame parameetri focus, et anda teada vajadusest viia fookus 
        # järgmise töö valimise tähise väljale lehekülje lõpus
        return self._redirect('index', focus='next')     

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE,
                                extra_info=self._index_d())            
        return Response(html)

    def _back_to_index(self):
        c = self.c
        url = self.url('sisestamine_testitood',
                       sessioon_id=c.testimiskord.testsessioon_id,
                       toimumisaeg_id=c.toimumisaeg.id,
                       sisestuskogum_id=c.sisestuskogum.id)
        return HTTPFound(location=url)


    def __before__(self):
        c = self.c
        c.sooritus = model.Sooritus.get(self.request.matchdict.get('sooritus_id'))
        c.sisestuskogum = model.Sisestuskogum.get(self.request.matchdict.get('sisestuskogum_id'))
        assert c.sisestuskogum.on_vastused, 'Pole vastuste sisestamise sisestuskogum'
        c.sisestus = self.request.matchdict.get('sisestus') # 1,2,p
        if c.sisestus in ('1','2'):
            c.sisestus = int(c.sisestus)
        c.hindamine_liik = const.HINDAJA1
        c.toimumisaeg = c.sooritus.toimumisaeg
        c.testimiskord = c.toimumisaeg.testimiskord
        c.kahekordne_sisestamine = c.toimumisaeg.kahekordne_sisestamine
        c.testiosa = c.sooritus.testiosa

    def _perm_params(self):
        return {'testiliik': self.c.testiosa.test.testiliik_kood}

def sisestaja_soorituskoht(kasutaja_id, testikoht_id):
    "Kontrollitakse, kas sisestaja on ise samas kohas sama testimiskorra sooritanud ES-147"
    # leiame testiliigi
    q = (model.SessionR.query(model.Test.testiliik_kood)
         .join(model.Test.testimiskorrad)
         .join(model.Testimiskord.toimumisajad)
         .join(model.Toimumisaeg.testikohad)
         .filter(model.Testikoht.id==testikoht_id)
         )
    testiliik, = q.first()
    if testiliik == const.TESTILIIK_RIIGIEKSAM:
        # kontroll teha ainult riigieksami korral
        # kontrollime, kas sisestaja on samas testikohas sooritanud
        q = (model.SessionR.query(model.Sooritus.id)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritus.testikoht_id==testikoht_id)
             )
        return q.count() > 0
    else:
        return False

def get_mittevalim_sooritus_id(sooritaja, tos):
    """Kui toimub valimi hindamiste sisestamine
    ja mittevalimi toimumise protokoll on sisestatud tulemustega,
    siis leitakse mittevalimi vastava sooritus ID,
    et võrrelda mittevalimi ja valimi tulemusi.
    """
    tk = sooritaja.testimiskord
    mittevalim_tk = tk and tk.valim_testimiskord or None
    if mittevalim_tk:
        mv_prot_vorm = mittevalim_tk.prot_vorm
        if mv_prot_vorm in (const.PROT_VORM_YLTULEMUS,
                            const.PROT_VORM_ALATULEMUS,
                            const.PROT_VORM_TULEMUS):
            # toimub valimi testimiskorra sisestamine ja
            # mittevalimi testimiskorra toimumise protokoll sisestati tulemustega
            kasutaja_id = sooritaja.kasutaja_id
            # leiame mittevalimi sooritus.id
            q = (model.SessionR.query(model.Sooritus.id)
                 .join(model.Sooritus.sooritaja)
                 .filter(model.Sooritaja.testimiskord_id==mittevalim_tk.id)
                 .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
                 .filter(model.Sooritus.testiosa_id==tos.testiosa_id))
            # mittevalimi soorituse ID
            mv_tos_id = q.scalar()
            return mv_tos_id

def cmp_mittevalim(handler, resultentry, v_items, tos, mv_tos_id):
    """
    Kui on ühekordne valimi sisestamine,
    siis võrreldakse testiosa tulemust ja ülesannete tulemust vastava mittevalimi tulemusega
    """
    mv_err = None
    fstr = handler.h.fstr
    # valimi soorituse ID
    v_tos_id = tos.id
    # ylesannete tulemuste võrdlus
    for prefix, rcd in v_items:
        for n1, rcd_ty in enumerate(rcd.get('ty')):        
            # iga testiylesande kohta
            ty_prefix = '%s.ty-%d' % (prefix, n1)
            ty_id = rcd_ty['ty_id']
            # ylesande tulemuse päring
            q = (model.SessionR.query(model.Ylesandevastus.pallid)
                 .filter(model.Ylesandevastus.testiylesanne_id==ty_id)
                 .filter(model.Ylesandevastus.loplik==True))
            # valimi tulemus
            v_pallid = q.filter_by(sooritus_id=v_tos_id).scalar()
            # mittevalimi tulemus
            mv_pallid = q.filter_by(sooritus_id=mv_tos_id).scalar()
            if not (v_pallid is None or mv_pallid is None):
                if round(v_pallid * 100) != round(mv_pallid * 100):
                    # ylesande pallid erinevad
                    resultentry.warnings[ty_prefix + '.toorpunktid'] = \
                      _("Ülesande tulemus ({s1}p) erineb kooli tulemusest ({s2}p)").format(
                          s1=fstr(v_pallid),
                          s2=fstr(mv_pallid))

    # testiosa kogutulemuse võrdlus
    mv_tos = model.Sooritus.get(mv_tos_id)
    mv_pallid = mv_tos.pallid
    v_pallid = tos.pallid
    if mv_pallid is not None and v_pallid is not None:
        if round(mv_pallid * 100) != round(v_pallid * 100):
            # testiosa pallid erinevad
            mv_err = _("Testiosa tulemus ({s1}p) erineb kooli tulemusest ({s2}p). ").format(
                s1=fstr(v_pallid),
                s2=fstr(mv_pallid))
    return mv_err

        
