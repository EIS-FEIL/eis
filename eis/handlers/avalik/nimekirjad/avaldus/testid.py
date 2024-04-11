from eis.lib.base import *
_ = i18n._
import eis.lib.xtee.ehis as ehis
import eis.lib.regpiirang as regpiirang
from eis.handlers.avalik.regamine.avaldus.testid import suuna_kohtaeg, save_vvkohad
import eis.handlers.ekk.otsingud.kohateated as kt
log = logging.getLogger(__name__)

class TestidController(BaseController):
    _permission = 'nimekirjad'
    def index(self):
        self._index_d()
        return self.render_to_response('avalik/nimekirjad/avaldus.testid.mako')

    def _index_d(self):
        c = self.c
        c.testiliik = self.request.params.get('testiliik') or const.TESTILIIK_RIIGIEKSAM
        liigid = c.user.get_testiliigid(self._permission)
        if liigid and None not in liigid and c.testiliik not in liigid:
            c.testiliik = liigid[0]

        c.opt_testiliigid = self._get_opt_testiliigid(c.testiliik)
        c.sooritajad = c.kasutaja.get_reg_sooritajad(c.testiliik)

        q = (model.Sooritaja.queryR
             .filter(model.Sooritaja.kasutaja_id==c.kasutaja.id)
             .filter(model.Sooritaja.staatus>=const.S_STAATUS_ALUSTAMATA)
             .filter(model.Sooritaja.testimiskord_id!=None)
             .join(model.Sooritaja.test)
             .filter(model.Test.testiliik_kood==c.testiliik)
             .order_by(model.Sooritaja.algus))
        c.ajalugu = q.all()
        return self.response_dict

    def _get_opt_testiliigid(self, def_liik):
        testiliigid = self.c.opt.testiliik
        d = date.today()
        koht_id = self.c.user.koht_id
        q = (model.SessionR.query(model.Test.testiliik_kood).distinct()
             .join(model.Test.testimiskorrad)
             .filter(model.Test.eeltest_id==None)
             .filter(sa.or_(model.Testimiskord.reg_kool_eis==True,
                            sa.and_(model.Testimiskord.reg_kool_valitud==True,
                                    sa.exists().where(sa.and_(
                                        model.Regkoht_kord.koht_id==koht_id,
                                        model.Regkoht_kord.testimiskord_id==model.Testimiskord.id))
                                    )
                            ))
             .filter(model.Testimiskord.reg_kool_alates<=d)
             .filter(model.Testimiskord.reg_kool_kuni>=d))
        regatavad = [r for r, in q.all()]
        opilane = self.c.kasutaja.opilane
        if opilane and opilane.klass in ('7','8','9'):
            # ES-1174 blokeerime 7.-9. kl õpilaste riigieksamitele regamise
            regatavad = [r for r in regatavad if r[0] != const.TESTILIIK_RIIGIEKSAM]
        return [r for r in testiliigid if r[0] in regatavad or r[0] == def_liik]

    def create(self):
        """Testide lisamine valitud testide sekka
        """
        kasutaja = self.c.kasutaja
        testiliik = self.request.params.get('testiliik')
        esitaja_kasutaja_id = self.c.user.id
        esitaja_koht_id = self.c.user.koht_id

        # vajutati jätkamise nupule
        # salvestame rahvusvahelise keeleksami lisaandmed

        errors = dict()
        if testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            sooritajad = kasutaja.get_reg_sooritajad(const.TESTILIIK_RIIGIEKSAM)            

            # kui testide seas on rahvusvahelisi eksameid, siis kontrollime nende lisaandmete sisestamist
            errors = self._save_rahvusvahelised(errors, kasutaja, sooritajad)

        elif testiliik == const.TESTILIIK_SISSE:
            # sisseastumiseksami korral salvestatakse e-posti aadress
            errors = self._save_sisse(errors, kasutaja)
            
        if not errors:
            model.Session.commit()
            if self.request.params.get('tagasi'):
                url = self.url('nimekirjad_avaldus_isikuandmed', id=kasutaja.id, testiliik=testiliik)
            else:
                url = self.url('nimekirjad_avaldus_edit_kinnitamine', id=kasutaja.id, testiliik=testiliik)
            return HTTPFound(location=url)
        else:
            self.form.errors = errors
            model.Session.rollback()
            extra_info = self._index_d()
            html = self.form.render('avalik/nimekirjad/avaldus.testid.mako', extra_info=extra_info)
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

    def _save_sisse(self, errors, kasutaja):
        
        self.form = Form(self.request, schema=forms.avalik.nimekirjad.SisseastumineForm)
        if not self.form.validate():
            errors.update(self.form.errors)
            return errors
        else:
            data = self.form.data
            epost = data.get('k_epost')
            if epost:
                kasutaja.epost = epost
            else:
                errors['k_epost'] = _("Palun sisestada")
            return errors
        
        
    def edit(self):
        "Dialoogiaknas olemasoleva testi piirkonna ja keele muutmine"
        c = self.c
        self._edit_sooritaja()
        if not c.sooritaja:
            buf = _("Registreering on juba kustutatud!")
            return Response(buf)
        assert c.sooritaja.kasutaja_id == c.kasutaja.id, _("Vale kasutaja")
        return self.render_to_response('avalik/nimekirjad/avaldus.test.mako')

    def _edit_sooritaja(self):
        c = self.c
        c.regpiirang = regpiirang
        c.testiliik = self.request.params.get('testiliik')
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        c.sooritaja = model.Sooritaja.get(sooritaja_id)

    def update(self):
        "Dialoogiaknas olemasoleva testi piirkonna ja keele muutmine"
        errors = {}
        params = self.request.params
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        sooritaja = model.Sooritaja.get(sooritaja_id)
        assert sooritaja.kasutaja_id == self.c.kasutaja.id, _("Vale kasutaja")
        testiliik = sooritaja.test.testiliik_kood
        lang = self.params_lang()
        piirkond_id = params.get('piirkond_id')
        kord = sooritaja.testimiskord
        
        vvkohad_id = params.getall('vvk')
        vvk_oma = params.get('vvk_oma')        
        if kord and kord.reg_kohavalik and kord.regkohad:
            if not vvkohad_id:
                errors['vvk'] = _("Palun valida õppeasutused, millele avaldatakse testitulemused")
            else:
                # salvestame koolid, kes võivad tulemusi vaadata
                opilane = sooritaja.kasutaja.opilane
                save_vvkohad(sooritaja, vvkohad_id, vvk_oma, opilane, self.c.user.koht_id)

        kohtaeg = params.get('kohtaeg')
        if kord and kord.reg_kohavalik and kohtaeg:
            # kui regamisel valitakse esimese testiosa soorituskoht ja aeg
            if not suuna_kohtaeg(self, sooritaja, kohtaeg):
                errors['kohtaeg'] = _("Viga")
                
        kursus = params.get('kursus')
        if kursus:
            sooritaja.kursus_kood = kursus
        if lang:
            sooritaja.lang = lang
        if piirkond_id:
            sooritaja.piirkond_id = int(piirkond_id)

        sooritaja.reg_markus = self.request.params.get('reg_markus')

        if errors:
            self.form = Form(self.request, schema=forms.NotYetImplementedForm)
            self.form.errors = errors
            model.Session.rollback()
            self._edit_sooritaja()
            template = 'avalik/nimekirjad/avaldus.test.mako'
            html = self.form.render(template, extra_info=self.response_dict)            
            return Response(html)            
            
        model.Session.commit()
        self.success()
        return self._redirect('index', testiliik=testiliik)

    def delete(self):
        id = self.request.matchdict.get('id')
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        rcd = model.Sooritaja.get(sooritaja_id)
        if rcd:
            staatus = rcd.staatus
            testiliik = rcd.test.testiliik_kood
            koht_id = self.c.user.koht_id
            if rcd.kool_voib_tyhistada(koht_id, testiliik):
                assert rcd.kasutaja_id == int(id), _("vale kasutaja")
                kt.send_tyhteade(self, rcd.kasutaja, rcd)
                rcd.tyhista()
                if staatus == const.S_STAATUS_REGAMATA:
                    model.Session.flush()
                    rcd.delete()
                model.Session.commit()
        return HTTPFound(location=self.url('nimekirjad_avaldus_testid', id=id, testiliik=testiliik))

    def __before__(self):
        id = self.request.matchdict.get('id')
        self.c.kasutaja = model.Kasutaja.get(id)

    def _perm_params(self):
        testiliik = self.request.params.get('testiliik')
        if testiliik:
            return {'testiliik': testiliik, 'koht_id': self.c.user.koht_id}
        
