# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class SisestuskogumidController(BaseResourceController):

    _permission = 'testimiskorrad'

    _MODEL = model.Sisestuskogum
    _EDIT_TEMPLATE = 'ekk/testid/kogumid.mako'
    _ITEM_FORM = forms.ekk.testid.SisestuskogumForm
    
    def _new_d(self):
        self.c.item = model.Sisestuskogum(testiosa=self.c.testiosa)
        model.Session.autoflush = False
        self.c.item.post_create()
        self._edit(self.c.item)
        return self.response_dict

    def _create(self, **kw):
        kw['testiosa_id'] = int(self.request.params.get('testiosa_id')) 
        item = BaseResourceController._create(self, **kw)
        return item
    
    def _edit(self, item):
        self.c.testiosa_id = item.testiosa_id
        self.c.sisestuskogum = item

    def _update(self, item, lang=None):
        self._bind_parent(item)
        item.from_form(self.form.data, self._PREFIX, lang=lang)

        hk_id_list = list(map(int, self.request.params.getall('hk_id')))
        self._update_hindamiskogumid(item, hk_id_list)

        for rcd_ty in self.form.data.get('ty'):
            ty = model.Testiylesanne.get(rcd_ty['id'])
            if ty.hindamiskogum.sisestuskogum == item:
                if item.on_skannimine:
                    # toimub skannimine, aga märgime õige sisestusviisi,
                    # sest selle järgi toimub tulemuste arvutamine
                    if ty.hindamiskogum.on_digiteerimine:
                        # vastused olemas, arvutihinnatav tulemuste arvutamine
                        ty.sisestusviis = const.SISESTUSVIIS_VASTUS
                    else:
                        # vastuseid pole, arvutatakse käsitsi antud pallide järgi
                        ty.sisestusviis = const.SISESTUSVIIS_PALLID
                else:
                    # toimub sisestamine
                    ty.sisestusviis = rcd_ty['sisestusviis']
                # kas kursor hyppab peale valikvälja sisestamist ise järgmisele väljale 
                ty.hyppamisviis = rcd_ty['hyppamisviis']

    def _update_hindamiskogumid(self, item, id_list):
        testiosa = item.testiosa or model.Testiosa.get(item.testiosa_id)
        on_hindamisprotokoll = False
        on_vastused = False
        sk_komplektivalik = -1
        err_kvalik = None
        eemaldatud = []
        for rcd in testiosa.hindamiskogumid:
            if rcd.id in id_list:
                # hindamiskogum kuulub sellesse sisestuskogumisse
                # kontrollime, et sisestuskogumis oleks yhe komplektivaliku hindamiskogumid
                if sk_komplektivalik == -1:
                    # esimene hindamiskogum, jätame meelde selle komplektivaliku
                    sk_komplektivalik = rcd.get_komplektivalik()
                elif rcd.get_komplektivalik() != sk_komplektivalik:
                    # komplektivalik ei lange kokku varem nähtud 
                    # samasse sisestuskogumisse kuuluvate hindamiskogumite komplektivalikuga
                    err_kvalik = True
                    if rcd.sisestuskogum == item:
                        rcd.sisestuskogum = None
                    continue

                if rcd.sisestuskogum != item:
                    # kuulub teise sisestuskogumisse
                    rcd.sisestuskogum = item
                if rcd.on_hindamisprotokoll:
                    on_hindamisprotokoll = True
                else:
                    on_vastused = True

            elif rcd.sisestuskogum == item:
                # hindamiskogum ei kuulu enam sellesse sisestuskogumisse, aga varem kuulus
                eemaldatud.append(rcd)
                
        for rcd in eemaldatud:
            # aga ühe komplektivaliku kõik ülesanded peavad kuuluma samasse sisestuskogumisse
            kv = rcd.get_komplektivalik()
            if kv and len(kv.komplektid) and rcd.staatus and kv == sk_komplektivalik:
                msg = _("Hindamiskogumit {s} ei saa sisestuskogumist eemaldada, sest selle ülesanded kuuluvad samasse komplektivalikusse antud sisestuskogumi ülesannetega").format(s=rcd.tahis)
                raise ValidationError(self, {}, msg)
            rcd.sisestuskogum = None

        if err_kvalik:
            msg = _("Sisestuskogumi kõik hindamiskogumid peavad olema sama komplektivaliku piires")
            raise ValidationError(self, {}, msg)
        if item.on_skannimine:
            on_hindamisprotokoll = on_vastused = False
        item.on_hindamisprotokoll = on_hindamisprotokoll
        item.on_vastused = on_vastused

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_kogumid', test_id=self.c.test.id))
        
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)

        self.c.testiosa_id = self.request.params.get('testiosa_id')
        if self.c.testiosa_id:
            self.c.testiosa = model.Testiosa.get(self.c.testiosa_id)
            assert self.c.testiosa.test_id == self.c.test.id, _("Vale test")

        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

