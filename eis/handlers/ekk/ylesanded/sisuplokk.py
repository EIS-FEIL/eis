from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController, _outer_xml
from eis.lib.inmemoryzip import InMemoryZip

log = logging.getLogger(__name__)

class SisuplokkController(BaseResourceController):
    """Ülesande sisu"""

    _permission = 'ylesanded'
    _MODEL = model.Sisuplokk

    _EDIT_TEMPLATE = 'ekk/ylesanded/sisuplokk.mako'
    _ITEM_FORM = forms.ekk.ylesanded.SisuplokkForm
    _get_is_readonly = False
    
    def _edit(self, item):
        if not item.ylesanne:
            # uue ploki loomisel
            item.ylesanne = model.Ylesanne.get(item.ylesanne_id)
        ylesanne = item.ylesanne
        self.c.orig_lang = ylesanne.lang
        # tekitame sisuploki mudeli objekti juurde pseudokontrolleri,
        # mis hiljem sisuploki välja joonistab
        ctrl = BlockController.get(item, ylesanne, self)
        # seame nõuded HTML päisele
        ctrl.include_edit()
        self.c.includes['ckeditor'] = True        

    def _new_transform(self):
        self.c.nkood = self.request.params.get('kood')
        return self.render_to_response('/sisuplokk/ihottext.transformer.dlg.mako')
    
    def update(self):
        err = False
        sub = self._get_sub()
        if sub == 'icons':
            # ipunkt nupuriba
            id = self.request.matchdict.get('id')            
            return self._update_icons(id)
        is_tr = self.request.params.get('is_tr')
        form = which_form(self, self.c.ylesanne, is_tr, self.c.can_update_hm)
        if not form:
            self.error(_("Ülesannet ei tohi enam muuta!"))
            return self.render_to_response(self._EDIT_TEMPLATE)
        
        self.form = Form(self.request, schema=form)
        if self.form.validate():
            item = self.c.item
            try:
                if item:
                    self._update(item)
            except ValidationError as e:
                self.form.errors = e.errors
                err = True

        if self.form.errors or err:
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self._edit_d()))

        if self._get_sub() == 'change':
            # salvestamist ei toimu, ainult vorm uuendatakse
            # (ei saa teha GET-iga, kuna URL läheks liiga pikaks)
            self.c.run_generate = True
            return self.render_to_response(self._EDIT_TEMPLATE)

        model.Session.commit()
        return self._after_update(item.id)

    def _new_d(self):
        # uue objekti väljad
        params = self.request.params
        tyyp = params.get('tyyp')
        ylesanne_id = self.c.ylesanne.id
        item = model.Sisuplokk.init(ylesanne_id=ylesanne_id, tyyp=tyyp)
        self.c.item = item
        if tyyp in (const.BLOCK_IMAGE, const.BLOCK_CUSTOM, const.BLOCK_MEDIA):
            # loome kohe kirje, et kasutaja saaks pilte lisama hakata
            item.post_create()
            model.Session.commit()
        else:
            # lülitame autoflushi välja, et ID ei genereeritaks
            model.Session.autoflush = False
            item.post_create()

        self._edit(item)
        return self.response_dict

    def _create(self, **kw):
        args = self._get_parents_from_routes()
        args.update(kw)
        item = self._MODEL.init(**args)
        self._update(item)
        return item

    def _create_change(self):
        "Andmevorm genereeritakse uuesti, ei salvestata"
        self.c.item = model.Sisuplokk.init(tyyp=self.request.params.get('tyyp'),
                                           ylesanne=self.c.ylesanne)
        # lülitame autoflushi välja, et ID ei genereeritaks
        model.Session.autoflush = False
        return self.update()

    def _update(self, item):
        # omistame vormilt saadud andmed
        item.from_form(self.form.data, self._PREFIX, lang=self.c.lang)
        if not item.ylesanne_id:
            # uus sisuplokk
            item.ylesanne = self.c.ylesanne
        if not item.tran(self.c.lang).sisu and item.tyyp != const.INTER_PUNKT:
            item.tran(self.c.lang).sisuvaade = ''
        if not item.id:
            item.post_create()
        ctrl = BlockController.get(item, self.c.ylesanne, self)
        f_nimi = self.form.data.get('f_nimi')
        if f_nimi:
            f_nimi, tree = ctrl._parse_rtf(f_nimi, 'f_nimi', None, False)
            item.tran(self.c.lang).nimi = f_nimi

        # kas on toimetamine/tõlkimine või tavaline koostamine
        is_tr = self.request.params.get('is_tr')
        # kas on lubatud ülesande sisu muuta või ainult hindamismaatriksit
        not_locked = not self.c.ylesanne.lukus
        ctrl.lang = self.c.lang
        ctrl.update(is_tr, not_locked)
        if self._get_sub() != 'change':
            model.Session.flush()
            # sätime valikvastuste viited
            if not is_tr:
                ctrl.set_valikvastused()
                if self.request.params.get('gendesc'):
                    ctrl.gen_selgitused(True)

            self.c.ylesanne.calc_max_pallid()

            # arvutame tähemärgid
            lang = is_tr and self.c.lang or None
            item.count_tahemargid(lang)
            self.c.ylesanne.sum_tahemargid()

            # kontrollime kysimuste unikaalsust
            kkoodid = []
            for sp in self.c.ylesanne.sisuplokid:
                if sp != item:
                    kkoodid.extend([k.kood for k in sp.kysimused if k.kood])
            korduvad = []
            for k in set(item.kysimused):
                if k.kood:
                    if k.kood in kkoodid:
                        korduvad.append(k.kood)
                    kkoodid.append(k.kood)

            if korduvad:
                err = _("Küsimuste koodid pole ülesande piires unikaalsed (korduvad koodid {s})").format(s=', '.join(korduvad))
                raise ValidationError(self, {}, err)

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        if not self.has_errors():
            self.success()

        kw = {'ylesanne_id': self.request.matchdict.get('ylesanne_id'),
              'id': id, 
              'lang': self.c.lang, 
              'is_tr': self.request.params.get('is_tr'),
              }
        for key, value in self.request.params.items():
            if key.endswith('.page'):
                # hoiame meeles hindamismaatriksi lehekylje
                if value != '1':
                    # vaikimisi on lk 1, seda pole vaja meeles hoida, teeb URLi koledaks
                    kw[key] = value

        return HTTPFound(location=self.url('ylesanne_edit_sisuplokk', **kw))

    def _edit_icons(self, id):
        # ipunkt nupuriba
        return self.render_to_response('ekk/ylesanded/sisuplokk.icons.mako')

    def _update_icons(self, id):
        rc = True
        icons = self.request.params.getall('icon')
        if not icons:
            self.error(_("Palun valida vähemalt üks nupp"))
            rc = False
        self.c.item.set_json_sisu({'icons':icons})
        model.Session.commit()
        if rc:
            self.c.updated = True
        return self._edit_icons(id)
    
    def _download(self, id, format=None):
        """Failide allalaadimine"""
        if not self.c.item:
            raise NotFound('Kirjet ei leitud')        
        objektid = [obj for obj in self.c.item.sisuobjektid if obj.filename]
        if len(objektid) == 1:
            obj = objektid[0]
            t_obj = obj.tran(self.c.lang)
            return utils.download(t_obj.filedata, obj.filename, obj.mimetype)
        else:
            zf = InMemoryZip()
            for obj in objektid:
                t_obj = obj.tran(self.c.lang)
                filedata = None
                if t_obj.has_file:
                    filedata = t_obj.filedata
                elif obj.has_file:
                    filedata = obj.filedata
                if filedata is not None:
                    zf.append(obj.filename, filedata)
            data = zf.close().read()
            fn = 'sp_%s%s.zip' % (self.c.item.id, self.c.lang or '')
            return utils.download(data, fn, const.MIMETYPE_ZIP)

    def _create_kopeeri(self):
        """Sisuplokist tehakse koopia.
        """
        assert not self.c.ylesanne.lukus, _("Ülesanne on lukus")
        
        sisuplokk_id = self.request.params.get('sisuplokk_id')
        kopeeritav = model.Sisuplokk.get(sisuplokk_id)
        ylesanne = self.c.ylesanne
        assert kopeeritav.ylesanne_id == ylesanne.id, _("Enda koopia")

        map_ok = {}
        for t in ylesanne.tulemused:
            map_ok[t.kood] = t.oigsus_kysimus_id

        # leitakse kõik olemasolevad kysimuste koodid
        olemas_koodid = [t.kood for t in ylesanne.tulemused]
        for p in ylesanne.sisuplokid:
            olemas_koodid += [k.kood for k in p.kysimused]

        # teeme sisuplokist koopia
        with model.Session.no_autoflush:
            koopia = kopeeritav.copy()
            koopia.ylesanne = ylesanne
            for k in koopia.kysimused:
                t = k.tulemus
                if t:
                    ylesanne.tulemused.append(t)
                    #t.ylesanne = ylesanne
                    # paneme tagasi, mille igaks juhuks kustutasime
                    t.oigsus_kysimus_id = map_ok.get(t.kood)
         
            koopia_kysimustele_uued_koodid(self, koopia, ylesanne, olemas_koodid)
         
            # lisame uue sisuploki kopeeritava sisuploki järele
            for block in self.c.ylesanne.sisuplokid:
                if block.seq > kopeeritav.seq:
                    block.seq += 1
            koopia.seq = kopeeritav.seq + 1

            model.Session.commit()
            self.success(_("Sisuplokist tehti koopia"))
            
        if self.request.params.get('edit'):
            url = self.url('ylesanded_edit_sisu', id=self.c.ylesanne.id)
        else:
            url = self.url('ylesanded_sisu', id=self.c.ylesanne.id)            
        return HTTPFound(location=url)

    def showtool(self):
        "Abivahendi kuvamine"
        c = self.c
        vahend_kood = self.request.matchdict.get('vahend')
        ylesanne_id = self.request.matchdict.get('task_id')
        q = (model.Session.query(model.Vahend.id)
             .filter_by(ylesanne_id=ylesanne_id)
             .filter_by(vahend_kood=vahend_kood))
        if not q.count():
            err = _("Vahend pole lubatud")
            log.info(err)
        else:
            self.c.item = model.Klrida.get_by_kood('VAHEND', vahend_kood)
            template = '/avalik/lahendamine/abivahend.mako'
            return self.render_to_response(template)
        
        return Response(err, content_type='text/plain')

    def _delete(self, item):
        item.delete()
        model.Session.commit()
        self.success(_("Andmed on kustutatud"))
            
    def _after_delete(self, parent_id=None):
        if not self.has_errors():
            self.c.ylesanne.check(self)
            self.c.ylesanne.sum_tahemargid()
            model.Session.commit()
        return HTTPFound(location=self.url('ylesanded_edit_sisu', id=self.c.ylesanne.id))
    
    def __before__(self):
        """Väärtustame self.c.item ylesandega ning self.c.lang keelega,
        seejuures kontrollime, et self.c.lang oleks selle ülesande tõlkekeel.
        """
        c = self.c
        c.lang = self.params_lang()
        id = self.request.matchdict.get('ylesanne_id')
        c.ylesanne = model.Ylesanne.get(id)
        if not c.ylesanne:
            raise NotAuthorizedException('avaleht', message=_("Ülesanne puudub"))
        if c.lang and (c.lang == c.ylesanne.lang or c.lang not in c.ylesanne.keeled):
            c.lang = None
        id = self.request.matchdict.get('id')
        if id:
            c.item = model.Sisuplokk.get(id)
            
        c.can_update = c.user.has_permission('ylesanded', const.BT_UPDATE, c.ylesanne)
        if c.can_update and c.item and \
               c.item.tyyp == const.BLOCK_HEADER and \
               not c.user.has_permission('srcedit', const.BT_UPDATE):
            # lähtekoodi muutmiseks on eriõigust vaja
            c.can_update = False
            
        c.can_update_sisu = c.can_update and c.ylesanne and not c.ylesanne.lukus
        c.can_update_hm = c.can_update and c.ylesanne and c.ylesanne.lukus_hm_muudetav

    def _perm_params(self):
        c = self.c
        sp_tyyp = c.item and c.item.tyyp or self.request.params.get('f_tyyp')
        if sp_tyyp == const.BLOCK_HEADER and c.action in ('edit','update','create','new'):
            # lähtekoodi muutmiseks on eriõigust vaja
            # sisuploki kustutamiseks ei ole eriõigust vaja
            if not self.c.user.has_permission('srcedit', const.BT_UPDATE):
                return False
                
        return {'obj':self.c.ylesanne}

