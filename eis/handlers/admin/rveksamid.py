# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
_ = i18n._

log = logging.getLogger(__name__)

class RveksamidController(BaseResourceController):
    """Rahvusvaheliste eksamite tunnistused
    """
    _permission = 'rveksamid'

    _MODEL = model.Rveksam
    _EDIT_TEMPLATE = 'admin/rveksam.mako'
    _INDEX_TEMPLATE = 'admin/rveksamid.mako'
    _ITEM_FORM = forms.admin.RveksamForm
    _DEFAULT_SORT = 'rveksam.nimi'
    
    def index(self):
        self.c.items = model.Rveksam.query.order_by(model.Rveksam.nimi).all()
        return self.render_to_response(self._INDEX_TEMPLATE)

    def _edit(self, item):
        if self.request.params.get('lisaosaoskus'):
            # lisada tabelisse uus osaoskuse rida
            self.c.lisaosaoskus = True
    
    def _update(self, item):
        # omistame vormilt saadud andmed
        item.from_form(self.form.data, self._PREFIX)
        if item.kantav_tulem and item.tulemusviis != model.Rveksam.TULEMUSVIIS_PALL:
            err = {'f_kantav_tulem': _("Tulemusi saab testisooritusele kanda ainult siis, kui tulemused esitatakse punktidena")}
            raise ValidationError(self, err)
        BaseGridController(item.rveksamitulemused,
                           model.Rveksamitulemus).\
                           save(self.form.data.get('tulemus'))

        vanad = list(item.rvosaoskused)
        uued_id = list()
        for rcd in self.form.data.get('osa'):
            osa_id = rcd['id']
            uued_id.append(osa_id)
            self._update_osa(item, osa_id, rcd)
        for r in vanad:
            if r.id not in uued_id:
                r.delete()
        model.Session.flush()
        model.Klrida.clean_cache('Rveksam')
        
    def _update_osa(self, item, osa_id, rcd):
        if osa_id:
            osa = model.Rvosaoskus.get(osa_id)
            assert osa.rveksam_id == item.id
        else:
            li = [r.seq for r in item.rvosaoskused if r.seq]
            if li:
                seq = max(li) + 1
            else:
                seq = 1
            osa = model.Rvosaoskus(seq=seq)
            item.rvosaoskused.append(osa)

        osa.nimi = rcd['nimi']
        osa.alates = rcd['alates']
        osa.kuni = rcd['kuni']
        BaseGridController(osa.rvosatulemused,
                           model.Rvosatulemus).\
                           save(rcd.get('tulemus'))        

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if self.request.params.get('lisaosaoskus'):
            return self._redirect('edit', id, lisaosaoskus=1)
        return BaseResourceController._after_update(self, id)

    def _download(self, id, format=None):
        """Näita faili"""
        if format == 'raw':
            # testi eksport
            import eis.lib.raw_export as raw_export
            item = model.Rveksam.get(id)            
            filedata = raw_export.export(item, False)
            filename = 'rveksam%s.raw' % id
            mimetype = 'application/octet-stream'
            return utils.download(filedata, filename, mimetype)
        
