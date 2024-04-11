# -*- coding: utf-8 -*- 
# $Id$

from eis.lib.baseresource import *
log = logging.getLogger(__name__)

class TyhistamineController(BaseResourceController):
    """Tunnistuste tühistamine
    """
    _permission = 'tunnistused'
    _MODEL = model.Tunnistus
    _INDEX_TEMPLATE = 'ekk/muud/tunnistused.tyhistamine.mako'
    _LIST_TEMPLATE = 'ekk/muud/tunnistused.tyhistamine_list.mako'
    _EDIT_TEMPLATE = 'ekk/muud/tunnistused.tyhistamine.edit.mako'
    _DEFAULT_SORT = 'tunnistus.id' # vaikimisi sortimine
    _SEARCH_FORM = forms.ekk.muud.TyhistamisedForm
    _ITEM_FORM = forms.ekk.muud.TyhistamineForm 
    
    def _search(self, q):
        if not self.c.isikukood and not self.c.tunnistusenr:
            self.error("Palun sisestada otsingutingimused")
            return
        
        if self.c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))                        
        if self.c.tunnistusenr:
            q = q.filter(model.Tunnistus.tunnistusenr==self.c.tunnistusenr)
            
        return q

    def _search_default(self, q):
        return

    def _query(self):
        q = (model.Session.query(model.Tunnistus,
                                 model.Kasutaja)
             .join(model.Tunnistus.kasutaja)
             )
        return q

    def _update(self, item, lang=None):
        # omistame vormilt saadud andmed
        staatus = self.form.data['staatus']
        if staatus == const.N_STAATUS_KEHTETU:
            # tyhistamine
            if item.staatus == const.N_STAATUS_KEHTETU:
                self.error('Tunnistus on juba kehtetu')
                return
        else:
            # ennistamine
            if item.staatus != const.N_STAATUS_KEHTETU:
                self.error('Tunnistus on juba kehtiv')
                return

        item.tyh_pohjendus = self.form.data['tyh_pohjendus']
        item.staatus = staatus

        if staatus == const.N_STAATUS_KEHTETU:
            # tyhistamine
            if self.form.data.get('tyh_sooritused'):
                # tyhistada ka testisooritused
                for r in item.testitunnistused:
                    sooritaja = r.sooritaja
                    for tos in sooritaja.sooritused:
                        if tos.staatus == const.S_STAATUS_TEHTUD:
                            tos.staatus = const.S_STAATUS_EEMALDATUD
                            #tos.hindamine_staatus = const.H_STAATUS_HINDAMATA
                            tos.pallid = 0
                    sooritaja.pallid = 0
                    sooritaja.tulemus_protsent = sooritaja.hinne = None
                    sooritaja.keeletase_kood = sooritaja.tulemus_piisav = None
                    sooritaja.update_staatus()
                    #resultentry = ResultEntry(self, None)            
                    #resultentry.update_sooritaja(sooritaja)                
        else:
            # ennistamine
            # kas on tyhistatud testisooritusi?
            # siin ei saa neid taastada, kuna ei ole teada, millised testiosasooritused tuleb taastada
            for r in item.testitunnistused:
                sooritaja = r.sooritaja
                if sooritaja.staatus == const.S_STAATUS_EEMALDATUD:
                    self.notice('Tühistatud testisoorituste taastamiseks palun märkida sooritused toimumisprotokollil tehtuks')
                    break
                
    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
            return self._redirect('index')
        else:
            return self._redirect('edit', id)

    def _download(self, id, format):
        """Näita faili"""
        item = self._MODEL.get(id)
        
        if not item:
            raise NotFound('Ei leitud')
        filename = item.filename
        filedata = item.filedata
        mimetype = item.mimetype
        if not filedata:
            raise NotFound('Dokumenti ei leitud')

        return utils.download(filedata, filename, mimetype)

