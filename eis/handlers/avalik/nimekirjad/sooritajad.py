from cgi import FieldStorage
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import ehis
from eis.lib.xtee import set_rr_pohiandmed
import eis.handlers.ekk.otsingud.kohateated as kt
import eis.lib.regpiirang as regpiirang
log = logging.getLogger(__name__)

class SooritajadController(BaseResourceController):
    """Testimiskorra sooritajate nimekirja kuvamine
    ja sinna sooritajate lisamine
    """
    _permission = 'nimekirjad'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'avalik/nimekirjad/nimekiri.mako'
    _LIST_TEMPLATE = 'avalik/nimekirjad/sooritajad_list.mako'
    _SEARCH_FORM = forms.avalik.testid.SooritajaFilterForm 
    _DEFAULT_SORT = 'sooritaja.id' # vaikimisi sortimine

    def _query(self):
        q = (model.Sooritaja.query
             .filter_by(testimiskord_id=self.c.testimiskord_id)
             .filter_by(kool_koht_id=self.c.user.koht_id))
        return q

    def _create(self):            
        """Isiku lisamine sooritajaks
        Parameetrites on olemas isikukoodid ja nimed
        Kasutaja on isiku leidnud kas otsides isikukoodi järgi
        või küsides EHISest klassi järgi.
        """
        self.c.keel = self.request.params.get('keel') or self.c.test.lang
        kursus = self.request.params.get('kursus')
        # EHISe nimekirjaga laadimine
        opilased_id = self.request.params.getall('oid')
        # yhe isikukoodiga laadimine
        userid = self.request.params.get('ik')
        if userid:
            usp = eis.forms.validators.IsikukoodP(userid)
            li_ik = [usp.isikukood]
        else:
            li_ik = None
        self._registreeri_sooritajad(opilased_id, li_ik, kursus)
        return self.c.testimiskord

    def _create_fail(self):            
        """Failist isikute lisamine sooritajaks
        Failis on ainult isikukoodid, tuleb küsida Rahvastikuregistrist nimed ka
        """
        self.c.keel = self.request.params.get('keel') or self.c.test.lang
        kursus = self.request.params.get('kursus')
        value = self.request.params.get('ik_fail')

        koht = self.c.user.koht
        err = True
        if isinstance(value, FieldStorage):
            # value on FieldStorage objekt
            err = False
            filename = value.filename
            value = value.value
            settings = self.request.registry.settings
            csv_data = int(settings.get('csv.data',0))

            # faili sisuks on lahendajate isikukoodid eraldatuna reavahetustega
          
            # failis on iga sooritaja jaoks üks rida
            # reas võib olla mitu veergu, eraldatuna semikooloniga
            # esimeses veerus on isikukood
            # teised veerud võivad puududa või olla: eesnimi, perekonnanimi, klass, paralleel
            li_ik = []
            for line in value.splitlines():
                line = line.strip()
                if line:
                    line = utils.guess_decode(line)
                    li = [s.strip() for s in line.split(';')]
                    userid = li[0]
                    usp = eis.forms.validators.IsikukoodP(userid)
                    if not usp.isikukood:
                        if filename.rsplit('.',1)[-1] in ('xlsx','xls'):
                            self.error(_("Palun kasutada CSV formaadis faili"))
                        else:
                            self.error(_("Vigane isikukood"))
                        err = True
                        break

                    li_ik.append(usp.isikukood)
                    if csv_data and koht and len(li) >= 4:
                        # testsüsteemis - kontrollime kohe, kas on 
                        # kasutaja olemas ja kui pole, siis lisame
                        self._load_opilane(li, koht)

        if not err:
            self._registreeri_sooritajad(None, li_ik, kursus)
            model.Session.commit()

        return self._after_update(self.c.testimiskord_id)

    def _registreeri_sooritajad(self, opilased_id, li_ik, kursus):
        # registreerime õpilase testile
        c = self.c
        cnt_olemas = 0
        puuduvad_isikukoodid = []
        pole_meie_opilane = []
        pole_inimene = []
        if not opilased_id and not li_ik:
            self.error(_("Palun valida õpilased, keda registreerida!"))
            return
        if li_ik and self.request.is_ext():
            # uuendame õpilaste andmed, et hiljem kontrollida õppimise piirangut
            isikukoodid = [ik for ik in li_ik if not re.match(r'[A-Z]{2}', ik)]
            err = ehis.uuenda_opilased(self, isikukoodid)
            if err:
                self.error(err)
                return

        errors = []
        for value in opilased_id or li_ik:
            if opilased_id:
                opilane = model.Opilane.get(value)
                isikukood = opilane.isikukood
            else:
                isikukood = value
                opilane = model.Opilane.get_by_ik(value)
            if not opilane or opilane.koht_id != c.user.koht_id or opilane.on_lopetanud:
                if not c.testimiskord.reg_voorad:
                    # kool ei või võõraid regada
                    pole_meie_opilane.append(value)
                    continue
            if opilane:
                kasutaja = opilane.give_kasutaja()
            else:
                kasutaja = model.Kasutaja.get_by_ik(isikukood)
                if not kasutaja:
                    kasutaja = set_rr_pohiandmed(self, None, isikukood)
                else:
                    model.Session.flush()
            if not kasutaja:
                pole_inimene.append(isikukood)
                continue
            
            err = None
            testiliik = c.test.testiliik_kood
            if testiliik == const.TESTILIIK_RIIGIEKSAM:
                if opilane.klass in ('7','8','9') and c.test.aine_kood != const.AINE_ET2:
                    # ES-1174 blokeerida 7.-9. kl õpilaste riigieksamitele regamine
                    err = _("{s}. klassi õpilasi ei või riigieksamile registreerida").format(s=opilane.klass)
                else:
                    err = regpiirang.reg_r_lisaeksam(self, kasutaja.id, c.test, c.testimiskord)
                if not err and c.test.aine_kood == const.AINE_EN:
                    # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                    err = regpiirang.reg_rven_cae(self, kasutaja.id, c.test, [c.testimiskord])

            elif testiliik == const.TESTILIIK_RV:
                if c.testimiskord.cae_eeltest:
                    # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                    err = regpiirang.reg_rven_cae(self, kasutaja.id, c.test, [c.testimiskord])
                    if not err:
                        err = regpiirang.reg_rv_cae(self, kasutaja.id, c.test, c.testimiskord)
            if not err and c.test.aine_kood == const.AINE_ET2:
                err = regpiirang.reg_et2(self, kasutaja, c.test, opilane)

            if err:
                if err not in errors:
                    self.error(err)
                errors.append(err)
                continue

            if not self._append_sooritaja(kasutaja, c.keel, kursus):
                cnt_olemas += 1

        if len(pole_meie_opilane):
            buf = ', '.join(pole_meie_opilane)
            if len(pole_meie_opilane) == 1:
                self.error(_("{s} ei ole meie kooli õpilane").format(s=buf))
            else:
                self.error(_("{s} ei ole meie kooli õpilased").format(s=buf))

        if len(pole_inimene):
            buf = ', '.join(pole_inimene)
            self.error(_("Ei leitud isikut {s}").format(s=buf))
                
        if cnt_olemas:
            if cnt_olemas == 1:
                self.notice(_("Registreering oli juba olemas"))
            else:
                self.notice(_("{n} registreeringut oli juba olemas").format(n=cnt_olemas))

    def _load_opilane(self, li, koht):
        """Testkeskonnas laadimise lihtsustamiseks lubame failist laadida ka nimesid ja klasse,
        kuna test-RR-ist ega test-EHISest neid ei saa
        """
        isikukood = li[0]
        eesnimi = li[1]
        perenimi = li[2]
        klass = li[3]
        paralleel = len(li) > 4 and li[4] or None

        opilane = model.Opilane.get_by_ik(isikukood)

        if not opilane:
            isikukood = validators.IsikukoodP(isikukood).isikukood
            if not isikukood:
                self.error(_("Vigane isikukood {s}").format(s=isikukood))
                return
        
        if not eesnimi or not perenimi or not klass:
            # pole andmeid
            return
        
        lubatud_klassid = [k[0] for k in const.EHIS_KLASS]
        if klass not in lubatud_klassid:
            self.error(_("Vigane klass {s1} (lubatud on: {s2})").format(s1=klass, s2=','.join(lubatud_klassid)))
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
                            seisuga=datetime(2020,1,1))
        rcd.kasutaja = model.Kasutaja.get_by_ik(isikukood)
        rcd.flush()
        
    def _append_sooritaja(self, kasutaja, lang, kursus):
        """Lisatakse sooritaja või muudetakse olemasolevat.
        """
        piirkond_id = None
        esitaja_kasutaja_id=self.c.user.id
        esitaja_koht_id=self.c.user.koht_id or None
        testimiskord = self.c.testimiskord
        test = self.c.test
        if not testimiskord:
            if test.testityyp == const.TESTITYYP_EKK and test.eeltest_id:
                # Innove tehtud eeltest, mis on määratud pedagoogidele proovimiseks
                # vajame testimiskorda, et saaks EKK vaates statistikat arvutada
                testimiskord = test.get_testimiskord()
            
        added, sooritaja = model.Sooritaja.registreeri(kasutaja, 
                                                       self.c.test.id, 
                                                       testimiskord, 
                                                       lang, 
                                                       piirkond_id, 
                                                       const.REGVIIS_KOOL_EIS,
                                                       esitaja_kasutaja_id, 
                                                       esitaja_koht_id,
                                                       kinnitatud=True)
        if sooritaja:
            sooritaja.kursus_kood = kursus
        if testimiskord and test.testiliik_kood != const.TESTILIIK_EELTEST:
            if self.request.is_ext():
                kt.send_regteade(self, kasutaja, test.testiliik_kood)
            
        return added

    def _delete(self, item):
        staatus = item.staatus
        if staatus <= const.S_STAATUS_ALUSTAMATA:
            item.logi_pohjus = self.request.params.get('pohjus')            
            kt.send_tyhteade(self, item.kasutaja, item)
            item.tyhista()
            if staatus == const.S_STAATUS_REGAMATA:
                model.Session.flush()
                item.delete()
            model.Session.commit()
            self.success(_("Registreering on tühistatud!"))
        else:
            self.error(_('Sooritajat ei saa eemaldada, kuna ta on juba alustanud sooritamist'))

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('nimekirjad_testimiskord_korrasooritajad', testimiskord_id=self.c.testimiskord.id))

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        if not self.has_errors():
            self.success()
        return HTTPFound(location=self.url('nimekirjad_testimiskord_korrasooritajad', testimiskord_id=self.c.testimiskord.id))

    def __before__(self):
        """Väärtustame testimiskorra id
        """
        c = self.c
        c.testimiskord_id = int(self.request.matchdict.get('testimiskord_id'))
        self.c.testimiskord = model.Testimiskord.get(c.testimiskord_id)
        self.c.test = self.c.testimiskord.test

    def _perm_params(self):
        # testi vaatamise õigus, et igaüks saaks oma teste suunata
        # õppealajuhatajatel peab olema neile suunata lubatud testidele see õigus
        return {'obj':self.c.testimiskord}
