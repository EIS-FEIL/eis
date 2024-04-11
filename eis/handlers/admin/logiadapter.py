from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class LogiadapterController(BaseResourceController):
    _permission = 'admin'

    _MODEL = model_log.Logi_adapter
    _SEARCH_FORM = forms.admin.LogiadapterForm
    _ITEM_FORM = None
    _INDEX_TEMPLATE = 'admin/logiadapter.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = None
    _LIST_TEMPLATE = 'admin/logiadapter_list.mako'
    _DEFAULT_SORT = '-logi_adapter.id' # vaikimisi sortimine

    def _query(self):
        return model_log.DBSession.query(model_log.Logi_adapter)

    def _search_default(self, q):
        self.c.alates = date.today()
        
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.id:
            q = q.filter(model_log.Logi_adapter.id == c.id)
        if not self._has_search_params():
            # kui parameetrid ei tulnud praegu vormilt, siis piirame alates kuupäeva
            c.alates = datetime.now()
        if c.alates:
            if c.alates_kell:
                try:
                    kell = forms.validators.EstTimeConverter().to_python(c.alates_kell)
                except forms.formencode.api.Invalid as ex:
                    raise ValidationError(self, {'alates_kell':_("tt.mm")})
                else:
                    c.alates = c.alates_kell = datetime.combine(c.alates, time(*kell))
            q = q.filter(model_log.Logi_adapter.aeg >= c.alates)
        if c.kuni:
            kuni = c.kuni + timedelta(1)
            if c.kuni_kell:
                try:
                    kell = forms.validators.EstTimeConverter().to_python(c.kuni_kell)
                except forms.formencode.api.Invalid as ex:
                    raise ValidationError(self, {'kuni_kell':_("tt.mm")})
                else:
                    kuni = c.kuni_kell = datetime.combine(c.kuni, time(*kell))
            q = q.filter(model_log.Logi_adapter.aeg < kuni + timedelta(minutes=1))
        if c.isikukood:
            if c.isikukood.startswith('EE'):
                userid = c.isikukood
            else:
                userid = 'EE%s' % c.isikukood
            if '%' in userid:
                q = q.filter(model_log.Logi_adapter.userid.like(userid))
            else:
                q = q.filter(model_log.Logi_adapter.userid == userid)
        if c.client:
            if '%' in c.client:
                q = q.filter(model_log.Logi_adapter.client.like(c.client))
            else:
                q = q.filter(model_log.Logi_adapter.client == c.client)
        if c.service:
            if '%' in c.client:            
                q = q.filter(model_log.Logi_adapter.service.like(c.service))
            else:
                q = q.filter(model_log.Logi_adapter.service == c.service)
        if c.input:
            q = q.filter(model_log.Logi_adapter.input_xml.like('%' + c.input + '%'))
        if c.output:
            q = q.filter(model_log.Logi_adapter.output_xml.like('%' + c.output + '%'))            
        if c.xls:
            return self._index_xls(q)        
        return q

    def _prepare_items(self, q):
        return BaseResourceController._prepare_items(self, q.limit(10000))

    def _prepare_header(self):
        li = [_("ID"),
              _("Aeg"),
              _("Klient"),
              _("Kasutaja"),
              _("Teenus"),
              _("Sisend"),
              _("Väljund"),
              ]
        return li

    def _prepare_item(self, rcd, n=None):
        h = self.h
        li = [rcd.id,
              h.str_from_datetime(rcd.aeg, microseconds=True),
              rcd.client,
              rcd.userid,
              rcd.service,
              '',
              '',
              ]
        return li

    def _download(self, id, format=None):
        """Näita faili"""
        try:
            fn = f'{id}.{format}'
            id, direction, format = fn.split('.')
            assert direction in ('in', 'out')
        except:
            pass
        else:
            item = model_log.DBSession.query(model_log.Logi_adapter).filter_by(id=id).first()
            if item:
                dt = item.aeg.strftime('%y%m%d.%H%M%S')
                if format == 'xml':
                    mimetype = 'application/xml'
                    filename = '%s.%s.%s.xml' % (dt, item.service, direction)
                elif format == 'json' and direction != 'in':
                    mimetype = 'application/json'
                    filename = '%s.%s.%s.json' % (dt, item.service, direction)
                else:
                    mimetype = 'text/plain'
                    filename = 'logi%d.%s.%s' % (item.id, direction, format)
                if direction == 'in':
                    filedata = item.input_xml
                    if format == 'json':
                        filedata = item.url
                else:
                    filedata = item.output_xml
                if filedata:
                    filedata = filedata.encode('utf-8')
                    return utils.download(filedata, filename, mimetype, inline=True)

        return Response('Faili ei leitud')
