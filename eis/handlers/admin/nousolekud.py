from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class NousolekudController(BaseResourceController):
    _permission = 'kasutajad'
    _MODEL = model.Nousolek
    _ITEM_FORM = forms.admin.NousolekudForm
    _INDEX_TEMPLATE = '/admin/kasutaja.nousolekud.mako' 
    _DEFAULT_SORT = '-toimumisaeg.alates'

    def _query(self):
        q = (model.Session.query(model.Toimumisaeg, model.Test, model.Nousolek)
             .filter(model.Toimumisaeg.reg_labiviijaks==True)
             .join(model.Toimumisaeg.testiosa)
             .join(model.Testiosa.test)
             .join(model.Toimumisaeg.nousolekud)
             .join(model.Toimumisaeg.testimiskord)
             .filter(model.Nousolek.kasutaja_id==self.c.kasutaja.id)
             .filter(sa.or_(model.Toimumisaeg.kuni>=date.today(),
                            model.Toimumisaeg.kuni==None))                        
             )
        liigid = self.c.user.get_testiliigid(self._permission)
        if None not in liigid:
            q = q.filter(model.Test.testiliik_kood.in_(liigid))
        return q

    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """

        c = self.c
        # sessioonide valik ainult nendest sessioonidest, kus on võimalikke teste
        q1 = q.with_entities(model.Testimiskord.testsessioon_id.distinct())
        sessioonid_id = [s_id for s_id, in q1.all()]
        c.opt_testsessioon = [r for r in c.opt.testsessioon if r[0] in sessioonid_id]
        
        if c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==c.testsessioon_id)
        return q

    def _paginate(self, q):
        return q.all()

    def _new_prk(self):
        "Piirkondade valiku dialoogiakna kuvamine"
        return self.render_to_response('/avalik/nousolekud/piirkonnad.mako')

    def _create_prk(self):
        "Piirkondade valiku salvestamine"
        id_list = [rcd.piirkond_id for rcd in self.c.kasutaja.kasutajapiirkonnad]

        piirkonnad = self.request.params.get('piirkonnad').split(',')
        for piirkond_id in piirkonnad:
            if not piirkond_id:
                continue
            if piirkond_id in id_list:
                # juba olemas, andmebaasis ei muuda midagi
                id_list.remove(piirkond_id)
            else:
                # lisame
                rcd = model.Kasutajapiirkond(kasutaja=self.c.kasutaja,
                                             piirkond_id=piirkond_id)

        for rcd in self.c.kasutaja.kasutajapiirkonnad:
            if rcd.piirkond_id in id_list:
                # eemaldame
                rcd.remove()

        model.Session.commit()
        self.success()

        return self._redirect('index')

    def new(self):
        """Avatakse dialoogiaken, et valida test, millele läbiviija kirje lisada
        """
        sub = self._get_sub()
        if sub:
            return eval('self._new_%s' % sub)()
        return self._index_testid()

    def _index_testid(self):
        dd = date.today()
        q = (model.SessionR.query(model.Toimumisaeg, model.Nousolek)
             .filter(model.Toimumisaeg.reg_labiviijaks==True)
             .filter(sa.or_(model.Toimumisaeg.alates>=date.today(),
                            model.Toimumisaeg.alates==None))
             .outerjoin((model.Nousolek,
                         sa.and_(model.Nousolek.toimumisaeg_id==model.Toimumisaeg.id,
                                 model.Nousolek.kasutaja_id==self.c.kasutaja.id)))
                         
             )
        # veel tuleks kontrollida, et sellel toimumisajal on vaja intervjueerijat või EKK hindajat II

        self.c.testsessioon_id = self.request.params.get('testsessioon_id')
        if self.c.testsessioon_id:
            q = q.join(model.Toimumisaeg.testimiskord).\
                filter(model.Testimiskord.testsessioon_id==int(self.c.testsessioon_id))
        self.c.vastvorm = self.request.params.get('vastvorm')
        if self.c.vastvorm:
            q = q.filter(model.Toimumisaeg.testiosa.has(
                    model.Testiosa.vastvorm_kood==self.c.vastvorm))
        q = q.order_by(model.Toimumisaeg.alates)

        self.c.items = q.all()
        return self.render_to_response('/admin/kasutaja.testivalik.mako')        

    def _create(self):
        self._update_nousolekud()
        model.Session.commit()
        self.success()
        return self._redirect('index', testsessioon_id=self.request.params.get('testsessioon_id'))

    def _update_nousolekud(self):
        d = datetime.now()
        for rcd in self.form.data.get('ta'):
            toimumisaeg_id = rcd.get('toimumisaeg_id')
            ta = model.Toimumisaeg.get(toimumisaeg_id)
            if rcd.get('on_vaatleja') or \
                    rcd.get('on_hindaja') or \
                    rcd.get('on_intervjueerija'):
                item = ta.give_nousolek(self.c.kasutaja.id)

                if rcd.get('on_vaatleja') and not item.on_vaatleja:
                    item.vaatleja_ekk = True
                    item.vaatleja_aeg = d
                if rcd.get('on_hindaja') and not item.on_hindaja:
                    item.hindaja_ekk = True
                    item.hindaja_aeg = d
                if rcd.get('on_intervjueerija') and not item.on_intervjueerija:
                    item.intervjueerja_ekk = True
                    item.intervjueerija_aeg = d                    

                item.from_form(rcd)
            else:
                item = ta.get_nousolek(self.c.kasutaja.id)
                if item:
                    item.delete()

    def _delete(self, item):
        item.delete()
        #item.kasutaja_id = None
        self.success(_("Andmed on kustutatud"))
        model.Session.commit()

    def _after_update(self, parent_id=None):
        """Kuhu peale muutmist minna
        """
        return self._redirect('index')

    def _after_delete(self, parent_id=None):
        """Kuhu peale läbiviija kirje kustutamist minna
        """
        return self._redirect('index')

    def __before__(self):
        self.c.kasutaja = model.Kasutaja.get(self.request.matchdict.get('kasutaja_id'))
