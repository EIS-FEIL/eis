# -*- coding: utf-8 -*- 
# $Id: tklassifikaatorid.py 890 2016-09-29 13:46:02Z ahti $

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController

log = logging.getLogger(__name__)

class TKlassifikaatoridController(BaseResourceController):
    "Klassifikaatorite haldamine"
    
    _permission = 'klassifikaatorid'
    _MODEL = model.Klassifikaator
    _ITEM_FORM = forms.admin.TKlassifikaatorForm
         
    _INDEX_TEMPLATE = 'admin/klassifikaatorid.mako' # otsinguvormi mall
    _LIST_TEMPLATE = '/admin/tklassifikaatorid_list.mako'
    _EDIT_TEMPLATE = 'admin/tklassifikaator.mako' # muutmisvormi mall
    _APP = const.APP_EIS
    _DEFAULT_SORT = 'nimi'
    
    def index(self):
        if not self.c.lang:
            return HTTPFound(location=self.h.url('admin_klassifikaatorid'))
        return BaseResourceController.index(self)
    
    def _query(self):
        q = model.Klassifikaator.query.\
            filter(model.Klassifikaator.app==self._APP)
        return q

    def _paginate(self, q):
        return q.all()
    
    def _edit(self, item):
        # seame valikud, nagu need varem olid
        if not self.c.lang:
            return HTTPFound(location=self.h.url('admin_klassifikaatorid'))
                    
        if self.c.item.kood == 'ERIVAJADUS':
            if self.c.aste == '':
                self.c.items = ''
            else:
                self.c.items = [r for r in self.c.item.read if r.bitimask == self.c.aste]
        elif not self.c.item.ylem_kood:
            # kui pole mitut taset, siis näidatakse kõik alamad
            self.c.items = self.c.item.read
        elif self.c.ylem_id:
            # aga kui on mitu taset
            # ja ylem on juba varem valitud
            self.c.items = [r for r in self.c.item.read if r.ylem_id == self.c.ylem_id]
        # kui ylem pole valitud, siis ei näidata algul midagi
        # ja pärast kasutaja valib ning klread kontroller näitab

    def _after_update(self, id):
        params = {}
        if self.c.ylem_id:
            params['ylem_id'] = self.c.ylem_id
        if self.c.ylem_id2:
            params['ylem_id2'] = self.c.ylem_id2            
        if self.c.aste != '':
            params['aste'] = str(self.c.aste)
        return HTTPFound(location=self.url('admin_edit_tklassifikaator', id=id, lang=self.c.lang, **params))

    def _update(self, item):
        if item.app != self._APP:
            self.error(_("Võõra rakenduse klassifikaator"))
            return HTTPFound(location=self.h.url('klassifikaatorid'))

        lang = self.c.lang
        
        nimi = self.form.data['f_nimi']
        if nimi:
            item.give_tran(lang).nimi = nimi
        else:
            tran = item.tran(lang, False)
            if tran:
                tran.delete()
                
        for valik in self.form.data['k']:
            rcd = model.Klrida.get(valik['id'])
            if rcd:
                if item.kood == 'TOOKASK':
                    nimi = valik['kirjeldus']
                else:
                    nimi = valik['nimi']
                
                if nimi:
                    trcd = rcd.give_tran(lang)
                    if item.kood == 'TOOKASK':
                        trcd.kirjeldus = nimi
                    else:
                        trcd.nimi = nimi
                else:
                    trcd = rcd.tran(lang, False)
                    if trcd:
                        trcd.delete()

    def _edit_kirjeldus(self, id):
        self.c.item = model.Klrida.get(id)
        return self.render_to_response('admin/tklrida.kirjeldus.mako')

    def _update_kirjeldus(self, id):
        item = model.Klrida.get(id)
        self.form = Form(self.request, schema=forms.admin.TKlridaKirjeldusForm)
        if not self.form.validate():
            return Response(self._INDEX_TEMPLATE, extra_info=self._index_d())

        tran = item.give_tran(self.c.lang)
        tran.kirjeldus = self.form.data.get('f_kirjeldus')
        #tran.pais = self.form.data.get('pais')
        model.Session.commit()
        self.success()
        return self._after_update(item.klassifikaator_kood)

    def __before__(self):
        c = self.c
        c.lang = self.params_lang()
        if not c.lang:
            c.lang = self.request.matchdict.get('lang')
        if not re.match(r'^[a-z]{2}$', self.c.lang):
            c.lang = None
        
        c.ylem_id = self.request.params.get('ylem_id')
        if c.ylem_id:
            c.ylem_id = int(self.c.ylem_id)
            c.ylem = model.Klrida.get(self.c.ylem_id)

        c.ylem_id2 = self.request.params.get('ylem_id2')
        if c.ylem_id2:
            c.ylem_id2 = int(self.c.ylem_id2)

        aste = self.request.params.get('aste')
        if aste:
            c.aste = int(aste)

        BaseResourceController.__before__(self)        

