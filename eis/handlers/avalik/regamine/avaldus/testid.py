from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import ehis
_ = i18n._
import eis.lib.regpiirang as regpiirang
import eis.handlers.ekk.otsingud.kohateated as kt
log = logging.getLogger(__name__)

class TestidController(BaseResourceController):
    _permission = 'sooritamine'
    _get_is_readonly = False
    _log_params_post = True
    _actions = 'index,create,delete'
    _INDEX_TEMPLATE = 'avalik/regamine/avaldus.testid.mako'
    
    def index(self):
        c = self.c
        err = ehis.uuenda_opilased(self, [c.kasutaja.isikukood])
        if err:
            self.error(err)
            return HTTPFound(location=self.url('regamised'))
        model.Session.commit()
        d = self._index_d()
        return self.render_to_response(self._INDEX_TEMPLATE)

    def tyhista(self):
        "Saabumine tyhistamise nupuga"
        self.c.is_edit = True
        return self.index()
    
    def _index_d(self):
        c = self.c
        test_id = self.request.matchdict.get('test_id')
        c.testiliik, c.opt_testiliigid = self._get_testiliik(test_id)
        if not c.opt_testiliigid:
            self.error(_("Praegu ei ole ühelegi testile iseregistreerimist avatud!"))
            raise HTTPFound(location=self.url('regamised'))
        
        on_tseis = c.testiliik in (const.TESTILIIK_SEADUS, const.TESTILIIK_TASE)
        if on_tseis or not c.kasutaja.opilane:
            # kui on TE/SE, siis on vaja uuendada, et kontrollida kodakondsust
            # kui ei ole õppur, siis on vaja uuendada, et saada värske nimi
            if xtee.uuenda_rr_pohiandmed(self, c.kasutaja, force=on_tseis):
                model.Session.commit()

        if c.testiliik == const.TESTILIIK_SEADUS:
            if c.kasutaja.kodakond_kood == const.RIIK_EST:
                self.error(_("Rahvastikuregistri andmetel olete Eesti Vabariigi kodanik. Põhiseaduse ja kodakondsuse seaduse tundmise eksam on mõeldud neile, kes soovivad taotleda Eesti kodakondust."))
            
        if test_id:
            # tuldud on kindlale testile regama
            # kontrollime, kas on juba sellele testile regatud
            li = c.kasutaja.get_reg_sooritajad(c.testiliik, peitmata=True, regamine=True)
            if len([r for r in c.sooritajad if r.test_id == test_id]) == 0:
                # sellele testile ei ole veel regatud
                c.test_id = test_id
            else:
                self.notice(_("Oled juba sellele testile registreeritud!"))

        # testid, kuhu saab registreerida
        c.items = self._list_testivalik()
        return self.response_dict

    def _get_opt_testiliigid(self, def_liik):
        """Testiliikide valikvälja valikud"""
        testiliigid = self.c.opt.klread_kood('TESTILIIK')
        d = date.today()
        q = (model.SessionR.query(model.Test.testiliik_kood).distinct()
             .join(model.Test.testimiskorrad)
             .filter(model.Test.eeltest_id==None)
             .filter(model.Test.avaldamistase==const.AVALIK_EKSAM)
             .filter(model.Testimiskord.reg_sooritaja==True)
             .filter(model.Testimiskord.reg_sooritaja_alates<=d)
             .filter(model.Testimiskord.reg_sooritaja_kuni>=d)
             .filter(model.Test.staatus==const.T_STAATUS_KINNITATUD))

        ained = self.c.kasutaja.get_opetaja_ained()
        if ained:
            # pedagoog saab oma õppeaine koolitustele regada
            f_aine = sa.or_(model.Test.testiliik_kood!=const.TESTILIIK_KOOLITUS,
                            model.Test.aine_kood.in_(ained))
            # eesti keel teise keelena eksamile saavad ka eesti keele õpetajad
            if const.AINE_ET in ained:
                f_aine = sa.or_(f_aine, model.Test.aine_kood==const.AINE_ET2)
            q = q.filter(f_aine)
        else:
            # kui pole pedagoog, siis ei saa koolitusele
            q = q.filter(model.Test.testiliik_kood != const.TESTILIIK_KOOLITUS)

        regatavad = [r for r, in q.all()]

        if not model.Kasutaja.is_isikukood_ee(self.c.user.isikukood):
            # kui kasutajal pole Eesti isikukoodi, siis saab ainult tasemeeksamile
            regatavad = [r for r in regatavad if r == const.TESTILIIK_TASE]
            
        if const.TESTILIIK_SEADUS in regatavad and self.c.kasutaja.kodakond_kood == const.RIIK_EST:
            # seaduse tundmise eksam on mõeldud ainult kodakondsuse taotlejatele
            regatavad = [r for r in regatavad if r != const.TESTILIIK_SEADUS]

        if def_liik:
            # kuvame ka selle liigi, mille regamise URLile tuldi, isegi kui teste pole
            regatavad.append(def_liik)

        # kui saab regada nii rv kui ka riigieksamitele, siis need on sama valikuna
        on_r = const.TESTILIIK_RIIGIEKSAM in regatavad
        on_rv = const.TESTILIIK_RV in regatavad
        opt_liigid = []
        for r in testiliigid:
            kood, nimi = r[:2]
            if kood not in regatavad:
                # sellele testiliigile ei saa regada
                continue
            if kood == const.TESTILIIK_RV and on_r:
                # ei kuva eraldi rv, sest r juba on
                continue
            if kood == const.TESTILIIK_RIIGIEKSAM and on_rv:
                if not on_r:
                    # ei kuva eraldi r, sest rv kuvatakse
                    continue
                else:
                    # muudame nimetuse, et kataks mõlemad testiliigid
                    nimi = _("Riigieksamid ja rahvusvahelised võõrkeele eksamid")
            opt_liigid.append((kood, nimi))
        return opt_liigid

    def _get_testiliik(self, test_id):
        """Leitakse valitud või vaikimisi testiliik"""
        testiliik = self.request.params.get('tliik') or \
                    self.request.matchdict.get('testiliik')

        # routing regamine_avaldus_testid_test korral on URLis olemas testi ID
        if test_id:
            test = model.Test.get(test_id)
            if test:
                # kui test on antud, siis see määrab ka testiliigi
                testiliik = test.testiliik_kood

        # testiliikide valik, kuhu saab praegu regada
        opt_testiliigid = self._get_opt_testiliigid(testiliik)

        if not testiliik:
            # testiliik pole veel määratud, pakume välja vaikimisi testiliigi
            values = [r[0] for r in opt_testiliigid]
            if values:
                # vaikimisi pakume riigieksami
                preferred = [const.TESTILIIK_RIIGIEKSAM]
                opilane = self.c.opilane
                if opilane and opilane.klass == '9':
                    # 9. kl õpilastele pakume vaikimisi sisseastumiseksamit
                    preferred.insert(0, const.TESTILIIK_SISSE)
                # kui valikus on mõni eelistatud testiliik, siis kasutame seda
                for l in preferred:
                    if l in values:
                        testiliik = l
                        break
                if not testiliik:
                    # kui eelistatud liiki polnud valikus, siis võtame esimese valikus oleva liigi
                    testiliik = values[0]
        return testiliik, opt_testiliigid

    def _list_testivalik(self):
        c = self.c
        d = date.today()
        q = (model.Session.query(model.Testimiskord, model.Sooritaja)
             .join(model.Testimiskord.test)
             .filter(model.Test.eeltest_id==None)
             .filter(model.Test.avaldamistase==const.AVALIK_EKSAM)
             .filter(model.Test.staatus==const.T_STAATUS_KINNITATUD)
             .outerjoin((model.Sooritaja,
                         sa.and_(model.Sooritaja.testimiskord_id==model.Testimiskord.id,
                                 model.Sooritaja.kasutaja_id==c.kasutaja.id)))
             .filter(sa.or_(
                 # testimiskorrad, mille regamine on avatud või kuhu olen juba regatud
                 sa.and_(model.Testimiskord.reg_sooritaja==True,
                         model.Testimiskord.reg_sooritaja_alates<=d,
                         model.Testimiskord.reg_sooritaja_kuni>=d),
                 sa.and_(sa.or_(model.Testimiskord.kuni>=d,
                                model.Testimiskord.kuni==None),
                         model.Sooritaja.staatus<const.S_STAATUS_POOLELI)
                 ))
             )

        c.regpiirang = regpiirang
        if c.test_id:
            # URLis etteantud test, routing regamine_avaldus_testid_test
            q = q.filter(model.Testimiskord.test_id==c.test_id)
        if c.testiliik:
            if c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                q = q.filter(model.Test.testiliik_kood.in_((const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV)))
            else:
                q = q.filter(model.Test.testiliik_kood==c.testiliik)

        if c.testiliik == const.TESTILIIK_TASE:
            # tasemeeksami korral võib olla ajaline piirang,
            # millisest kuupäevast alates tohib uut eksamit teha
            dt_min, piirang = regpiirang.reg_te_piirang(self, c.kasutaja.id)            
            if dt_min:
                # isikul on ajaline piirang
                q = q.filter(model.Testimiskord.alates>=dt_min)
            # kui yle 65a isik registreerib B1 taseme tasemeeksamile,
            # siis ta võib saada kirjutamisest vabastuse
            vanus = c.kasutaja.vanus
            if vanus and vanus >= 65 and c.kasutaja.kodakond_kood != const.RIIK_EST:
                c.voib_vabastada_k = True

            items = q.order_by(model.Test.nimi).all()                    
            # kas olen mõnele regatud?
            olemas = [j for (tk, j) in items if j]
            if not olemas:
                # mitmele tasemeeksamile ei või korraga regada
                piirang = regpiirang.reg_te_piirang1(self, c.kasutaja.id)
                if piirang:
                    self.error(piirang)
                    return

        elif c.testiliik == const.TESTILIIK_SEADUS:
            # mitmele seaduse tundmise eksamile ei või korraga regada
            items = q.order_by(model.Test.nimi).all()
            # kas olen mõnele regatud?
            olemas = [j for (tk, j) in items if j]
            if not olemas:
                piirang = regpiirang.reg_se_piirang1(self, c.kasutaja.id)
                if piirang:
                    self.error(piirang)
                    return

        elif c.testiliik in (const.TESTILIIK_RV, const.TESTILIIK_RIIGIEKSAM):
            # CAE testile saab regada ainult 11. või 12. kl õpilasi, kellel on CAE eeltest sooritatud
            not_cae = regpiirang.err_rv_cae(self, c.kasutaja, c.opilane)
            if not_cae:
                # CAE testid jäävad välja
                q = q.filter(sa.or_(model.Testimiskord.cae_eeltest==False,
                                    model.Testimiskord.cae_eeltest==None))
            items = q.order_by(model.Test.nimi).all()                                    

        elif c.testiliik == const.TESTILIIK_KOOLITUS:
            ained = c.kasutaja.get_opetaja_ained()
            if not ained:
                self.error(_("Koolitusele saavad registreeruda ainult selle õppeaine õpetajad!"))
                q = q.filter(model.Test.id==0)
            else:
                f_aine = model.Test.aine_kood.in_(ained)
                # eesti keel teise keelena eksamile saavad ka eesti keele õpetajad
                if const.AINE_ET in ained:
                    f_aine = sa.or_(f_aine, model.Test.aine_kood==const.AINE_ET2)
                q = q.filter(f_aine)
            items = q.order_by(model.Test.nimi).all()
        else:
            items = q.order_by(model.Test.nimi).all()                    
        return items

    def _create(self):
        """Testidele registreerimine
        """
        cnt = 0
        self.c.testiliik = self.request.matchdict.get('testiliik')
        params = self.request.params
        errors = {}
        today = date.today()
        regatud_ained = [r.test.aine_kood for r in self.c.kasutaja.get_reg_sooritajad(self.c.testiliik)]
        # valitud testimiskorrad
        korrad_id = list(params.getall('valik_id'))
        korrad = [model.Testimiskord.get(kord_id) for kord_id in korrad_id]
        for kord in korrad:
            kord_id = kord.id
            suffix = f'_{kord_id}'

            test = kord.test
            if self.c.testiliik == const.TESTILIIK_KOOLITUS:
                ained = self.c.kasutaja.get_opetaja_ained()
                if test.aine_kood not in ained and \
                  not ((test.aine_kood == const.AINE_ET2) and (const.AINE_ET in ained)):
                    self.error(_("Koolitusele saavad registreeruda ainult selle õppeaine õpetajad!"))
                    continue
                
            regatud_ained.append(test.aine_kood)
            sooritaja = self._get_sooritaja(kord)
            if sooritaja:
                # juba on registreeritud
                errors2 = save_reg(self, sooritaja, suffix)
            else:
                # lisame registreeringu
                rc, errors2 = self._append_sooritaja(kord, korrad, suffix)
                
            if errors2:
                errors.update(errors2)
                
        if self.c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            if const.AINE_ET in regatud_ained and const.AINE_ET2 in regatud_ained:
                error = _("Korraga ei või registreerida nii eesti keele riigieksamile kui ka eesti keele teise keelena riigieksamile")
                self.error(error)

        if self.has_errors() or errors:
            raise ValidationError(self, errors)

    def _get_sooritaja(self, kord):
        "Leitakse olemasolev registreering"
        q  = (model.Session.query(model.Sooritaja)
              .filter_by(kasutaja_id=self.c.kasutaja.id)
              .filter_by(test_id=kord.test_id)
              .filter_by(testimiskord_id=kord.id)
              .filter(model.Sooritaja.staatus > const.S_STAATUS_TYHISTATUD))
        return q.first()

    def _append_sooritaja(self, kord, testimiskorrad, suffix):
        c = self.c
        errors = {}
        err = None
        kasutaja = c.kasutaja
        test_id = kord.test_id
        test = kord.test
        esitaja_kasutaja_id = c.user.id
        esitaja_koht_id = c.user.koht_id or None

        params = self.request.params
        lang = params.get('lang' + suffix)
        piirkond_id = params.get('piirkond_id' + suffix)
        kohtaeg = params.get('kohtaeg' + suffix)
        vvkohad_id = params.getall('vvk' + suffix)
        vvk_oma = params.get('vvk_oma' + suffix)
        kursus = params.get('kursus' + suffix)
        vabastet = params.get('vabastet' + suffix)
        reg_markus = params.get('reg_markus' + suffix)
        soovib = bool(params.get('soovib_konsultatsiooni' + suffix))
        if kord.reg_kohavalik and not kohtaeg:
            errors['kohtaeg' + suffix] = _("Palun valida soorituskoht!")
            return False, errors
        if kord.reg_kohavalik and kord.regkohad and not vvkohad_id:
            errors['vvk' + suffix] = _("Palun valida õppeasutused, millele avaldatakse testitulemused")
            return False, errors
    
        piirkond_id = piirkond_id and int(piirkond_id) or None
        nimekiri = None
        opilane = c.opilane
        if opilane and not opilane.on_lopetanud:
            koht_id = opilane.koht_id
            if koht_id:
                # paneme kooli nimekirja, et kool saaks registreerimist vaadata
                nimekiri = model.Nimekiri.give_nimekiri(koht_id, test, kord.id)

        # ei ole veel regatud, kontrollime, kas saab regada
        d = date.today()

        if not (kord.reg_sooritaja and \
                kord.reg_sooritaja_alates <= d <= kord.reg_sooritaja_kuni):
            err = _('Testile {s} ei saa registreerida').format(s=kord.test.nimi)

        elif not test.staatus == const.T_STAATUS_KINNITATUD:
            err = _('Test {s} pole kinnitatud').format(s=test.nimi)
            
        if not test.avaldamistase==const.AVALIK_EKSAM:
            err = _('Test {s} pole testimiskorraga test').format(s=test.nimi)

        testiliik = test.testiliik_kood
        if not err and testiliik == const.TESTILIIK_RV:
            # EH-301. õpilane ise ei tohi end saada registreerida:
            # - korraga yhe võõrkeele erineva tasemega rv eksamitele
            # - korraga vene ja saksa keele rv eksamitele
            err = regpiirang.reg_ise_rv(self, kasutaja.id, test, kord)
            if not err and kord.cae_eeltest:
                err = ehis.uuenda_opilased(self, [kasutaja.isikukood])
                if not err:
                    # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                    err = regpiirang.reg_rven_cae(self, kasutaja.id, test, testimiskorrad)                
                if not err:
                    err = regpiirang.reg_rv_cae(self, kasutaja.id, test, kord)
                   
        elif not err and testiliik == const.TESTILIIK_RIIGIEKSAM:
            err = regpiirang.reg_r_lisaeksam(self, kasutaja.id, test, kord)
            if not err and test.aine_kood == const.AINE_EN:
                # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                err = regpiirang.reg_rven_cae(self, kasutaja.id, test, testimiskorrad)
                
        elif not err and testiliik == const.TESTILIIK_SISSE:
            err = regpiirang.reg_sisse(self, kasutaja, test)

        elif not err and testiliik == const.TESTILIIK_TASE:
            err = regpiirang.reg_te_piirang1(self, kasutaja.id)
            
        elif not err and testiliik == const.TESTILIIK_SEADUS:
            err = regpiirang.reg_se_piirang1(self, kasutaja.id)
            
        if not err and test.aine_kood == const.AINE_ET2:
            err = regpiirang.reg_et2(self, kasutaja, test, opilane)

        if not err and kord.reg_piirang == const.REGPIIRANG_H:
            # testimiskord, millele registreerimisel on vajalik pärida EHISest haridustöötaja andmed
            err = ehis.uuenda_isikukaart(self, kasutaja)
            
        if err:
            errors['err' + suffix] = err
            return False, errors

        varemlopetanu = not opilane or opilane.on_lopetanud
        if testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS) \
           or testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV) and varemlopetanu:
            if not piirkond_id:
                err = _('Palun valida piirkond')
                errors['piirkond_id' + suffix] = err
                return False, errors
        
        added, sooritaja = model.Sooritaja.registreeri(kasutaja, 
                                                       test_id, 
                                                       kord, 
                                                       lang, 
                                                       piirkond_id, 
                                                       const.REGVIIS_SOORITAJA,
                                                       esitaja_kasutaja_id, 
                                                       esitaja_koht_id,
                                                       nimekiri=nimekiri)
        if sooritaja:
            if kord.reg_piirang == const.REGPIIRANG_H:
                # salvestame registreeringu juurde kehtiva isikukaardi viite
                sooritaja.isikukaart_id = kasutaja.isikukaart_id
            
            sooritaja.kursus_kood = kursus
            sooritaja.reg_markus = reg_markus
            sooritaja.soovib_konsultatsiooni = soovib
            
            # salvestame koolid, kes võivad tulemusi vaadata
            save_vvkohad(sooritaja, vvkohad_id, vvk_oma, opilane)

            if kord.reg_kohavalik:
                # kui regamisel valitakse esimese testiosa soorituskoht ja aeg
                if not suuna_kohtaeg(self, sooritaja, kohtaeg):
                    return False, errors
                
        # kui muudetakse juba kinnitatud registreeringut, siis seatakse vabastus ja erivajaduste olemasolu;
        # kui lisatakse uus registreering, siis siin seda ei tehta, tehakse kinnitamisel
        vanus = kasutaja.vanus
        sooritaja.set_vabastet(vabastet and vanus and vanus >= 65)
        return True, errors
    
    def _after_create(self, id):
        return HTTPFound(location=self.url('regamine_avaldus_isikuandmed', testiliik=self.c.testiliik))

    def _error_create(self):
        extra_info = self._index_d()
        if isinstance(extra_info, (HTTPFound, Response)):
            return extra_info
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=extra_info)
        return Response(html)
        
    def delete(self):
        testimiskord_id = self.request.matchdict.get('id')
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        rcd = model.Sooritaja.get(sooritaja_id)
        if rcd and not rcd.voib_reg():
            self.error(_("Registreerimine on lõpetatud, enam ei saa tühistada"))
        elif rcd:
            assert rcd.kasutaja_id == self.c.kasutaja.id, 'Vale kasutaja'
            testiliik = rcd.test.testiliik_kood
            staatus = rcd.staatus
            if staatus >= const.S_STAATUS_POOLELI:
                self.error(_("Sooritamist on alustatud, ei saa enam tühistada"))
            else:
                rcd.logi_pohjus = self.request.params.get('pohjus')
                kt.send_tyhteade(self, rcd.kasutaja, rcd)            
                rcd.tyhista()
                if staatus == const.S_STAATUS_REGAMATA:
                    model.Session.flush()
                    rcd.delete()
                model.Session.commit()
        self.c.testimiskord = model.Testimiskord.get(testimiskord_id)
        self.c.testiliik = self.request.matchdict.get('testiliik') or self.c.testimiskord.test.testiliik_kood
        self.c.regpiirang = regpiirang
        self.c.is_edit = True
        template = '/avalik/regamine/avaldus.test.mako'
        return self.render_to_response(template)

    def __before__(self):
        self.c.kasutaja = self.c.user.get_kasutaja()
        if self.c.kasutaja:
            self.c.opilane = self.c.kasutaja.opilane
        
