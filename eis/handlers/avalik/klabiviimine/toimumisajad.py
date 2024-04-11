from eis.lib.baseresource import *
_ = i18n._
from eis.lib.examclient import ExamClient
from eis.handlers.avalik.klabiviimine.labiviimised import LabiviimisedController

log = logging.getLogger(__name__)

class ToimumisajadController(LabiviimisedController):
    """Testimiskorraga kirjalike e-testide otsimine läbiviimiseks.
    """
    _permission = 'testiadmin'
    _INDEX_TEMPLATE = 'avalik/klabiviimine/toimumisajad.mako'
    _LIST_TEMPLATE = 'avalik/klabiviimine/toimumisajad_list.mako'
    _EDIT_TEMPLATE = 'avalik/klabiviimine/toimumisaeg.labiviimine.mako' 
    _SEARCH_FORM = forms.avalik.labiviimine.ToimumisajadForm 
    _DEFAULT_SORT = 'testiruum.id'
    
    def _query(self):
        """Läbiviimise õigus on sellistele testidele:
        test.staatus=T_STAATUS_KINNITATUD
        test.avaldamistase:
        AVALIK_SOORITAJAD (tohivad kõik kasutada),
        AVALIK_OPETAJAD (tohivad kõik pedagoogid kasutada),
        AVALIK_TEST (testiisikud, kes on läbiviijad ja on toimumisaeg)
        AVALIK_MAARATUD (testiisikud, kes on omanikud)
        AVALIK_MAARATUD (tesiisikud, kes on korraldajad)        
        """
        if not self.c.user.koht_id:
            self.error(_("Soorituskoht on määramata"))
            return None

        q = (model.Session.query(model.Testiruum.id,
                                 model.Testikoht.tahis,
                                 model.Testiruum.tahis,
                                 model.Koht.nimi,
                                 model.Ruum.tahis,
                                 model.Testiosa.tahis,
                                 model.Toimumisaeg.tahised,
                                 model.Test.nimi,
                                 model.Testiruum.algus)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.toimumisaeg)
             .join(model.Toimumisaeg.testimiskord)
             .join(model.Testimiskord.test)
             .join(model.Toimumisaeg.testiosa)
             .join(model.Testikoht.koht)
             .outerjoin(model.Testiruum.ruum))
        return q

    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        Kui soovitakse, et sellist vaikimisi otsingut ei tehtaks,
        siis tuleb tagastada None.
        """
        return self._search(q)
    
    def _search(self, q0):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if not q0:
            return
        today = date.today()
        vastvorm_e = (const.VASTVORM_KE, const.VASTVORM_SE)
        q = (q0.filter(model.Testiosa.vastvorm_kood.in_(vastvorm_e))
             .filter(model.Test.staatus==const.T_STAATUS_KINNITATUD)
             .filter(model.Toimumisaeg.on_hindamisprotokollid==1)
             .filter(sa.or_(model.Test.avaldamistase==const.AVALIK_EKSAM,
                            sa.and_(model.Test.avaldamistase>const.AVALIK_EKSAM,
                                    sa.or_(model.Test.avalik_alates <= today,
                                           model.Test.avalik_alates == None),
                                    sa.or_(model.Test.avalik_kuni > today + timedelta(1),
                                           model.Test.avalik_kuni == None))
                            ))
             .filter(model.Testiruum.algus >= today)
             .filter(sa.or_(model.Testimiskord.sooritajad_peidus_kuni==None,
                            model.Testimiskord.sooritajad_peidus_kuni<datetime.now()))
             )
        q = (q.join(model.Testiruum.labiviijad)
             .filter(model.Labiviija.kasutaja_id==c.user.id)
             .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN))

        if c.test_id:
            q = q.filter(model.Test.id==c.test_id)
            q_test = q
            
        if c.nimi:
            like_expr = '%%%s%%' % c.nimi
            q = q.filter(model.Test.nimi.ilike(like_expr))
        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)

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
        q1 = model.Session.query(model.Test).filter_by(id=c.test_id)
        test = q1.first()
        if not test:
            errors.append(_("Test pole avalik."))
        else:
            today = date.today()
            if test.avaldamistase > const.AVALIK_EKSAM:
                # AVALIK: LITSENTS, SOORITAJAD, OPETAJAD, MAARATUD
                if test.avalik_alates and test.avalik_alates > today:
                    errors.append(_("Test {id} on avalik alates {s}.").format(id=test.id, s=test.avalik_alates.strftime('%d.%m.%Y')))
                elif test.avalik_kuni and test.avalik_kuni < today:
                    errors.append(_("Test {id} oli avalik kuni {s}.").format(id=test.id, s=test.avalik_kuni.strftime('%d.%m.%Y')))

            if test.avaldamistase != const.AVALIK_EKSAM:
                if c.user.has_permission('omanimekirjad', const.BT_SHOW, test=test):
                    url = self.url('test_nimekirjad',test_id=test.id, testiruum_id=0)
                    errors.append(_('See pole tsentraalselt korraldatud test, aga seda saab kasutada <a href="{url}">töölaua kaudu</a>.').format(url=url))
                else:
                    errors.append(_("See pole tsentraalselt korraldatud test.").format(id=test.id))
                
            if not errors and  test.staatus != const.T_STAATUS_KINNITATUD:
                errors.append(_("Test ei ole Harnos kinnitatud."))            

            if not errors:
                q = (q.filter(model.Test.id==test.id)
                     .join(model.Testiruum.labiviijad)
                     .filter(model.Labiviija.kasutaja_id==self.c.user.id)
                     .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
                     )
                if q.count() == 0:
                    errors.append(_("Kasutaja {s} ei ole antud soorituskohas määratud antud testi administraatoriks").format(s=self.c.user.fullname))

        if not errors:
            for rcd in q.all():
                tr_id, tk_tahis, tr_tahis, koht_nimi, r_tahis, osa_tahis, ta_tahised, t_nimi, tr_algus = rcd
                testiruum = model.Testiruum.get(tr_id)
                testikoht = testiruum.testikoht
                toimumisaeg = testikoht.toimumisaeg
                testiosa = toimumisaeg.testiosa
                test = testiosa.test
                if not testiruum.algus:
                    errors.append(_("Testiruum {s1}: toimumisaja {s2} algust ei ole määratud.").format(s1=testiruum.tahis, s2=ta_tahised))
                elif testiruum.algus.date() < date.today():
                    errors.append(_("Testiruum {s1}: toimumisaja {s2} kuupäev {s3} on juba möödas!").format(
                        s1=testiruum.tahis, s2=ta_tahised, s3=testiruum.algus.strftime('%d.%m.%Y')))

                elif testiosa.vastvorm_kood not in (const.VASTVORM_KE, const.VASTVORM_SE):
                    errors.append(_("Testiruum {s1}: toimumisaeg {s2} ei ole interaktsioonis arvutiga.").format(
                        s1=testiruum.tahis, s2=ta_tahised))
                elif not toimumisaeg.on_kogused:
                    errors.append(_("Toimumisaja {s} kogused on eksamikeskuses veel arvutamata.").format(s=ta_tahised))
                elif not toimumisaeg.on_hindamisprotokollid:
                    errors.append(_("Toimumisaja {s} hindamisprotokollid on eksamikeskuses veel loomata.").format(s=ta_tahised))

        if not errors:
            # test on kättesaadav, aga ei vasta otsingutingimustele
            def join_ja(li):
                if len(li) > 1:
                    return ', '.join(li[:-1]) + _(" ja ") + li[-1]
                elif len(li) == 1:
                    return li[-1]
                else:
                    return ''

            ferrors = []
            if c.nimi:
                like_expr = '%%%s%%' % c.nimi
                q = (model.Session.query(model.Test)
                     .filter_by(id=test.id)
                     .filter(model.Test.nimi.like(like_expr)))
                if q.count() == 0:
                    ferrors.append(_("nimetus"))
            if c.aine:
                if test.aine_kood != c.aine:
                    ferrors.append(_("õppeaine"))
            if ferrors:
                errors.append(_("Testil on erinev {omadused}.").format(omadused=join_ja(ferrors)))
        
        if errors:
            if other_result:
                err = _("Kuvatakse test {id}, aga see ei vasta otsingutingimustele.").format(id=test.id)
            else:
                err = _("Test {id} ei vasta otsingutingimustele.").format(id=c.test_id)
            msg = err + ' ' + ' '.join(errors)
            self.warning(msg)
        
    def _edit(self, item):
        LabiviimisedController._edit(self, item)
        if self.c.veel_ei_toimu:
            algus = self.c.testiruum.algus
            msg = _("Test viiakse läbi {d}").format(d=self.h.str_from_date(algus))
            self.notice(msg)
            
    def _get_sooritused(self):
        self._refresh_sooritused()
        q = (model.Sooritus.query
             .filter(model.Sooritus.testikoht_id==self.c.testikoht.id)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             .filter(model.Sooritus.staatus>=const.S_STAATUS_REGATUD)
             )
        if self.c.testiruum:
            q = q.filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
        return q.order_by(model.Sooritus.tahis).all()

    def _refresh_sooritused(self):
        testikoht_id = self.c.testikoht.id
        testiruum_id = self.c.testiruum and self.c.testiruum.id or None
        q = (model.Session.query(sa.distinct(model.Sooritaja.klaster_id))
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritaja.klaster_id!=None)
             .filter(model.Sooritus.testikoht_id==testikoht_id))
        if testiruum_id:
            q = q.filter(model.Sooritus.testiruum_id==testiruum_id)
        for klaster_id, in q.all():
            host = model.Klaster.get_host(klaster_id)
            log.debug(f'host{host}/{klaster_id}')
            if host:
                ExamClient(self, host).refresh_sooritused(testikoht_id, testiruum_id)
        # võiks teha commiti, aga ei tee, et ei tekiks deadlock
        #model.Session.commit()
    
    def _check_sooritus(self, rcd):
        """Kontrollitakse, kas parameeter on lubatud sooritus.
        """
        rc = rcd.testiruum and rcd.testiruum == self.c.testiruum
        if not rc:
            log.debug('testikoht.koht_id=%s,user.koht_id=%s, toimumisaeg.id=%s, self.c.toimumisaeg.id=%s' % (rcd.testikoht and rcd.testikoht.koht_id, self.c.user.koht_id, rcd.toimumisaeg.id, self.c.toimumisaeg.id)) 

        return rc

    def _show_checkprot(self, id):
        "Kontrollitakse, kas toimumise protokoll on täidetud"
        c = self.c
        q = (model.SessionR.query(model.Labiviija.id)
             .filter_by(testiruum_id=c.testiruum.id)
             .filter(model.Labiviija.staatus==const.L_STAATUS_MAARATUD))
        taidetud = q.count() == 0
        if taidetud:
            q = (model.SessionR.query(model.Sooritus.id)
                 .filter_by(testiruum_id=c.testiruum.id)
                 .filter(model.Sooritus.staatus.in_((const.S_STAATUS_REGATUD,
                                                     const.S_STAATUS_ALUSTAMATA,
                                                     const.S_STAATUS_POOLELI,
                                                     const.S_STAATUS_KATKESTATUD)))
                 )
            taidetud = q.count() == 0
        res = {'rc': not taidetud}
        # rc on True, kui on veel vaja protokolli täita
        return Response(json_body=res)
    
    def _edit_sooritaja(self, id):
        return self.render_to_response('avalik/klabiviimine/sooritajad.mako')

    def _update_sooritaja(self, id):
        """Sooritajate lisamine testile registreeritud õppurite seast.
        """
        sooritused_id = list(map(int, self.request.params.getall('sooritus_id')))
        testiosa_id = self.c.toimumisaeg.testiosa_id
        cnt = 0
        for sooritus_id in sooritused_id:
            sooritus = model.Sooritus.get(sooritus_id)
            if sooritus:
                assert sooritus.sooritaja.testimiskord_id == \
                    self.c.toimumisaeg.testimiskord_id and \
                    sooritus.testiosa == self.c.toimumisaeg.testiosa

                if sooritus.staatus >= const.S_STAATUS_POOLELI:
                    # on juba alustanud
                    continue
                sooritus.testikoht_id = self.c.testikoht.id
                if self.c.testiruum:
                    sooritus.testiruum_id = self.c.testiruum.id
                cnt += 1
        model.Session.commit()
        self.success(_("Lisatud {n} sooritajat").format(n=cnt))
        return self._after_update()

    def __before__(self):
        c = self.c
        testiruum_id = self.request.matchdict.get('id')
        if testiruum_id:
            c.testiruum = model.Testiruum.get(testiruum_id)
            if c.testiruum:
                c.toimumisaeg = c.testiruum.testikoht.toimumisaeg
                c.testiosa = c.testiruum.testikoht.testiosa
                c.test = c.testiosa.test
                algus = c.testiruum.algus

                # enne alguse kuupäeva ei tohi alustada
                c.veel_ei_toimu = algus.date() > date.today()
        LabiviimisedController.__before__(self)

    def _after_update(self):
        return HTTPFound(location=self.url('klabiviimine_edit_toimumisaeg', id=self.c.testiruum.id))

    def _perm_params(self):
        # kontrollida testi läbiviimisõigus selles kohas
        c = self.c
        if c.toimumisaeg and c.toimumisaeg.testimiskord.sooritajad_peidus:
            return False
        return {'obj': c.testiruum}

