from eis.lib.baseresource import *
import eis.lib.regpiirang as regpiirang
from eis.handlers.avalik.regamine.avaldus.testid import suuna_kohtaeg, save_vvkohad
_ = i18n._

log = logging.getLogger(__name__)

class OtsitestidController(BaseResourceController):
    """Testide otsimine dialoogiaknas.
    """
    _permission = 'nimekirjad'
    _MODEL = model.Testimiskord
    _INDEX_TEMPLATE = 'avalik/nimekirjad/avaldus.otsitestid.mako'
    _DEFAULT_SORT = 'test.nimi' # vaikimisi sortimine
    _no_paginate = True
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        c.regpiirang = regpiirang
        if c.testiliik:
            if c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                q = q.filter(model.Test.testiliik_kood.in_((const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV)))
            else:
                q = q.filter(model.Test.testiliik_kood==c.testiliik)
        if not c.testiliik or c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            opilane = c.kasutaja.opilane
            if opilane and opilane.klass in ('7','8','9'):
                # ES-1174 blokeerida 7.-9. kl õpilaste riigieksamitele regamine
                q = q.filter(model.Test.testiliik_kood!=const.TESTILIIK_RIIGIEKSAM)
        return q

    def _search_default(self, q):
        return self._search(q)

    def _query(self):
        d = date.today()
        koht_id = self.c.user.koht_id
        q = (model.Testimiskord.query
             .join(model.Testimiskord.test)
             .filter(sa.or_(model.Testimiskord.reg_kool_eis==True,
                            sa.and_(model.Testimiskord.reg_kool_valitud==True,
                                    sa.exists().where(sa.and_(
                                        model.Regkoht_kord.koht_id==koht_id,
                                        model.Regkoht_kord.testimiskord_id==model.Testimiskord.id))
                                        )
             ))
             .filter(model.Testimiskord.reg_kool_alates<=d)
             .filter(model.Testimiskord.reg_kool_kuni>=d)
             .filter(~ model.Testimiskord.sooritajad.any(
                 sa.and_(model.Sooritaja.kasutaja_id==self.c.kasutaja.id,
                         model.Sooritaja.staatus!=const.S_STAATUS_TYHISTATUD)))
            )
        return q

    def _create(self):
        """Testide lisamine valitud testide sekka
        """
        c = self.c
        kasutaja = self.c.kasutaja
        params = self.request.params
        c.testiliik = params.get('testiliik')
        esitaja_kasutaja_id = c.user.id
        esitaja_koht_id = c.user.koht_id
        opilane = kasutaja.opilane
        errors = {}
        # valiti teste
        korrad = [model.Testimiskord.get(kord_id) for kord_id in params.getall('valik_id')]
        for kord in korrad:
            kord_id = kord.id
            lang = params.get('lang_%s' % kord_id)
            piirkond_id = params.get('piirkond_id_%s' % kord_id)
            piirkond_id = piirkond_id and int(piirkond_id) or None
            kohtaeg = params.get('kohtaeg_%s' % kord_id)
            vvkohad_id = params.getall('vvk_%s' % kord_id)
            vvk_oma = params.get('vvk_oma_%s' % kord_id)
            kursus = params.get('kursus_%s' % kord_id)
            err = None
            test = kord.test
            varemlopetanu = not opilane or opilane.on_lopetanud
            if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
                err = regpiirang.reg_r_lisaeksam(self, kasutaja.id, test, kord)
                if not err and test.aine_kood == const.AINE_EN:
                    # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                    err = regpiirang.reg_rven_cae(self, kasutaja.id, test, korrad)

            elif test.testiliik_kood == const.TESTILIIK_RV and kord.cae_eeltest:
                # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                err = regpiirang.reg_rven_cae(self, kasutaja.id, test, korrad)
                if not err:
                    err = regpiirang.reg_rv_cae(self, kasutaja.id, test, kord)

            # kool peab saama sisseastumiseksamile regada ka muid peale 9. kl õpilaste
            #elif test.testiliik_kood == const.TESTILIIK_SISSE:
            #    err = regpiirang.reg_sisse(self, kasutaja, test)

            if not err and test.aine_kood == const.AINE_ET2:
                err = regpiirang.reg_et2(self, kasutaja, test, opilane)
            if not err and kord.reg_kohavalik and not kohtaeg:
                err = _("Palun valida soorituskoht!")
            if not err and kord.reg_kohavalik and kord.regkohad and not vvkohad_id:
                err = _("Palun valida õppeasutused, millele avaldatakse testitulemused")

            if err:
                self.error(err)
                continue
            if test.testiliik_kood in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV) and varemlopetanu:
                if not piirkond_id:
                    errors['piirkond_id_%s' % kord_id] = _("Palun valida piirkond")
                    continue
                
            added, sooritaja = model.Sooritaja.registreeri(kasutaja, 
                                                           test.id, 
                                                           kord, 
                                                           lang, 
                                                           piirkond_id, 
                                                           const.REGVIIS_KOOL_EIS,
                                                           esitaja_kasutaja_id, 
                                                           esitaja_koht_id)
            if sooritaja:
                sooritaja.reg_markus = self.request.params.get('reg_markus_%s' % kord_id)           
                sooritaja.soovib_konsultatsiooni = bool(self.request.params.get('soovib_konsultatsiooni_%s' % kord_id))
                sooritaja.kursus_kood = kursus
                # salvestame koolid, kes võivad tulemusi vaadata
                save_vvkohad(sooritaja, vvkohad_id, vvk_oma, opilane, c.user.koht_id)
                if kord.reg_kohavalik:
                    # kui regamisel valitakse esimese testiosa soorituskoht ja aeg
                    if not suuna_kohtaeg(self, sooritaja, kohtaeg):
                        # lisati self.error
                        break

                sooritaja.nimekiri = model.Nimekiri.give_nimekiri(c.user.koht_id, test, kord_id)
            if not sooritaja:
                self.error(_('Kasutajat ei saa testile "{s}" rohkem registreerida').format(s=kord.test.nimi))

        if errors:
            self.form.errors = errors
            if not self.has_errors():
                self.error(_("Palun kõrvaldada vead"))
        if self.has_errors():
            model.Session.rollback()
            q = self._order(self._search(self._query()))
            c.items = self._paginate(q)
            
            html = self.form.render(self._INDEX_TEMPLATE,
                                    extra_info=self.response_dict)
            return Response(html)            
        else:    
            model.Session.commit()
            self.success()
            return HTTPFound(location=self.url('nimekirjad_avaldus_testid',
                                               id=kasutaja.id,
                                               testiliik=c.testiliik))


    def __before__(self):
        self.c.kasutaja = model.Kasutaja.get(self.request.matchdict.get('kasutaja_id'))

