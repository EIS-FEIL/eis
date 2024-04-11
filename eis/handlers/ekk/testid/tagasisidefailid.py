from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TagasisidefailidController(BaseResourceController):
    """Tagasisidevormidel kasutatud failide laadimine 
    """
    _permission = 'ekk-testid'
    _MODEL = model.Tagasisidefail
    _INDEX_TEMPLATE = 'ekk/testid/tagasiside.failid.mako'
    _actions = 'index,create,delete'

    def _index_d(self):
        c = self.c
        q = (model.Session.query(model.Tagasisidefail)
             .filter_by(test_id=c.test.id)
             .order_by(model.Tagasisidefail.filename)
             )
        c.items = list(q.all())
        return self.response_dict
        
    def _create(self, **kw):
        c = self.c
        value = self.form.data.get('upload')
        if value != b'':
            localfn = _fn_local(value.filename)
            try:
                basename, ext = localfn.rsplit('.',1)
            except:
                basename = localfn
                ext = ''

            # kontrollime, kas failinimi on juba kasutusel
            for n in range(100):
                fn = n and f'{basename}-{n}' or basename
                if ext:
                    fn += '.' + ext
                q = (model.Session.query(sa.func.count(model.Tagasisidefail.id))
                     .filter_by(test_id=c.test_id)
                     .filter_by(filename=fn))
                if q.scalar() == 0:
                    # sellise nimega faili veel pole
                    break

            # salvestame faili
            filedata = value.value
            item = model.Tagasisidefail(test_id=c.test.id)
            item.filename = fn
            item.filedata = filedata
            item.filesize = filedata is not None and len(filedata) or 0
            model.Session.commit()
            
            res = {"uploaded": 1,
                   "fileName": fn,
                   "url": f'testimages/{fn}'
                   }
        else:
            res = {"uploaded": 0,
                   "error": {
                       "message": "Fail puudub"
                       }
                   }
        return Response(json_body=res)

    def _delete(self, item):
        if item.test_id == self.c.test.id:
            item.delete()
            model.Session.commit()

    def __before__(self):
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        
    def _perm_params(self):
        return {'obj':self.c.test}

def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath
