from eis.lib.baseresource import *
from eis.lib.block import BlockController
_ = i18n._
log = logging.getLogger(__name__)

class YldandmedController(BaseResourceController):

    _permission = 'testid'

    _MODEL = model.Test
    _EDIT_TEMPLATE = 'avalik/testid/yldandmed.mako'
    _ITEM_FORM = forms.avalik.testid.YldandmedForm
    _actions = 'create,new,show,update,delete,edit,download' # võimalikud tegevused    

    def _new(self, item):
        item.skeeled = item.lang = const.LANG_ET
        self.c.test = item
        
    def _delete(self, item):
        try:
            rc = True
            if len(item.sooritajad):
                self.error(_('Testi ei saa kustutada, sest sellel on juba sooritajaid'))
                rc = False
            if not rc:
                return self._redirect('show', item.id)
            item.delete()
        except Exception as e:
            self.error(_('Ei saa kustutada. ')+repr(e))
        else:
            self.success(_('Andmed on kustutatud!'))
            model.Session.commit()

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('avaleht'))

    def _create(self, **kw):
        item = BaseResourceController._create(self,
                                              testityyp=const.TESTITYYP_AVALIK,
                                              testiliik_kood=const.TESTILIIK_AVALIK,
                                              staatus=const.T_STAATUS_KINNITATUD,
                                              lang=const.LANG_ET)
        item.logi('Loomine', None, None, const.LOG_LEVEL_GRANT)

        # testi looja saab kohe testiga seotud isikuks koostaja rollis
        item.add_testiisik(const.GRUPP_T_OMANIK)
        return item

    def _delete_isik(self, id):
        isik_id = self.request.params.get('isik_id')
        isik = model.Testiisik.get(isik_id)
        if isik and isik.test_id == int(id):
            test = model.Test.get(id)
            if len(test.testiisikud) == 1:
                self.error(_('Kõiki omanikke ei saa eemaldada'))
            else:
                test.logi(_('Isiku eemaldamine'),
                          '%s\n%s\n%s' % (isik.kasutajagrupp.nimi,
                                           isik.kasutaja.nimi,
                                           isik.kasutaja.isikukood),
                          None,
                          const.LOG_LEVEL_GRANT)
                isik.delete()
                model.Session.commit()
                self.success(_('Andmed on kustutatud!'))
        return self._redirect('edit', id)

    def _update(self, item, lang=None):
        # salvestatakse andmed
        log.debug('oige_naitamine:%s' % item.oige_naitamine)

        #old_avaldamistase = item.avaldamistase
        old_staatus = item.staatus
        tag = self.form.data.get('aine_kood')
        if model.Klrida.get_str('AINE', tag):
            # aine on klassifikaatorist
            item.aine_kood = tag
            item.aine_muu = None
        else:
            # aine on väljastpoolt klassifikaatorit
            item.aine_kood = None
            item.aine_muu = tag
        item.from_form(self.form.data, self._PREFIX)
        item.oige_naitamine = bool(item.oige_naitamine)
        item.staatus = const.T_STAATUS_KINNITATUD
        item.avaldamistase = const.AVALIK_MAARATUD
        #item.skeeled = ' '.join(self.form.data.get('skeel'))
        item.update_lang_by_y()
        if self.form.data.get('pole_salastatud'):
            item.salastatud = const.SALASTATUD_POLE
        else:
            item.salastatud = const.SALASTATUD_SOORITATAV
        c = self.c
        if c.nimekiri:
            c.nimekiri.alates = alates = self.form.data.get('n_alates')
            c.nimekiri.kuni = kuni = self.form.data.get('n_kuni')

            if item.avalik_kuni and kuni and kuni > item.avalik_kuni:
                err = _("Lahendamise viimane võimalik kuupäev on {kpv}").format(kpv=self.h.str_from_date(item.avalik_kuni))
                raise ValidationError(self, errors={'n_kuni': err})
            
            if c.testiruum:
                if c.nimekiri.alates == c.nimekiri.kuni:
                    # kui läbiviimine toimub yhel päeval,
                    # siis märgime selle testiruumi alguseks,
                    # et saaks arvestada sooritus.kavaaeg ja sooritajate arvu
                    algus = c.nimekiri.alates
                else:
                    algus = None
                if c.testiruum.algus != algus:
                    c.testiruum.muuda_algus(algus)                    
                
        if old_staatus != item.staatus:
            item.logi('Oleku muutmine',
                      model.Klrida.get_str('T_STAATUS', old_staatus) or '',
                      item.staatus_nimi,
                      const.LOG_LEVEL_GRANT)                      
            
        # luuakse kirjed, mis on vajalikud selleks, et saaks
        # avalikus vaates koostatud lihtsaid teste kasutada
        # sarnaselt keerukate EKK testidega

        # kui veel pole, siis luuakse ka testiosa
        testiosa = item.give_testiosa()
        testiosa.vastvorm_kood = const.VASTVORM_KE
        testiosa.piiraeg = self.form.data.get('piiraeg')
        kvalik = testiosa.give_komplektivalik()
        komplekt = kvalik.give_komplekt()
        komplekt.gen_tahis()
        komplekt.staatus = const.K_STAATUS_KINNITATUD
        komplekt.copy_lang(item)
        
    def _update_isik(self, id):            
        """Isiku lisamine ülesandega seotuks
        """
        item = model.Test.get(id)
        grupp_id = int(self.request.params.get('grupp_id'))
        assert grupp_id in (const.GRUPP_T_OMANIK, const.GRUPP_T_TOOVAATAJA), 'imelik grupp'
        
        #kasutajad_id = self.request.params.getall('kasutaja_id')
        isikukoodid = self.request.params.getall('oigus')
        not_added = []
        added = False
        #for kasutaja_id in kasutajad_id:
        for ik in isikukoodid:
            if ik[0] == 'K':
                # olemasolev kasutaja
                kasutaja_id = ik[1:]
                kasutaja = model.Kasutaja.get(kasutaja_id)
                if not kasutaja:
                    # keegi teeb lolli nalja
                    continue
            else:
                # RRist küsitud andmed
                kasutaja = model.Kasutaja.get_by_ik(ik)
                if not kasutaja:
                    eesnimi = self.request.params.get('i%s_eesnimi' % ik)
                    perenimi = self.request.params.get('i%s_perenimi' % ik)
                    kasutaja = model.Kasutaja.add_kasutaja(ik, eesnimi, perenimi)
                    model.Session.flush()
                    
            if item._on_testiisik(kasutaja.id, grupp_id):
                not_added.append(kasutaja.nimi)
            else:
                added = True
                isik = model.Testiisik(test=item,
                                       kasutaja=kasutaja,
                                       kasutajagrupp_id=grupp_id)
                item.testiisikud.append(isik)

                item.logi(_('Testiga seotud isiku lisamine'),
                          None,
                          '%s\n%s' % (kasutaja.nimi,
                                       kasutaja.isikukood),
                          const.LOG_LEVEL_GRANT)

                #if not kasutaja.epost:
                #    # kui kasutajale veel pole sisestatud e-posti aadressi, siis saab sisestada
                #    epost = self.request.params.get('i%s_epost' % ik)
                #    if epost:
                #        kasutaja.epost = epost
                    
        if not_added:
            if len(not_added) == 1:
                buf = _('Kasutaja {s2} on juba lisatud').format(s2=', '.join(not_added))
            else:
                buf = _('Kasutajad {s2} on juba lisatud').format(s2=', '.join(not_added))
            self.error(buf)
        if added:
            model.Session.commit()
            self.success()

        return self._redirect('edit', id)

    def _create_copy(self):            
        """Testi kopeerimine
        """
        copy_id = self.request.params.get('id')
        if copy_id:
            # tehakse koopia olemasolevast 
            item = model.Test.get(copy_id)
            if item and self.c.user.has_permission('testid', const.BT_SHOW, obj=item):
                cp = item.copy()
                cp.staatus = const.T_STAATUS_KINNITATUD
                cp.avaldamistase = const.AVALIK_MAARATUD
                cp_testiosa = cp.give_testiosa()
                cp_komplekt = cp_testiosa.give_komplektivalik().give_komplekt()
                cp_komplekt.staatus = const.K_STAATUS_KINNITATUD
                cp_komplekt.copy_lang(cp)
                cp.logi('Loomine koopiana', None, None, const.LOG_LEVEL_GRANT)
                # testi looja saab kohe testiga seotud isikuks koostaja rollis
                cp.add_testiisik(const.GRUPP_T_OMANIK)
                model.Session.flush()                
                if item.testityyp == const.TESTITYYP_TOO:
                    model.Nimekiri.lisa_nimekiri(self.c.user, 
                                                 const.REGVIIS_KOOL_EIS,
                                                 cp)
                model.Session.commit()
                self.success(_('Testist on tehtud koopia'))
                return self._redirect('edit', id=cp.id)

        self.error(_('Testist koopia tegemine ei olnud võimalik'))
        return self._redirect('new')

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
        url = self.url('testid_edit_yldandmed', id=id, testiruum_id=self.c.testiruum_id)
        return HTTPFound(location=url)

    def _download(self, id, format=None):
        """Näita faili"""
        # eristuskirja allalaadimine
        ek = (model.Session.query(model.Eristuskiri)
              .filter_by(test_id=id)
              .first())
        if not ek or not ek.has_file:
            raise NotFound('Kirjet %s ei leitud' % id)
        return utils.download(ek.filedata, ek.filename, ek.mimetype)

    def __before__(self):
        c = self.c
        c.test_id = self.request.matchdict.get('id')
        c.testiruum_id = self.request.matchdict.get('testiruum_id') or 0
        if int(c.testiruum_id):
            c.testiruum = model.Testiruum.get(c.testiruum_id)
            if c.testiruum:
                c.nimekiri = c.testiruum.nimekiri
            else:
                c.testiruum_id = 0
        if c.test_id:
            c.test = model.Test.get(c.test_id)
        
    def _perm_params(self):
        return {'obj': self.c.test}

