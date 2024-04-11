# -*- coding: utf-8 -*- 
from cgi import FieldStorage
import formencode
from eis.forms import validators
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class AmetnikulaadimineController(BaseResourceController):
    "Innove vaate kasutajate laadimine failist"

    #_MODEL = model.Kasutaja
    _SEARCH_FORM = forms.admin.AmetnikulaadimineForm
    _ITEM_FORM = forms.admin.AmetnikulaadimineForm
    _INDEX_TEMPLATE = '/admin/ametnikulaadimine.mako'
    _index_after_create = True
            
    _permission = 'ametnikud'

    def _query(self):
        pass
 
    def _create(self, **kw):
        c = self.c
        c.kasutajagrupp_id = self.form.data.get('kasutajagrupp_id')
        c.aine_kood = self.form.data.get('aine_kood')
        c.piirkond_id = self.form.data.get('piirkond_id')
        c.testiliik_kood = self.form.data.get('testiliik_kood')
        c.jira_nr = self.form.data.get('jira_nr')
        c.selgitus = self.form.data.get('selgitus')
        
        if c.kasutajagrupp_id == const.GRUPP_AINETOORYHM:
            aine_kood = c.aine_kood
        else:
            aine_kood = None

        if c.kasutajagrupp_id in (const.GRUPP_SISESTAJA,
                                  const.GRUPP_REGAJA,
                                  const.GRUPP_P_KORRALDUS,
                                  const.GRUPP_VAIDEKOM_ESIMEES,
                                  const.GRUPP_VAIDEKOM):
            testiliik_kood = c.testiliik_kood
        else:
            testiliik_kood = None

        if c.kasutajagrupp_id == const.GRUPP_P_KORRALDUS:
            piirkond_id = c.piirkond_id
        else:
            piirkond_id = None
        
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            raise ValidationError(self, {'fail': 'Palun sisestada fail'})

        if not c.jira_nr and not c.selgitus:
            raise ValidationError(self, {'jira_nr': _("Palun sisestada")})
        
        #ained = [r[0] for r in self.c.opt.klread_kood('AINE')]
        #keeled = [r[0] for r in self.c.opt.klread_kood('SOORKEEL')]

        # value on FieldStorage objekt
        value = value.value
        total = 0
        for ind, line in enumerate(value.splitlines()):
            line = utils.guess_decode(line).strip()
            if line:
                cnt, err = self.insert_roll(line, c.kasutajagrupp_id, aine_kood, testiliik_kood, piirkond_id, c.jira_nr, c.selgitus)
                if err:
                    err = _('Viga real {n}.').format(n=ind+1) + '\n' + err
                    raise ValidationError(self, errors={}, message=err)
                total += cnt
                
        model.Session.commit()
        self.notice(_("Failist laaditud {n} kasutajakontot").format(n=total))
        return self._redirect('index',
                              kasutajagrupp_id=self.c.kasutajagrupp_id,
                              aine_kood=self.c.aine_kood,
                              testiliik_kood=self.c.testiliik_kood)
                             

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def insert_roll(self, line, grupp_id, aine_kood, testiliik_kood, piirkond_id, jira_nr, selgitus):
        # Kasutajakontode loomine. Failis on:
        # isikukood; eesnimi; perekonnanimi; e-posti aadress; rolli lõppkuupäev; Innove kasutajakonto lõppkuupäev
        li, err = self._split_line(line, 6, 3)
        if err or not li:
            return 0, err

        ik, eesnimi, perenimi, epost, roll_kuni, konto_kuni = li
        usp = validators.IsikukoodP(ik)
        ik = usp.isikukood
        if not ik:
            err = _('Vigane isikukood "{s}"').format(s=ik)
        if not err:
            if not eesnimi:
                err = _('Puudub eesnimi')
            if not perenimi:
                err = _('Puudub perekonnanimi')
        if not err:
            try:
                validators.Email(strip=True, max=255).to_python(epost)
            except formencode.api.Invalid as ex:
                err = _("Vigane e-posti aadress {s}").format(s=epost)

        if not err:
            try:
                roll_kuni = validators.EstDateConverter(strip=True, max=255).to_python(roll_kuni)
            except formencode.api.Invalid as ex:
                err = _("Vigane kuupäev {s}").format(s=roll_kuni)
        if not err:
            try:
                konto_kuni = validators.EstDateConverter(strip=True, max=255).to_python(konto_kuni)
            except formencode.api.Invalid as ex:
                err = _("Vigane kuupäev {s}").format(s=konto_kuni)
        if err:
            return 0, err

        kasutaja = model.Kasutaja.get_by_ik(ik)
        if kasutaja:
            if kasutaja.eesnimi != eesnimi or kasutaja.perenimi != perenimi:
                kasutaja.eesnimi = eesnimi
                kasutaja.perenimi = perenimi
                kasutaja.set_nimi()
            kasutaja.on_ametnik = True
        else:
            kasutaja = model.Kasutaja.add_kasutaja(ik,eesnimi,perenimi)
            kasutaja.on_ametnik = True
            model.Session.flush()
        if epost:
            kasutaja.epost = epost

        rollid = list(kasutaja.kasutajarollid)

        # Innove vaate kasutaja roll
        ametnikuroll = None
        for r in rollid:
            if r.kasutajagrupp_id == const.GRUPP_AMETNIK:
                ametnikuroll = r
                break
        if not ametnikuroll:
            is_update = False
            ametnikuroll = kasutaja.lisaroll(const.GRUPP_AMETNIK)
            ametnikuroll.kasutajagrupp_id = const.GRUPP_AMETNIK
        else:
            is_update = True
        if konto_kuni:
            ametnikuroll.kehtib_kuni = konto_kuni
        elif not ametnikuroll.kehtib_kuni:
            ametnikuroll.kehtib_kuni = const.MAX_DATE
        self._log_roll(ametnikuroll, is_update, False, jira_nr, selgitus)
            
        if grupp_id:
            # kui on antud ka roll, siis lisame rolli
            roll = None
            for r in rollid:
                if r.kasutajagrupp_id == grupp_id and \
                   (not aine_kood or r.aine_kood == aine_kood) and \
                   (not testiliik_kood or r.testiliik_kood == testiliik_kood) and \
                   (not piirkond_id or r.piirkond_id == piirkond_id):
                    roll = r
                    break
            if not roll:
                is_update = False
                roll = kasutaja.lisaroll(grupp_id)
                roll.kasutajagrupp_id = grupp_id
            else:
                is_update = True
            if roll_kuni:
                roll.kehtib_kuni = roll_kuni
            elif not roll.kehtib_kuni:
                roll.kehtib_kuni = const.MAX_DATE

            roll.aine_kood = aine_kood
            roll.testiliik_kood = testiliik_kood
            roll.piirkond_id = piirkond_id
            self._log_roll(roll, is_update, False, jira_nr, selgitus)
            
        return 1, None

    def _split_line(self, line, cnt, cnt_min=None):
        err = None
        line = line.strip()
        if line:
            li = [s.strip() for s in line.split(';')]
            if len([s for s in li if s]) == 0:
                return
            if cnt_min and len(li) >= cnt_min: 
                while len(li) < cnt:
                    li.append('')
            if len(li) != cnt:
                err = _("Vigane rida {s}. Real peab olema {n} välja.").format(s=line.strip(), n=cnt)
                li = None
            return li, err
        return None, None

    def _log_roll(self, roll, is_update, is_delete, jira_nr, selgitus):
        grupp_id = roll.kasutajagrupp_id
        old_values, new_values = roll._get_changed_values()
        if not new_values:
            return
        sisu = roll.get_str()

        krl = model.Kasutajarollilogi(kasutaja_id=roll.kasutaja_id,
                                      muutja_kasutaja_id=self.c.user.id,
                                      aeg=datetime.now(),
                                      sisu=sisu,
                                      kasutajagrupp_id=grupp_id,
                                      tyyp=const.USER_TYPE_EKK,
                                      jira_nr=jira_nr,
                                      selgitus=selgitus)
        roll.kasutajarollilogid.append(krl)
