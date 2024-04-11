from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class StruktuurController(BaseResourceController):
    """Testi struktuur (jaotumine testiosadeks, alatestideks, testiplokkideks ja ülesanded)
    """
    _permission = 'ekk-testid'

    _MODEL = model.Testiosa
    _EDIT_TEMPLATE = 'ekk/testid/struktuur.mako'
    _INDEX_TEMPLATE = 'ekk/testid/struktuur.mako'
    _ITEM_FORM = forms.ekk.testid.StruktuurForm 
    _get_is_readonly = False

    def _update(self, item):
        order = self.request.params.get('order')
        if order:
            # order on selline: alatest_3,testiplokk_5,alatest_5,testiylesanne_9
            alatest = None
            testiplokk = None
            testiylesanne = None
            d_seq_alatest = dict()
            seq_testiplokk = 0
            seq_testiylesanne = 0
            for name in order.split(','):
                row_type, id = name.split('_')

                if row_type == 'alatest':
                    alatest = model.Alatest.get(id)
                    testiplokk = None
                    assert alatest.testiosa_id == item.id, _("Vale alatest")
                    kursus = alatest.kursus_kood
                    alatest.seq = d_seq_alatest[kursus] = (d_seq_alatest.get(kursus) or 0) + 1
                    seq_testiplokk = 0
                    seq_testiylesanne = 0
                elif row_type == 'testiplokk':
                    testiplokk = model.Testiplokk.get(id)
                    seq_testiplokk += 1

                    testiplokk.seq = seq_testiplokk
                    testiplokk.alatest = alatest
                elif row_type == 'testiylesanne':
                    testiylesanne = model.Testiylesanne.get(id)
                    assert testiylesanne.testiosa_id == item.id, _("Vale testiosa")
                    seq_testiylesanne += 1
                    testiylesanne.seq = seq_testiylesanne
                    testiylesanne.alatest_seq = alatest and alatest.seq or None
                    testiylesanne.testiplokk = testiplokk
                    testiylesanne.alatest = alatest
                else:
                    raise Exception()
            
        # diagnoosivas testis ylesannete kustutamine
        if self.request.params.get('deltasks'):
            try:
                for vy_id in self.request.params.getall('vy_id'):
                    vy = model.Valitudylesanne.get(vy_id)
                    if vy:
                        vy.testiylesanne.delete()
            except sa.exc.IntegrityError as e:
                self.error(_("Ei saa enam kustutada, sest on seotud andmeid"))
                return
        # debug kustutamine
        if self.request.params.get('deltasks2'):
            try:
                for ty_id in self.request.params.getall('ty_id'):
                    ty = model.Testiylesanne.get(ty_id)
                    if ty and ty.testiosa.test_id == self.c.test.id:
                        ty.delete()
            except sa.exc.IntegrityError as e:
                self.error(_("Ei saa enam kustutada, sest on seotud andmeid"))
                return
        model.Session.flush()
        self.c.test.arvuta_pallid()

    def _kontroll(self):
        # paigutame need testiylesanded alatesti alla,
        # mis mingi vea tõttu on ilma alatestita
        for testiosa in self.c.test.testiosad:
            if len(testiosa.alatestid):
                alatest = testiosa.alatestid[0]
                for ty in testiosa.testiylesanded:
                    if not ty.alatest:
                        ty.alatest = alatest
                
        # arvutame testiga saadavate max pallide arvu
        self.c.test.arvuta_pallid()
        self.c.test.count_tahemargid()
        self.c.test.sum_tahemargid()

        # arvutame eri kursuste yhisosa, kui on mitu kursust
        errors = self.c.test.calc_yhisosa()
        return errors

    def _edit(self, item):
        self.set_debug()
        return BaseResourceController._edit(self, item)

    def _edit_kontroll(self, id):
        """Kontrolli ja arvuta
        """
        errors = self._kontroll()
        if errors:
            self.error(errors)

        model.Session.commit()
        return self.render_to_response('/ekk/testid/kontroll.mako')

    def _edit_kinnita(self, id):
        """Kontrolli ja arvuta ja kui klapib, siis kinnita struktuur
        """
        self.c.item = model.Testiosa.get(id)
        rc = True
        if not self.c.item.lotv:
            for ty in self.c.item.testiylesanded:
                if ty.liik == const.TY_LIIK_Y and ty.max_pallid is None:
                    self.error(_("Ei saa kinnitada, sest kõigil ülesannetel ei ole pallide arv määratud"))
                    rc = False
                    break
        if rc:
            errors = self._kontroll()
            if errors:
                self.error(errors)
            else:
                old_staatus_nimi = self.c.test.staatus_nimi
                self.c.test.staatus = const.T_STAATUS_KINNITATUD
                self.c.test.logi(_("Testi olek"),
                                 old_staatus_nimi,
                                 self.c.test.staatus_nimi,
                                 const.LOG_LEVEL_GRANT,
                                 model.Testilogi.TESTILOGI_TYYP_OLEK)
                if self.c.test.diagnoosiv:
                    # kinnitame ka komplektid, kuna selle jaoks eraldi vormi ei ole
                    for osa in self.c.test.testiosad:
                        for kv in osa.komplektivalikud:
                            for k in kv.komplektid:
                                k.staatus = const.K_STAATUS_KINNITATUD                                
                model.Session.commit()
                self.notice('Testi struktuur on kinnitatud')
                self.c.dialog_kinnita = True
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_testiosad', test_id=parent_id))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)

        self.c.lang = self.params_lang()
        if self.c.test:
            if self.c.lang and (self.c.lang == self.c.test.lang or self.c.lang not in self.c.test.keeled):
                self.c.lang = None
        else:
            self.c.lang = None
        super(StruktuurController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.test}