def save_reg(handler, sooritaja, suffix=''):
    "Olemasoleva registreeringu andmete muutmine (avalduses või regamise vaatamiselt)"
    errors = {}
    params = handler.request.params
    kord = sooritaja.testimiskord
    testiliik = sooritaja.test.testiliik_kood

    piirkond_id = params.get('piirkond_id' + suffix)
    vvkohad_id = params.getall('vvk' + suffix)
    vvk_oma = params.get('vvk_oma' + suffix)

    if kord and kord.reg_kohavalik and kord.regkohad:
        if not vvkohad_id:
            errors['vvk'+suffix] = _("Palun valida õppeasutused, millele avaldatakse testitulemused")
        else:
            # salvestame koolid, kes võivad tulemusi vaadata
            opilane = sooritaja.kasutaja.opilane
            save_vvkohad(sooritaja, vvkohad_id, vvk_oma, opilane)
            # kui kool juba on valitud, siis piirkonda ei salvesta
            piirkond_id = None
            
    if not sooritaja.voib_reg():
        # muid andmeid saab muuta ainult siis, kui regamine on avatud
        return errors

    sooritaja.kursus_kood = params.get('kursus' + suffix)
    sooritaja.reg_markus = params.get('reg_markus' + suffix)
    sooritaja.soovib_konsultatsiooni = bool(params.get('soovib_konsultatsiooni' + suffix))
    lang = params.get('lang' + suffix)

    if lang:
        sooritaja.lang = lang
    if piirkond_id:
        sooritaja.piirkond_id = int(piirkond_id)

    kohtaeg = params.get('kohtaeg' + suffix)
    if kord and kord.reg_kohavalik:
        # kui regamisel valitakse esimese testiosa soorituskoht ja aeg
        if not kohtaeg:
            errors['kohtaeg'+suffix] = _("Palun valida soorituskoht")
        elif not suuna_kohtaeg(handler, sooritaja, kohtaeg):
            errors['kohtaeg'+suffix] = _("Viga")

    if not kord or not kord.reg_kohavalik and not piirkond_id:
        if testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS) \
        or testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV) \
        and not sooritaja.kool_koht_id:
            errors['piirkond_id' + suffix] = 'Palun valida piirkond'

    vabastet = params.get('vabastet' + suffix)            
    sooritaja.set_vabastet(vabastet and True or False)
    return errors
    
