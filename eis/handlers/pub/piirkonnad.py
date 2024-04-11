from simplejson import dumps
from eis.lib.base import *
_ = i18n._

log = logging.getLogger(__name__)

class PiirkonnadController(BaseController):
    """Piirkonna valiku dialoog jsTree jaoks
    """
    _authorize = False
    
    def index(self):
        format = self.request.matchdict.get('format')
        return self._index_json()

    def _index_json(self):
        data = []
        parent = None
        id = self.request.params.get('id') or None
        op = self.request.params.get('op')

        if id == '-':
            # piirkondade halduse aknas:
            # tekitame kirje, mille alla lohistades saab 
            # olemasolevalt piirkonnalt ülempiirkonna ära võtta
            rcd = {"id":'0',
                   "text":_("Ülempiirkonnata"),
                   "children": True
                   }
            data.append(rcd)
            id = None
        elif id:
            parent = model.Piirkond.get(id)

        for item in model.Piirkond.query.filter_by(ylem_id=id).order_by(model.Piirkond.nimi):
            if op == 'kohad':
                closed = bool(len(item.alamad) or len(item.kohad))
            else:
                closed = bool(len(item.alamad))
            rcd = {"id": item.id,
                   "text": item.nimi,
                   "state": { "opened": not closed },
                   }
            if closed:
                rcd['children'] = True
            data.append(rcd)

        if op == 'kohad' and id != '0':
            if parent:
                kohad = parent.kohad
            else:
                kohad = model.Koht.query\
                    .filter_by(piirkond_id=None)\
                    .order_by(model.Koht.nimi).all()
            for item in kohad:
                rcd = {"id":"K%d" % item.id, 
                       "text": item.nimi,
                       "a_attr": {"href": self.url('admin_koht', id=item.id),
                                  "class": "koht",
                                  },
                       "icon": "glyphicon glyphicon-home",
                       }
                data.append(rcd)
                
        return Response(json_body=data)
