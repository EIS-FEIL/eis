from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class YlesandedController(BaseResourceController):

    _permission = 'ylesanded'

    _MODEL = model.Ylesanne
    _INDEX_TEMPLATE = 'ekk/ylesanded/otsing.mako'
    _EDIT_TEMPLATE = 'ekk/ylesanded/yldandmed.mako' 
    _LIST_TEMPLATE = 'ekk/ylesanded/otsing_list.mako'
    _SEARCH_FORM = forms.ekk.ylesanded.OtsingForm 
    _ITEM_FORM = forms.ekk.ylesanded.YldandmedForm
    _DEFAULT_SORT = 'ylesanne.id' # vaikimisi sortimine
    _get_is_readonly = False

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.idr:
            flt = forms.validators.IDRange.filter(c.idr, model.Ylesanne.id)
            if flt is not None:
                q = q.filter(flt)
        if c.id:
            q = q.filter_by(id=c.id)
        if c.marksona:
            like_expr = '%%%s%%' % c.marksona
            #q = q.filter(sa.or_(model.Ylesanne.marksonad.ilike(like_expr),
            #                    model.Ylesanne.nimi.ilike(like_expr)))
            Klaine = sa.orm.aliased(model.Klrida, name='klaine')
            Klteema = sa.orm.aliased(model.Klrida, name='klteema')
            Klalateema = sa.orm.aliased(model.Klrida, name='klalateema')
            q = q.filter(sa.or_(model.Ylesanne.marksonad.ilike(like_expr),
                                model.Ylesanne.trans.any(model.T_Ylesanne.marksonad.ilike(like_expr)),
                                model.Ylesanne.nimi.ilike(like_expr),
                                model.Ylesanne.ylesandeained.any(
                                    model.Ylesandeaine.ylesandeteemad.any(
                                        sa.and_(Klaine.klassifikaator_kood=='AINE',
                                                Klaine.kood==model.Ylesandeaine.aine_kood,
                                                Klaine.id==Klteema.ylem_id,
                                                Klteema.klassifikaator_kood=='TEEMA',
                                                Klteema.kood==model.Ylesandeteema.teema_kood,
                                                sa.or_(Klteema.nimi.ilike(like_expr),
                                                       sa.exists().where(
                                                           sa.and_(Klalateema.klassifikaator_kood=='ALATEEMA',
                                                                   Klalateema.kood==model.Ylesandeteema.alateema_kood,
                                                                   Klalateema.ylem_id==Klteema.id,
                                                                   Klalateema.nimi.ilike(like_expr))
                                                           )
                                                       )
                                                )
                                        )
                                    )
                                )
                         )

        if c.alates:
            q = q.filter(model.Ylesanne.created >= c.alates)
        if c.kuni:
            kuni = c.kuni + timedelta(1)
            q = q.filter(model.Ylesanne.created < kuni)

        if c.raskus_alates:
            q = q.filter(model.Ylesanne.raskus >= c.raskus_alates)
        if c.raskus_kuni:
            q = q.filter(model.Ylesanne.raskus <= c.raskus_kuni)            

        if c.lahendatavus_alates:
            q = q.filter(model.Ylesanne.lahendatavus >= c.lahendatavus_alates)
        if c.lahendatavus_kuni:
            q = q.filter(model.Ylesanne.lahendatavus <= c.lahendatavus_kuni)

        if c.vastvorm:
            q = q.filter_by(vastvorm_kood=c.vastvorm)
        if c.aine:
            f_aine = model.Ylesandeaine.aine_kood == c.aine
            if c.teema:
                teema = model.Klrida.get_by_kood('TEEMA', kood=c.teema, ylem_kood=c.aine)            
                c.teema_id = teema and teema.id
                if c.alateema:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(sa.and_(model.Ylesandeteema.teema_kood==c.teema,
                                            model.Ylesandeteema.alateema_kood==c.alateema)
                                    )
                               )
                else:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(model.Ylesandeteema.teema_kood==c.teema))
                f_aine = sa.and_(f_aine, f_teema)

            if c.opitulemus_id:
                f_aine = sa.and_(f_aine, model.Ylesandeaine.ylopitulemused.any(
                    model.Ylopitulemus.opitulemus_klrida_id==c.opitulemus_id))
            if c.oskus:
                f_aine = sa.and_(f_aine, model.Ylesandeaine.oskus_kood==c.oskus)
            q = q.filter(model.Ylesanne.ylesandeained.any(f_aine))
          
        if c.aste:
            aste_bit = c.opt.aste_bit(c.aste) or 0
            q = q.filter(model.Ylesanne.aste_mask.op('&')(aste_bit) > 0)                                    
        if c.mote:
            q = q.filter(model.Ylesanne.motlemistasandid\
                         .any(model.Motlemistasand.kood==c.mote))        
        if c.ylkogu_id:
            q = q.filter(model.Ylesanne.koguylesanded.any(
                model.Koguylesanne.ylesandekogu_id==c.ylkogu_id))
        if c.keeletase:
            q = q.filter_by(keeletase_kood=c.keeletase)

        if c.lang:
            q = q.filter(model.Ylesanne.skeeled.like('%' + c.lang + '%'))            

        if c.kysimus:
            q = q.filter(model.Ylesanne.sisuplokid\
                             .any(model.Sisuplokk.tyyp==c.kysimus))
        if c.filename:
            q = q.filter(model.Ylesanne.sisuplokid.any(
                model.Sisuplokk.sisuobjektid.any(\
                    model.Sisuobjekt.filename.ilike(c.filename))
                ))

        if c.vahend:
            q = q.filter(model.Ylesanne.vahendid\
                             .any(model.Vahend.vahend_kood==c.vahend))
        if c.kvaliteet:
            q = q.filter(model.Ylesanne.kvaliteet_kood==c.kvaliteet)
            
        if c.staatus:
            if len(c.staatus) > 1:
                q = q.filter(sa.or_(*[model.Ylesanne.staatus==v for v in c.staatus]))
            else:
                q = q.filter(model.Ylesanne.staatus == c.staatus[0])
        else:
            vaikimisi_peidus = (const.Y_STAATUS_ARHIIV,
                                const.Y_STAATUS_MALL,
                                const.Y_STAATUS_AV_MALL)
            q = q.filter(~ model.Ylesanne.staatus.in_(vaikimisi_peidus))

        # kas oma ylesanded või EKK ylesanded?
        lif = []
        if c.user.has_permission('ylesanded', const.BT_INDEX, gtyyp=const.USER_TYPE_AV):
            # võib vaadata avaliku vaate ylesandeid, kui on individuaalne õigus
            today = date.today()
            fst = sa.and_(model.Ylesanne.staatus.in_(const.Y_ST_AV),
                          model.Ylesanne.ylesandeisikud.any(sa.and_(
                              model.Ylesandeisik.kasutaja_id==c.user.id,
                              model.Ylesandeisik.kehtib_alates<=today,
                              model.Ylesandeisik.kehtib_kuni>=today))
                              )
            lif.append(fst)
        if c.user.has_permission('ylesanded', const.BT_INDEX, gtyyp=const.USER_TYPE_EKK):
            # võib otsida kõigi EKK ylesannete seast
            lif.append(~ model.Ylesanne.staatus.in_(const.Y_ST_AV))
        if not lif:
            # pole mingit õigust
            return
        elif len(lif) == 1:
            q = q.filter(lif[0])
        elif len(lif) > 1:
            q = q.filter(sa.or_(*lif))            
        
        if c.ptest:
            q = q.filter_by(ptest=True)
        if c.etest:
            q = q.filter_by(etest=True)
        if c.adaptiivne:
            q = q.filter_by(adaptiivne=True)
                
        if c.koostaja:
            like_expr = '%%%s%%' % c.koostaja
            q = q.filter(model.Ylesanne.ylesandeisikud.any(
                    sa.and_(model.Ylesandeisik.kasutajagrupp_id==const.GRUPP_Y_KOOSTAJA,
                            model.Ylesandeisik.kasutaja.has(model.Kasutaja.nimi.ilike(like_expr)))
                    ))
        if c.arvutihinnatav:
            # pole UI
            q = q.filter(model.Ylesanne.arvutihinnatav==True)
        if c.lukus:
            # pole UI
            if c.lukus == '0':
                lukus = None
            else:
                lukus = int(c.lukus)
            q = q.filter(model.Ylesanne.lukus==lukus)
            
        if c.csv:
            return self._index_csv(q)
        return q

    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        """
        return None

    def _prepare_header(self):
        header = [_("Ülesande ID"),
                  _("Nimetus"),
                  _("Õppeaine"),
                  _("Teema"),
                  _("Vastamise vorm"),
                  _("P-test"),
                  _("E-test"),
                  _("Toorpunktid"),
                  _("Koostaja"),
                  ]
        return header
    
    def _prepare_item(self, rcd, n):
        li = []
        for yi in rcd.ylesandeisikud:
            if yi.kasutajagrupp_id == const.GRUPP_Y_KOOSTAJA:
                li.append(yi.kasutaja.nimi)
        ained = []
        teemad = []
        for ya in rcd.ylesandeained:
            ained.append(ya.aine_nimi or ya.aine_kood)
            teemad.extend([r.teema_nimi for r in ya.ylesandeteemad if r.teema_nimi])
        item = [rcd.id,
                rcd.nimi,
                ', '.join(ained),
                ', '.join(teemad),
                rcd.vastvorm_nimi,
                rcd.ptest and 'Jah' or 'Ei',
                rcd.etest and 'Jah' or 'Ei',
                self.h.fstr(rcd.max_pallid),
                ', '.join(li)
                ]
        return item

    def _new_d(self):
        c = self.c
        copy_id = self.request.params.get('id')
        if copy_id:
            # tehakse koopia olemasolevast ülesandest
            item = model.Ylesanne.get(copy_id)
            c.item = item.copy()
            try:
                BlockController.after_copy_task(c.item, self)
            except ValidationError as ex:
                self.error(_("Ülesannet {id} ei saa kopeerida, sest selles on vigu").format(id=copy_id))
            else:
                c.item.logi(_("Loomine koopiana"), 'Alusülesanne %s' % copy_id, None, const.LOG_LEVEL_GRANT)
                model.Session.commit()
                self.success(_("Ülesanne on kopeeritud!"))
            return self.response_dict
        else:
            return BaseResourceController._new_d(self)

    def _new(self, item):
        item.ptest = True
        item.etest = True
        item.arvutihinnatav = True
        item.vastvorm_kood = const.VASTVORM_KE
        item.hindamine_kood = const.HINDAMINE_OBJ
        item.pallemaara = False
        item.max_pallid = 0
        self._set_st(item)

    def _set_st(self, item):
        if self.c.user.has_permission('ylesanded', const.BT_CREATE, gtyyp=const.USER_TYPE_EKK):
            item.staatus = const.Y_STAATUS_KOOSTAMISEL
        elif self.c.user.has_permission('ylesanded', const.BT_CREATE, gtyyp=const.USER_TYPE_AV):
            item.staatus = const.Y_STAATUS_AV_KOOSTAMISEL
        
    def _create(self, **kw):
        item = BaseResourceController._create(self)
        self._set_st(item)
        item.logi('Loomine', None, None, const.LOG_LEVEL_GRANT)
        return item

    def _delete(self, item):
        if len(item.valitudylesanded) > 0:
            self.error(_("Ülesannet ei saa kustutada, sest see on testi koosseisus"))
            return self._after_update(item.id)
        return BaseResourceController._delete(self, item)

    def _update(self, item):
        old_keeled = item.keeled
        old_lang = item.lang
        BaseResourceController._update(self, item)

        if self.c.user.has_permission('ylkvaliteet', const.BT_UPDATE, item):
            kvaliteet = self.request.params.get('kvaliteet_kood')
            # kui kasutajal on õigus
            item.kvaliteet_kood = kvaliteet or None

        self._update_kooliastmed(item)
        self._update_ylesandeained(item)
        self._update_testiliigid(item)
        self._update_motlemistasandid(item)
        self._update_tolkekeeled(item, old_lang, old_keeled)
        self._update_vahendid(item)
        self._update_koguylesanded(item)

        kasutliigid = [{'kasutliik_kood': r} for r in self.form.data.get('kasutliik_kood')]
        ctrl = BaseGridController(item.kasutliigid, model.Kasutliik, None, self, pkey='kasutliik_kood')        
        ctrl.save(kasutliigid)        

        # if self.c.user.has_permission('ylesandetahemargid', const.BT_UPDATE, item):
        #     on_tahemargid = self.form.data['on_tahemargid']
        #     if on_tahemargid and not item.on_tahemargid:
        #         # ylesanne märgiti tähemärkide lugemiseks
        #         item.count_tahemargid()
        #     item.on_tahemargid = on_tahemargid

    def _update_kooliastmed(self, item):
        # salvestame kooliastmed, kodeerides need maskiks
        peamine_aste_kood = self.form.data.get('f_aste_kood')
        kooliastmed = self.form.data.get('v_aste_kood')
        if peamine_aste_kood not in kooliastmed:
            kooliastmed = kooliastmed + [peamine_aste_kood]
        mask = 0
        for kood in kooliastmed:
            mask += self.c.opt.aste_bit(kood) or 0
        if mask != item.aste_mask:
            item.aste_mask = mask

    def _update_ylesandeained(self, item):
        yained = {r.id: r for r in item.ylesandeained}
        for seq, data in enumerate(self.form.data.get('ya')):
            ya_id = data['id']
            try:
                yaine = yained.pop(ya_id)
            except KeyError:
                yaine = model.Ylesandeaine(ylesanne=item)
            yaine.aine_kood = data['aine_kood']
            yaine.oskus_kood = data['oskus_kood']
            yaine.seq = seq
            
            # salvestame teemad ja valdkonnad
            teemad2 = data.get('teemad2')
            for r in list(yaine.ylesandeteemad):
                key = r.teema_kood
                if r.alateema_kood:
                    key += '.' + r.alateema_kood
                try:
                    teemad2.remove(key)
                    # oli alles
                except ValueError:
                    r.delete()
            for key in teemad2:
                koodid = key.split('.')
                r = model.Ylesandeteema(teema_kood=koodid[0],
                                        alateema_kood=len(koodid) > 1 and koodid[1] or None)
                yaine.ylesandeteemad.append(r)

            # salvestame õpitulemused
            opitulemused = data.get('opitulemused')
            for r in list(yaine.ylopitulemused):
                try:
                    opitulemused.remove(r.opitulemus_klrida_id)
                    # oli alles
                except ValueError:
                    r.delete()
            for klrida_id in opitulemused:
                r = model.Ylopitulemus(opitulemus_klrida_id=klrida_id)
                yaine.ylopitulemused.append(r)

        for yaine in list(yained.values()):
            yaine.delete()
        
    def _update_vahendid(self, item):
        vahendid = [{'vahend_kood': r} for r in self.form.data.get('vahend_kood')]
        #vahendid = self._unique_vahend_kood(self.form.data.get('vh'))
        ctrl = BaseGridController(item.vahendid, model.Vahend, None, self, pkey='vahend_kood')        
        ctrl.save(vahendid)        

    def _unique_vahend_kood(self, valikud):
        li = []
        koodid = []
        for n, v in enumerate(valikud):
            kood = v['vahend_kood']
            if kood not in koodid:
                koodid.append(kood)
                li.append(v)
        return li

    def _update_tolkekeeled(self, item, old_lang, old_keeled):
        item.skeeled = ' '.join(self.form.data.get('skeel'))
        item.set_lang()

        lang_switch = self.form.data.get('lang_switch')
        if lang_switch:
            # senine tõlkekeel muudeti põhikeeleks
            # põhikeel läheb tõlkekeeleks
            self._switch_lang(item, old_lang, item.lang)
            model.Session.flush()
            
        # eemaldame nende tõlkekeelte tõlked, mida enam ei ole
        def delete_tran(r, lang):
            if r:
                tr = r.tran(lang, False)
                if tr:
                    tr.delete()

        tran_keeled = [lang for lang in item.keeled if lang != item.lang]
        for lang in old_keeled:
            if not lang in tran_keeled:
                # keel on eemaldatud
                if lang == item.lang or self.request.params.get('f_lang_%s_del' % lang):
                    # kasutaja soovis tõlketekstid eemalda, mitte lihtsalt peita
                    delete_tran(item, lang)
                    delete_tran(item.lahendusjuhis, lang)
                    for a in item.hindamisaspektid:
                        delete_tran(a, lang)
                    for sp in item.sisuplokid:
                        delete_tran(sp, lang)
                        for r in sp.sisuobjektid:
                            delete_tran(r, lang)
                        for k in sp.kysimused:
                            delete_tran(k, lang)
                            for v in k.valikud:
                                delete_tran(v, lang)
                    for r in item.ylesandefailid:
                        delete_tran(r, lang)
                    for t in item.tulemused:
                        for r in t.hindamismaatriksid:
                            delete_tran(r, lang)
                        delete_tran(t, lang)
                    for np in item.normipunktid:
                        for ns in np.nptagasisided:
                            delete_tran(ns, lang)

    def _switch_lang(self, item, old_lang, new_lang):
        # senine tõlkekeel muudeti põhikeeleks (new_lang)
        # põhikeel läheb tõlkekeeleks (old_lang)

        def get_valued_fields(tr):
            "Leiame väljade nimed"
            keys = []
            for key in list(tr.__table__.columns.keys()):
                if key not in ('id', 'orig_id', 'lang', 'ylesandeversioon_id'):
                    #value = tr.__getattr__(key)
                    #if value is not None and value != '':
                    keys.append(key)
            return keys
        
        def copy_fields(item_to, item_from, fields):
            "Kopeeritakse väljad teise kirjesse"
            for key in fields:
                value = item_from.__getattr__(key)
                #log.debug('copy to %s from %s: %s=%s' % (item_to.__class__.__name__, item_from.__class__.__name__, key, value))
                if value is not None and value != '':
                    item_to.__setattr__(key, value)

        def switch(item):
            old_tr = item.tran(new_lang, False)
            if old_tr:
                fields = get_valued_fields(old_tr)
                if fields and old_lang:
                    # kopeerime väljad uude tõlkekeelde
                    tr = item.give_tran(old_lang)
                    copy_fields(tr, item, fields)
                    # kopeerime põhikirjesse tõlgitud väljad, mis olid varem tõlgitud
                    copy_fields(item, old_tr, fields)
                # eemaldame vana tõlkekirje, mida enam pole vaja
                old_tr.delete()
                
            
        switch(item)
        for a in item.hindamisaspektid:
            switch(a)
        for sp in item.sisuplokid:
            switch(sp)
            for r in sp.sisuobjektid:
                switch(r)
            for k in sp.kysimused:
                switch(k)
                for v in k.valikud:
                    switch(v)
        for r in item.ylesandefailid:
            switch(r)
        for t in item.tulemused:
            for r in t.hindamismaatriksid:
                switch(r)
        for np in item.normipunktid:
            for ns in np.nptagasisided:
                switch(ns)

        if not old_lang:
            # toimus kontroll
            return
        # importpackage.after_import_ylesanne
        # vajalik hottext, inlineTextEntry ja gapMatchInteraction korral
        keeled = item.keeled
        for sp in item.sisuplokid:
            if sp.tyyp in (const.INTER_HOTTEXT,
                           const.INTER_INL_TEXT,
                           const.INTER_GAP):
                for lang in (old_lang, new_lang):
                    ctrl = BlockController.get(sp, item, self)
                    if lang != item.lang:
                        ctrl.lang = lang
                        is_tr = True
                    else:
                        is_tr = False
                    sisu, tree = ctrl.parse_sisu()
                    if tree is not None:
                        ctrl._update_sisuvaade(tree, is_tr=is_tr)
        
    def _update_testiliigid(self, item):
        liigid = self.request.params.getall('tl.kood')
        for subitem in item.testiliigid:
            kood = subitem.kood
            if kood not in liigid:
                subitem.delete()
            else:
                liigid.pop(liigid.index(kood))
        for kood in liigid:
            subitem = model.Testiliik(kood=kood)
            item.testiliigid.append(subitem)        

    def _update_motlemistasandid(self, item):
        liigid = self.request.params.getall('mt.kood')
        for subitem in item.motlemistasandid:
            kood = subitem.kood
            if kood not in liigid:
                subitem.delete()
            else:
                liigid.pop(liigid.index(kood))
        for kood in liigid:
            subitem = model.Motlemistasand(kood=kood)
            item.motlemistasandid.append(subitem)        

    def _update_koguylesanded(self, item):
        kogud_id = list(map(int, self.request.params.getall('kogud_id') or []))
        if item.adaptiivne and kogud_id:
            raise ValidationError(self, {'kogud_id': _("Diagnostilise testi ülesanne ei saa kuuluda e-kogudesse")})
        kogud = [{'ylesandekogu_id': kogu_id} for kogu_id in kogud_id]
        ctrl = BaseGridController(item.koguylesanded, model.Koguylesanne, None, self, pkey='ylesandekogu_id')        
        ctrl.save(kogud)

    def _show_kontroll(self, id):
        c = self.c
        c.item = model.Ylesanne.get(id)
        c.item.check(self)
        c.rc, c.y_errors, c.sp_errors, c.k_errors, c.k_warnings = BlockController.check_ylesanne(self, c.item)
        return self.render_to_response('ekk/ylesanded/kontroll.mako')

    def _edit_kontroll(self, id):
        c = self.c
        c.item = model.Ylesanne.get(id)
        c.item.check(self)
        # eemaldame põhikeele tõlke kirjed, kui neid mingil põhjusel leidub
        self._switch_lang(c.item, None, c.item.lang)
        model.Session.commit()

        c.rc, c.y_errors, c.sp_errors, c.k_errors, c.k_warnings = BlockController.check_ylesanne(self, c.item)
        return self.render_to_response('ekk/ylesanded/kontroll.mako')

    def _perm_params(self):
        return {'obj':self.c.item}

    def __before__(self):
        """Väärtustame self.c.item ylesandega ning self.c.lang keelega,
        seejuures kontrollime, et self.c.lang oleks selle ülesande tõlkekeel.
        """
        self.c.lang = self.params_lang()
        id = self.request.matchdict.get('id')
        if id:
            self.c.item = model.Ylesanne.get(id)
            if self.c.lang and (self.c.lang == self.c.item.lang or self.c.lang not in self.c.item.keeled):
                self.c.lang = None
        else:
            self.c.lang = None
        super(YlesandedController, self).__before__()