def suuna_kohtaeg(handler, sooritaja, kohtaeg):
    "Kui regamisel valitakse esimese testiosa soorituskoht ja aeg"
    rc = False
    error = None
    if sooritaja.staatus > const.S_STAATUS_ALUSTAMATA:
        log.error(f'sooritaja staatus {sooritaja.staatus}')
        return False
    testikoht_id, algus = regpiirang.parse_kohtaeg(kohtaeg)
    if testikoht_id and algus:
        testikoht = model.Testikoht.get(testikoht_id)
        tos = None
        # leitakse esimene soorituskoht
        for tos1 in sooritaja.sooritused:
            # igaks juhuks kontrollime, et on õige toimumisaeg
            try:
                ta_id = tos1.toimumisaeg_id or tos1.toimumisaeg.id
            except:
                ta_id = None
            if ta_id == testikoht.toimumisaeg_id:
                # valitakse ainult esimese testiosa koht
                tos = tos1
                break

        if not tos:
            error = _("Ei saa soorituskohta suunata")
        else:
            old_testikoht = tos.testikoht
            old_testiruum = tos.testiruum
            if old_testikoht and old_testikoht.id == testikoht_id \
              and old_testiruum and old_testiruum.algus == algus:
                # juba õiges kohas
                return True
            else:
                # suuname teise kohta
                # leiame testiruumi, millel on sobiv algus ja kus on kohti
                testiruum = None
                for tr in testikoht.testiruumid:
                    if tr.algus == algus:
                        if tr.kohti is not None:
                            vabu = tr.kohti - tr.bron_arv
                            if vabu <= 0:
                                continue
                        testiruum = tr
                        break
                if not testiruum:
                    error = _("Valitud kellaajal ei ole selles soorituskohas enam vabu kohti")
                    rc = False
                else:
                    # suuname sooritaja testiruumi
                    rc, error = tos.suuna(testikoht, testiruum, err=True)
                    if rc:
                        model.Session.flush()
                        testiruum.set_sooritajate_arv()
                        if old_testiruum:
                            old_testiruum.set_sooritajate_arv()
                        if sooritaja.staatus in (const.S_STAATUS_REGATUD, const.S_STAATUS_ALUSTAMATA):
                            # kui juba regatud sooritaja kohta muudetakse, siis saadetakse teade
                            test = sooritaja.test
                            kasutaja = sooritaja.kasutaja
                            kt.send_regteade(handler, kasutaja, test.testiliik_kood, False, True)
    if error:
        handler.error(error)
                
    return rc

