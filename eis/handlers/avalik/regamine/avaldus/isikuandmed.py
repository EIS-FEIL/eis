from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
log = logging.getLogger(__name__)
_ = i18n._

class IsikuandmedController(BaseResourceController):
    _permission = 'sooritamine'
    _get_is_readonly = False
    _ITEM_FORM = forms.avalik.regamine.IsikuandmedForm
    _EDIT_TEMPLATE = 'avalik/regamine/avaldus.isikuandmed.mako'
    _actions = 'index,create'
    
    def index(self):
        c = self.c
        self._index_d()
        if len(c.sooritajad) == 0:
            self.error(_("Palun valida testid"))
            return HTTPFound(location=self.url('regamine_avaldus_testid', testiliik=c.testiliik))

        return self.render_to_response(self._EDIT_TEMPLATE)

    def _index_d(self):
        c = self.c
        c.sooritajad = c.kasutaja.get_reg_sooritajad(c.testiliik, peitmata=True, regamine=True)
        return self.response_dict

    def _create(self):
        c = self.c
        errors = dict()
        opilane = c.kasutaja.any_opilane
        oppeform = None

        # isikuandmete salvestamine
        c.kasutaja.from_form(self.form.data, 'k_')

        model.Aadress.adr_from_form(c.kasutaja, self.form.data, 'a_')
        aadress = c.kasutaja.aadress_id and model.Aadress.get(c.kasutaja.aadress_id) or None

        if c.testiliik not in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS, const.TESTILIIK_KOOLITUS):
            if not opilane:
                # õppimisandmete salvestamine - kui pole TE/SE ja pole õpilane
                oppeform = Form(self.request, schema=forms.avalik.regamine.OppimineForm)
                if not oppeform.validate():
                    errors = oppeform.errors
                else:
                    c.kasutaja.from_form(oppeform.data, 'ko_')
            if not c.kasutaja.epost:
                errors['k_epost'] = _("Palun sisestada e-posti aadress")

        sooritajad = c.kasutaja.get_reg_sooritajad(c.testiliik, peitmata=True, regamine=True)
                
        if c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            # kui andmeid EHISes pole, siis kontrollime kohustuslike andmete sisestatust
            if not opilane and sooritajad:
                errors = self._check_riigieksam(self.form.errors, oppeform.data, sooritajad)
            else:
                errors = dict()

            # kui testide seas on rahvusvahelisi eksameid, siis kontrollime nende lisaandmete sisestamist
            rvform = Form(self.request, schema=forms.avalik.regamine.RahvusvahelisedForm)
            if rvform.validate():
                errors = self._save_rahvusvahelised(errors, rvform.data, c.kasutaja, sooritajad)
            else:
                errors.update(rvform.errors)

            # kontrollime, kas valitud testide seas on rahvusvahelisi keeleeksameid
            on_rv = False
            for rcd in sooritajad:
                test = rcd.test
                if test.testiliik_kood == const.TESTILIIK_RV:
                    on_rv = True
                    break
            if on_rv:
                # kui on registreeritud mõnele rahvusvahelisele eksamile,
                # siis on kohustuslik sisestada: aadress, postiindeks,
                # telefon, e-post
                for key in ('k_postiindeks', 'k_telefon', 'k_epost'):
                    if not self.form.data.get(key):
                        if key == 'k_epost':
                            errors[key] = _("Palun sisestada e-posti aadress")
                        else:
                            errors[key] = _("Palun sisestada")
                if not aadress or not aadress.kood7 and not aadress.kood6 and not c.kasutaja.normimata:
                    errors['a_adr_id'] = _("Palun sisestada")
                    
        elif c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS):
            if not c.kasutaja.epost:
                aadress_puudub = not aadress or not aadress.kood7 and not aadress.kood6 and not c.kasutaja.normimata
                if aadress_puudub or not c.kasutaja.postiindeks:
                    if aadress_puudub:
                        errors['a_adr_id'] = _("Palun sisestada aadress ja/või e-post")
                    if not c.kasutaja.postiindeks:
                        errors['k_postiindeks'] = _("Palun sisestada aadress ja/või e-post")
                    errors['k_epost'] = _("Palun sisestada aadress ja/või e-post")
            if c.testiliik == const.TESTILIIK_TASE:
                c.kasutaja.from_form(self.form.data, 'kk_')
                    
                kood = self.form.data['kk_tvaldkond_kood']
                if not kood:
                    errors['kk_tvaldkond_kood'] = _("Palun sisestada")
                elif kood == const.TVALDKOND_MUU and not self.form.data['kk_tvaldkond_muu']:
                    errors['kk_tvaldkond_muu'] = _("Palun sisestada")

                if not self.form.data['kk_haridus_kood']:
                    errors['kk_haridus_kood'] = _("Palun sisestada")
                
                if not self.form.data['kk_amet_muu']:
                    errors['kk_amet_muu'] = _("Palun sisestada")

                oket = [r for r in self.form.data['oket'] if r['oppekohtet_kood']]
                if not oket:
                    errors['oket-0.oppekohtet_kood'] = _("Palun sisestada")
                else:
                    for sooritaja in sooritajad:
                        BaseGridController(sooritaja.oppekohad, model.Oppekoht, pkey='oppekohtet_kood').save(oket)
                        sooritaja.from_form(self.form.data, 'kk_')

        if not c.kasutaja.epost and c.testiliik not in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS):
            # TE/SE e-post on juba eespool kontrollitud, aga kõigi muude testiliikidega on e-post kohustuslik
            errors['k_epost'] = _("Palun sisestada e-posti aadress")
                        
        if errors:
            raise ValidationError(self, errors)

        if self.request.params.get('rr'):
            xtee.set_rr_pohiandmed(self, c.kasutaja, muuda=True)
            model.Session.commit()
            return self._redirect('index', testiliik=c.testiliik)

    def _after_create(self, id):
        return HTTPFound(location=self.url('regamine_avaldus_kinnitamine', testiliik=self.c.testiliik))

    def _error_create(self):
        extra_info = self._index_d()
        html = self.form.render(self._EDIT_TEMPLATE, extra_info=extra_info)
        return Response(html)
    
    def _check_riigieksam(self, errors, data, sooritajad):
        # riigieksamite kohustuslikud andmed
        
        msg = 'Palun sisestada'
        ko_lopetamisaasta = data.get('ko_lopetamisaasta')
        year = date.today().year

        if not data.get('ko_kool_koht_id') and not data.get('ko_kool_nimi'):
            errors['ko_kool_koht_id'] = msg
        if not data.get('ko_oppekeel'):
            errors['ko_oppekeel'] = msg
        if not ko_lopetamisaasta:
            errors['ko_lopetamisaasta'] = msg
        elif not year - 100 < ko_lopetamisaasta <= year:
            errors['ko_lopetamisaasta'] = "Palun sisestada neljakohaline aastaarv"
        else:
            # leiame kõige hilisema regatud eksami aasta
            aasta = max([j.testimiskord.aasta or 0 for j in sooritajad]) \
                    or date.today().year
            if ko_lopetamisaasta < aasta:
                if not data.get('ko_tunnistus_nr'):
                    errors['ko_tunnistus_nr'] = msg
                if not data.get('ko_tunnistus_kp'):
                    errors['ko_tunnistus_kp'] = msg

        return errors

    def _save_rahvusvahelised(self, errors, data, kasutaja, sooritajad):
        # rahvusvaheliste eksamite kohustuslikud andmed
        synnikoht_kood = data.get('f_synnikoht_kodakond_kood')
        synnikoht = data.get('f_synnikoht')
        rahvus = data.get('f_rahvus_kood')
        eesnimi_ru = data.get('f_eesnimi_ru')
        perenimi_ru = data.get('f_perenimi_ru')
        msg = _('Palun sisestada')
        
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
        
    def __before__(self):
        self.c.kasutaja = self.c.user.get_kasutaja(write=True)
        self.c.testiliik = self.request.matchdict.get('testiliik')
