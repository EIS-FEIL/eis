from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController

log = logging.getLogger(__name__)

class AmetnikurollidController(BaseResourceController):

    _ITEM = 'roll'
    _ITEMS = 'rollid'
    _MODEL = model.Kasutajaroll
    _ITEM_FORM = forms.admin.AmetnikurollForm
    _EDIT_TEMPLATE = '/admin/ametnik.roll.mako' 
    _INDEX_TEMPLATE = '/admin/ametnik.rollid.mako'
    _permission = 'ametnikud'
    _actions = 'create,new,update,delete,edit,index'
    _index_after_create = True
    
    def _index_d(self):
        c = self.c
        c.kasutaja = model.Kasutaja.get(c.kasutaja_id)
        c.kasutajarollid, c.ametnikuroll = self._get_rollid(c.kasutaja_id)
        return self.response_dict

    def _get_rollid(self, kasutaja_id):
        # leiame kirjete plokid, mis loodi koos ja mida muudetakse koos
        plokid = {}
        kasutajarollid = []
        ametnikuroll = None
        q = (model.Session.query(model.Kasutajaroll)
             .filter(model.Kasutajaroll.koht_id==const.KOHT_EKK)
             .filter(model.Kasutajaroll.kasutaja_id==kasutaja_id)
             .join(model.Kasutajaroll.kasutajagrupp)
             .order_by(model.Kasutajagrupp.nimi,
                       model.Kasutajaroll.piirkond_id,
                       model.Kasutajaroll.aine_kood,
                       model.Kasutajaroll.testiliik_kood))
        for r in q.all():
            if r.rolliplokk:
                pr = plokid.get(r.rolliplokk)
                if pr:
                    # plokk on juba olemas
                    aine = r.aine_nimi
                    if aine:
                        pr.ained.add(aine)
                    continue
                else:
                    plokid[r.rolliplokk] = r
            aine = r.aine_nimi
            r.ained = set(aine and [aine] or [])
            kasutajarollid.append(r)
        
        return kasutajarollid, ametnikuroll

    def _edit(self, item):
        c = self.c
        c.roll = item
        if item.rolliplokk:
            q = (model.Session.query(model.Kasutajaroll.aine_kood)
                 .distinct()
                 .filter_by(kasutaja_id=item.kasutaja_id)
                 .filter(model.Kasutajaroll.aine_kood!=None)
                 .filter(model.Kasutajaroll.rolliplokk==item.rolliplokk))
            c.ained = [a for a, in q.all()]
        elif item.aine_kood:
            c.ained = [item.aine_kood]
        else:
            c.ained = []

    def _create(self, **kw):
        grupp_id = self.form.data.get('r_kasutajagrupp_id')        
        item = model.Kasutajaroll(kasutaja_id=self.c.kasutaja_id,
                                  kehtib_alates=date.today(),
                                  kasutajagrupp_id=grupp_id)
        model.Session.flush()
        self._update(item)
        return item
    
    def _update(self, item, grupp_id=None):
        # ametniku rolli dialoogiaknas salvestamine
        c = self.c
        vanadrollid = list(c.kasutaja.kasutajarollid)
        data = self.form.data
        if not grupp_id:
            grupp_id = data.get('r_kasutajagrupp_id')
        grupp = model.Kasutajagrupp.get(grupp_id)
        jira_nr = data.get('jira_nr')
        selgitus = data.get('selgitus')
        op = data.get('op')
        if op == 'delete':
            self._upd_delete(item)
            return self.index()
        
        if grupp_id in (const.GRUPP_AINESPETS,
                        const.GRUPP_E_KORRALDUS,
                        const.GRUPP_AINETOORYHM,
                        const.GRUPP_HINDAMISJUHT,
                        const.GRUPP_HINDAMISEKSPERT):
            # grupid, mille korral saab valida mitu ainet
            ained = data['r_ained'] or [None]
            if len(ained) > 1 and not item.rolliplokk:
                # kui valiti mitu ainet, siis peab olema plokk
                item.rolliplokk = item.id
        else:
            # grupid, mille korral ainet ei saa valida või saab 1 aine valida
            aine_kood = data.get('r_aine_kood')
            ained = [aine_kood]

        rolliplokk = item.rolliplokk
        if rolliplokk:
            # antud grupi kõigi kirjete muutmine
            qr = (model.Session.query(model.Kasutajaroll)
                  .filter_by(kasutaja_id=self.c.kasutaja_id)
                  .filter_by(rolliplokk=item.rolliplokk)
                  .filter_by(koht_id=const.KOHT_EKK))
            rollid = list(qr.all())
        else:
            # yhe kirje muutmine, vbl uute kirjade lisamine
            roll = item
            if roll.kasutaja_id != self.c.kasutaja_id:
                raise Exception('Vale ametnik')

        for aine in ained:
            if rolliplokk:
                # leiame mõne rolli antud ainega
                roll = None
                for ind, r in enumerate(rollid):
                    if r.aine_kood == aine:
                        roll = rollid.pop(ind)
                        break
            if roll is None:
                roll = model.Kasutajaroll(kasutaja_id=self.c.kasutaja_id,
                                          kehtib_alates=date.today(),
                                          rolliplokk=rolliplokk)
            self._save_roll(roll, grupp, aine, data, jira_nr, selgitus)
            if self._check_uniq(roll, vanadrollid):
                raise ValidationError(self, {}, message=_("Roll on juba olemas"))
            roll = None

        if rolliplokk:
            # kui kõigi kirjete muutmisel jäi aineid vähemaks,
            # siis kustutame liigsed kirjed
            for r in rollid:
                self._log_roll(r, None, True, jira_nr, selgitus)
                r.delete()

        model.Session.flush()
        kuni = self.c.kasutaja.ametnik_kuni
        self.c.kasutaja.on_ametnik = kuni and kuni >= date.today() or False

    def _check_uniq(self, roll, vanadrollid):
        for r in vanadrollid:
            if r.id != roll.id and \
                r.kasutajagrupp_id == roll.kasutajagrupp_id and \
                r.koht_id == roll.koht_id and \
                r.piirkond_id == roll.piirkond_id and \
                r.aine_kood == roll.aine_kood and \
                r.oskus_kood == roll.oskus_kood and \
                r.testiliik_kood == roll.testiliik_kood and \
                r.lang == roll.lang:
                # roll kordub
                return True

    def _save_roll(self, roll, grupp, aine, data, jira_nr, selgitus):
        c = self.c
        is_update = roll.id is not None
        roll.kasutajagrupp_id = grupp.id
        roll.aine_kood = aine
        roll.piirkond_id = data['r_piirkond_id'] or None
        roll.oskus_kood = data['r_oskus_kood'] or None
        roll.testiliik_kood = data['r_testiliik_kood'] or None
        roll.kehtib_kuni = data['r_kehtib_kuni'] or const.MAX_DATE
        errors = {}

        if grupp.tyyp == const.USER_TYPE_AV:
            # oma testi korraldaja
            roll.aine_kood = None
            roll.oskus_kood = None
            roll.testiliik_kood = const.TESTILIIK_AVALIK
            roll.lang = None
            roll.allkiri_jrk = roll.allkiri_tiitel1 = roll.allkiri_tiitel2 = None
            roll.mk_kood = None
            roll.kov_kood = None
            roll.koht_id = const.KOHT_EKK
            
        elif grupp.tyyp == const.USER_TYPE_EKK:
            if grupp.id == const.GRUPP_ADMIN and not c.user.on_admin:
                raise ValidationError(self, {}, message=_("Puudub õigus hallata rolle"))

            if grupp.id not in model.Kasutajagrupp.ainegrupid:
                roll.aine_kood = None
            elif not aine:
                # osaspetsi korral on r_aine_kood, aga seda ei saa valimata jätta
                errors['r_ained'] = _("Palun valida aine")

            if grupp.id != const.GRUPP_OSASPETS:
                roll.oskus_kood = None
            elif not roll.oskus_kood:
                errors['r_oskus_kood'] = _("Väärtus puudub")

            elif grupp.id in (const.GRUPP_VAIDEKOM,
                              const.GRUPP_VAIDEKOM_SEKRETAR,
                              const.GRUPP_VAIDEKOM_ESIMEES):
                if not roll.testiliik_kood:
                    # testiliik peab olema
                    errors['r_testiliik_kood'] = _("Väärtus puudub")

            elif grupp.id not in (const.GRUPP_AINESPETS,
                                  const.GRUPP_INFOSPETS,
                                  const.GRUPP_SISESTAJA,
                                  const.GRUPP_REGAJA,
                                  const.GRUPP_ERIVAJADUS,
                                  const.GRUPP_KORRALDUS,
                                  const.GRUPP_P_KORRALDUS,
                                  const.GRUPP_VAIDEKOM_ESIMEES,
                                  const.GRUPP_VAIDEKOM_SEKRETAR,
                                  const.GRUPP_VAIDEKOM):
                roll.testiliik_kood = None
            elif not roll.testiliik_kood:
                # testiliik jäeti valimata, roll kehtib kõigile testiliikidele
                roll.testiliik_kood = None

            if grupp.id == const.GRUPP_UI_TOLKIJA:
                roll.lang = data['r_lang'] or None
            else:
                roll.lang = None

            if grupp.id in (const.GRUPP_VAIDEKOM, const.GRUPP_VAIDEKOM_ESIMEES, const.GRUPP_VAIDEKOM_SEKRETAR):
                roll.allkiri_jrk = data['r_allkiri_jrk']
                roll.allkiri_tiitel1 = data['r_allkiri_tiitel1']
                roll.allkiri_tiitel2 = data['r_allkiri_tiitel2']
                if not roll.allkiri_tiitel1 and not roll.allkiri_tiitel2:
                    errors['r_allkiri_tiitel1'] = _("Väärtus puudub")
            else:
                roll.allkiri_jrk = None
                roll.allkiri_tiitel1 = None
                roll.allkiri_tiitel2 = None
                
            if grupp.id != const.GRUPP_P_KORRALDUS:
                roll.mk_kood = None
                roll.kov_kood = None
            roll.koht_id = const.KOHT_EKK
        if errors:
            c.dialog = True
            raise ValidationError(self, errors)
        self._log_roll(roll, is_update, False, jira_nr, selgitus)

    def _upd_delete(self, item):
        params = self.request.params
        #self.form = Form(self.request, schema=self._ITEM_FORM)
        #if not self.form.validate():
        #    return self._error_update()
        data = self.form.data 
        jira_nr = data.get('jira_nr')
        selgitus = data.get('selgitus')
           
        if not jira_nr and not selgitus:
            raise ValidationError(self, {'jira_nr': _("Palun sisestada")})
        if item.kasutaja_id != self.c.kasutaja_id:
            raise Exception('Vale ametnik')
        if item.rolliplokk:
            # kõigi sama ploki rollide kustutamine
            q = (model.Session.query(model.Kasutajaroll)
                 .filter_by(kasutaja_id=self.c.kasutaja_id)
                 .filter_by(rolliplokk=item.rolliplokk)
                 .filter_by(koht_id=const.KOHT_EKK))
            for roll in list(q.all()):
                self._log_roll(roll, None, True, jira_nr, selgitus)
                roll.delete()
        else:
            self._log_roll(item, None, True, jira_nr, selgitus)
            item.delete()
        model.Session.flush()
        kuni = self.c.kasutaja.ametnik_kuni
        self.c.kasutaja.on_ametnik = kuni and kuni >= date.today() or False        
        model.Session.commit()
        self.success(_("Kasutajaroll on kustutatud!"))

    def _log_roll(self, roll, is_update, is_delete, jira_nr, selgitus):
        grupp_id = roll.kasutajagrupp_id
        if is_delete:
            sisu = 'Eemaldamine\n' + roll.get_str()
        else:
            old_values, new_values = roll._get_changed_values()
            if not new_values:
                return
            sisu = roll.get_str()
            
        krl = model.Kasutajarollilogi(kasutaja_id=roll.kasutaja_id,
                                      muutja_kasutaja_id=self.c.user.id,
                                      aeg=datetime.now(),
                                      sisu=sisu,
                                      kasutajagrupp_id=grupp_id,
                                      kasutajaroll=not is_delete and roll or None,
                                      tyyp=const.USER_TYPE_EKK,
                                      jira_nr=jira_nr,
                                      selgitus=selgitus)

    def __before__(self):
        self.c.kasutaja_id = int(self.request.matchdict['kasutaja_id'])
        self.c.kasutaja = model.Kasutaja.get(self.c.kasutaja_id)
