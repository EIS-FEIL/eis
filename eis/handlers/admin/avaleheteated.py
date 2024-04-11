from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AvaleheteatedController(BaseResourceController):

    _permission = 'olulineinfo'
    _ITEM_FORM = forms.admin.AvaleheteadeForm
    _INDEX_TEMPLATE = 'admin/avaleheteated.mako'
    _LIST_TEMPLATE = 'admin/avaleheteated_list.mako'
    _LOG_TEMPLATE = 'admin/avaleheteated.logi.mako'
    _index_after_create = True
    _log_params_post = True
    _MODEL = model.Avaleheinfo
    _DEFAULT_SORT = '-avaleheinfo.id'
    _actions = 'landing,index,new,create,update,delete,edit'
    
    def landing(self):
        template = 'admin/olulineinfo.mako'
        return self.render_to_response(template)

    @property
    def _EDIT_TEMPLATE(self):
        if self.c.item and self.c.item.tyyp == model.Avaleheinfo.TYYP_EMERGENCY:
            return 'admin/erakorralineteade.mako'
        else:
            return 'admin/avaleheteade.mako'
    
    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q):
        c = self.c
        q = q.filter(model.Avaleheinfo.tyyp != model.Avaleheinfo.TYYP_EMERGENCY)
        today = date.today()
        if not c.kehtetu:
            q = (q.filter(model.Avaleheinfo.alates <= today)
                .filter(model.Avaleheinfo.kuni >= today))
        if c.sisu:
            sisu = '%' + c.sisu + '%'
            q = q.filter(sa.or_(model.Avaleheinfo.pealkiri.ilike(sisu),
                                model.Avaleheinfo.sisu.ilike(sisu),
                                model.Avaleheinfo.lisasisu.ilike(sisu)))

        # erakorralise info kirje
        c.emergency_item = model.Avaleheinfo.get(model.Avaleheinfo.ID_EMERGENCY)
        if c.emergency_item and c.emergency_item.kuni < model.date.today():
            # kui pole aktiivne, siis ei kuva
            c.emergency_item = None
        return q

    def _edit_d(self):
        id = self.request.matchdict.get('id')
        self.c.item = self._MODEL.get(id)
        if not self.c.item:
            if int(id) == model.Avaleheinfo.ID_EMERGENCY and self.c.user.on_admin:
                # erakorralisele teatele reserveeritud id 0
                eile = date.today() - timedelta(days=1)
                self.c.item = model.Avaleheinfo(id=model.Avaleheinfo.ID_EMERGENCY,
                                                tyyp=model.Avaleheinfo.TYYP_EMERGENCY,
                                                kellele=model.Avaleheinfo.KELLELE_X,
                                                alates=eile,
                                                kuni=eile,
                                                pealkiri='',
                                                sisu='')
                model.Session.commit()
            else:
                raise NotFound('Kirjet %s ei leitud' % id)        
        rc = self._edit(self.c.item)
        if isinstance(rc, (HTTPFound, Response)):
            return rc        
        return self.response_dict

    
    def update(self):
        id = self.request.matchdict.get('id')
        item = self._MODEL.get(id)
        if self.request.params.get('op') == 'copy':
            # salvestamine koopiana
            item = item.copy()
            model.Session.flush()
            id = item.id
            
        err = False
        self.form = Form(self.request, schema=self._ITEM_FORM)
        if self.form.validate():
            try:
                if item:
                    rc = self._update(item)
                    if isinstance(rc, (HTTPFound, Response)):
                        return rc
            except ValidationError as e:
                self.form.errors = e.errors
                err = True

        if self.form.errors or err:
            model.Session.rollback()
            return self._error_update()

        model.Session.commit()
        self._after_commit(item)
        return self._after_update(id)
    
    def _update(self, item, lang=None):
        # omistame vormilt saadud andmed
        if item.tyyp == model.Avaleheinfo.TYYP_EMERGENCY:
            # erakorraline teade
            item.sisu = self.form.data['f_sisu']
            item.kellele = model.Avaleheinfo.KELLELE_X
            if self.form.data.get('kehtiv'):
                item.kuni = const.MAX_DATE
            else:
                # kehtetu, paneme vana kuupäeva
                item.kuni = item.alates
            return

        # tavaline avalehe teade
        item.from_form(self.form.data, self._PREFIX, lang=lang)

        li_kellele = self.form.data['kellele']
        if model.Avaleheinfo.KELLELE_X in li_kellele:
            # kui on kõigile, siis pole teisi vaja loetleda
            li_kellele = [model.Avaleheinfo.KELLELE_X]
        item.kellele = ','.join(li_kellele)
        
        if not item.kuni:
            item.kuni = const.MAX_DATE
            
    def _new(self, item):
        item.tyyp = model.Avaleheinfo.TYYP_INFO
        item.kellele = model.Avaleheinfo.KELLELE_X
        item.alates = date.today()
        
    def _index_log(self):
        if self.c.is_devel:
            path = '/admin/avaleheteated'
        else:
            path = '/ekk/admin/avaleheteated'
        page = 'avaleheteated'
        q = (model_log.DBSession.query(model_log.Logi.aeg,
                                       model_log.Logi.isikukood,
                                       model_log.Logi.sisu)
             .filter(model_log.Logi.tyyp==const.LOG_USER)
             .filter(model_log.Logi.path==path)
             .filter(model_log.Logi.kontroller==page)
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
            params = self.parse_log_params_list(sisu, ['kellele']) or {}
            obj = NewItem()
            obj.alates = params.get('f_alates')
            obj.kuni = params.get('f_kuni')
            obj.pealkiri = params.get('f_pealkiri')
            obj.sisu = params.get('f_sisu')
            obj.lisasisu = params.get('f_lisasisu')
            obj.kellele = ','.join(params.get('kellele') or [])
            items.append((aeg, ik, name, params))
        self.c.items = items
        return self.render_to_response(self._LOG_TEMPLATE)