def which_form(handler, ylesanne, is_tr, can_update_hm):
    """Valitakse valideerimisvorm, kuna
    väljad sõltuvad sellest, kas sisestatakse põhikeeles või tõlgitakse
    ning kas ja kui tõsiselt on ülesanne lukustatud.
    Kui muuta ei tohi, siis tagastab None.
    """
    form = None
    if is_tr:
        if not ylesanne or not ylesanne.lukus:
            form = forms.ekk.ylesanded.TranSisuplokkForm
        elif can_update_hm:
            form = forms.ekk.ylesanded.LukusTranSisuplokkForm
    else:
        if not ylesanne or not ylesanne.lukus:
            form = forms.ekk.ylesanded.SisuplokkForm
        elif can_update_hm:
            form = forms.ekk.ylesanded.LukusSisuplokkForm
    return form

def replace_sisu_koodid(handler, koopia, ylesanne, koodid):
    "Muudame kopeeritud sisuploki sisu tekstis olevad küsimuste koodid"

    if koopia.tyyp not in (const.INTER_INL_TEXT,
                           const.INTER_INL_CHOICE,
                           const.INTER_GAP,
                           const.INTER_HOTTEXT,
                           const.INTER_COLORTEXT):
        return

    is_tr = False
    # kopeerime sisuploki ja selle tõlked jooksvas versioonis
    trans = [r for r in koopia.trans if not r.ylesandeversioon_id]
    for item in [koopia] + trans:
        # muudame põhikirjet ja tõlkeid
        if not item.sisu:
            log.debug('sisutu')
            is_tr = True
            continue
        try:
            sisu, tree = koopia.parse_sisu(item.sisu)
        except:
            pass
        else:
            if koopia.tyyp == const.INTER_GAP:
                for n, field in enumerate(tree.xpath('//input[@type="text"]')):
                    kood = field.get('value')
                    if kood and kood in koodid:
                        field.attrib['value'] = koodid[kood]

            elif koopia.tyyp == const.INTER_INL_TEXT:
                for n, field in enumerate(tree.xpath('//input[@type="text"]')):
                    kood = field.get('value')
                    if kood and kood in koodid:
                        field.attrib['value'] = koodid[kood]
                for n, field in enumerate(tree.xpath('//textarea')):
                    kood = field.text
                    if kood and kood in koodid:
                        field.text = koodid[kood]

            elif koopia.tyyp == const.INTER_INL_CHOICE:
                for n, field in enumerate(tree.xpath('//select')):
                    label = field.find('option')
                    kood = label is not None and label.text and label.text.strip() or field.get('name')
                    if kood and kood in koodid:
                        if label is not None:
                            label.text = koodid[kood]
                        field.attrib['id'] = koodid[kood]
                        field.attrib['name'] = koodid[kood]

            elif koopia.tyyp in (const.INTER_HOTTEXT, const.INTER_COLORTEXT):
                for field in tree.xpath('//span[@class="hottext"]'):
                    kood = field.get('group')
                    if kood and kood in koodid:
                        field.attrib['group'] = koodid[kood]
                        
            item.sisu = _outer_xml(tree)
            ctrl = BlockController.get(koopia, ylesanne, handler)
            if isinstance(item, model.T_Sisuplokk):
                ctrl.lang = item.lang
            if koopia.tyyp == const.INTER_GAP:
                bkysimus = koopia.give_kysimus(0) 
                ctrl._update_sisu(tree, is_tr)                    
                if bkysimus.gap_lynkadeta:
                    ctrl._update_sisuvaade_lynkadeta(tree, is_tr)
                else:
                    ctrl._update_sisuvaade(tree, is_tr)
                    
            elif koopia.tyyp in (const.INTER_INL_TEXT, const.INTER_INL_CHOICE):
                ctrl._update_sisu(tree, is_tr)
                ctrl._update_sisuvaade(tree)
            elif koopia.tyyp in (const.INTER_HOTTEXT, const.INTER_COLORTEXT):
                ctrl._update_sisu(tree)
                ctrl._update_sisuvaade(tree, is_tr)

        is_tr = True
        
