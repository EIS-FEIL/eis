from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.ekk.korraldamine.koht import otsilabiviijad

log = logging.getLogger(__name__)

class OtsilabiviijadController(otsilabiviijad.OtsilabiviijadController):
    """Läbiviijate otsimine dialoogiaknas.
    """
    _permission = 'avalikadmin'
    _INDEX_TEMPLATE = 'avalik/korraldamine/otsilabiviijad.mako'
    _no_paginate = True
    _ITEM_FORM = forms.admin.ProfiilForm
    _EDIT_TEMPLATE = '/avalik/korraldamine/labiviijaprofiil.mako' # profiili muutmise vormi mall
    
    def _search(self, q1):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        self.c.grupp_id = int(self.c.grupp_id)

        # kui kool määrab suulise osa hindajaid, siis need ei pea olema eelnevalt käskkirja kantud,
        # kuna käskkirja kantakse nad alles peale määramist (EH-300)
        testiosa = self.c.toimumisaeg.testiosa
        if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
            on_kaskkiri = False
        else:
            on_kaskkiri = True
            
        if self.c.isikukood:
            q = self.c.testikoht.get_valik_q(self.c.grupp_id, on_kasutamata=False, on_kaskkiri=on_kaskkiri)
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        else:
            # vaikimisi näitame kohaga seotuid ehk kiirvalikus olevaid isikuid
            q = self.c.testikoht.get_kiirvalik_q(self.c.grupp_id, on_kasutamata=True, lang=None, on_kaskkiri=on_kaskkiri)

        if self.c.isikukood and q.count() == 0:
            self._selgita_sobimatust(on_kaskkiri=on_kaskkiri)

        return q

    def _search_default(self, q):
        return self._search(q)

    def _edit(self, item):
        c = self.c
        kasutaja = item
        koht = c.testikoht.koht
        grupp_id = c.grupp_id
        viga_profiilis, errors = otsilabiviijad.selgita_lv_sobimatust(self, kasutaja, c.toimumisaeg, koht, grupp_id, lang=c.lang)
        if errors:
            msg = ' '.join(errors)
            self.error(msg)

    def _update(self, item):
        # avalikus vaates saab testidega seotud isikute profiili 
        # täiendada uute rollide ja ainetega,
        # kuid olemasolevaid andmeid muuta ega ära võtta ei saa

        epost = self.form.data.get('k_epost')
        if epost and not item.epost:
            item.epost = epost
        
        item.on_labiviija = True
        profiil = item.give_profiil()
        profiil.from_form(self.form.data, 'f_', add_only=True)

        def _add_lang(keeled, key):
            li = (keeled or '').split()
            for lang in self.form.data.get(key):
                if lang not in li:
                    li.append(lang)
            return ' '.join(li)
            
        profiil.v_skeeled = _add_lang(profiil.v_skeeled, 'v_skeel')
        profiil.k_skeeled = _add_lang(profiil.k_skeeled, 'k_skeel')
        profiil.s_skeeled = _add_lang(profiil.s_skeeled, 's_skeel')
        
        # lisame uued aineprofiilid
        err = None
        for rcd in self.form.data.get('a'):
            # kontrollime, et seda rolli juba varasemast olemas ei ole
            found = False
            for a in item.aineprofiilid:
                if a.aine_kood == rcd['aine_kood'] and \
                        a.kasutajagrupp_id == rcd['kasutajagrupp_id'] and \
                        (a.keeletase_kood or None) == (rcd['keeletase_kood'] or None):
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

    def _update_seo(self, id):
        "Seo isik soorituskohaga"
        k = model.Kasutaja.get(id)
        koht = self.c.testikoht.koht
        q = (model.Session.query(model.Kasutajakoht)
             .filter(model.Kasutajakoht.koht==koht)
             .filter(model.Kasutajakoht.kasutaja==k))
        if q.count():
            self.notice('Isik on juba soorituskohaga seotud')
        else:
            model.Kasutajakoht(kasutaja=k, koht=self.c.testikoht.koht)
            model.Session.commit()

        self.c.isikukood = k.isikukood
        q = self._query()
        q = self._search(q)
        self.c.items = self._paginate(q)
        return self._showlist()

    def _paginate(self, q):
        if not q.count():
            return ''
        else:
            return q.all()

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        c = self.c
        if self.has_errors():
            return self._redirect('edit', id, labiviija_id=c.labiviija_id, grupp_id=c.grupp_id)
        else:
            self.success()
            kasutaja = model.Kasutaja.get(id)            
            return self._redirect('index', grupp_id=c.grupp_id, labiviija_id=c.labiviija_id, isikukood=kasutaja.isikukood)
        
    def __before__(self):
        c = self.c
        c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))
        c.toimumisaeg = c.testikoht.toimumisaeg
        labiviija_id = self.request.params.get('labiviija_id')
        if labiviija_id:
            c.labiviija = model.Labiviija.get(labiviija_id)
            if c.labiviija:
                c.labiviija_id = c.labiviija.id
                c.grupp_id = c.labiviija.kasutajagrupp_id
        else:
            c.grupp_id = int(self.request.params.get('grupp_id'))
            
    def _perm_params(self):
        c = self.c
        if c.testikoht.koht_id != c.user.koht_id:
            return False
        if not c.grupp_id:
            return False
