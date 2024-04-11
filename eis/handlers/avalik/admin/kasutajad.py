from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.admin import kasutajad
log = logging.getLogger(__name__)

class KasutajadController(kasutajad.KasutajadController):

    _MODEL = model.Kasutaja
    _SEARCH_FORM = forms.admin.KasutajadForm
    _ITEM_FORM = forms.admin.ProfiilForm
    _INDEX_TEMPLATE = '/avalik/admin/kasutajad.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = '/avalik/admin/kasutaja.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/avalik/admin/kasutajad_list.mako'
    _DEFAULT_SORT = 'perenimi'
    _get_is_readonly = False
    _permission = 'avalikadmin'
                    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(self.c.isikukood).filter(model.Kasutaja))
            item = q.first()
            if item and not item.on_labiviija:
                self.error(_("Selle isikukoodiga kasutaja ei ole seotud testide läbiviimisega"))
        else:
            q = q.filter(model.Kasutaja.on_labiviija==True)

        if self.c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(self.c.eesnimi))
        if self.c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(self.c.perenimi))

        if not self.c.isikukood and not self.c.eesnimi and not self.c.perenimi:
            self.error(_("Palun sisesta otsinguparameetrid"))
            return None
        else:
            return q
           
    def new(self):
        # erinevalt eksamikeskuse vaatest saab avalikus vaates
        # uut kasutajat lisada ainult isikukoodi järgi otsides

        item = None
        isikukood = self.request.params.get('isikukood')
        if isikukood:
            # kui uue isiku loomisel on isikukood ette antud, siis 
            # otsitakse selle isikukoodi järgi andmeid
            # esmalt EISist
            isikukood = isikukood.strip()
            item = model.Kasutaja.get_by_ik(isikukood)
            if not item:
                # kui EISis pole, siis otsitakse RRist
                item = xtee.set_rr_pohiandmed(self, None, isikukood=isikukood)
                if item:
                    # isik leiti RRist, salvestame
                    model.Session.commit()

        if item:
            self.c.item = item
            template = self._EDIT_TEMPLATE
        else:
            self.c.isikukood = isikukood
            template = 'avalik/admin/kasutaja.uus.mako'
        return self.render_to_response(template)


    def _update(self, item):
        # avalikus vaates saab testidega seotud isikute profiili 
        # täiendada uute rollide ja ainetega,
        # kuid olemasolevaid andmeid muuta ega ära võtta ei saa

        item.on_labiviija = True

        epost = self.form.data.get('k_epost')
        if epost and not item.epost:
            item.epost = epost
            
        profiil = item.give_profiil()
        profiil.from_form(self.form.data, 'f_', add_only=True)
        for lang in self.form.data.get('k_skeel'):
            profiil.set_k_lang(lang)
        for lang in self.form.data.get('s_skeel'):
            profiil.set_s_lang(lang)
        for lang in self.form.data.get('v_skeel'):
            profiil.set_v_lang(lang)

        # lisame uued aineprofiilid
        err = None
        for rcd in self.form.data.get('a'):
            # kontrollime, et seda rolli juba varasemast olemas ei ole
            found = False
            for a in item.aineprofiilid:
                if a.aine_kood == rcd['aine_kood'] and \
                       a.kasutajagrupp_id == rcd['kasutajagrupp_id'] and \
                       (not rcd['keeletase_kood'] or a.keeletase_kood == rcd['keeletase_kood']):
                    found = True
                    err = _("Olemasolevaid rolle lisada ega muuta ei saa")
                    break
            if not found:
                # kui rolli juba pole, siis võime lisada
                subitem = model.Aineprofiil()
                subitem.from_form(rcd)
                item.aineprofiilid.append(subitem)

        if err:
            self.error(err)
