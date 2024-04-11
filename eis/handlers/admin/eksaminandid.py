from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import ehis
from .kasutajad import KasutajadController
log = logging.getLogger(__name__)

class EksaminandidController(KasutajadController):
    "Testisooritajate haldus"

    _MODEL = model.Kasutaja
    _SEARCH_FORM = forms.admin.EksaminandidForm
    _ITEM_FORM = forms.admin.EksaminandForm
    _INDEX_TEMPLATE = '/admin/eksaminandid.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = '/admin/eksaminand.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/admin/eksaminandid_list.mako'
    _DEFAULT_SORT = 'perenimi,eesnimi'

    _permission = 'eksaminandid'

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(c.isikukood)
                         .filter(model.Kasutaja))

        if c.testiliik:
            q = q.filter(model.Kasutaja.sooritajad.any(\
                    model.Sooritaja.test.has(\
                        model.Test.testiliik_kood==c.testiliik)))

        if c.epost:
            q = q.filter(model.Kasutaja.epost.ilike(c.epost))
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))
        if c.kool or c.klass:
            f_op = sa.and_(model.Opilane.kasutaja_id==model.Kasutaja.id,
                           model.Opilane.on_lopetanud==False)
            if c.kool:
                f_op = sa.and_(f_op,
                               model.Opilane.koht_id==model.Koht.id,
                               model.Koht.nimi.ilike(c.kool))
            if c.klass:
                f_op = sa.and_(f_op,
                               model.Opilane.klass==c.klass)
            q = q.filter(sa.exists().where(f_op))

        if c.mitukooli:
            Opilane1 = sa.orm.aliased(model.Opilane)
            Opilane2 = sa.orm.aliased(model.Opilane)
            q = q.filter(sa.exists().where(sa.and_(
                Opilane1.kasutaja_id==model.Kasutaja.id,
                Opilane1.on_lopetanud==False,
                Opilane1.prioriteet>0,
                Opilane2.kasutaja_id==model.Kasutaja.id,
                Opilane2.on_lopetanud==False,
                Opilane2.prioriteet>0,
                Opilane1.id!=Opilane2.id)))

        return q

    def _edit(self, item):
        # leiame soorituste kirjed
        self._list_sooritajad(item.id)
        self._list_rvsooritajad(item.id)

    def _update(self, item):
        eesnimi = self.form.data.get('k_eesnimi')
        perenimi = self.form.data.get('k_perenimi')
        item.set_kehtiv_nimi(eesnimi, perenimi)
        # isikuandmed
        item.from_form(self.form.data, 'k_')
        # õppimisandmed
        item.from_form(self.form.data, 'ko_')        
        model.Aadress.adr_from_form(item, self.form.data, 'a_')
        # isikukood, synniaeg ja sugu
        self._save_ik(item, True)
            
        # kui isik õpib EHISe andmetel mitmes koolis, siis määratakse prioriteetne kool,
        # mille andmed lisatakse registreeringutele
        opilane_id = self.form.data.get('prioriteet_op_id')
        if opilane_id:
            opilane_id = int(opilane_id)
            opilane = item.opilane
            if opilane_id != opilane.id:
                # kui kehtiv vaikimisi prioriteet vajab muutmist
                for op in item.opilased:
                    if op.id == opilane_id:
                        op.prioriteet = model.Opilane.PRIORITEET_KASITSI
                    else:
                        op.set_prioriteet(op.koht)
                model.Session.flush()

    def _show_oppurid(self, id):
        "Õppimise päring EHISest ühe isiku kohta"

        self.c.kasutaja = item = model.Kasutaja.get(id)
        isikukoodid = [item.isikukood]
        reg = ehis.Ehis(handler=self)
        message, oppimised = reg.oppurid_ik(isikukoodid)
        if message:
            self.error(message)
        else:
            model.Opilane.update_opilased(oppimised, isikukoodid)
            model.Session.commit()
        return self.render_to_response('/admin/eksaminand.oppurid.mako')

    def _show_sooritajad(self, id):
        self.c.item = model.Kasutaja.get(id)
        self._list_sooritajad(id)
        return self.render_to_response('/admin/eksaminand.sooritajad.mako')

    def _list_sooritajad(self, k_id):
        c = self.c
        q = (model.Session.query(model.Sooritaja)
             .filter(model.Sooritaja.kasutaja_id==k_id)
             .join(model.Sooritaja.test)
             .filter(model.Test.testiliik_kood!=const.TESTILIIK_KOOLIPSYH)
             )
        c.testiliik = self.request.params.get('testiliik')
        # millist liiki teste kasutaja võib näha
        liigid = self.c.user.get_testiliigid(self._permission)
        if None not in liigid:
            # ei või kõiki liike näha
            q = q.filter(model.Test.testiliik_kood.in_(liigid))
        if c.testiliik:
            q = (q.join(model.Sooritaja.test)
                .filter_by(testiliik_kood=c.testiliik))                

        c.staatus = self.request.params.get('staatus')
        if c.staatus:
            q = q.filter(model.Sooritaja.staatus==c.staatus)
        q = q.order_by(model.Sooritaja.id)
        c.sooritajad = q.all()

    def _list_rvsooritajad(self, k_id):
        c = self.c
        q = (model.Session.query(model.Rvsooritaja)
             .join(model.Rvsooritaja.tunnistus)
             .filter(model.Tunnistus.kasutaja_id==k_id)
             .order_by(model.Tunnistus.valjastamisaeg))
        c.rvsooritajad = q.all()
        
        
