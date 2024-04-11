# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)

class YldandmedController(BaseResourceController):
    _permission = 'korraldamine'
    _ITEM_FORM = forms.ekk.korraldamine.KohtYldandmedForm
    _INDEX_TEMPLATE = '/ekk/korraldamine/koht.yldandmed.mako' 
    _index_after_create = True

    def _query(self):
        return None

    def _create(self):
        """Testiruumide valiku salvestamine
        """
        testiosa = self.c.toimumisaeg.testiosa
        vastvorm_kood = testiosa.vastvorm_kood

        # arvutame igaks juhuks sooritajate arvu yle
        for tr in self.c.testikoht.testiruumid:
            tr.set_sooritajate_arv()

        class TestiruumGridController(BaseGridController):
            def create_subitem(self, rcd, lang=None):
                subitem = model.Testiruum()
                subitem.from_form(rcd, lang=lang)
                self._COLLECTION.append(subitem)
                subitem.testikoht = self.parent
                self.parent.testiruumid.append(subitem)
                subitem.gen_tahis(self.parent)
                subitem.algus = subitem.uus_algus = rcd.get('uus_algus')
                return subitem
            
            def update_subitem(self, subitem, rcd, lang=None):
                oli_lopp = subitem.lopp
                subitem.from_form(rcd, lang=lang)
                subitem.uus_algus = rcd.get('uus_algus')
                if subitem.lopp and oli_lopp and subitem.lopp != oli_lopp:
                    model.Sooritus.set_piiraeg_muutus(testiosa.id, testiruum_id=subitem.id)
                return subitem

            def can_delete(self, subitem):
                return subitem.sooritajate_arv == 0

        errors = dict()
        
        # loeme postitatud andmed ja jagame ruumide kaupa
        rdata = {}
        rlist = []
        rfwd = {}
        for n_ruum, row in enumerate(self.form.data.get('ruum')):
            ruum_id = row.get('id')
            if not ruum_id:
                # määramata ruum, kas on valitud valikust uus ruum?
                uus_ruum_id = row.get('uus_ruum_id')
                if uus_ruum_id:
                    ruum_id = rfwd[None] = uus_ruum_id
            if ruum_id:
                ruum = model.Ruum.get(ruum_id)
                assert ruum.koht_id == self.c.testikoht.koht_id, _("Vale koha ruum")
            tr_rows = row.get('tr')
            if ruum_id not in rdata:
                rdata[ruum_id] = []
                rlist.append(ruum_id)
            rdata[ruum_id].append((n_ruum, tr_rows))

        # jagame andmebaasis olevad testiruumid ruumide kaupa
        testiruumid = dict()
        for tr in self.c.testikoht.testiruumid:
            ruum_id = tr.ruum_id
            if ruum_id is None:
                ruum_id = rfwd.get(ruum_id)
            if ruum_id in testiruumid:
                testiruumid[ruum_id].append(tr)
            else:
                testiruumid[ruum_id] = [tr]

        # salvestame muudatused
        voib_korduda = self.c.toimumisaeg.ruum_voib_korduda
        for ruum_id in rlist:
            paevad = set()
            tr_rows2 = [] # jada, kuhu on mitu jada kokku pandud, kui määramata ruum on teiseks ruumiks tõstetud
            
            for n_ruum, tr_rows in rdata[ruum_id]:
                for n_tr, tr_row in enumerate(tr_rows):
                    tr_row['ruum_id'] = ruum_id
                    toimumispaev_id = tr_row.get('toimumispaev_id')
                    if not voib_korduda:
                        if toimumispaev_id in paevad:
                            prefix = 'ruum-%d.tr-%d' % (n_ruum, n_tr)
                            errors['%s.toimumispaev_id' % prefix] = _("Üht ruumi ei tohi ühel toimumispäeval mitu korda kasutada")
                        paevad.add(toimumispaev_id)

                    tpv = model.Toimumispaev.get(toimumispaev_id)
                    if tpv:
                        kell = tr_row.get('kell')
                        if kell:
                            tr_row['uus_algus'] = datetime.combine(tpv.aeg, time(kell[0],kell[1]))
                        else:
                            tr_row['uus_algus'] = tpv.aeg

                        lopp = tr_row.get('t_lopp')
                        if lopp:
                            tr_row['lopp'] = datetime.combine(tpv.lopp or tpv.aeg, time(lopp[0],lopp[1]))
                        else:
                            tr_row['lopp'] = tpv.lopp
                    tr_rows2.append(tr_row)

            if ruum_id in testiruumid:
                ruumi_testiruumid = testiruumid[ruum_id]
            else:
                ruumi_testiruumid = list()
            g = TestiruumGridController(ruumi_testiruumid, model.Testiruum, parent=self.c.testikoht)
            g.save(tr_rows2)

            for testiruum in ruumi_testiruumid:
                if testiruum not in g.deleted:
                    self.c.testikoht.set_testiruum(testiruum)
                    testiruum.give_labiviijad(self.c.testikoht)
                    try:
                        uus_algus = testiruum.uus_algus
                    except AttributeError:
                        pass
                    else:
                        if testiruum.algus != uus_algus:
                            testiruum.muuda_algus(uus_algus)
                        
        if errors:
            raise ValidationError(self, errors)
        model.Session.flush()
        model.Session.refresh(self.c.testikoht)
        testiruumid = list(self.c.testikoht.testiruumid)
        if not testiruumid:
            # kui kõik testiruumid on eemaldatud, siis eemaldame ka testikoha
            nimi = self.c.testikoht.koht.nimi
            self.c.testikoht.delete()
            model.Session.commit()
            self.success(_("{s} eemaldati toimumisaja soorituskohtade seast").format(s=nimi))
            return HTTPFound(location=self.url('korraldamine_soorituskohad', toimumisaeg_id=self.c.toimumisaeg.id))
        self.c.testikoht.alates = min([tr.algus for tr in testiruumid])
        model.Session.commit()
        self.success()
        return self._redirect('index')

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE,
                                extra_info=self._index_d())            
        return Response(html)

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))

    def _perm_params(self):
        return {'obj':self.c.testikoht}
