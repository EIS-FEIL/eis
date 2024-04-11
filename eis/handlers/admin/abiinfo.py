from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AbiinfoController(BaseResourceController):

    _permission = 'olulineinfo'
    _ITEM_FORM = forms.admin.OlulineinfoForm
    _INDEX_TEMPLATE = 'admin/abiinfo.mako'
    _EDIT_TEMPLATE = 'admin/abiinfo.mako'
    _LOG_TEMPLATE = 'admin/abiinfo.logi.mako'
    _index_after_create = True
    _log_params_post = True

    def _index_d(self):
        return self.response_dict
    
    def _create(self, **kw):
        kood = self.form.data['kood']
        item = model.Abiinfo.give_info(kood)
        if kood == 'EKSAMISTATISTIKA':
            key = 'sisu2'
        item.sisu = self.form.data[key]
        return item

    def create(self):
        err = False
        self.form = Form(self.request, schema=self._ITEM_FORM)
        if self.form.validate():
            try:
                item = self._create()
                if isinstance(item, (HTTPFound, Response)):
                    return item
            except ValidationError as e:
                self.form.errors = e.errors
                err = True

        if self.form.errors or err:
            # vead võivad olla tulnud vormi valideerimisest 
            # või olla käsitsi pandud _create() sees
            log.debug(self.form.errors)
            model.Session.rollback()
            return self._error_create()

        model.Session.commit()
        return self._after_update(None)

    def _index_log(self):
        kood = self.request.params.get('kood')
        q = (model_log.DBSession.query(model_log.Logi.aeg,
                                       model_log.Logi.isikukood,
                                       model_log.Logi.sisu)
             .filter(model_log.Logi.tyyp==const.LOG_USER)
             .filter(sa.or_(model_log.Logi.path=='/ekk/admin/olulineinfo',
                            model_log.Logi.path=='/ekk/admin/abiinfo'))
             .filter(sa.or_(model_log.Logi.kontroller==f'abiinfo/{kood}',
                            model_log.Logi.kontroller==f'olulineinfo/{kood}'))
             .filter(model_log.Logi.meetod=='POST')
             .order_by(sa.desc(model_log.Logi.aeg))
             .limit(100)
             )
        items = []
        names = {}
        for r in q.all():
            aeg, ik, sisu = r
            name = names.get(ik)
            if not name:
                k = model.Kasutaja.get_by_ik(ik)
                name = k and k.nimi or ''
                names[ik] = name
            items.append((aeg, ik, name, sisu))
        self.c.items = items
        return self.render_to_response(self._LOG_TEMPLATE)

    def _log_params_sisu(self, controller, param):
        "Võimalus muuta logi sisu"
        sisu = None
        method = self.request.method.upper()
        kood = self.request.params.get('kood')
        if kood and method == 'POST':
            controller = f'abiinfo/{kood}'
            param = None
            if kood == 'EKSAMISTATISTIKA':
                key = 'sisu2'
            sisu = self.request.params.get(key)
        return controller, param, sisu
