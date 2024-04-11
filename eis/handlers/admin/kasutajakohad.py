from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)

class KasutajakohadController(BaseResourceController):
    _permission = 'kasutajad'
    _INDEX_TEMPLATE = '/admin/kasutaja.kohad.mako' # otsinguvormi mall

    def _query(self):
        return None

    def _new_roll(self):
        "Soorituskoha administraatoriks määramine"
        self.c.roll = self.c.new_item()

        lubatud = self.c.user.get_kasutaja().get_piirkonnad_id('kasutajad', const.BT_SHOW)
        if None not in lubatud:
            self.c.piirkond_filtered = lubatud
        else:
            self.c.piirkond_filtered = None

        return self.render_to_response('/admin/kasutaja.koht.mako')

    def _create_roll(self):
        "Soorituskoha administraatoriks määramine"
        self.c.roll = self.c.new_item()
        self.c.nosub = True

        self.form = Form(self.request, schema=forms.admin.KasutajarollForm)
        if not self.form.validate():        
            return Response(self.form.render('admin/kasutaja.koht.mako', 
                                             extra_info=self._index_d()))

        data = self.form.data
        koht_id = data.get('koht_id')
        kehtib_kuni = data.get('kehtib_kuni') or const.MAX_DATE
        kasutajagrupp_id = int(data.get('kasutajagrupp_id'))
        if kasutajagrupp_id == const.GRUPP_AINEOPETAJA:
            aine_kood = data.get('aine_kood')
        else:
            aine_kood = None

        antavad_grupid = [r[0] for r in self.c.opt.get_antav_kooligrupp(self.c.app_ekk)]
        lubatud = self.c.user.get_kasutaja().get_piirkonnad_id('kasutajad', const.BT_UPDATE)
        if None not in lubatud and model.Koht.get(koht_id).piirkond_id not in lubatud:
            self.error(_("Puudub õigus antud piirkonna kohta"))
        elif kasutajagrupp_id not in antavad_grupid:
            self.error(_("Antud rolli ei saa anda"))
        elif model.Kasutajaroll.query.\
               filter_by(kasutaja_id=self.c.kasutaja.id).\
               filter_by(koht_id=koht_id).\
               filter_by(aine_kood=aine_kood).\
               filter_by(kasutajagrupp_id=kasutajagrupp_id).\
               count() > 0:
            self.error(_("Valitud soorituskohaga on isik valitud rollis juba seotud"))
        else:
            rcd = model.Kasutajaroll(kasutaja_id=self.c.kasutaja.id,
                                     koht_id=koht_id,
                                     kasutajagrupp_id=kasutajagrupp_id,
                                     aine_kood=aine_kood,
                                     kehtib_alates=date.today(),
                                     kehtib_kuni=kehtib_kuni)
            self._log_roll(rcd, False)
            model.Session.commit()
            self.success()
        return HTTPFound(location=self.url('admin_kasutaja_kohad', kasutaja_id=self.c.kasutaja.id))
   
    def _edit_roll(self, id):
        self.c.roll = model.Kasutajaroll.get(id)
        return self.render_to_response('/admin/kasutaja.kehtib_kuni.mako')
    
    def _update_roll(self, id):
        self.c.roll = model.Kasutajaroll.get(id)
        self.form = Form(self.request, schema=forms.admin.KehtibkuniForm)
        if not self.form.validate():        
            return Response(self.form.render('admin/kasutaja.kehtib_kuni.mako', 
                                             extra_info=self._index_d()))
        
        self.c.roll.kehtib_kuni = self.form.data.get('kehtib_kuni') or const.MAX_DATE
        self._log_roll(self.c.roll, False)
        model.Session.commit()
        self.success()
        return HTTPFound(location=self.url('admin_kasutaja_kohad', kasutaja_id=self.c.kasutaja.id))

    def _delete_roll(self, id):
        rcd = model.Kasutajaroll.get(id)
        assert rcd.kasutaja_id == self.c.kasutaja.id, _("Vale kasutaja")
        self._log_roll(rcd, True)
        rcd.delete()
        model.Session.commit()
        return HTTPFound(location=self.url('admin_kasutaja_kohad', kasutaja_id=self.c.kasutaja.id))
    
    def _new_koht(self):
        "Soorituskoha kiirvalikusse määramine"
        self.c.roll = self.c.new_item()

        lubatud = self.c.user.get_kasutaja().get_piirkonnad_id('kasutajad', const.BT_SHOW)
        if None not in lubatud:
            self.c.piirkond_filtered = lubatud
        else:
            self.c.piirkond_filtered = None

        return self.render_to_response('/admin/kasutaja.koht.mako')
    
    def _create_koht(self):
        "Soorituskoha kiirvalikusse määramine"
        self.form = Form(self.request, schema=forms.admin.KasutajakohtForm)
        self.c.roll = self.c.new_item()     
        if not self.form.validate():   
            return Response(self.form.render('admin/kasutaja.koht.mako', 
                                             extra_info=self._index_d()))
        
        koht_id = self.form.data.get('koht_id')
        lubatud = self.c.user.get_kasutaja().get_piirkonnad_id('kasutajad', const.BT_UPDATE)
        if None not in lubatud and model.Koht.get(koht_id).piirkond_id not in lubatud:
            self.error(_("Puudub õigus antud piirkonna kohta"))
            
        elif model.Kasutajakoht.query.\
                filter_by(kasutaja_id=self.c.kasutaja.id).\
                filter_by(koht_id=koht_id).\
                count() > 0:
            self.error(_("Valitud soorituskohaga on isik juba seotud"))
            return Response(self.form.render('admin/kasutaja.koht.mako', 
                                             extra_info=self._index_d()))
        else:
            model.Kasutajakoht(kasutaja_id=self.c.kasutaja.id,
                               koht_id=koht_id)

            koht = model.Koht.get(koht_id)
            model.Kasutajapiirkond.give(self.c.kasutaja, koht.piirkond)
            model.Session.commit()
            self.success()
        return HTTPFound(location=self.url('admin_kasutaja_kohad', kasutaja_id=self.c.kasutaja.id))

    def _delete_koht(self, id):
        rcd = model.Kasutajakoht.get(id)
        assert rcd.kasutaja_id == self.c.kasutaja.id, _("Vale kasutaja")
        rcd.delete()
        model.Session.commit()
        return HTTPFound(location=self.url('admin_kasutaja_kohad', kasutaja_id=self.c.kasutaja.id))

    def _log_roll(self, roll, is_delete):
        grupp_id = roll.kasutajagrupp_id
        if is_delete:
            sisu = 'Eemaldamine\n' + roll.get_str()
        else:
            old_values, new_values = roll._get_changed_values()
            if not new_values:
                return
            sisu = roll.get_str()
        krl = model.Kasutajarollilogi(kasutaja_id=roll.kasutaja_id,
                                      muutja_kasutaja_id=self.c.user.id,
                                      aeg=datetime.now(),
                                      sisu=sisu,
                                      kasutajagrupp_id=grupp_id,
                                      kasutajaroll=not is_delete and roll or None,
                                      tyyp=const.USER_TYPE_KOOL)
           
    def __before__(self):
        self.c.kasutaja = model.Kasutaja.get(self.request.matchdict.get('kasutaja_id'))
