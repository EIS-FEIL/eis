from eis.lib.baseresource import *
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)
_ = i18n._

class NousolekudController(BaseResourceController):
    _permission = 'nousolekud'
    _MODEL = model.Labiviija
    _ITEM_FORM = forms.avalik.admin.NousolekudForm
    _INDEX_TEMPLATE = '/avalik/nousolekud/nousolekud.mako' 
    _LIST_TEMPLATE = '/avalik/nousolekud/nousolekud_list.mako'
    _DEFAULT_SORT = '-toimumisaeg.alates'
    _UNIQUE_SORT = 'toimumisaeg.id'

    def _query(self):
        q = (model.SessionR.query(model.Toimumisaeg, model.Test)
             .filter(model.Toimumisaeg.reg_labiviijaks==True)
             .join(model.Toimumisaeg.testimiskord)
             .join(model.Testimiskord.test)
             .join(model.Toimumisaeg.testiosa)
             .filter(model.Test.avaldamistase==const.AVALIK_EKSAM)
             .filter(sa.or_(model.Toimumisaeg.alates>=date.today(),
                            model.Toimumisaeg.alates==None))
             )

        vastvorm_k = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_KP)
        vastvorm_s = (const.VASTVORM_SH, const.VASTVORM_SP)
        f_prof = sa.and_(model.Aineprofiil.kasutaja_id==self.c.user.id,
                         model.Aineprofiil.aine_kood==model.Test.aine_kood,
                         sa.or_(sa.and_(model.Aineprofiil.kasutajagrupp_id==const.GRUPP_INTERVJUU,
                                        model.Toimumisaeg.intervjueerija_maaraja!=None),
                                sa.and_(model.Aineprofiil.kasutajagrupp_id==const.GRUPP_HINDAJA_K,
                                        model.Testiosa.vastvorm_kood.in_(vastvorm_k)),
                                sa.and_(model.Aineprofiil.kasutajagrupp_id==const.GRUPP_HINDAJA_S,
                                        model.Testiosa.vastvorm_kood.in_(vastvorm_s))
                                ))
        f = sa.exists().where(f_prof)

        profiil = self.c.kasutaja.profiil
        if profiil and profiil.on_vaatleja:
            q = q.filter(sa.or_(f, model.Toimumisaeg.vaatleja_maaraja==True))
        else:
            q = q.filter(f)
        #model.log_query(q)
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
                self.c.kasutaja.kasutajapiirkonnad.append(rcd)

        for rcd in self.c.kasutaja.kasutajapiirkonnad:
            if rcd.piirkond_id in id_list:
                # eemaldame
                rcd.remove()

        model.Session.commit()
        self.success()

        return self._redirect('index')

    def _create(self):
        """Andmete salvestamine
        """
        self.c.kasutaja.epost = self.form.data.get('k_epost')
        if self._update_nousolekud():
            if not self.c.kasutaja.epost:
                errors = {'k_epost': _('Palun sisestada e-posti aadress')}
                raise ValidationError(self, errors)

        return self.c.kasutaja

    def _error_create(self):
        form = self.form
        self.form = None # et index_d teostaks search()
        extra_info = self._index_d()
        html = form.render(self._INDEX_TEMPLATE, extra_info=extra_info)
        return Response(html)

    def _update_nousolekud(self):
        d = datetime.now()
        noustus = False
        for rcd in self.form.data.get('ta'):
            toimumisaeg_id = rcd.get('toimumisaeg_id')

            ta = model.Toimumisaeg.get(toimumisaeg_id)
            if rcd.get('on_vaatleja') is not None or \
                    rcd.get('on_hindaja') is not None or \
                    rcd.get('on_intervjueerija') is not None:
                item = ta.give_nousolek(self.c.kasutaja.id)
                if rcd.get('on_vaatleja') and not item.on_vaatleja:
                    item.vaatleja_ekk = False
                    item.vaatleja_aeg = d
                if rcd.get('on_hindaja') and not item.on_hindaja:
                    item.hindaja_ekk = False
                    item.hindaja_aeg = d
                if rcd.get('on_intervjueerija') and not item.on_intervjueerija:
                    item.intervjueerja_ekk = False
                    item.intervjueerija_aeg = d                    

                item.from_form(rcd)
                noustus |= item.on_vaatleja or item.on_hindaja or item.on_intervjueerija or False
            else:
                item = ta.get_nousolek(self.c.kasutaja.id)
                if item:
                    item.delete()
        if noustus:
            self.notice(_('Täname! Teie nõusolek kinnitatud!'))
        return noustus
    
    def _delete(self, item):
        item.delete()
        #item.kasutaja_id = None
        self.success(_('Andmed on kustutatud!'))
        model.Session.commit()

    def _after_delete(self, parent_id=None):
        """Kuhu peale läbiviija kirje kustutamist minna
        """
        return HTTPFound(location=self.url('nousolekud', testsessioon_id=self.c.testsessioon_id))

    def _after_update(self, id=None):
        """Kuhu peale salvestamist minna
        """
        model.Session.commit()
        self.success()
        return HTTPFound(location=self.url('nousolekud', testsessioon_id=self.c.testsessioon_id))

    def __before__(self):
        self.c.kasutaja = self.c.user.get_kasutaja(write=True)
        self.c.testsessioon_id = self.request.params.get('testsessioon_id')