def koopia_kysimustele_uued_koodid(handler, koopia, ylesanne, olemas_koodid):
    # loome koopia küsimustele uued koodid
    koodid = {}
    for k in list(koopia.kysimused):
        vana_kood = k.kood
        if vana_kood:
            if vana_kood not in olemas_koodid:
                uus_kood = vana_kood
            else:
                uus_kood = ylesanne.gen_kysimus_kood(None, olemas_koodid)
                koodid[vana_kood] = k.kood = uus_kood
                if k.tulemus:
                    k.tulemus.kood = uus_kood
                if k.sisuobjekt:
                    k.sisuobjekt.kood = uus_kood
            olemas_koodid.append(uus_kood)
    if koopia.tyyp in (const.INTER_TXPOS, const.INTER_TXPOS2, const.INTER_TXGAP, const.INTER_TXASS):
        bkysimus = koopia.kysimus
        for valik in bkysimus.valikud:
            valik.kood = koodid[valik.kood]
    elif koopia.tyyp == const.INTER_COLORAREA:
        for k in list(koopia.pariskysimused):
            for prk in k.valikud:
                prk.kood = k.kood
                break
   
    # vahetame kysimuste koodid ka sisus
    replace_sisu_koodid(handler, koopia, ylesanne, koodid)
    # vajadusel muudame sisuploki teksti (kui seal on ploki ID)
    keeled = ylesanne.keeled
    BlockController.after_copy_block(ylesanne, koopia, keeled, handler)
