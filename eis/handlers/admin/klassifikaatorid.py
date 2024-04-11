from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
import eis.lib.raw_export as raw_export

log = logging.getLogger(__name__)

class KlassifikaatoridController(BaseResourceController):
    "Klassifikaatorite haldamine"
    
    _permission = 'klassifikaatorid'
    _ITEM = 'klassifikaator'
    _ITEMS = 'klassifikaatorid'
    _MODEL = model.Klassifikaator

    @property
    def _ITEM_FORM(self):
        kood = self.request.matchdict.get('id')
        if kood in (const.KL_KOOLITYYP, const.KL_OMANDIVORM, const.KL_ALAMLIIK, const.KL_KAVATASE):
            return forms.admin.KlassifikaatorEHISForm
        else:
            return forms.admin.KlassifikaatorForm
         
    _INDEX_TEMPLATE = 'admin/klassifikaatorid.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = 'admin/klassifikaator.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/admin/klassifikaatorid_list.mako'
    _DEFAULT_SORT = 'nimi'
    _no_paginate = True
    
    _APP = const.APP_EIS

    def index(self):
        lang = self.params_lang()
        if lang:
            return HTTPFound(location=self.h.url('admin_tklassifikaatorid', lang=lang))
        return BaseResourceController.index(self)

    def _query(self):
        q = model.Klassifikaator.query.\
            filter(model.Klassifikaator.app==self._APP)
        return q

    def _paginate(self, q):
        return q.all()

    def _edit(self, item):
        c = self.c
        #log.debug(str(dir(item.read)))
        # seame valikud, nagu need varem olid
                    
        if c.item.kood == 'ERIVAJADUS':
            if c.aste == '':
                c.items = ''
            else:
                c.items = [r for r in c.item.read if r.bitimask == c.aste]
        elif c.item.kood == 'HTUNNUS':
            c.testiklass = self.request.params.get('testiklass')
            c.items = [r for r in c.item.read if r.ylem_id == c.ylem_id and r.testiklass_kood==c.testiklass]            
        elif c.item.kood == 'KEELETASE':
            # keeletaseme klassifikaatori read on ilma aineta
            # ainega seotud kirjetes on ainult koodid
            c.items = [r for r in c.item.read if not r.ylem_id]
            if c.ylem_id:
                c.seostatud = [r.kood for r in c.item.read if r.ylem_id==c.ylem_id and r.kehtib]
            log.debug('READ=%s' % len(c.items))
        elif not c.item.ylem_kood:
            # kui pole mitut taset, siis näidatakse kõik alamad
            c.items = c.item.read
        elif c.ylem_id:
            # aga kui on mitu taset
            # ja ylem on juba varem valitud
            c.items = [r for r in c.item.read if r.ylem_id == c.ylem_id]

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
        if self.c.testiklass:
            params['testiklass'] = self.c.testiklass
        return HTTPFound(location=self.url('admin_edit_klassifikaator', id=id, **params))

    def _update(self, item):
        if item.app != self._APP:
            self.error(_("Võõra rakenduse klassifikaator"))
            return self._redirect('index')

        self.c.item = item
        item.from_form(self.form.data, self._PREFIX)
        #if item.kood == 'ASTE' and self.c.ylem_id == '':
        #    self.c.ylem_id = None
        if item.kood == 'HTUNNUS':
            self.c.testiklass = self.form.data.get('testiklass')            

        if not item.ylem_kood or self.c.ylem_id != '' or item.kood == 'KEELETASE':
            # on tasemeta klassifikaator või on valitud tase
            # filtreerime klassifikaatori kõigist ridadest need, mida praegu muudetakse
            valikud = self.form.list_in_posted_order('k')
              
            if self.c.ylem_id != '':
                collection = [r for r in item.read if r.ylem_id == self.c.ylem_id]
                if item.kood == 'HTUNNUS':
                    collection = [r for r in collection if r.testiklass_kood==self.c.testiklass]
            elif item.kood == 'KEELETASE':
                collection = [r for r in item.read if not r.ylem_id]
            else:
                collection = item.read

            self.current_id = item.kood

            # muudame read
            koodid = []
            if item.kood == 'ERIVAJADUS':
                if self.c.aste == '':
                    return
                collection = []
                for r in item.read:
                    if r.bitimask == self.c.aste:
                        collection.append(r)
                    else:
                        koodid.append(r.kood)
                collection = [r for r in item.read if r.bitimask == self.c.aste]
                self._unique_kood(valikud, 'k', koodid)
                for v in valikud:
                    v['bitimask'] = self.c.aste
                    v['klassifikaator_kood'] = item.kood
                    if self.c.ylem_id:
                        v['ylem_id'] = self.c.ylem_id                    
            else:
                self._unique_kood(valikud, 'k', [])
                for v in valikud:
                    v['bitimask'] = v.get('bit') and sum([int(b) for b in v['bit']]) or None
                    v['klassifikaator_kood'] = item.kood
                    if self.c.ylem_id:
                        v['ylem_id'] = self.c.ylem_id
                        if item.kood == 'HTUNNUS':
                            v['testiklass_kood'] = self.c.testiklass

            if item.kood == 'KEELETASE' and self.c.ylem_id:
                pkey = 'kood'
            else:
                pkey = 'id'
            KlassifikaatorGridController(collection, model.Klrida, None, self, pkey=pkey, supercollection=item.read).save(valikud)

            # eemaldame primmi, mille IntegrityErrori vältimiseks oleme pannud
            model.Session.flush()
            for r in collection:
                if r.kood.endswith("'"): r.kood = r.kood[:-1]

            # uuendame hierarhia koodi
            for r in collection:
                r.update_hkood()

            if item.kood == 'NULLIPOHJ':
                self._save_nullipaine(item)

            # kustutame selle klassifikaatori väärtused mälupuhvrist,
            # kuna need on muutunud ja tuleks uuesti andmebaasist pärida
            model.Klrida.clean_cache(item.kood)

    def _save_nullipaine(self, item):
        "Salvestame õppeained, mille korral nulli põhjus on e-testis kasutusel"
        values = self.request.params.getall('nullipaine')
        q = (model.Session.query(model.Klrida)
             .filter(model.Klrida.klassifikaator_kood=='AINE'))

        # eemaldame
        q1 = (q.filter(model.Klrida.nullipohjus==True)
              .filter(~ model.Klrida.kood.in_(values)))
        for r in q1.all():
            r.nullipohjus = None

        # lisame
        q2 = (q.filter(model.Klrida.nullipohjus==None)
              .filter(model.Klrida.kood.in_(values)))
        for r in q2.all():
            r.nullipohjus = True

        model.Klrida.clean_cache('NULLIPAINE')
        
    def _unique_kood(self, valikud, prefix, koodid):
        errors = {}
        c = self.c
        for v in valikud:
            kood = v.get('kood')
            n = v.get('_arr_ind')
            if kood:
                if kood in koodid:
                    errors['%s-%s.kood' % (prefix, n)] = _("Pole unikaalne")
                else:
                    koodid.append(kood)

            if c.item.kood == 'ASTE':
                err = self._check_astendaja(kood)
                if err:
                    errors['%s-%s.kood' % (prefix, n)] = err

            if c.item.kood == 'SPTYYP':
                # kehtivuse linnuke määrab tegelikult avalikus vaates kehtivuse
                v['avalik'] = v['kehtib']
                v['kehtib'] = True
                del v['nimi']
                
        # lisame koodid, kus veel pole
        gen_cnt = 0
        for v in valikud:
            if not v.get('kood'):
                while True:
                    gen_cnt += 1
                    kood = str(gen_cnt)
                    if kood not in koodid:
                        koodid.append(kood)
                        v['kood'] = kood
                        break
                
        if errors:
            kood = self.request.matchdict.get('id')
            args = {}
            if c.ylem_id:
                args['ylem_id'] = c.ylem_id
            if c.ylem_id2:
                args['ylem_id2'] = c.ylem_id2
            raise ValidationError(self, errors)

    
    def _check_astendaja(self, kood):
        "Kontrollime, et astme/eriala kood oleks teisendatav astendajaks"
        ## vaikimisi kooliastmed
        if kood not in (const.ASTE_I, const.ASTE_II, const.ASTE_III, const.ASTE_G, const.ASTE_Y):
            try:
                astendaja = int(kood)
            except:
                return _("Peab olema täisarv") + " (5-20)"
            
    # def _edit_kirjeldus(self, id):
    #     self.c.item = model.Klrida.get(id)
    #     return self.render_to_response('admin/klrida.kirjeldus.mako')

    # def _update_kirjeldus(self, id):
    #     item = model.Klrida.get(id)
    #     self.form = Form(self.request, schema=forms.admin.KlridaKirjeldusForm)
    #     if not self.form.validate():
    #         return Response(self._INDEX_TEMPLATE, extra_info=self._index_d())
        
    #     item.from_form(self.form.data, self._PREFIX)
    #     model.Session.commit()
    #     self.success()
    #     self.c.ylem_id = item.ylem_id
    #     return self._after_update(item.klassifikaator_kood)

    def _download(self, id, format=None):
        kl = model.Klassifikaator.get(id)
        filedata = raw_export.export_klread(kl)
        filename = '%s.raw' % id
        mimetype = 'application/binary'
        return utils.download(filedata, filename, mimetype)

    def __before__(self):
        c = self.c
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


class KlassifikaatorGridController(BaseGridController):
    def can_delete(self, rcd):
        return not rcd.in_use

    def update_subitem(self, subitem, rcd, lang=None):
        """
        subitem - mudeli objekt
        rcd - vormilt postitatud andmed valideerituna
        """
        if subitem.kood != rcd['kood'] and len(rcd['kood']) < 10:
            # kui kahe kirje koodid vahetatakse, siis võib tulla IntegrityError,
            # kui yks neist on andmebaasi kirjutatud ja teine veel mitte
            # seepärast kirjutame esmalt andmebaasi primmiga koodi
            # ja hiljem kaotame primmi ära
            rcd['kood'] += "'"
        BaseGridController.update_subitem(self, subitem, rcd, lang)
        #self._save_alamad(subitem, rcd, lang)
        return subitem
    
    def create_subitem(self, rcd, lang=None):
        subitem = BaseGridController.create_subitem(self, rcd, lang)
        #self._save_alamad(subitem, rcd, lang)
        return subitem
    
