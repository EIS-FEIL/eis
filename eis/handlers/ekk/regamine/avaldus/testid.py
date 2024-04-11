from eis.lib.base import *
from eis.lib.basegrid import BaseGridController
import eis.handlers.ekk.otsingud.kohateated as kt
from .otsitestid import registreeri
_ = i18n._
log = logging.getLogger(__name__)

class TestidController(BaseController):
    _permission = 'regamine'
    _get_is_readonly = False
    
    def index(self):
        self._index_d()
        return self.render_to_response('ekk/regamine/avaldus.testid.mako')
        
    def _index_d(self):
        c = self.c
        c.testiliik = self.request.params.get('testiliik') or const.TESTILIIK_RIIGIEKSAM

        liigid = c.user.get_testiliigid(self._permission)
        if liigid and None not in liigid and c.testiliik not in liigid:
            c.testiliik = liigid[0]

        korrad_id = self.request.params.get('korrad_id')
        if korrad_id:
            # kui tuldi korraldusest, siis on testimiskord seal juba valitud
            for kord_id in korrad_id.split('-'):
                kord = model.Testimiskord.get(kord_id)
                if kord:
                    test = kord.test
                    testiliik = test.testiliik_kood
                    if not liigid or None in liigid or testiliik in liigid:
                        self.c.testiliik = testiliik
                        ained = self.c.user.get_ained(self._permission)
                        if None in ained or test.aine_kood in ained:
                            sooritaja = registreeri(self, c.kasutaja, kord, None, None, None)
            model.Session.commit()
            
        c.sooritajad = c.kasutaja.get_reg_sooritajad(c.testiliik)

        q = (model.Sooritaja.query
             .filter(model.Sooritaja.kasutaja_id==c.kasutaja.id)
             .filter(model.Sooritaja.staatus>=const.S_STAATUS_ALUSTAMATA)
             .filter(model.Sooritaja.testimiskord_id!=None)
             .join(model.Sooritaja.test)
             .filter(model.Test.testiliik_kood==c.testiliik)
             .order_by(model.Sooritaja.algus))
        c.ajalugu = q.all()
        return self.response_dict

    def create(self):
        """Testide lisamine valitud testide sekka
        """
        kasutaja = self.c.kasutaja
        testiliik = self.request.params.get('testiliik')

        # vajutati jätkamise nupule
        # salvestame rahvusvahelise keeleksami lisaandmed
        errors = dict()
        if testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            sooritajad = kasutaja.get_reg_sooritajad(const.TESTILIIK_RIIGIEKSAM)                            
            errors = self._save_rahvusvahelised(errors, kasutaja, sooritajad)
        elif testiliik == const.TESTILIIK_TASE:
            sooritajad = kasutaja.get_reg_sooritajad(const.TESTILIIK_TASE)                            
            errors = self._save_tasemeeksam(errors, kasutaja, sooritajad)                
        if not errors:
            model.Session.commit()
            return HTTPFound(location=self.url('regamine_avaldus_edit_kinnitamine', id=kasutaja.id, testiliik=testiliik))
        else:
            self.form.errors = errors
            model.Session.rollback()
            extra_info = self._index_d()
            html = self.form.render('ekk/regamine/avaldus.testid.mako', extra_info=extra_info)
            return Response(html)

    def _save_rahvusvahelised(self, errors, kasutaja, sooritajad):
        
        self.form = Form(self.request, schema=forms.ekk.regamine.RahvusvahelisedForm)
        if not self.form.validate():
            errors.update(self.form.errors)
            return errors
        else:
            data = self.form.data
            synnikoht_kood = data.get('f_synnikoht_kodakond_kood')
            synnikoht = data.get('f_synnikoht')
            rahvus = data.get('f_rahvus_kood')
            eesnimi_ru = data.get('f_eesnimi_ru')
            perenimi_ru = data.get('f_perenimi_ru')
            msg = _("Palun sisestada väärtus")

            for rcd in sooritajad:
                test = rcd.test
                if test.testiliik_kood != const.TESTILIIK_RV:
                    continue
                
                if test.aine_kood == const.AINE_DE:
                    if not synnikoht_kood:
                        errors['f_synnikoht_kodakond_kood'] = msg
                    else:
                        rcd.synnikoht_kodakond_kood = synnikoht_kood
                            
                if test.aine_kood == const.AINE_RU:
                    if not eesnimi_ru:
                        errors['f_eesnimi_ru'] = msg
                    else:
                        rcd.eesnimi_ru = eesnimi_ru
                    if not perenimi_ru:
                        errors['f_perenimi_ru'] = msg
                    else:
                        rcd.perenimi_ru = perenimi_ru

                if test.aine_kood == const.AINE_FR:
                    if not rahvus:
                        errors['f_rahvus_kood'] = msg
                    else:
                        rcd.rahvus_kood = rahvus

                    if kasutaja.synnikoht:
                        rcd.synnikoht = kasutaja.synnikoht
                    else:
                        if not synnikoht_kood:
                            errors['f_synnikoht_kodakond_kood'] = msg
                        else:
                            rcd.synnikoht_kodakond_kood = synnikoht_kood

                        if not synnikoht:
                            errors['f_synnikoht'] = msg
                        else:
                            rcd.synnikoht = synnikoht
                        
            return errors

    def _save_tasemeeksam(self, errors, kasutaja, sooritajad):
        
        self.form = Form(self.request, schema=forms.ekk.regamine.TasemeeksamidForm)
        if not self.form.validate():
            errors.update(self.form.errors)
            return errors
        else:
            data = self.form.data
            oket = [r for r in data['oket'] if r['oppekohtet_kood']]
            if not oket:
                errors['oket-0.oppekohtet_kood'] = 'Palun sisestada'
            else:
                for sooritaja in sooritajad:
                    BaseGridController(sooritaja.oppekohad, model.Oppekoht, pkey='oppekohtet_kood').save(oket)
                    sooritaja.from_form(self.form.data, 'f_')
            return errors

    def edit(self):
        "Dialoogiaknas olemasoleva testi piirkonna ja keele muutmine"
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        self.c.sooritaja = model.Sooritaja.get(sooritaja_id)
        assert self.c.sooritaja.kasutaja_id == self.c.kasutaja.id, _("Vale kasutaja")
        self.c.testiliik = self.c.sooritaja.test.testiliik_kood
        return self.render_to_response('ekk/regamine/avaldus.test.mako')

    def update(self):
        "Dialoogiaknas olemasoleva testi piirkonna ja keele muutmine"
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        sooritaja = model.Sooritaja.get(sooritaja_id)
        assert sooritaja.kasutaja_id == self.c.kasutaja.id, _("Vale kasutaja")
        testiliik = sooritaja.test.testiliik_kood
        lang = self.params_lang()
        piirkond_id = self.request.params.get('piirkond_id')
        kursus = self.request.params.get('kursus')
        if lang:
            sooritaja.lang = lang
        if piirkond_id:
            sooritaja.piirkond_id = int(piirkond_id)
        sooritaja.reg_markus = self.request.params.get('reg_markus')
        sooritaja.kursus_kood = kursus
        sooritaja.soovib_konsultatsiooni = bool(self.request.params.get('soovib_konsultatsiooni'))
        for tos in sooritaja.sooritused:
            toimumispaev_id = self.request.params.get('toimumispaev_id_%s' % tos.toimumisaeg_id) or None
            tos.reg_toimumispaev_id = toimumispaev_id
        model.Session.commit()
        self.success()
        return self._redirect('index', testiliik=testiliik)

    def delete(self):
        id = self.request.matchdict.get('id')
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        rcd = model.Sooritaja.get(sooritaja_id)
        if rcd:
            assert rcd.kasutaja_id == int(id), _("vale kasutaja")
            staatus = rcd.staatus
            testiliik = rcd.test.testiliik_kood
            if staatus < const.S_STAATUS_POOLELI:
                kt.send_tyhteade(self, rcd.kasutaja, rcd)            
                rcd.tyhista()
                if staatus <= const.S_STAATUS_REGAMATA:
                    model.Session.flush()
                    rcd.delete()
                model.Session.commit()
        else:
            testiliik = self.request.params.get('testiliik')
        return HTTPFound(location=self.url('regamine_avaldus_testid', id=id, testiliik=testiliik))

    def __before__(self):
        id = self.request.matchdict.get('id')
        self.c.kasutaja = model.Kasutaja.get(id)

    def _perm_params(self):
        testiliik = self.request.params.get('testiliik')
        if testiliik:
            return {'testiliik': testiliik}
        
