# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController

log = logging.getLogger(__name__)

class PiirkonnadController(BaseResourceController):
    _permission = 'piirkonnad'
    _MODEL = model.Piirkond
    _SEARCH_FORM = forms.admin.PiirkonnadForm
    _ITEM_FORM = forms.admin.PiirkondForm
    _INDEX_TEMPLATE = 'admin/piirkonnad.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = 'admin/piirkond.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/admin/piirkonnad_list.mako'
    _DEFAULT_SORT = 'nimi'

    def create(self):
        "Piirkondade andmete salvestamine"

        def can_update(prk):
            "Kontrollitakse, et on piirkonna andmete muutmise õigus"
            if not prk:
                # kui piirkonda pole, siis võib muuta
                return True
            # muidu kontrollime õigust
            return prk.has_permission('piirkonnad', const.BT_UPDATE, self.c.user)

        data = self.request.params.get('changed_data')
        di = {}
        li_deleted = []
        err_koht = err_prk = None

        for item in data.split('\n'):
            if item:
                id, parent_id, name = item.split(':',3)
                # kuskilt tuleb \r andmebaasi
                name = name.replace('\r','').strip()
                di[id] = (parent_id, name)
        for id in di:
            koht = piirkond = None
            parent_id, name = di[id]
            if id[0] == 'K':
                # olemasolev soorituskoht
                koht_id = int(id[1:])
                koht = model.Koht.get(koht_id)
                if not can_update(koht.piirkond):
                    err_koht = koht
                    break
                    
                if name:
                    koht.nimi = name
            else:
                # olemasolev või uus piirkond
                piirkond_id = int(id)
                if piirkond_id < 0:
                    # uue lisamine
                    piirkond = model.Piirkond(nimi=name)
                else:
                    # olemasoleva muutmine
                    piirkond = model.Piirkond.get(piirkond_id)
                    if not can_update(piirkond):
                        err_prk = piirkond
                        break

                    if name:
                        # nimi muutus ka
                        piirkond.nimi = name

            if parent_id:
                if parent_id == 'DELETED':
                    if piirkond:
                        if not can_update(piirkond):
                            err_prk = piirkond
                            break

                        li_deleted.append(piirkond.id)
                        try:
                            piirkond.delete()
                            model.Session.flush()
                        except sa.exc.IntegrityError as e:
                            self.error('Prooviti kustutada juba kasutusele võetud piirkonda')
                            model.Session.rollback()
                            break
                elif parent_id[0] != 'K':
                    # parent_id võib olla:
                    # tühi string, kui pole muutunud
                    # 0, kui vanem puudub
                    # positiivne arv, kui on vanem
                    if parent_id == '':
                        # pole muudetud
                        continue
                    if parent_id == '#':
                        # ülempiirkonnata
                        parent_id = None
                    else:
                        parent_id = int(parent_id) or None
                        if parent_id in li_deleted:
                            # kustutatud 
                            continue
                    if parent_id:
                        # pole piirkonnata
                        parent = model.Piirkond.get(parent_id)
                        if not can_update(parent):
                            err_prk = parent
                            break

                    if piirkond:
                        piirkond.ylem_id = parent_id
                    else:
                        koht.piirkond_id = parent_id

        if err_koht:
            self.error('Puudub õigus soorituskoha "%s" andmete muutmiseks.' % (err_koht.nimi))
        elif err_prk:
            self.error('Puudub õigus piirkonna "%s" andmete muutmiseks.' % (err_prk.nimi))
        else:
            try:
                model.Session.commit()
                self.success()
            except sa.exc.IntegrityError as e:
                self.error('Prooviti kustutada juba kasutusele võetud piirkonda')
                model.Session.rollback()

        return HTTPFound(location=self.url('admin_piirkonnad'))

