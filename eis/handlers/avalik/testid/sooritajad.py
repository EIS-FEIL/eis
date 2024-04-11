from cgi import FieldStorage
from eis.lib.baseresource import *
from eis.lib.xtee import ehis
from eis.handlers.ekk.otsingud.kohateated import send_regteade
from eis.handlers.avalik.testid.testinimekirjad import send_nimekirjateade
_ = i18n._
log = logging.getLogger(__name__)

class SooritajadController(BaseResourceController):
    """Testimiskorrata testi sooritajate nimekirja kuvamine
    ja sinna sooritajate lisamine
    """
    _permission = 'omanimekirjad'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'avalik/testid/nimekiri.mako'
    _LIST_TEMPLATE = 'avalik/testid/sooritajad_list.mako'
    _SEARCH_FORM = forms.avalik.testid.SooritajaFilterForm 
    _DEFAULT_SORT = 'sooritaja.id' # vaikimisi sortimine
    _actions = 'index,create,delete' # võimalikud tegevused
    
    def _query(self):
        c = self.c
        if c.nimekiri_id == 0:
            raise HTTPFound(location=self.url('test_nimekirjad', test_id=c.test_id, testiruum_id=c.testiruum_id))
        q = model.Sooritaja.query.filter_by(nimekiri_id=c.nimekiri_id)
        return q

    def _give_nimekiri(self):
        "Luuakse uus nimekiri (kui kasutajal veel ei ole oma nimekirja)"
        c = self.c
        c.item = model.Nimekiri.lisa_nimekiri(c.user, 
                                              const.REGVIIS_KOOL_EIS,
                                              c.test)
        if c.test.testiliik_kood == const.TESTILIIK_TKY:
            # taustakysitluse õpetaja osa suunata õpetajale
            kasutaja = c.user.get_kasutaja()
            model.Sooritaja.reg_tky_opetaja(kasutaja, c.test, c.item)

        model.Session.flush()
        c.nimekiri = c.item
        c.nimekiri_id = c.item.id
            
    def _create(self):            
        """Isiku lisamine sooritajaks
        Parameetrites on olemas isikukoodid ja nimed
        Kasutaja on isiku leidnud kas otsides isikukoodi järgi
        või küsides EHISest klassi järgi.
        """
        c = self.c
        uus_nimekiri = False
        if not c.nimekiri:
            # kasutaja pole veel nimekirja loonud
            self._give_nimekiri()
            uus_nimekiri = True
            
        params = self.request.params
        c.keel = params.get('keel') or c.test.lang
        kursus = params.get('kursus')
        vanem_nous = params.get('vanem_nous') and True or None
        isikukoodid = params.getall('oigus') # EHISest õpilaste valimisel
        kasutajad_id = params.getall('k_id') # ryhmast õpilaste valimisel
        if c.nimekiri.esitaja_koht_id != c.user.koht_id:
            self.error(_("Nimekiri on loodud teise õppeasutuse jaoks"))
            return c.nimekiri
        truumid = self._get_truumid()

        cnt_olemas = 0
        for ik in isikukoodid:
            kasutaja = self._give_kasutaja(ik)
            if kasutaja:
                if not self._append_sooritaja(kasutaja, c.keel, truumid, kursus, vanem_nous):
                    cnt_olemas += 1
        for k_id in kasutajad_id:
            kasutaja = model.Kasutaja.get(k_id)
            if kasutaja:
                if not self._append_sooritaja(kasutaja, c.keel, truumid, kursus, vanem_nous):
                    cnt_olemas += 1                

        if cnt_olemas:
            if len(isikukoodid) == 1:
                self.notice(_('Registreering oli juba olemas'))
            else:
                self.notice(_('{d} registreeringut oli juba olemas').format(d=cnt_olemas))

        model.Session.commit()
        if uus_nimekiri:
            send_nimekirjateade(self, c.nimekiri, c.test)        
        return c.nimekiri

    def _create_fail(self):            
        """Failist isikute lisamine sooritajaks
        Failis on ainult isikukoodid, tuleb küsida Rahvastikuregistrist nimed ka
        """
        
        def _read_file(value, stru):
            # failist andmeväljade lugemine
            # value on FieldStorage objekt
            err = data = None
            fbuf = isinstance(value, FieldStorage) and value.value or None
            if fbuf and b'\x00' in fbuf:
                # vist Excel
                err = _('Fail on vales vormingus. Laadida saab CSV failist.')
                fbuf = None
            if fbuf:
                # failis on iga sooritaja jaoks üks rida
                # reas võib olla mitu veergu, eraldatuna semikooloniga
                # esimeses veerus on isikukood
                # teised veerud võivad puududa või olla: eesnimi, perekonnanimi, klass, paralleel
                data = []
                n_cols = len(stru) + 1
                for ind, line in enumerate(fbuf.splitlines()):
                    line = utils.guess_decode(line)
                    if not line.strip():
                        continue
                    li = [s.strip() for s in line.split(';')]
                    if len(li) < n_cols:
                        err = _("Faili igal real peab olema {n} välja (viga real {i})").format(n=n_cols, i=ind+1)
                        break
                    userid = li[0]
                    usp = eis.forms.validators.IsikukoodP(userid)
                    if not usp.isikukood:
                        err = _("Isikukood puudub (viga real {i})").format(i=ind+1)
                        break
                    data.append((usp.isikukood, li))
            if not data and not err:
                err = _("Faili sisu puudub")
            return err, data

        def _add_testdata(data, stru):
            try:
                # nime välja indeks
                ind_nimi = stru.index('en') + 1
            except:
                # nime pole failis
                return
            settings = self.request.registry.settings
            csv_data = int(settings.get('csv.data',0))
            if csv_data:
                koht = self.c.user.koht
                if koht:
                    for li in data:
                        self._load_opilane(li, koht, ind_nimi)

        def _register(data, stru, params):
            truumid = self._get_truumid()
            keel = self.c.keel = params.get('keel') or self.c.test.lang
            kursus = params.get('kursus')
            vanem_nous = params.get('vanem_nous') and True or None
            
            # keele veeru jrk failis
            try:
                ind_lang = stru.index('lang') + 1
            except:
                ind_lang = -1
            # võimalikud keeled
            opt_keeled = c.testimiskord and c.testimiskord.opt_keeled or c.test.opt_keeled
            keeled = [r[0] for r in opt_keeled]
                
            # registreerime õpilase testile
            cnt_olemas = 0
            puuduvad_isikukoodid = []
            for ind, li in enumerate(data):
                isikukood, li = li
                kasutaja = self._give_kasutaja(isikukood)
                if not kasutaja:
                    puuduvad_isikukoodid.append(isikukood)
                if kasutaja:
                    if ind_lang > -1:
                        keel = li[ind_lang]
                    if keel not in keeled:
                        self.error(_("Vale keele kood (viga real {i})").format(i=ind+1))
                        return
                    if not self._append_sooritaja(kasutaja, keel, truumid, kursus, vanem_nous):
                        cnt_olemas += 1

            # teatame isikukoodidest, millele vastavaid õpilasi ei leitud
            if len(puuduvad_isikukoodid):
                buf = ', '.join(puuduvad_isikukoodid)
                if len(puuduvad_isikukoodid) == 1:
                    self.error(_('Isikukoodiga {s} õpilast ei leitud!').format(s=buf))
                else:
                    self.error(_('Isikukoodidega {s} õpilasi ei leitud!').format(s=buf))

            if cnt_olemas:
                self.notice(_('{d} registreeringut oli juba olemas').format(d=cnt_olemas))

            model.Session.commit()
                    
        params = self.request.params
        err = None
        c = self.c
        uus_nimekiri = False
        if not c.nimekiri:
            # kasutaja pole veel nimekirja loonud
            self._give_nimekiri()
            uus_nimekiri = True
            
        if c.nimekiri.esitaja_koht_id != c.user.koht_id:
            self.error(_("Nimekiri on loodud teise õppeasutuse jaoks"))
            return self._after_update(c.nimekiri_id)
        
        value = params.get('ik_fail')
        stru = params.getall('stru')

        # fail loetakse
        err, data = _read_file(value, stru)
        if err:
            self.error(err)
        elif data:
            # lisatakse uued kasutajad (testkeskkond ja ATS)
            _add_testdata(data, stru)

            # EHISe päring
            li_ik = [r[0] for r in data if r[0]]
            if li_ik:
                err = ehis.uuenda_opilased(self, li_ik)
                if err:
                    self.error(err)
            if not err:
                model.Session.commit()
                if uus_nimekiri:
                    send_nimekirjateade(self, c.nimekiri, c.test)
                _register(data, stru, params)

        if err and uus_nimekiri:
            # nimekirja varem polnud ja ei loodud ka, sest oli viga
            c.nimekiri_id = 0
        return self._after_update(c.nimekiri_id)

    def _load_opilane(self, li, koht, ind_nimi):
        """Testkeskonnas laadimise lihtsustamiseks lubame failist laadida ka nimesid ja klasse,
        kuna test-RR-ist ega test-EHISest neid ei saa
        """
        isikukood, li = li
        eesnimi = li[ind_nimi]
        perenimi = li[ind_nimi+1]
        klass = li[ind_nimi+2]
        paralleel = li[ind_nimi+3] or None

        opilane = None
        if isikukood:
            opilane = model.Opilane.get_by_ik(isikukood)
        
        if not eesnimi or not perenimi or not klass:
            # pole andmeid
            return
        
        lubatud_klassid = [k[0] for k in const.EHIS_KLASS]
        if klass not in lubatud_klassid:
            self.error(_('Vigane klass {s1} (lubatud on: {s2})').format(s1=klass, s2=','.join(lubatud_klassid)))
            return 

        if opilane:
            # õpilane on juba olemas
            opilane.eesnimi = eesnimi
            opilane.perenimi = perenimi
            opilane.klass = klass
            opilane.paralleel = paralleel
            opilane.koht = koht
            opilane.kool_id = koht.kool_id
            opilane.on_ehisest = False
            opilane.on_lopetanud = False
            return

        rcd = model.Opilane(isikukood=isikukood,
                            eesnimi=eesnimi,
                            perenimi=perenimi,
                            klass=klass,
                            paralleel=paralleel,
                            koht=koht,
                            kool_id=koht.kool_id,
                            on_ehisest=False,
                            on_lopetanud=False,
                            seisuga=date.today())
        if isikukood:
            rcd.kasutaja = model.Kasutaja.get_by_ik(isikukood)
        rcd.flush()
        
    def _get_truumid(self):
        truumid = {}
        if not self.c.testimiskord:
            # soorituskohaks on kasutaja koht
            koht_id = self.c.user.koht_id or const.KOHT_EKK
            for osa in self.c.test.testiosad:
                testikoht = model.Testikoht.give_testikoht(koht_id, osa.id, None)
                testiruum = self.c.nimekiri.give_avalik_testiruum(testikoht)
                truumid[osa.id] = (testikoht, testiruum)
        return truumid

    def _give_kasutaja(self, isikukood):
        """Leitakse sooritaja kasutaja kirje
        """
        opilane = None
        kasutaja = model.Kasutaja.get_by_ik(isikukood)
        if not kasutaja:
            opilane = model.Opilane.get_by_ik(isikukood)
            if opilane:
                kasutaja = opilane.give_kasutaja()
            else:
                # uus isik
                kasutaja = xtee.set_rr_pohiandmed(self, None, isikukood)
            model.Session.flush()
        return kasutaja

    def _append_sooritaja(self, kasutaja, lang, truumid, kursus, vanem_nous):
        """Lisatakse sooritaja või muudetakse olemasolevat.
        """
        piirkond_id = None
        esitaja_kasutaja_id=self.c.user.id
        esitaja_koht_id=self.c.user.koht_id or None
        testimiskord = self.c.testimiskord
        test = self.c.test
        mittekorduv = True
        if not testimiskord:
            if test.testityyp == const.TESTITYYP_EKK and test.eeltest_id:
                # Innove tehtud eeltest, mis on määratud pedagoogidele proovimiseks
                # vajame testimiskorda, et saaks EKK vaates statistikat arvutada
                testimiskord = test.get_testimiskord()
            elif test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
                mittekorduv = False
        added, sooritaja = model.Sooritaja.registreeri(kasutaja, 
                                                       test.id, 
                                                       testimiskord, 
                                                       lang, 
                                                       piirkond_id, 
                                                       const.REGVIIS_KOOL_EIS,
                                                       esitaja_kasutaja_id, 
                                                       esitaja_koht_id,
                                                       nimekiri=self.c.nimekiri,
                                                       kinnitatud=True,
                                                       mittekorduv=mittekorduv)
        
        if sooritaja:
            sooritaja.kursus_kood = kursus
            sooritaja.vanem_nous = vanem_nous
            for sooritus in sooritaja.sooritused:
                osa_id = sooritus.testiosa_id
                tkoht, truum = truumid[osa_id]
                sooritus.suuna_korrata(tkoht, truum)
                truum.set_sooritajate_arv()
                
        if testimiskord and test.testiliik_kood != const.TESTILIIK_EELTEST:
            send_regteade(self, kasutaja, test.testiliik_kood)
            
        return added

    def _delete(self, item):
        if item.staatus in (const.S_STAATUS_TYHISTATUD,
                            const.S_STAATUS_REGAMATA,
                            const.S_STAATUS_TASUMATA,
                            const.S_STAATUS_REGATUD,
                            const.S_STAATUS_ALUSTAMATA,
                            const.S_STAATUS_EEMALDATUD,
                            const.S_STAATUS_PUUDUS):
            return BaseResourceController._delete(self, item)
        else:
            self.error(_('Sooritajat ei saa eemaldada, kuna ta on juba alustanud sooritamist'))

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_nimekiri', test_id=self.c.test.id, testiruum_id=self.c.testiruum_id, id=self.c.nimekiri_id))

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        if not self.has_errors():
            self.success()
        return HTTPFound(location=self.url('test_nimekiri', test_id=self.c.test.id, testiruum_id=self.c.testiruum_id, id=self.c.nimekiri_id))

    def __before__(self):
        """Väärtustame testimiskorra id
        """
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        c.nimekiri_id = int(self.request.matchdict.get('nimekiri_id'))
        if c.nimekiri_id != 0:
            c.item = c.nimekiri = model.Nimekiri.get(c.nimekiri_id)
        if not c.testiruum_id:
            tr = c.item and c.item.testiruum1
            c.testiruum_id = tr and tr.id or '0'
        BaseResourceController.__before__(self)

    def _perm_params(self):
        # testi vaatamise õigus, et igaüks saaks oma teste suunata
        # õppealajuhatajatel peab olema neile suunata lubatud testidele see õigus
        if self.c.nimekiri:
            return {'obj': self.c.nimekiri}
        else:
            # nimekirja veel pole loodud
            return {'obj': self.c.test}
