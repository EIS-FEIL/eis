# -*- coding: utf-8 -*- 

import os.path
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class ToofailidController(BaseResourceController):

    _permission = 'failid'

    _MODEL = model.Toofail
    _INDEX_TEMPLATE = 'ekk/muud/toofailid.mako'
    _LIST_TEMPLATE = 'ekk/muud/toofailid_list.mako'
    _EDIT_TEMPLATE = 'ekk/muud/toofail.mako' 

    _SEARCH_FORM = forms.ekk.muud.ToofailidForm 
    _ITEM_FORM = forms.ekk.muud.ToofailForm
    _DEFAULT_SORT = '-toofail.id' # vaikimisi sortimine
    
    def _create(self, **kw):
        item = model.Toofail()
        self._update(item)
        if not item.filedata:
            self.error(_("Fail puudub"))
            return self._redirect('new')
        return item

    def _update(self, item):
        # omistame vormilt saadud andmed
        #filename, filedata = self._check_filename(None)
        #if filename and filedata:
        #    item.filename = filename
        #    item.filedata = filedata
        if not self.form.data['f_oppetase_kood']:
            self.form.data['f_oppetase_kood'] = None
        item.from_form(self.form.data, 'f_')
        filename = self.form.data['filename']
        if filename:
            item.filename = filename

        avalik_alates = self.form.data['avalik_kuupaev']
        if avalik_alates:
            kell = self.form.data['avalik_kell']
            if kell:
                avalik_alates = datetime.combine(avalik_alates, time(kell[0], kell[1]))
        else:
            avalik_alates = datetime.now()
        item.avalik_alates = avalik_alates

        test_id = self.form.data['test_id']
        if test_id:
            test = model.Test.get(test_id)
            if not test:
                raise ValidationError(self, {'test_id': _("Testi {id} ei leitud").format(id=test_id)})
        item.test_id = test_id
                
        # salvestame haridustasemed
        tasemed = self.request.params.getall('tase_kood')
        lubatud = [r[1] for r in self.c.opt.klread('KAVATASE', ylem_kood=item.oppetase_kood)]
        for r in item.toofailitasemed:
            if r.kavatase_kood not in tasemed or r.kavatase_kood not in lubatud:
                r.delete()
            else:
                tasemed.pop(tasemed.index(r.kavatase_kood))
        for kood in tasemed:
            if kood in lubatud:
                model.Toofailitase(kavatase_kood=kood, toofail=item)

    def _check_filename(self, item_id):
        filevalue = self.form.data.get('f_filedata')
        if filevalue != b'':
            # kui anti fail, siis muudame filedata ja filename
            # value on FieldStorage objekt
            filename = _fn_local(filevalue.filename)
            filedata = filevalue.value
            return filename, filedata
        return None, None

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.filename:
            q = q.filter(model.Toofail.filename.ilike('%'+self.c.filename+'%'))
        if self.c.kirjeldus:
            q = q.filter(model.Toofail.kirjeldus.ilike('%'+self.c.kirjeldus+'%'))
        return q

def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath

