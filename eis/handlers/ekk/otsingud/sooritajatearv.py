from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class SooritajatearvController(BaseResourceController):
    """Samaaegsete sooritajate arvu päring
    """
    _permission = 'aruanded-sooritajatearv'
    _INDEX_TEMPLATE = 'ekk/otsingud/sooritajatearv.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/sooritajatearv_list.mako'
    _SEARCH_FORM = forms.ekk.otsingud.SooritajatearvForm 
    _ignore_default_params = ['csv','otsi']
    _actions = 'index'

    def _query(self):
        return 

    def _search(self, q1):
        c = self.c
        if not c.otsi and not c.page and not c.csv:
            return
        
        DURATION = timedelta(minutes=60) # piirajata testi eeldatav kestus
        STEP_MIN = c.step or 10
        STEP = timedelta(minutes=STEP_MIN)

        if not c.alates:
            c.alates = c.kuni or date.today()
        kell = (0, 0)
        if c.alates_kell:
            try:
                kell = forms.validators.EstTimeConverter().to_python(c.alates_kell)
            except forms.formencode.api.Invalid as ex:
                raise ValidationError(self, {'alates_kell':_("tt.mm")})
        c.alates = c.alates_kell = datetime.combine(c.alates, time(*kell))

        if not c.kuni:
            c.kuni = c.alates
        if STEP_MIN != 1440:
            kuni_d = isinstance(c.kuni, date) and c.kuni or c.kuni.date()
            if kuni_d != c.alates.date():
                self.notice(_("Kellaajalise täpsusega saab pärida ainult ühe päeva siseselt"))
                c.kuni = c.alates
        kell = (23, 59)
        if c.kuni_kell:
            try:
                kell = forms.validators.EstTimeConverter().to_python(c.kuni_kell)
            except forms.formencode.api.Invalid as ex:
                raise ValidationError(self, {'kuni_kell':_("tt.mm")})
        c.kuni = c.kuni_kell = datetime.combine(c.kuni, time(*kell))

        Kell = model.SessionR.query(
            sa.func.generate_series(c.alates, c.kuni, STEP).label('kell')
            ).subquery()
        q = (model.SessionR.query(Kell.c.kell,
                                 sa.func.count(model.Sooritus.id),
                                 sa.func.array_agg(
                                     sa.func.coalesce(
                                         model.Toimumisaeg.tahised,
                                         sa.sql.expression.cast(
                                             model.Testiosa.test_id,
                                             sa.String)
                                         ).distinct()
                                     )
                                 )
             .join(model.Sooritus.testiosa)
             .filter(model.Testiosa.vastvorm_kood.in_((const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I)))
             .filter(model.Sooritus.staatus!=const.S_STAATUS_TYHISTATUD)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_REGAMATA)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             .outerjoin(model.Sooritus.toimumisaeg)
             )
        if STEP_MIN == 1440:
            # sooritused yhe päeva jooksul
            q = q.filter(sa.func.date_trunc('day', sa.func.coalesce(model.Sooritus.algus, model.Sooritus.kavaaeg)) == sa.func.date_trunc('day', Kell.c.kell))
        elif STEP_MIN == 60:
            # sooritused yhe tunni jooksul
            q = q.filter(sa.func.date_trunc('hour', sa.func.coalesce(model.Sooritus.algus, model.Sooritus.kavaaeg)) == sa.func.date_trunc('hour', Kell.c.kell))            
        else:
            # sooritused antud hetkel
            q = (q.filter(sa.func.coalesce(model.Sooritus.algus, model.Sooritus.kavaaeg) > 
                          Kell.c.kell - sa.func.coalesce(model.Testiosa.piiraeg*timedelta(seconds=1), DURATION))
                 .filter(sa.func.coalesce(model.Sooritus.algus, model.Sooritus.kavaaeg) <= Kell.c.kell)             
                 #.filter(model.Sooritus.kavaaeg > Kell.c.kell - DURATION)
                 #.filter(model.Sooritus.kavaaeg <= Kell.c.kell)
                 .filter(sa.or_(model.Sooritus.lopp==None,
                                model.Sooritus.lopp>Kell.c.kell))
                 )
        q = q.group_by(Kell.c.kell)
        #               model.Testiosa.test_id,
        #               model.Toimumisaeg.tahised)
        q = q.order_by(Kell.c.kell)
        #               model.Testiosa.test_id,
        #               model.Toimumisaeg.tahised)
        #model.log_query(q)

        c.prepare_item = self._prepare_item
        c.prepare_header = self._prepare_header
                
        if c.csv:
            # väljastame CSV
            return self._index_csv(q)
        return q

    def _prepare_header(self):
        header = [(None, _("Aeg")),
                  (None, _("Sooritajate arv")),
                  (None, _("Testid")),
                  ]       
        return header

    def _order(self, q, sort=None):
        return q
    
    def _prepare_item(self, rcd, n=None):
        dt, cnt, testid = rcd
        if self.c.step == 1440:
            aeg = self.h.str_from_date(dt)
        elif self.c.step == 60:
            aeg = '%s %s:00-%s:59' % (self.h.str_from_date(dt),
                                      dt.hour,
                                      dt.hour)
        else:
            aeg = self.h.str_from_datetime(dt)
        s_testid = ', '.join(sorted(testid))
        item = [aeg, cnt, s_testid]
        return item

