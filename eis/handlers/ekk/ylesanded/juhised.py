from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
_ = i18n._

log = logging.getLogger(__name__)

class JuhisedController(BaseResourceController):
    """Ülesande juhised, mis pole ühegi sisuploki omad"""

    _permission = 'ylesanded'
    _MODEL = model.Ylesanne
    _EDIT_TEMPLATE = 'ekk/ylesanded/juhised.mako'
    _ITEM_FORM = forms.ekk.ylesanded.JuhisedForm 

    def _edit_aspekt(self, id):
        aspekt_id = self.request.params.get('aspekt_id')
        if aspekt_id:
            # muutmine
            self.c.aspekt = model.Hindamisaspekt.get(aspekt_id)
        return self.render_to_response('ekk/ylesanded/aspekt.mako')

    def _update_aspekt(self, id):
        ylesanne = self._MODEL.get(id)
        self.form = Form(self.request, schema=forms.ekk.ylesanded.AspektForm)
        if not self.form.validate():
            self.c.dialog_aspekt = True
            return self._error_aspekt()
        else:
            data = self.form.data
            aspekt_id = self.request.params.get('aspekt_id')
            data['a_aine_kood'], data['a_aspekt_kood'] = data['a_aspekt_kood'].split('.', 1)
            aspekt_kood = data['a_aspekt_kood']
            kordub = [ha.id for ha in ylesanne.hindamisaspektid if ha.aspekt_kood == aspekt_kood]
            if aspekt_id:
                aspekt_id = int(aspekt_id)
                kordub = [ha_id for ha_id in kordub if ha_id != aspekt_id]
            if kordub:
                self.error(_("Valitud hindamisaspekt on ülesandes juba kasutusel!"))
                return self._error_aspekt()
            
            if aspekt_id:
                aspekt = model.Hindamisaspekt.get(aspekt_id)
                if aspekt.ylesanne_id != int(id):
                    raise Exception('Vale aspekt')
            else:
                aspekt = model.Hindamisaspekt(ylesanne=ylesanne)
            old_seq = aspekt.seq
            aspekt.from_form(data, 'a_')
            if aspekt.max_pallid == None:
                aspekt.max_pallid = 0

            # salvestame punktide kirjeldused
            # ainult need, millel on kirjeldus
            # ja millel pole deleted märget (see märge on siis, kui on vale intervalliga)
            rows = [r for r in data['pkirjeldus'] if r['kirjeldus'] and not r.get('deleted')]
            BaseGridController(aspekt.punktikirjeldused, model.Punktikirjeldus, None, self).save(rows)

            # anname aspektidele uued järjekorranumbrid
            # nii, et kõik järjekorranumbrid on järjest ja praeguse aspekti järjekord säilib
            li = [ha for ha in ylesanne.hindamisaspektid if ha != aspekt]
            li.insert(aspekt.seq-1, aspekt)
            for seq, ha in enumerate(li):
                ha.seq = seq + 1

            ylesanne.calc_max_pallid()
            model.Session.commit()
            self.success()
            return self._redirect('edit', id)

    def _error_aspekt(self):
        template = 'ekk/ylesanded/aspekt.mako'
        html = self.form.render(template, extra_info=self.response_dict)            
        return Response(html)

    def _delete_aspekt(self, id):
        aspekt_id = self.request.params.get('aspekt_id')
        aspekt = model.Hindamisaspekt.get(aspekt_id)
        if aspekt and aspekt.ylesanne_id == int(id):
            try:
                aspekt.delete()
                model.Session.commit()
            except sa.exc.IntegrityError as e:
                msg = _("Ei saa enam kustutada, sest on seotud andmeid")
                self.error(msg)
                model.Session.rollback()
            else:
                self.c.item.calc_max_pallid()
                model.Session.commit()            
                self.success(_("Andmed on kustutatud"))
        return self._redirect('edit', id)

    def _delete_fail(self, id):
        item_id = self.request.params.get('fail_id')
        item = model.Ylesandefail.get(item_id)
        if item and item.ylesanne_id == int(id):
            try:
                item.delete()
                model.Session.commit()
            except sa.exc.IntegrityError as e:
                msg = _("Ei saa enam kustutada, sest on seotud andmeid")
                self.error(msg)
                model.Session.rollback()
            else:
                self.success(_("Andmed on kustutatud"))
        return self._redirect('edit', id)

    def _update(self, item):
        item.from_form(self.form.data, self._PREFIX)
        self._update_grid(item, model.Ylesandeobjekt, const.OBJ_ASSESSMENT)
        self._update_grid(item, model.Lahendusobjekt, const.OBJ_SOLUTION)
        self._update_grid(item, model.Lahteobjekt, const.OBJ_ORIGIN)
        self._update_grid(item, model.Hindamisobjekt, const.OBJ_MARKING)        

    def _update_grid(self, item, rowmodel, row_type):
        ctrl = BaseGridController(item.ylesandefailid, rowmodel, None, self)
        files = self.form.data[row_type]
        if len(files):
            new_rcd = files[0]
            update_files = files[1:]
            ctrl.save(update_files)
            if new_rcd.get('filedata') != None \
                    and new_rcd.get('filedata') != b'':
                # kui on fail, siis soovitakse uut kirjet lisada
                ctrl.create_subitem(new_rcd)

    def download(self):
        """Näita faili
        """
        id = self.request.matchdict.get('id')
        ylesandefail_id = self.request.matchdict.get('ylesandefail_id')
        format = self.request.matchdict.get('format')
        
        item = model.Ylesandefail.get(ylesandefail_id)
        if not item:
            raise NotFound('Kirjet ei leitud')
        assert item.ylesanne_id == int(id), _("Vale ülesanne")
        #return Response(item.filedata, content_type=item.mimetype, charset='utf-8')
        return utils.download(item.filedata, item.filename, item.mimetype)

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('ylesanded_juhised', id=parent_id))


    def _edit_markus(self, id):
        """Märkuse lisamise vormi avamine
        """
        self.c.fail_id = int(self.request.params.get('fail_id'))
        self.c.fail = model.Ylesandefail.get(self.c.fail_id)
        ylem_id = self.request.params.get('ylem_id')
        if ylem_id:
            self.c.ylem = model.Ylesandefailimarkus.get(ylem_id)
            assert self.c.ylem.ylesandefail_id == self.c.fail_id, _("Vale fail")
        return self.render_to_response('ekk/ylesanded/ylesandefailimarkus.mako')

    def _show_markus(self, id):
        """Märkuste vaatamine
        """
        self.c.fail_id = int(self.request.params.get('fail_id'))
        self.c.fail = model.Ylesandefail.get(self.c.fail_id)
        return self.render_to_response('ekk/ylesanded/ylesandefailimarkused.mako')

    def _update_markus(self, id):
        """Märkuse salvestamine
        """
        self.c.fail_id = int(self.request.params.get('fail_id'))
        self.c.fail = model.Ylesandefail.get(self.c.fail_id)
        self.form = Form(self.request, schema=forms.ekk.ylesanded.YlesandefailimarkusForm)
        if not self.form.validate():
            self.c.dialog_markus = True
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self.response_dict))
        else:
            model.Ylesandefailimarkus(ylesandefail_id=self.c.fail_id,
                         sisu=self.form.data.get('sisu'),
                         teema=self.form.data.get('teema'),
                         ylem_id=self.form.data.get('ylem_id'),
                         kasutaja_id=self.c.user.id)

            model.Session.commit()
            self.success(_("Märkus on lisatud!"))
            return HTTPFound(location=self.url('ylesanded_juhised', id=id))

    def __before__(self):
        self.c.item = model.Ylesanne.get(self.request.matchdict.get('id'))

    def _get_permission(self):
        action = self.c.action
        sub = self.request.params.get('sub')
        if action in ('edit','update','delete','create', 'new'):
            permission = 'ylesanded-failid'
        else:
            permission = 'ylesanded'
        return permission

    def _perm_params(self):
        return {'obj':self.c.item}


