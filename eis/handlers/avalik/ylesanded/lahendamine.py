"Ülesande vaatamine pedagoogi jaoks"

from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.avalik.lahendamine.lahendamine as lahendamine
from eis.handlers.avalik.tookogumikud.ylesandeotsing import YlesandeotsingController
log = logging.getLogger(__name__)

class LahendamineController(lahendamine.LahendamineController):
    _permission = 'avylesanded,lahendamine'
    _EDIT_TEMPLATE = 'avalik/ylesanded/lahendamine.mako' 
    _authorize = True
    _get_is_readonly = False
    _actions = 'show,update,edit'

    def edit(self):
        # esmalt kontrollime ylesande ja loome ettetehtud esitluse
        c = self.c
        ylesanne_id = c.ylesanne.id
        if self.request.method == 'GET' and c.user.has_permission('avylesanded', const.BT_UPDATE, c.ylesanne):
            c.ylesanne.check(self)
            model.Session.commit()
            c.ylesanne = model.Ylesanne.get(ylesanne_id)
        sub = self._get_sub()
        if sub == 'kogumikku':
            return self._edit_kogumikku(ylesanne_id)
        return lahendamine.LahendamineController.edit(self)
    
    def update(self):
        """Lahendaja salvestab oma vastuse
        """
        sub = self._get_sub()
        if sub == 'kogumikku':
            id = self.request.matchdict.get('id')
            return self._update_kogumikku(id)
        return lahendamine.LahendamineController.update(self)
    
    def _get_next_tookogumikust(self, params, current_id):
        q = (model.SessionR.query(model.Tkylesanne.ylesanne_id)
             .join(model.Tkylesanne.tkosa)
             .join(model.Tkosa.tookogumik)
             .filter(model.Tookogumik.kasutaja_id==self.c.user.id)
             )
        q = q.order_by(model.Tkylesanne.seq)
        return q
    
    def _get_next_ykogust(self, params, current_id):
        kogu_id = params.get('ykyk_id')
        testiliik = params.get('testiliik')
        kasutliik = params.get('kasutliik')
        muu = params.get('muu')
        q = (model.SessionR.query(model.Koguylesanne.ylesanne_id)
             .filter(model.Koguylesanne.ylesandekogu_id==kogu_id)
             .join(model.Koguylesanne.ylesanne)
             )
        if self.c.user.on_pedagoog:
            q = q.filter(model.Ylesanne.staatus.in_(
                (const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG)))
        else:
            q = q.filter(model.Ylesanne.staatus==const.Y_STAATUS_AVALIK)

        if testiliik:
            q = q.filter(model.Ylesanne.testiliigid
                         .any(model.Testiliik.kood==testiliik))
        elif kasutliik:
            q = q.filter(model.Ylesanne.kasutliigid
                         .any(model.Kasutliik.kasutliik_kood==kasutliik))
        elif muu:
            q = (q.filter(~ model.Ylesanne.testiliigid.any())
                .filter(~ model.Ylesanne.kasutliigid.any())
                 )
        # järjestatud ylesande nime järgi
        q = q.order_by(model.Ylesanne.nimi)
        return q

    def _get_next_otsingust(self, params, current_id):
        # muudame dicti form_resultiks
        ctrl = YlesandeotsingController(self.request, pseudo=True)
        form_data = ctrl._ITEM_FORM.to_python(params)
        # jätame otsinguparameetrid meelde (neid kasutab _search)
        ctrl._copy_search_params(form_data)
        # koostame päringu
        q = ctrl._search(ctrl._query())
        # lisame sortimise
        q = ctrl._order(q, params.get('sort'))
        self.request.handler = self
        return q
    
    def _get_next(self, id):
        """Leitakse järgmine ülesanne
        """
        prev_id = self.request.params.get('prev_id')
        next_id = self.request.params.get('next_id')
        if next_id:
            # on juba varasemast teada
            return prev_id, next_id

        if self.c.list_url:
            # muudame loetelu URLi dictiks
            params = lahendamine.url_to_dict(self.c.list_url)
            current_id = int(id)

            if self.c.list_url == 'TKO':
                # siia tuldi oma töökogumiku seest
                q = self._get_next_tookogumikust(params, current_id)
                get_id = lambda r: r[0]
            elif 'ykyk_id' in params:
                # siia tuldi ylesandekogus olevate ylesannete loetelust
                q = self._get_next_ykogust(params, current_id)
                get_id = lambda r: r[0]
            else:
                # siia tuldi ylesannete otsingus olevast loetelust
                q = self._get_next_otsingust(params, current_id)
                get_id = lambda r: r.id
            if q:
                step_id = None
                found = False
                #model.log_query(q)
                for r in q.all():
                    y_id = get_id(r)
                    if self.c.user.has_permission('lahendamine', const.BT_SHOW, ylesanne_id=y_id):
                        if y_id == current_id:
                            # leiti praegune ylesanne
                            found = True
                            # eelmine oli eelmine ylesanne
                            prev_id = step_id
                        elif found:
                            # leiti järgmine ylesanne
                            next_id = y_id
                            break
                        else:
                            # jätame meelde
                            step_id = y_id
        # järgmist ei leitud
        return prev_id, next_id

    def _edit_kogumikku(self, id):
        "Ylesande lisamine töökogumikku"
        c = self.c
        c.opt_kogu = model.Tookogumik.get_opt(c.user.id, id)
        if not c.opt_kogu:
            # kasutajal pole töökogumikke, lisame automaatselt uue
            item = model.Tookogumik.lisa_tookogumik(c.user.id)
            model.Session.commit()
            c.opt_kogu = model.Tookogumik.get_opt(c.user.id, id)
        return self.render_to_response('/avalik/ylesanded/lahendamine.lisakogumikku.mako')

    def _update_kogumikku(self, id):
        "Ylesande lisamine töökogumikku"
        tookogumik_id = self.request.params.get('op')
        if model.Tookogumik.lisa_ylesanne(self.c.user.id, id, tookogumik_id):
            model.Session.commit()
            msg = _("Ülesanne lisati töökogumikku")
        else:
            msg = _("Ülesanne on juba töökogumikku lisatud")
        return Response(msg)

    def _check_status(self, item):
        if not item:
            self.error(_("Pole avalik ülesanne"))
            raise HTTPFound(location=self.url('avaleht'))
        elif self.c.user.has_permission('avylesanded', const.BT_SHOW, obj=item):
            return True
        elif self.c.user.has_permission('lahendamine', const.BT_SHOW, obj=item):
            return True        
        else:
            self.error(_("Pole avalik ülesanne"))
            raise HTTPFound(location=self.url('avaleht'))

    def __before__(self):
        super().__before__()
        # eistest päringud teha ilma puhvrita, et koostaja saaks värske
        self.c.test_cachepurge = True
        
    def _perm_params(self):
        if not self.c.ylesanne:
            return False
        return {'obj':self.c.ylesanne}

    def _get_perm_bit(self):
        # lahendamine ei muuda ylesannet
        return const.BT_SHOW
