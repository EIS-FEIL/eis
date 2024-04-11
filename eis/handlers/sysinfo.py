import os
from eis.lib.base import *
_ = i18n._
log = logging.getLogger(__name__)

class SysinfoController(BaseController):
    """Süsteemi info sysadminile
    """
    _authorize = True
    _permission = 'sysinfo'
    
    @action(renderer='avaleht.mako')
    def index(self):
        if self.request.params.get('hpdf'):
            from eis.lib.html_export import export_test_pdf
            k = model.Komplekt.get(104)
            filedata = export_test_pdf(k, 'et', self)
            return utils.download(filedata, 'test.pdf')

        if self.request.params.get('sleep'):
            import time
            sec = int(self.request.params.get('sleep'))
            time.sleep(sec)
        
        self.request.session['is_debug'] = self.c.is_debug = self.request.params.get('is_debug') and True or False

        self.c.version = eis.__version__
        self.c.hostname = os.getenv('HOSTNAME')
        self.c.test_data = dict()
        for key in self.request.environ:
            value = self.request.environ[key]
            self.c.test_data[key] = value

        if self.request.params.get('crash'):
            crash()
        if self.request.params.get('mail'):
            buf = 'Test message %s' % (self.request.params.get('mail'))
            self._error_mail(buf)

        q = (model.Arvutusprotsess.query
             .filter(model.Arvutusprotsess.lopp==None)
             .order_by(model.Arvutusprotsess.id))
        self.c.protsessid = list(q.all())
            
        if self.request.params.get('pdf'):
            from eis.lib.pdf.testpdf import TestpdfDoc
            doc = TestpdfDoc()
            data = doc.generate()
            return utils.download(data, 'test.pdf', const.CONTENT_TYPE_PDF)

        if self.request.params.get('hds'):
            return self.render_to_response('/test2.mako')

        self.c.list_dbconn = self._list_dbconn()
    
        return self.response_dict

    def _list_dbconn(self):
        data = {}
        values = None
            
        sql = "select datname, state, count(*) from pg_stat_activity " +\
              " where usename like 'eisik%' and datname like 'eis%' " +\
              " group by datname, state order by datname, state" 
        #log.debug(sql)
        keys1 = []
        for datname, state, cnt in model.Session.execute(model.sa.text(sql)):
            key = datname
            value = '%s %d' % (state, cnt)
            if key not in keys1:
                keys1.append(key)
                data[key] = values = []
            values.append(value)

        keys2 = []
        for datname, state, cnt in model_log.DBSession.execute(model.sa.text(sql)):
            key = datname
            value = '%s %d' % (state, cnt)
            if key in keys1:
                # sama baasiserver
                continue
            if key not in keys2:
                keys2.append(key)
                data[key] = values = []
            values.append(value)

        return [(key, data[key]) for key in keys1 + keys2]
