import json
from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class LogiController(BaseResourceController):
    _permission = 'logi'

    _MODEL = model_log.Logi
    _SEARCH_FORM = forms.admin.LogiForm
    _ITEM_FORM = None
    _INDEX_TEMPLATE = 'admin/logi.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = None
    _LIST_TEMPLATE = 'admin/logi_list.mako'
    _DEFAULT_SORT = '-logi.id' # vaikimisi sortimine

    def _query(self):
        return model_log.DBSession.query(model_log.Logi)

    def _search_default(self, q):
        self.c.alates = date.today()
        
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.idr:
            flt = forms.validators.IDRange.filter(c.idr, model_log.Logi.id)
            if flt is not None:
                q = q.filter(flt)            
        if c.id:
            q = q.filter(model_log.Logi.id == c.id)
        if c.uuid:
            q = q.filter(model_log.Logi.uuid == c.uuid)
        if c.request_id:
            q = q.filter(model_log.Logi.request_id == c.request_id)
        if c.isikukood:
            ik = validators.IsikukoodP(c.isikukood).isikukood
            if ik and ('%' in ik):
                q = q.filter(model_log.Logi.isikukood.like(ik))
            else:
                q = q.filter(model_log.Logi.isikukood==ik)

        if c.nimi:
            q1 = (model.SessionR.query(model.Kasutaja.isikukood)
                  .filter(model.Kasutaja.nimi.ilike(c.nimi)))
            lik = [ik for ik, in q1.limit(30).all()]
            if lik:
                q = q.filter(model_log.Logi.isikukood.in_(lik))

        if not self._has_search_params():
            # kui parameetrid ei tulnud praegu vormilt, siis piirame alates kuupäeva
            c.alates = datetime.now()
        if c.alates:
            if c.alates_kell:
                try:
                    kell = forms.validators.EstTimeConverter().to_python(c.alates_kell)
                except forms.formencode.api.Invalid as ex:
                    raise ValidationError(self, {'alates_kell':_("tt.mm.ss")})
                else:
                    c.alates = c.alates_kell = datetime.combine(c.alates, time(*kell))
            q = q.filter(model_log.Logi.aeg >= c.alates)
        if c.kuni:
            kuni = c.kuni + timedelta(1)
            if c.kuni_kell:
                try:
                    kell = forms.validators.EstTimeConverter().to_python(c.kuni_kell)
                except forms.formencode.api.Invalid as ex:
                    raise ValidationError(self, {'kuni_kell':_("tt.mm.ss")})
                else:
                    kuni = c.kuni_kell = datetime.combine(c.kuni, time(*kell))
            q = q.filter(model_log.Logi.aeg <= kuni)

        if c.tyyp:
            q = q.filter(model_log.Logi.tyyp == c.tyyp)
        if c.remote_addr:
            q = q.filter(model_log.Logi.remote_addr==c.remote_addr)            
        if c.server_addr:
            q = q.filter(model_log.Logi.server_addr==c.server_addr)
        if c.param:
            q = q.filter(model_log.Logi.param.ilike(c.param))
        if c.url:
            q = q.filter(model_log.Logi.url.ilike(c.url))
        if c.path:
            if '%' in c.path:
                q = q.filter(model_log.Logi.path.ilike(c.path))            
            else:
                q = q.filter(model_log.Logi.path==c.path)
        if c.method:
            q = q.filter(model_log.Logi.meetod==c.method)
        if c.sisu:
            q = q.filter(model_log.Logi.sisu.ilike(c.sisu))
        if c.kestus:
            q = q.filter(model_log.Logi.kestus!=None)
        if c.ylesanne_id:
            path1 = f"%/{c.ylesanne_id}/edittask"
            path2 = f"%/{c.ylesanne_id}/updatetask"            
            q = q.filter(sa.or_(model_log.Logi.path.like(path1),
                                model_log.Logi.path.like(path2)))
        if c.xls:
            return self._index_xls(q)        
        return q

    def _prepare_items(self, q):
        return BaseResourceController._prepare_items(self, q.limit(10000))

    def _prepare_header(self):
        li = [_("ID"),
              _("Aeg"),
              _("Kestus"),              
              _("Kasutaja"),
              _("Logi tüüp"),
              _("Lehekülg"),
              _("Tegevus"),
              _("Parameetrid"),
              _("Logi"),
              _("Server"),
              _("Klient"),
              _("Brauser"),
              ]
        return li

    def _prepare_item(self, rcd, n=None):
        h = self.h
        userid = rcd.isikukood or ''
        li = [rcd.id,
              h.str_from_datetime(rcd.aeg, microseconds=True),
              h.fstr(rcd.kestus),
              userid,
              rcd.tyyp_nimi,
              rcd.kontroller,
              rcd.tegevus,
              rcd.param,
              ' '.join([rcd.sisu or '', rcd.meetod, rcd.url]),
              rcd.server_addr,
              rcd.remote_addr,
              rcd.user_agent,
              ]
        return li

    def _download(self, id, format=None):
        """Näita faili"""
        item = model_log.DBSession.query(model_log.Logi).filter_by(id=id).first()
        if item:
            dt = item.aeg.strftime('%y%m%d.%H%M%S')
            filedata = item.sisu.encode('utf-8')
            if format == 'xml':
                mimetype = 'application/xml'
                filename = '%s.%s.xml' % (dt, item.param.replace(' ','.'))
            elif format == 'json':
                mimetype = 'text/plain'
                filename = 'logi%d.%s' % (item.id, format)
                try:
                    # paremini loetavaks
                    filedata = json.dumps(json.loads(filedata), indent=4)
                except json.decoder.JSONDecodeError:
                    pass
            else:
                mimetype = 'text/plain'
                filename = 'logi%d.%s' % (item.id, format)
            return utils.download(filedata, filename, mimetype, inline=True)

