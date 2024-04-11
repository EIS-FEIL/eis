from cgi import FieldStorage
import formencode
from eis.forms import validators
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class VeriffidController(BaseResourceController):
    _INDEX_TEMPLATE = '/admin/veriffid.mako'
    _index_after_create = True
    _permission = 'admin'
    _actions = 'index,create'

    def index(self):
        return self.render_to_response(self._INDEX_TEMPLATE)
    
    def create(self):
        c = self.c
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            raise ValidationError(self, {'fail': 'Palun sisestada fail'})

        # value on FieldStorage objekt
        value = value.value
        items = []
        header = None
        for ind, line in enumerate(value.splitlines()):
            line = utils.guess_decode(line).strip()
            if line:
                li = _split_row(line)
                if len(li):
                    if not header:
                        header = ['isikukood','ip'] + li
                    else:
                        row = self._handle_row(li)
                        items.append(row)
        fn = 'veriffid.xls'
        return utils.download_xls(header, items, fn)    

    def _handle_row(self, li):
        uuid = li[0]
        ip = li[3]
        
        uuid = uuid.split()[0].strip()
        dt = date.today() - timedelta(days=30)
        q = (model.Session.query(model.Kasutaja.isikukood, model.Verifflog.sooritus_id, model.Sooritus.remote_addr)
             .join((model.Verifflog, model.Verifflog.kasutaja_id==model.Kasutaja.id))
             .filter(model.Verifflog.created > dt)
             .filter(model.Verifflog.sess_data.like('%' + uuid + '%'))
             .outerjoin((model.Sooritus, model.Sooritus.id==model.Verifflog.sooritus_id))
             )
        cnt = q.count()
        if cnt != 1:
            raise Exception(f'uuid "{uuid}" annab {cnt} vastet')
        
        ik, sooritus_id, remote_addr = q.first()
        if remote_addr and remote_addr not in ip:
            log.info(f'{ik} {remote_addr} / Veriff {ip}')

        return [ik, remote_addr] + li

def _split_row(line):
    li = []
    word = ''
    inword = False
    for ch in line:
        if ch == ',' and not inword:
            li.append(word)
            word = ''
        elif ch == '"' and not inword:
            inword = True
        elif ch == '"' and inword:
            inword = False
        else:
            word += ch
    if word:
        li.append(word)
    return li
