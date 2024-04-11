# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class KasutajaametidController(BaseResourceController):
    _permission = 'kasutajad'
    _INDEX_TEMPLATE = '/admin/kasutaja.kohad.mako' # otsinguvormi mall

    def index(self):
        return self.render_to_response('/admin/kasutaja.ametikohad.mako')

    def new(self):
        "Pedagoogiks määramine"
        self.c.roll = self.c.new_item()
        return self.render_to_response('/admin/kasutaja.koht.mako')

    def _create(self):
        "Pedagoogiks määramine"
        self.c.roll = self.c.new_item()
        self.c.nosub = True

        self.form = Form(self.request, schema=forms.admin.KasutajakohtForm)
        if not self.form.validate():        
            return Response(self.form.render('admin/kasutaja.koht.mako', 
                                             extra_info=self.response_dict))
        
        koht_id = self.form.data.get('koht_id')
        today = date.today()
        YEAR_END = date(today.year, 12, 31)
        kehtib_kuni = self.form.data.get('kehtib_kuni') or YEAR_END
        koht = model.Koht.get(koht_id)
        if not koht:
            self.error(_("Kool valimata"))
        elif kehtib_kuni < today:
            self.error(_("Kuupäev on möödas"))
        else:
            if not koht.kool_id:
                self.notice(_("Valitud koht ei ole EHISes õppeasutus!"))
            q = (model.Pedagoog.query
                 .filter_by(kasutaja_id=self.c.kasutaja.id)
                 .filter_by(koht_id=koht_id))
            item = q.first()
            if item:
                self.error(_("Isikul on juba ametikoht valitud õppeasutuses"))
                if not item.on_ehisest and kehtib_kuni:
                    item.seisuga = datetime.now()
                    item.kehtib_kuni = kehtib_kuni
                    model.Session.commit()
                    self.success()                    
            else:
                model.Pedagoog(kasutaja_id=self.c.kasutaja.id,
                               isikukood=self.c.kasutaja.isikukood,
                               koht_id=koht_id,
                               kool_id=koht.kool_id,
                               eesnimi=self.c.kasutaja.eesnimi,
                               perenimi=self.c.kasutaja.perenimi,
                               kasutajagrupp_id=const.GRUPP_OPETAJA,
                               seisuga=datetime.now(),
                               kehtib_kuni=kehtib_kuni,
                               on_ehisest=False)
                model.Session.commit()
                self.success()

        return HTTPFound(location=self.url('admin_kasutaja', id=self.c.kasutaja.id))
    
    def delete(self):
        pedagoog_id = self.request.matchdict.get('id')
        item = model.Pedagoog.get(pedagoog_id)
        if item.kasutaja_id==self.c.kasutaja.id and \
           item.on_ehisest==False:
            BaseResourceController._delete(self, item)
        return HTTPFound(location=self.url('admin_kasutaja', id=self.c.kasutaja.id))
    
    def __before__(self):
        self.c.kasutaja = model.Kasutaja.get(self.request.matchdict.get('kasutaja_id'))