def save_vvkohad(sooritaja, vvkohad_id, vvk_oma, opilane, reg_kool_id=None):
    # salvestame koolid, kes võivad tulemusi vaadata
    vvkohad_id = [int(k_id) for k_id in vvkohad_id or []]
    kndkohad = [{'koht_id': k_id, 'automaatne': False} for k_id in vvkohad_id]

    # kui oma kool pole valitud, siis lisame automaatseks valikuks, kui on linnutatud vvk_oma
    omakoht_id = vvk_oma and opilane and opilane.koht_id
    if omakoht_id and omakoht_id not in vvkohad_id:
        # oma kool pole valitud
        testimiskord_id = sooritaja.testimiskord_id
        q = (model.Session.query(model.Testikoht.koht_id)
             .join(model.Testikoht.toimumisaeg)
             .filter(model.Toimumisaeg.testimiskord_id==testimiskord_id)
             .filter(model.Testikoht.koht_id==omakoht_id))
        if q.count() > 0:
            # oma kool on selle testi soorituskohtade seas
            # ja võib saada õpilase tulemusi näha
            r = {'koht_id': omakoht_id,
                 'automaatne': True}
            kndkohad.append(r)

    class VVKGridController(BaseGridController):
        def can_delete(self, rcd):
            # kui regab sooritaja ise, siis saab kõiki valikuid muuta
            # kui regab kool, siis saab ainult sellele koolile näitamist muuta
            return not reg_kool_id or rcd.koht_id == reg_kool_id

    VVKGridController(sooritaja.kandideerimiskohad,
                      model.Kandideerimiskoht,
                      pkey='koht_id').\
            save(kndkohad)
    
