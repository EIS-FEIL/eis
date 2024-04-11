from cgi import FieldStorage
import formencode
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class CAEeeltestController(BaseResourceController):
    "CAE eeltesti sooritanute laadimine failist"

    _INDEX_TEMPLATE = '/admin/caeeeltest.mako'
    _LIST_TEMPLATE = '/admin/caeeeltest_list.mako'
    _index_after_create = True
    _DEFAULT_SORT = '-caetestitud.id'
    _permission = 'caeeeltest'
    _ignore_default_params = ['otsi']
    
    def _query(self):
        q = (model.SessionR.query(model.Caetestitud.isikukood,
                                 model.Opilane.eesnimi,
                                 model.Opilane.perenimi,
                                 model.Koht.nimi,
                                 model.Opilane.klass,
                                 model.Opilane.paralleel)
             .outerjoin((model.Opilane, model.Opilane.isikukood==model.Caetestitud.isikukood))
             .outerjoin((model.Koht, model.Opilane.koht_id==model.Koht.id))
             )
        self.c.prepare_header = self._prepare_header
        self.c.prepare_item = self._prepare_item
        return q

    def _search_default(self, q):
        pass
    
    def _search(self, q):
        c = self.c
        if c.isikukood:
            usp = validators.IsikukoodP(c.isikukood)
            q = q.filter(model.Caetestitud.isikukood==usp.isikukood)
        if c.eesnimi:
            q = q.filter(model.Opilane.eesnimi==c.eesnimi)
        if c.perenimi:
            q = q.filter(model.Opilane.perenimi==c.perenimi)
        return q

    def _prepare_header(self):
        "Loetelu päis"
        li = [('caeeltest.isikukood', _("Isikukood")),
              (None, _("Eesnimi")),
              (None, _("Perekonnanimi")),
              (None, _("Kool")),
              (None, _("Klass")),
              ]
        return li

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        ik, o_eesnimi, o_perenimi, koht_nimi, klass, paralleel = rcd
        item = [ik,
                o_eesnimi,
                o_perenimi,
                koht_nimi,
                '%s%s' % (klass or '', paralleel or '')]
        return item

    def _create(self):
        errors = {}
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            errors['fail'] = _("Faili ei leitud")
        else:
            # value on FieldStorage objekt
            filename = value.filename
            value = value.value

            cnt_old = cnt_new = 0
            for line in value.splitlines():
                line = line.strip()
                if line:
                    line = utils.guess_decode(line)
                    li = [s.strip() for s in line.split(';')]
                    ik = li[0]
                    if ik:
                        usp = validators.IsikukoodP(ik)
                        if not usp.isikukood:
                            errors['fail'] = _("Esitati vigane isikukood {s}").format(s=ik)
                            break
                        item = model.Caetestitud.get_by_ik(usp.isikukood)
                        if item:
                            cnt_old += 1
                        else:
                            cnt_new += 1
                            item = model.Caetestitud(isikukood=usp.isikukood)
        if errors:
            raise ValidationError(self, errors)
        else:
            if cnt_new:
                self.notice(_("CAE eeltesti sooritamise märge lisatud {n} isikule").format(n=cnt_new))
            if cnt_old:
                self.notice(_("CAE eeltesti sooritamise märge oli juba varem olemas {n} isikul").format(n=cnt_old))
            model.Session.commit()
        return self._redirect('index')

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def _split_line(self, line, cnt, cnt_min=None):
        err = None
        line = line.strip()
        if line:
            li = [s.strip() for s in line.split(';')]
            if len([s for s in li if s]) == 0:
                return
            if cnt_min and len(li) >= cnt_min: 
                while len(li) < cnt:
                    li.append('')
            if len(li) != cnt:
                err = _("Vigane rida {s}. Real peab olema {n} välja.").format(s=line.strip(), n=cnt)
                li = None
            return li, err
        return None, None
