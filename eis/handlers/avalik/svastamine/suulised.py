from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class SuulisedController(BaseResourceController):
    """Intervjuu või suulise vastamisvormiga testide otsing
    """
    _permission = 'intervjuu'
    _MODEL = model.Testiruum
    _INDEX_TEMPLATE = 'avalik/svastamine/suulised.mako'
    _LIST_TEMPLATE = 'avalik/svastamine/suulised_list.mako'
    _EDIT_TEMPLATE = 'avalik/svastamine/suuline.mako' 
    _DEFAULT_SORT = '-toimumisaeg.alates'
    _SEARCH_FORM = forms.avalik.hindamine.SvastamineOtsingForm 

    def _query(self):
        q = (model.Session.query(model.Testiruum, 
                                 model.Testikoht, 
                                 model.Test,
                                 model.Toimumisaeg)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.toimumisaeg)
             .join(model.Toimumisaeg.testimiskord)
             .join(model.Testimiskord.test)
             .join(model.Toimumisaeg.testiosa)
             )
        return q

    def _search_default(self, q):
        return self._search(q)
     
    def _search(self, q0):
        c = self.c
        today = date.today()
        q = (q0.filter(model.Test.avaldamistase==const.AVALIK_EKSAM)
             .filter(model.Testiosa.vastvorm_kood.in_((const.VASTVORM_SH, const.VASTVORM_I)))
             .join(model.Toimumisaeg.labiviijad)
             .filter(model.Labiviija.kasutaja_id==c.user.id)
             .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_INTERVJUU)
             .filter(sa.or_(model.Labiviija.testiruum_id==model.Testiruum.id,
                            model.Labiviija.testiruum_id==None))
             .filter(model.Testiruum.algus >= today)
             .filter(model.Testiruum.algus < today + timedelta(days=1))
             )
        if c.test_id:
            q_test = q = q.filter(model.Testimiskord.test_id==c.test_id)        
        if c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==int(c.testsessioon_id))
        if c.test_id and q.count() == 0:
            other_result = q_test.count() > 0
            self._explain_test(other_result, q0)
            q = q_test

        return q

    def _explain_test(self, other_result, q):
        """Põhjendame, miks antud testi ei saa läbi viia.
        """
        c = self.c
        errors = []
        test_id = c.test_id
        test = model.Test.get(test_id)
        if not test:
            errors.append(_("Testi {id} ei ole olemas.").format(id=test_id))
        else:
            if test.avaldamistase != const.AVALIK_EKSAM:
                if c.user.has_permission('omanimekirjad', const.BT_SHOW, test=test):
                    url = self.url('test_nimekirjad',test_id=test.id, testiruum_id=0)
                    errors.append(_('See pole tsentraalselt korraldatud test, aga seda saab kasutada <a href="{url}">töölaua kaudu</a>.').format(url=url))
                else:
                    errors.append(_("See pole tsentraalselt korraldatud test.").format(id=test.id))
            else:
                q = (q.filter(model.Test.id==test_id)
                     .order_by(sa.desc(model.Testiruum.algus)))
                if q.count() == 0:
                    errors.append(_("Testi {id} ei ole antud soorituskohas korraldatud.").format(id=test_id))

            if not errors:
                q = (q.join(model.Toimumisaeg.labiviijad)
                     .filter(model.Labiviija.kasutaja_id==c.user.id)
                     .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_INTERVJUU))

                if q.count() == 0:
                    err = _("Kasutaja {s} ei ole määratud antud testi suuliseks hindajaks.").format(s=self.c.user.fullname)
                    errors.append(err)

            if not errors:
                today = date.today()

                for rcd in q.all():
                    testiruum, testikoht, test, toimumisaeg = rcd
                    testiosa = toimumisaeg.testiosa
                    if not testiruum.algus:
                        errors.append(_("Toimumisaja {s2} algust ei ole määratud.").format(s2=toimumisaeg.tahised))
                    elif testiosa.vastvorm_kood not in (const.VASTVORM_I, const.VASTVORM_SH):
                        errors.append(_("Testiosa {s2} pole mõeldud intervjueerija abil läbi viimiseks.").format(s2=testiosa.tahis))
                    elif not toimumisaeg.on_kogused:
                        errors.append(_("Toimumisaja {s} kogused on eksamikeskuses veel arvutamata.").format(s=toimumisaeg.tahised))
                    elif not toimumisaeg.on_hindamisprotokollid:
                        errors.append(_("Toimumisaja {s} hindamisprotokollid on eksamikeskuses veel loomata.").format(s=toimumisaeg.tahised))
                    elif test.staatus != const.T_STAATUS_KINNITATUD:
                        errors.append(_("Test ei ole Harnos kinnitatud."))            
                    elif test.avaldamistase > const.AVALIK_EKSAM:
                        if test.avalik_alates and test.avalik_alates > today:
                            errors.append(_("Test {id} on avalik alates {s}.").format(id=test_id, s=test.avalik_alates.strftime('%d.%m.%Y')))
                            return
                        elif test.avalik_kuni and test.avalik_kuni < today:
                            errors.append(_("Test {id} oli avalik kuni {s}.").format(id=test_id, s=test.avalik_kuni.strftime('%d.%m.%Y')))

        if errors:
            msg = ' '.join(errors)            
            if test:
                if other_result:
                    err = _("Kuvatakse test {id}, aga see ei vasta otsingutingimustele.").format(id=test_id)
                else:
                    err = _("Test {id} ei vasta otsingutingimustele.").format(id=test_id)
                msg = err + ' ' + msg
            self.warning(msg)

    def __before__(self):
        id = self.request.matchdict.get('id')
        if id:
            self.c.testiruum = model.Testiruum.get(id)

    def _perm_params(self):
        return {'obj': self.c.testiruum}
