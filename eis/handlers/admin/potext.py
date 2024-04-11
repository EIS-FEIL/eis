# -*- coding: utf-8 -*- 

import formencode
from eis.lib.baseresource import *
from eis.forms.validators import *
from eis.model.potext import Potext
_ = i18n._
log = logging.getLogger(__name__)

class ItemForm(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fiels = False
    id = Int
    msgstr = String(max=1024)
    
class SaveForm(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fiels = False
    p = formencode.ForEach(ItemForm)

log = logging.getLogger(__name__)

class PotextController(BaseResourceController):
    """.po failide tõlkimise kasutajaliides
    """
    _permission = 'ui-tolkimine'
    _INDEX_TEMPLATE = 'admin/potext/potext.mako'
    _LIST_TEMPLATE = 'admin/potext/potext_list.mako'
    _ITEM_FORM = SaveForm
    _DEFAULT_SORT = 'potext.id' # vaikimisi sortimine
    
    def _query(self):
        self.Potext_en = Potext_en = sa.orm.aliased(Potext)
        q = (model.SessionR.query(Potext.id, Potext.msgid, Potext_en.msgstr, Potext.msgstr)
             .outerjoin((Potext_en,
                         sa.and_(Potext_en.msgid==Potext.msgid,
                                 Potext_en.lang=='en'))))
        return q

    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q):
        #self.c.hide_header_footer = True
        q = q.filter(Potext.lang==self.c.lang)
        if self.c.msgstr:
            value = self.c.msgstr
            if not self.c.tapne:
                value = '%' + value + '%'
            q = q.filter(sa.or_(Potext.msgstr.ilike(value),
                                Potext.msgid.ilike(value)))
        if self.c.tolketa:
            q = q.filter(Potext.msgstr=='')
        self.c.can_update = self._can_update()
        return q

    def _paginate(self, q):
        if self._no_paginate:
            return q.all()
        page = self.c.page or self.request.params.get('page') or 1
        return SqlalchemyOrmPage(q, 
                                 page=page,
                                 items_per_page=self._items_per_page,
                                 url=self.h.url_current_params)

    def create(self):
        if not self._can_update():
            self.error(_("Puudub õigus"))
        else:
            self.form = Form(self.request, schema=self._ITEM_FORM)
            if self.form.validate():
                errors = {}
                for ind, r in enumerate(self.form.data.get('p')):
                    potext_id = r['id']
                    msgstr = r['msgstr']
                    if msgstr:
                        item = Potext.get(potext_id)
                        params1 = set(re.findall('({[^}]+})', item.msgid))
                        params2 = set(re.findall('({[^}]+})', msgstr))
                        missing = params1 - params2
                        extra = params2 - params1
                        if missing:
                            err = _("Tõlketekstis puuduvad parameetrid {s}").format(s=', '.join(missing))
                            errors['p-%d.msgstr' % ind] = err
                        elif extra:
                            err = _("Tõlketekstis on liigsed parameetrid {s}").format(s=', '.join(extra))
                            errors['p-%d.msgstr' % ind] = err
                        item.msgstr = msgstr
                if errors:
                    self.form.errors = errors
            if self.form.errors:
                log.debug(self.form.errors)
                model.Session.rollback()
                self.error(_("Palun kõrvaldada vead"))
                return self._error_create()
            self.success()
            model.Session.commit()
        return self._redirect('index', lang=self.c.lang)

    def _error_create(self):
        self.c.can_update = True
        err_form = self.form
        
        q = self._query()
        default_params = self._get_default_params()
        q = self._index_handle_params(q, False, default_params)
        q = self._order(q)
        self.c.items = self._paginate(q)

        html = err_form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def __before__(self):
        self.c.lang = self.request.matchdict.get('lang')

    def _can_update(self):
        keeled = self.c.user.get_kasutaja().get_keeled('ui-tolkimine', const.BT_UPDATE)
        return None in keeled or self.c.lang in keeled or self.c.user.on_admin
        
    def _perm_params(self):
        if self.c.is_edit:
            return {'lang': self.c.lang}

