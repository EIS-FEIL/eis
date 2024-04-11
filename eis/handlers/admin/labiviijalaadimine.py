from cgi import FieldStorage
import formencode
from eis.forms import validators
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class LabiviijalaadimineController(BaseResourceController):
    "Läbiviijate laadimine failist"

    #_MODEL = model.Kasutaja
    _SEARCH_FORM = forms.admin.LabiviijalaadimineForm
    _ITEM_FORM = forms.admin.LabiviijalaadimineForm
    _INDEX_TEMPLATE = '/admin/labiviijalaadimine.mako'
    _index_after_create = True
            
    _permission = 'kasutajad'

    def _query(self):
        pass
 
    def _create(self, **kw):
        self.c.kasutajagrupp_id = self.form.data.get('kasutajagrupp_id')
        
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            raise ValidationError(self, {'fail': 'Palun sisestada fail'})

        ained = [r[0] for r in self.c.opt.klread_kood('AINE')]
        keeled = [r[0] for r in self.c.opt.klread_kood('SOORKEEL')]

        # value on FieldStorage objekt
        value = value.value
        resultbuf = ''
        for ind, line in enumerate(value.splitlines()):
            line = utils.guess_decode(line).strip()
            if line:
                resultline = err = None
                if self.c.kasutajagrupp_id == const.GRUPP_T_ADMIN:
                    resultline, err = self.insert_admin(line)
                elif self.c.kasutajagrupp_id == const.GRUPP_HINDAJA_K:
                    resultline, err = self.insert_hindaja(line, ained, keeled)
                if err:
                    err = _('Viga real {n}.').format(n=ind+1) + '\n' + err
                    raise ValidationError(self, errors={}, message=err)
                if resultline:
                    resultbuf += resultline + '\r\n'
                    
        model.Session.commit()
        return utils.download(resultbuf, 'passwd.csv', 'text/csv')

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def insert_admin(self, line):
        # Testi administraatorite kontode loomine. Failis on:
        # kasutajatunnus;eesnimi;perekonnanimi

        # Süsteem loob kasutajakontod ning märgib profiili,
        # et isik võib tegutseda testi administraatorina.

        # VAREM oli failis ka kooli tähis ning isik seoti kooliga

        li, err = self._split_line(line, 3, 3)
        if err or not li:
            return None, err

        userid, eesnimi, perenimi = li
        usp = validators.IsikukoodP(userid)
        if not usp.isikukood:
            err = _('Vigane isikukood "{s}"').format(s=userid)
        else:
            if not eesnimi:
                err = _('Puudub eesnimi')
            if not perenimi:
                err = _('Puudub perekonnanimi')
        if err:
            return None, err
        kasutaja = usp.get(model.Kasutaja)

        parool = '-'
        if kasutaja:
            if kasutaja.eesnimi != eesnimi or kasutaja.perenimi != perenimi:
                kasutaja.eesnimi = eesnimi
                kasutaja.perenimi = perenimi
                kasutaja.set_nimi()
            kasutaja.on_labiviija = True
        elif ik:
            if self.request.is_ext():
                reg = rahvastikuregister.Rahvastikuregister(handler=self)
                kasutaja = rahvastikuregister.set_rr_pohiandmed(self, kasutaja, isikukood=ik, reg=reg)
            else:
                kasutaja = model.Kasutaja.add_kasutaja(ik,eesnimi,perenimi)
                kasutaja.on_labiviija = True
            if kasutaja:
                model.Session.flush()
                parool = User.gen_pwd()
                kasutaja.set_password(parool, True)

        if kasutaja:
            resultline = '%s;%s;%s;%s' % (ik, eesnimi, perenimi, parool)
            # märgime testi administraatoriks sobivaks
            profiil = kasutaja.give_profiil()
            profiil.on_testiadmin = True
        else:
            resultline = None
        return resultline, err
    
    def insert_hindaja(self, line, ained, keeled):
        # Hindajate kontode loomine. Failis on:
        # õppeaine kood;piirkonna nimi;hindamiskeel;kasutajatunnus;eesnimi;perekonnanimi

        # Süsteem loob kasutajakontod, märgib piirkonna ning
        # antud õppeaine antud keeles kirjaliku hindaja profiili.

        li, err = self._split_line(line, 6, 6)
        if not li or err:
            return None, err

        aine, prk_tahis, lang, userid, eesnimi, perenimi = li
        usp = validators.IsikukoodP(userid)
        if not usp.isikukood:
            err = _('Vigane isikukood "{s}"').format(s=userid)
        else:
            if not eesnimi:
                err = _('Puudub eesnimi')
            elif not perenimi:
                err = _('Puudub perekonnanimi')
            elif aine not in ained:
                err = _('Tundmatu õppeaine kood "{s}"').format(s=aine)
            elif lang not in keeled:
                err = _('Tundmatu keel "{s}"').format(s=lang)
        if err:
            return None, err
        kasutaja = usp.get(model.Kasutaja)
        if not err:
            q = model.Session.query(model.Piirkond).filter_by(nimi=prk_tahis)
            cnt = q.count()
            if cnt != 1:
                err = _('Nimega {s} on {n} piirkonda').format(s=prk_tahis, n=cnt)
            else:
                prk = q.first()
                piirkond_id = prk.id

        if err:
            return None, err

        if kasutaja:
            if kasutaja.eesnimi != eesnimi or kasutaja.perenimi != perenimi:
                kasutaja.eesnimi = eesnimi
                kasutaja.perenimi = perenimi
                kasutaja.set_nimi()
            kasutaja.on_labiviija = True
            parool = '-'
        elif usp.isikukood_ee:
            ik = usp.isikukood_ee
            if self.request.is_ext():
                reg = rahvastikuregister.Rahvastikuregister(handler=self)
                kasutaja = rahvastikuregister.set_rr_pohiandmed(self, kasutaja, isikukood=ik, reg=reg)
            else:
                kasutaja = model.Kasutaja.add_kasutaja(ik,eesnimi,perenimi)
                kasutaja.on_labiviija = True
            if kasutaja:
                parool = User.gen_pwd()
                kasutaja.set_password(parool, True)

        if kasutaja:
            resultline = '%s;%s;%s;%s' % (ik, eesnimi, perenimi, parool)
        
            # lisame kasutajapiirkonna
            found = False
            for r in kasutaja.kasutajapiirkonnad:
                if r.piirkond_id == piirkond_id:
                    found = True
            if not found:
                r = model.Kasutajapiirkond(kasutaja=kasutaja, piirkond_id=piirkond_id)
                kasutaja.kasutajapiirkonnad.append(r)

            # loome läbiviija profiili
            profiil = kasutaja.give_profiil()
            profiil.set_k_lang(lang)
            model.Session.flush()

            # loome hindaja tähise
            lv_tahis = model.Ainelabiviija.give_tahis_for(aine, kasutaja)

            # märgime hindajaks sobivaks
            found = False
            grupp = const.GRUPP_HINDAJA_K
            for r in kasutaja.aineprofiilid:
                if r.aine_kood == aine and r.kasutajagrupp_id == grupp:
                    found = True
            if not found:
                r = model.Aineprofiil(kasutaja=kasutaja,
                                    aine_kood=aine,
                                    kasutajagrupp_id=grupp)
                kasutaja.aineprofiilid.append(r)
        else:
            resultline = None
        return resultline, err

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
