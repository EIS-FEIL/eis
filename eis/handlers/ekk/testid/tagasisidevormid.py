import pickle
import urllib.request, urllib.parse, urllib.error
from lxml import etree
import json
import base64
import html
from eis.lib.baseresource import *
from eis.lib.feedbackreport import FeedbackReport, AutoFormGenerator
from eis.handlers.ekk.testid.tagasisideeelvaade import GenRndSooritaja
_ = i18n._

log = logging.getLogger(__name__)

class TagasisidevormidController(BaseResourceController):
    """Testiosa normipunktid (profiililehe seaded)
    """
    _permission = 'ekk-testid'
    _MODEL = model.Tagasisidevorm
    _INDEX_TEMPLATE = 'ekk/testid/tagasiside.vorm.mako'
    _EDIT_TEMPLATE = 'ekk/testid/tagasiside.vorm.mako'    
    _actions = 'index,new,create,edit,show,update,delete'
    _ITEM_FORM = forms.ekk.testid.TagasisidevormVabaForm

    def _index_d(self):
        c = self.c
        c.items = model.Tagasisidevorm.get_list_f(c.test, c)
        if len(c.items):
            item_id = c.items[0].id
            return self._redirect('edit', id=item_id)

        return self.response_dict
        
    def _create(self, **kw):
        if not self.c.user.has_permission('ekk-testid', const.BT_UPDATE, self.c.test):
            raise ValidationError(self, {}, message='Puudub testi muutmise õigus')
        if self.request.params.get('genereeri'):
            item = self._genereeri()
        else:
            args = {}
            sup_id = self.form.data['sup_id']
            if sup_id:
                # loodi malli alamosa
                args['ylem_id'] = sup_id
            else:
                # loodi malli põhiosa
                args['test'] = self.c.test
            item = model.Tagasisidevorm.init(liik=self.form.data['liik'],
                                             staatus=const.B_STAATUS_KEHTETU,
                                             **args)
            self._update(item)
        return item

    def _create_diag(self):
        if self.c.lang:
            schema = forms.ekk.testid.TranTagasisidevormDiagForm
        else:
            schema = forms.ekk.testid.TagasisidevormDiagForm
        tsvorm_id = self.request.matchdict.get('id')
        err = False
        self.form = Form(self.request, schema=schema)
        if self.form.validate():
            try:
                self._save_diag()
            except ValidationError as e:
                self.form.errors = e.errors
                err = True
        if self.form.errors or err:
            model.Session.rollback()
            return self._error_create()
        model.Session.commit()
        return self._after_create(tsvorm_id)

    def _save_diag(self):
        tts = self.c.test.testitagasiside
        if not tts:
            tts = model.Testitagasiside(test=self.c.test)
        if self.c.lang:
            tran = tts.give_tran(self.c.lang)
        else:
            tran = tts
        tran.from_form(self.form.data, 's_')
        if not self.c.lang:
            tts.from_form(self.form.data, 'f_')
            if tts.ylgrupp_kuva == const.KUVA_HOR and tts.nsgrupp_kuva == const.KUVA_HOR:
                raise ValidationError(self, {}, message='Mõlemad grupid kõrvuti ei saa')

        lang = self.c.lang or None
        tts.count_tahemargid(lang)
        self.c.test.sum_tahemargid_lang(lang)

    def _get_tv(self, id):
        c = self.c
        c.items = model.Tagasisidevorm.get_list_f(c.test, c)
        item = None
        if id in ('F1','F2','F3','F4'):
            # süsteemisisesed d-testi tagasisidevormid
            for r in c.items:
                if r.id == id:
                    item = r
                    break
        else:
            item = model.Tagasisidevorm.get(id)
            if item and item.get_root().test_id != c.test.id:
                raise NotFound('Kirjet %s ei leitud' % id)                
        if not item:
            raise NotFound('Kirjet %s ei leitud' % id)
        return item
    
    def _show_d(self):
        id = self.request.matchdict.get('id')
        self.c.item = self._get_tv(id)
        self._show(self.c.item)
        return self.response_dict
        
    def _edit_d(self):
        id = self.request.matchdict.get('id')
        self.c.item = self._get_tv(id)
        rc = self._edit(self.c.item)
        if isinstance(rc, (HTTPFound, Response)):
            return rc        
        return self.response_dict
            
    def _edit(self, item):
        c = self.c
        c.tvorm = item
        c.tvorm_id = item.id
        if self.c.test.tagasiside_mall == const.TSMALL_NONE:
            self.warning(_("Tagasisidevormid ei ole kasutusel, sest testi tulemuste kuvamine on seadistatud ilma tagasisideta!"))
        params = self.request.params
        self.c.tookood = params.get('tookood')
        self.c.testimiskord_id = params.get('testimiskord_id')
        self.c.kool_koht_id = params.get('kool_koht_id')
        
        def tk_statistikad_opt(tk):
            # leitakse statistika kirjed, mida kasutatakse grupi tagasisides
            li = []
            q = (model.SessionR.query(model.Koht.id, model.Koht.nimi)
                 .filter(sa.exists().where(
                     sa.and_(model.Sooritaja.testimiskord_id==tk.id,
                             model.Sooritaja.kool_koht_id==model.Koht.id,
                             model.Sooritaja.staatus==const.S_STAATUS_TEHTUD,
                             model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD))
                         )
                 .order_by(model.Koht.nimi)
                 )
            
            for koht_id, koht_nimi in q.all():
                li.append((koht_id, koht_nimi))
            return li
        
        self.c.tk_statistikad_opt = tk_statistikad_opt

    def _edit_diag(self, id):
        c = self.c
        c.items = model.Tagasisidevorm.get_list_f(c.test, c)
        for item in c.items:
            if str(item.id) == id:
                c.tvorm = item
                c.tvorm_id = item.id
                break
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _show_diag(self, id):
        return self._edit_diag(id)
   
    def _new(self, item):
        return self._new_vaba(item)

    def _new_vaba(self, item):
        params = self.request.params
        copy_id = params.get('copy_id')
        test_id = params.get('test_id')
        sup_id = params.get('sup_id')
        op = params.get('op')
        if sup_id:
            sup = model.Tagasisidevorm.get(sup_id)
            if sup and sup.test_id == self.c.test.id:
                item.ylem_id = sup.id
        if test_id:
            item.test_id = test_id
        if not sup_id and not item.liik:
            item.liik = model.Tagasisidevorm.LIIK_OPILANE
        
    def _update_diag(self, id):
        return self._create_diag()

    def _fix_wysiwyg(self, item):
        # parandame vead, mille tekitab brauser HTMLis, kui tekstitoimeti viiakse WYSIWYG resiimi
        sisu = item.sisu
        
        # tal-atribuutide väärtustes dekodeerida &lt;
        pattern = ' (tal:[a-z]+)="([^"]+)"'
        def repl_attr(m):
            li = m.groups()
            return ' %s="%s"' % (li[0], html.unescape(li[1]))
        sisu = re.sub(pattern, repl_attr, sisu)
        
        # <!--?python ... ?--> eemaldada kommentaar ja viia kujule <?python ... ?>
        #sisu = re.sub(re.compile(r'<!--\?python(.*)\?-->', re.DOTALL), '<?python\\1?>', sisu)
        sisu2 = ''
        n0 = 0
        while True:
            n1 = sisu.find('<!--?python', n0)
            if n1 > -1:
                n2 = sisu.find('?-->', n1)
                if n2 > -1:
                    sisu2 += sisu[n0:n1+1] + sisu[n1+4:n2] + '?>'
                    n0 = n2 + 4
                    continue
            sisu2 += sisu[n0:]
            break

        item.sisu = sisu2

    def _check_diagram(self, item):
        "Kontrollitakse vormil olevad diagrammid"
        handler = self
        request = handler.request
        
        class ChkD:
            seq = 0

            def handle_dgm(self, m):
                buf = m.groups()[0]
                #print(buf)
                res = re.findall(r' (\w+)="([^"]*)"', buf)
                di = {key.lower(): val for (key, val) in res}
                cls = di.get('class') or ''
                b64data = di.get('params')
                if 'fbdiagram' in cls:
                    self.seq += 1
                    err = None
                    try:
                        txt = base64.b64decode(b64data)
                        data = json.loads(txt)
                    except Exception as ex:
                        err = _("Diagrammi parameetreid ei saa lugeda.")
                    if not err:
                        dname = data.get('dname')
                        if item.liik == model.Tagasisidevorm.LIIK_KIRJELDUS:
                            err = _("Kirjelduse osas ei saa kasutada diagramme.")
                        elif not model.Tagasisidevorm.can_dgm(item.liik, dname):
                            err = _("Diagrammi liik ei sobi selle vormi liigiga.")
                        if err:
                            err = _("{n}. diagramm on vigane.").format(n=self.seq) + \
                                  ' ' + err
                            errors = {'f_sisu': err}
                            raise ValidationError(handler, errors)

                        # lisame id väärtuse, mille järgi on võimalik diagrammi eraldi uuendada
                        label = handler.c.opt.title_feedbackdgm(dname)
                        width = data.get('with') or ''
                        fbd_id = f'fbd_{item.id}_{self.seq}'
                        buf = f'<div class="fbdiagram" contenteditable="false" ' +\
                              f'fbtype="{dname}" params="{b64data}" id="{fbd_id}" width="{width}">' +\
                              label +\
                              '</div>'
                        
                return buf

        # igale diagrammi parameetrid salvestatatakse eraldi kirjes
        # ja tagasisidevormis asendatakse diagrammi URL, et see viitaks diagrammi kirjele
        chkD = ChkD()
        sisu = item.sisu
        # lisaks <div ... > argumentidele kirjutame yle ka <div> sisu,
        # sest ckeditor võis sinna mingit kujundust lisada
        pattern = r'(<div class="fbdiagram"[^>]+>)((?!</div>).)*</div>'
        # kontrollime ja lisame igale diagrammile seq atribuudi
        item.sisu = re.sub(pattern, chkD.handle_dgm, sisu)

    def _genereeri(self):
        item = model.Tagasisidevorm.init(liik=self.form.data['liik'],
                                         staatus=const.B_STAATUS_KEHTETU)
        item.test = self.c.test
        item.nimi = item.liik_nimi
        kursus = self.form.data.get('kursus')
        if item.liik == model.Tagasisidevorm.LIIK_GRUPPIDETULEMUSED:
            item.sisu = AutoFormGenerator.gen_template_gruppidetulemused(self, self.c.test, kursus)
        elif item.liik == model.Tagasisidevorm.LIIK_OSALEJATETULEMUSED:
            item.sisu = AutoFormGenerator.gen_template_osalejatetulemused(self, self.c.test, kursus)
        return item

    def _update(self, item, lang=None):
        if self.request.params.get('genereeri'):
            item = self._genereeri()
            model.Session.commit()
            return self._after_update(item.id)
        elif self.request.params.get('copy'):
            cp = item.copy(staatus=const.B_STAATUS_KEHTETU)
            model.Session.commit()
            return self._after_update(cp.id)
        
        item.from_form(self.form.data, self._PREFIX, lang=lang)
        item.lang = self.form.data['f_lang'] or None
        item.kursus_kood = self.form.data['f_kursus'] or None
        if item.ylem_id:
            item.liik = None
            liik = item.get_root().liik
        else:
            liik = self.form.data['liik']
            kursus = item.kursus_kood
            self._set_staatus(item, liik, kursus)

        if liik != model.Tagasisidevorm.LIIK_KIRJELDUS:
            item.sisu_jatk = None
        model.Session.flush()
        #item.sisu = 'aaa <!--?python oioi ?-->EI<!--?pythonXXX?-->JAA'
        self._fix_wysiwyg(item)
        self._check_diagram(item)

        self.c.ekk_preview_rnd = True
        fr = FeedbackReport(self, None, self.c.test, item.sisu, item.liik, lang)
        id = self.request.matchdict.get('id')
        tsmall = self.c.test.tagasiside_mall
        sooritaja = GenRndSooritaja(self).create(id, tsmall, item.liik, lang)
        err, data = fr.generate(sooritaja, testimiskord_id=-1)
        if err:
            errors = {'f_sisu': 'Ei ole korrektne (%s)' % err}
            raise ValidationError(self, errors)

        if not item.nimi:
            item.nimi = item.liik_nimi

        # nseq on alamosa uus jrk nr 
        nseq = self.form.data.get('seq')
        if item.ylem_id and nseq:
            item.seq = nseq
            model.Session.flush()
            q = (model.Session.query(model.Tagasisidevorm)
                 .filter_by(ylem_id=item.ylem_id)
                 .order_by(model.Tagasisidevorm.seq))
            for ind, r in enumerate(q.all()):
                seq = ind + 1
                if seq < nseq:
                    r.seq = seq
                elif item != r:
                    r.seq = seq + 1
            
    def _set_staatus(self, item, liik, kursus):
        if self.form.data['staatus']:
            # samast liigist ja samal testil ja samas keeles saab ainult üks vorm olla kehtiv
            q = (model.Tagasisidevorm.query
                 .filter_by(test_id=item.test.id)
                 .filter_by(liik=liik)
                 .filter_by(kursus_kood=kursus)
                 .filter_by(staatus=const.B_STAATUS_KEHTIV)
                 .filter(model.Tagasisidevorm.id!=item.id)
                 .filter(model.Tagasisidevorm.lang==item.lang))
            #model.log_query(q)
            for tv in q.all():
                self.notice('Varasem kehtiv vorm muutus kehtetuks')
                tv.staatus = const.B_STAATUS_KEHTETU
                log.debug('Kehtetuks %s' % tv.id)
            model.Session.flush()
            item.staatus = const.B_STAATUS_KEHTIV
        else:
            item.staatus = const.B_STAATUS_KEHTETU       
        item.liik = liik
        
    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
        return self._redirect('edit', id, lang=self.c.lang)

    def _get_sub(self):
        if self.request.matchdict.get('id') in ('F1','F2','F3','F4'):
            # süsteemisisesed vormid
            if self.c.test.tagasiside_mall == const.TSMALL_DIAG:
                return 'diag'

    def delete(self):
        id = self.request.matchdict.get('id')
        item = model.Tagasisidevorm.get(id)
        parent_id = None
        if item:
            if item.ylem_id:
                parent_id = item.get_root().id
            rc = self._delete_except(item)
            if isinstance(rc, (HTTPFound, Response)):
                return rc
        if parent_id:
            return self._redirect('edit', id=parent_id)
        else:
            return self._redirect('index')
        
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)

        testiosa_id = int(self.request.matchdict.get('testiosa_id'))
        if testiosa_id:
            self.c.testiosa = model.Testiosa.get(testiosa_id)
            if self.c.testiosa.test_id != self.c.test.id:
                self.c.testiosa = None
        if not self.c.testiosa:
            for self.c.testiosa in self.c.test.testiosad:
                break
            
        self.c.lang = self.params_lang()
        if self.c.test:
            if self.c.lang and (self.c.lang == self.c.test.lang or self.c.lang not in self.c.test.keeled):
                self.c.lang = None
        else:
            self.c.lang = None
        
    def _perm_params(self):
        return {'obj':self.c.test}

