from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController, _outer_xml
from .sisuplokk import koopia_kysimustele_uued_koodid

log = logging.getLogger(__name__)

class SisuController(BaseResourceController):
    """Ülesande sisu"""

    _permission = 'ylesanded'

    _MODEL = model.Ylesanne
    _EDIT_TEMPLATE = 'ekk/ylesanded/sisu.mako'
    #_ITEM_FORM = forms.ekk.ylesanded.SisuForm 
    _get_is_readonly = False

    @property
    def _ITEM_FORM(self):
        is_tr = self.request.params.get('is_tr')
        if is_tr:
            return forms.ekk.ylesanded.SisuTranForm
        else:
            return forms.ekk.ylesanded.SisuForm
        
    def _edit(self, item):
        self.c.include_jqueryui = True # lohistamine
        if item.is_encrypted:
            return
        on_sisuplokid = False
        for block in item.sisuplokid:
            # tekitame sisuploki mudeli objekti juurde pseudokontrolleri,
            # mis hiljem sisuploki välja joonistab
            ctrl = BlockController.get(block, item, self)
            ctrl.lang = self.c.lang
            # seame nõuded HTML päisele
            ctrl.include_view()
            on_sisuplokid = True
        q = (model.Session.query(model.Ylesanne.id,
                                 model.Ylesanne.nimi)
             .filter(model.Ylesanne.sisuplokid.any())
             )
        if self.c.app_ekk:
            q = q.filter(model.Ylesanne.staatus.in_(
                (const.Y_STAATUS_MALL, const.Y_STAATUS_AV_MALL)))
        else:
            q = q.filter(model.Ylesanne.staatus==const.Y_STAATUS_AV_MALL)
        q = q.order_by(model.Ylesanne.nimi)
        self.c.opt_mall = [(r_id, r_nimi) for (r_id, r_nimi) in q.all()]

    def _show(self, item):
        if self.request.params.get('sub') == 'markus':
            sisuplokk_id = self.request.params.get('sisuplokk_id')            
            self.c.sisuplokk = model.Sisuplokk.get(sisuplokk_id)
            self.c.dialog_markused = True
        return self._edit(item)

    def _edit_markus(self, id):
        self.c.sisuplokk_id = int(self.request.params.get('sisuplokk_id'))
        ylem_id = self.request.params.get('ylem_id')
        if ylem_id:
            self.c.ylem = model.Plokimarkus.get(ylem_id)
            assert self.c.ylem.sisuplokk_id == self.c.sisuplokk_id, _("Vale sisuplokk")
        return self.render_to_response('ekk/ylesanded/plokimarkus.mako')

    def _show_markus(self, id):
        sisuplokk_id = self.request.params.get('sisuplokk_id')
        self.c.sisuplokk = model.Sisuplokk.get(sisuplokk_id)
        return self.render_to_response('ekk/ylesanded/plokimarkused.mako')

    def _delete_markus(self, id):
        markus_id = self.request.params.get('markus_id')
        m = model.Plokimarkus.get(markus_id)
        error = None
        if m.kasutaja_id != self.c.user.id:
            self.error(_("Ainult märke lisaja ise saab oma märget kustutada"))
        elif len(m.alamad) > 0:
            self.error(_("Märke kustutamiseks tuleb esmalt kustutada kõik selle alamad märkused"))
        else:
            m.delete()
            model.Session.commit()
        sisuplokk_id = self.request.params.get('sisuplokk_id')
        self.c.sisuplokk = model.Sisuplokk.get(sisuplokk_id)
        return self.render_to_response('ekk/ylesanded/plokimarkused.mako')

    def _update_markus(self, id):
        if not self.c.user.id:
            self.error(_("Autentimata kasutaja ei saa märkeid teha!"))
            return self._redirect('edit', id)            

        self.form = Form(self.request, schema=forms.ekk.ylesanded.MarkusForm)
        if not self.form.validate():
            self.c.dialog_markus = True
            html = self.form.render(self._EDIT_TEMPLATE,
                                    extra_info=self._edit_d())            
            return Response(html)

        sisuplokk_id = int(self.request.params.get('sisuplokk_id'))
        model.Plokimarkus(sisuplokk_id=sisuplokk_id, 
                          sisu=self.form.data.get('sisu'),
                          teema=self.form.data.get('teema'),
                          ylem_id=self.form.data.get('ylem_id'),
                          kasutaja_id=self.c.user.id)
        
        model.Session.commit()
        self.success(_("Märkus on lisatud!"))
        return HTTPFound(location=self.url_current('show'))

    def _update_tcolumn(self, id):
        "Luuakse tcolumn"
        c = self.c
        sp = model.Sisuplokk(tyyp=const.BLOCK_TCOLUMN)
        c.item.sisuplokid.add(sp)
        model.Session.commit()
        return self._after_update(c.item.id)        

    def _update(self, item):
        BaseResourceController._update(self, item, lang=self.c.lang)
        juhis = item.give_lahendusjuhis()
        juhis.from_form(self.form.data, 'j_', lang=self.c.lang)
        self._count_tahemargid(item, self.form.data, juhis)
        
        sp_seq = 0
        for key in self.form.data:
            if key.startswith('order_'):
                paan_seq = int(key.split('_')[1])
                order = self.form.data[key]
                if order:
                    # order on kujul: i_1,i_3,i_2
                    li = [int(i.split('_')[1]) for i in order.split(',') if i and i.startswith('i_')]
                    for sp_id in li:
                        block = model.Sisuplokk.get(sp_id)
                        assert block.ylesanne_id == item.id, 'Vale ülesanne'
                        sp_seq += 1
                        block.seq = sp_seq
                        block.paan_seq = paan_seq
                        #for block in item.sisuplokid:
                        #block.seq = li.index(block.id) + 1

        if self.request.params.get('kasutamalli'):
            mall_id = self.request.params.get('mall_id')
            if not mall_id:
                raise ValidationError(self, errors={'mall_id': _("Malli kasutamiseks palun valida mall")})
            mall = model.Ylesanne.get(mall_id)
            if not mall or \
                   self.c.app_eis and mall.staatus != const.Y_STAATUS_AV_MALL or \
                   mall.staatus not in (const.Y_STAATUS_AV_MALL, const.Y_STAATUS_MALL):
                raise ValidationError(self, errors={'mall_id': _("Malli ei leitud")})

            # leitakse kõik olemasolevad kysimuste koodid
            olemas_koodid = [t.kood for t in item.tulemused]
            for p in item.sisuplokid:
                olemas_koodid += [k.kood for k in p.kysimused]

            with model.Session.no_autoflush:
                # kopeerime sisuplokid mall-ylesandest
                map_ok = mall._map_oigsus()
                seq = len(item.sisuplokid)
                for orig_p in mall.sisuplokid:
                    cp_p = orig_p.copy(ylesanne_id=item.id)
                    seq += 1
                    cp_p.seq = seq
                    item.sisuplokid.append(cp_p)

                    koopia_kysimustele_uued_koodid(self, cp_p, self.c.item, olemas_koodid)
                    
                item._copy_oigsus(map_ok)
                            
                BlockController.after_copy_task(item, self)
                                            
        if item.segamini:
            # märgime sisuplokid, mis jäävad juhuslikul järjestamisel kindlale kohale
            spfixpos = list(map(int, self.request.params.getall('fixpos')))
            for sp in item.sisuplokid:
                sp.fikseeritud = sp.id in spfixpos or None

    def _count_tahemargid(self, item, data, juhis):
        keeled = item.keeled
        for lang in keeled:
            if lang == item.lang:
                lang = None
            juhis.count_tahemargid(lang)
        item.sum_tahemargid()

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        self.success()
        return HTTPFound(location=self.url('ylesanded_edit_sisu', 
                                           id=id, 
                                           lang=self.c.lang, 
                                           is_tr=self.request.params.get('is_tr')))


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
        super(SisuController, self).__before__()

    def _get_permission(self):
        sub = self.request.params.get('sub')
        if sub == 'markus':
            permission = 'ylesanded-markused'
            return permission
        return BaseResourceController._get_permission(self)

    def _perm_params(self):
        return {'obj':self.c.item}
