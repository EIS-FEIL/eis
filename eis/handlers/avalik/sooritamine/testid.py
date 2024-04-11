from eis.lib.baseresource import *

_ = i18n._

log = logging.getLogger(__name__)

class TestidController(BaseResourceController):
    """Sooritatavate testide loetelu. 
    Siin on nii suulised kui ka kirjalikud, e- ja p-testid.
    Sooritada saab ainult kirjalikke e-teste, aga ülejäänute kohta saab siin vaadata,
    kus ja millal toimub.
    """
    _permission = 'sooritamine'
    _MODEL = model.Test
    _INDEX_TEMPLATE = 'avalik/sooritamine/otsing.mako'
    _SEARCH_FORM = forms.avalik.sooritamine.OtsingForm 
    _DEFAULT_SORT = '-sooritaja.id' # vaikimisi sortimine
    _ignore_default_params = ['otsi']
    _actions = 'index'
    
    def _query(self):
        q = (model.SessionR.query(model.Test, model.Sooritaja)
             .filter(sa.or_(model.Sooritaja.regviis_kood!=const.REGVIIS_EELVAADE,
                            model.Sooritaja.id==None)))
        return q
    
    def _search_default(self, q):
        return self._search(q)
        
    def _search(self, q):
        """Kui otsitakse testi ID järgi ja leitakse, siis suunatakse kasutaja kohe editisse.
        Muidu otsitakse sooritajaid.
        """
        c = self.c
        c.olen_tugiisik = c.avaldamistase == 11
        if not c.avaldamistase:
            c.avaldamistase = const.AVALIK_POLE

        if c.test_id:
            test = model.Test.get(c.test_id)
            if not test:
                self.error(_("Sellise ID-ga testi pole olemas"))
            elif c.otsi and not c.olen_tugiisik:
                can_do, sooritaja, error = TestSaga(self).get_sooritaja_for(test, c.user.id)
                if not can_do:
                    self.error(error)
                elif c.otsi:
                    if sooritaja:
                        url = self.url('sooritamine_alustamine', test_id=test.id, sooritaja_id=sooritaja.id)
                    else:
                        url = self.url('sooritamine_test', test_id=test.id)
                    return HTTPFound(location=url)
                                                           
        q = q.filter(model.Test.staatus==const.T_STAATUS_KINNITATUD)
        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)
        if c.nimi:
            like_expr = '%' + c.nimi + '%'
            q = q.filter(model.Test.nimi.ilike(like_expr))
        if c.omanik:
            like_expr = '%' + c.omanik + '%'
            q = q.filter(model.Test.testiisikud.any(\
                    model.Testiisik.kasutaja.has(\
                        model.Kasutaja.nimi.ilike(like_expr))))

        # jagatud töö võib ka tehtud olla, sest selle ylesandeid võib uuesti lahendada
        f_s = sa.and_(model.Sooritaja.test_id==model.Test.id,
                      model.Sooritaja.staatus>=const.S_STAATUS_REGATUD,
                      sa.or_(model.Sooritaja.staatus<=const.S_STAATUS_KATKESTATUD,
                             model.Test.testityyp==const.TESTITYYP_TOO),
                      sa.or_(model.Sooritaja.testimiskord_id==None,
                             ~ model.Sooritaja.testimiskord.has(
                                 model.Testimiskord.sooritajad_peidus_kuni>=datetime.now())),
                      ~ model.Sooritaja.nimekiri.has(
                         model.sa.or_(model.Nimekiri.alates>date.today(),
                                      model.Nimekiri.kuni<date.today()))
                      )
        
        if c.olen_tugiisik:
            q = (q.join(model.Sooritaja.test)
                 .join(model.Sooritaja.sooritused)
                 .filter(model.Sooritus.tugiisik_kasutaja_id==c.user.id)
                 .filter(f_s)
                 )
        elif c.avaldamistase == const.AVALIK_SOORITAJAD:
            # kõigile lahendamiseks testid
            dt = date.today()
            q = q.filter(sa.and_(model.Test.avaldamistase==const.AVALIK_SOORITAJAD,
                                 sa.or_(model.Test.avalik_alates <= dt, 
                                        model.Test.avalik_alates == None),
                                 sa.or_(model.Test.avalik_kuni >= dt,
                                        model.Test.avalik_kuni == None)))

            f_s = sa.and_(f_s, model.Sooritaja.kasutaja_id==c.user.id)
            q = q.outerjoin((model.Sooritaja, f_s))

        else:
            # mulle suunatud, const.AVALIK_POLE
            f_s = sa.and_(f_s, model.Sooritaja.kasutaja_id==c.user.id)
            q = q.join((model.Sooritaja, f_s))

            # osalemine on nähtav või
            # olen ise sooritaja ilma tugiisikuta)
            q = q.filter(sa.or_(
                model.Sooritaja.testimiskord.has(
                    model.Testimiskord.osalemise_naitamine==True),
                sa.and_(model.Sooritaja.testimiskord_id==None,
                        model.Test.osalemise_peitmine==False),
                model.Sooritaja.sooritused.any(
                    model.Sooritus.tugiisik_kasutaja_id==None)
                ))

            # kui tuli avalehelt lingiga
            if c.too == 'y':
                q = q.filter(model.Test.testityyp==const.TESTITYYP_TOO)
            elif c.too == 'n':
                q = q.filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_EKK)))
                
        # kui testimiskord_id või test_id võeti mälust, siis ei suunatud kohe ymber
        # kuvame testi loetelus
        if c.testimiskord_id:
            q = q.filter(model.Test.testimiskorrad.any(
                model.Testimiskord.id==c.testimiskord_id))
        elif c.test_id:
            q = q.filter(model.Test.id==c.test_id)
        return q

    def _showlist(self):
        """Otsingu tulemuste kuvamine.
        """
        if self.request.params.get('partial'):
            if self.c.avaldamistase == const.AVALIK_SOORITAJAD:
                return self.render_to_response('/avalik/sooritamine/testid_list.mako')
            else:
                return self.render_to_response('/avalik/sooritamine/suunamised_list.mako')
        else:
            return self.render_to_response(self._INDEX_TEMPLATE)

