from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class Sooritajatearv2Controller(BaseResourceController):
    """Samaaegsete sooritajate arvu päring
    """
    _permission = 'aruanded-sooritajatearv'
    _INDEX_TEMPLATE = 'ekk/otsingud/sooritajatearv2.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/sooritajatearv2_list.mako'
    _SEARCH_FORM = forms.ekk.otsingud.SooritajatearvForm 
    _ignore_default_params = ['csv','otsi']
    _actions = 'index'

    def _query(self):
        return 

    def _search(self, q1):
        c = self.c

        if not c.step or c.viimane:
            c.step = 5

        STEP_MIN = c.step
        STEP = timedelta(minutes=STEP_MIN)

        if not c.alates and not c.kuni or c.viimane:
            c.kuni = datetime.now()
            c.alates = c.alates_kuni = c.kuni - STEP
        else:
            if not c.alates:
                c.alates = c.kuni or date.today()
            kell = (0, 0)
            if c.alates_kell and STEP_MIN == 1440:
                self.notice(_("Kellaajalise täpsusega saab pärida ainult ühe päeva siseselt"))
            elif c.alates_kell:
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

        if c.viimane:
            # iga testiosa eraldi real
            q = (model_log.DBSession.query(
                sa.func.count(model_log.Logi.id),
                sa.func.avg(model_log.Logi.kestus),
                sa.func.max(model_log.Logi.kestus),
                sa.func.count(model_log.Logi.isikukood.distinct()),
                model_log.Logi.testiosa_id)
                 )
        else:
            # kõik sama ajavahemiku testiosad koos
            q = (model_log.DBSession.query(
                sa.func.count(model_log.Logi.id),
                sa.func.avg(model_log.Logi.kestus),
                sa.func.max(model_log.Logi.kestus),
                sa.func.count(
                    sa.func.concat(model_log.Logi.isikukood,
                                   sa.sql.expression.cast(
                                       model_log.Logi.testiosa_id,
                                        sa.String)
                                   ).distinct()),
                sa.func.array_agg(
                    model_log.Logi.testiosa_id.distinct()
                    )
                ))
        q = (q.filter(model_log.Logi.testiosa_id!=None)
             .filter(model_log.Logi.tyyp==const.LOG_USER)
             )

        if c.viimane:
            q = q.group_by(model_log.Logi.testiosa_id)
        
        c.prepare_item = self._prepare_item
        c.prepare_header = self._prepare_header
        if c.csv:
            # väljastame CSV
            return self._index_csv(q)
        return q

    def _query_ylesandevaatamine(self):
        q = model_s.DBSession.query(sa.func.count(model_s.Ylesandevaatamine.id))
        return q
    
    def _paginate(self, q):
        c = self.c
        qyv = self._query_ylesandevaatamine()
        STEP = timedelta(minutes=c.step)
        dt = c.alates
        items = []
        while dt < min(c.kuni, datetime.now()):
            dt2 = dt + STEP
            q1 = (q.filter(model_log.Logi.aeg >= dt)
                  .filter(model_log.Logi.aeg < min(dt2, c.kuni))
                  )
            for r in q1.all():
                r = list(r)
                if r[0]:
                    # kuvame ainult need read, kus on pöördumisi
                    # ylesandevaatamiste arv sooritaja kohta
                    qyv1 = (qyv.filter(model_s.Ylesandevaatamine.algus >= dt)
                            .filter(model_s.Ylesandevaatamine.algus < min(dt2, c.kuni))
                            )
                    ryv = list(qyv1.first())

                    item = [dt] + r + ryv
                    items.append(item)
            dt = dt2
        return items
    
    def _prepare_header(self):
        header = [(None, _("Aeg")),
                  (None, _("Testi pöördumiste arv")),
                  (None, _("Keskmine pöördumise kestus")),
                  (None, _("Max pöördumise kestus")),
                  (None, _("Testisoorituste arv")),
                  (None, _("Pöördumiste arv sooritaja kohta")),
                  (None, _("Ülesande avamisi sooritaja kohta")),
                  #(None, _("Ühel ülesandel olemise aeg")),                  
                  (None, _("Testid"))
                  ]       
        return header

    def _order(self, q, sort=None):
        return q
    
    def _prepare_item(self, rcd, n=None):
        c = self.c
        h = self.h
        STEP = timedelta(minutes=c.step)
        dt, cnt, avg_d, max_d, cnt_t, testiosad_id, cnt_yva = rcd
        if self.c.step == 1440:
            aeg = self.h.str_from_date(dt)
        elif self.c.step == 60:
            aeg = '%s %s:00-%s:59' % (h.str_from_date(dt),
                                      dt.hour,
                                      dt.hour)
        else:
            aeg = '%s %s-%s' % (h.str_from_date(dt),
                                h.str_time_from_datetime(dt),
                                h.str_time_from_datetime(dt+STEP))
        testid = self._prepare_testid(testiosad_id)
        s_testid = ', '.join(sorted(testid))
        poordumisi_per_s = cnt_t and cnt / cnt_t or None
        yva_per_s = cnt_t and cnt_yva and cnt_yva / cnt_t or None
        item = [aeg, cnt, h.fstr(avg_d), h.fstr(max_d), cnt_t,
                h.fstr(poordumisi_per_s,1),
                h.fstr(yva_per_s,1),
                #mode_yva,
                s_testid]
        return item

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        header = self._prepare_header()
        data = self._paginate(q)
        items = [self._prepare_item(rcd, n) for n, rcd in enumerate(data)]
        return header, items
    
    def _prepare_testid(self, testiosad_id):
        c = self.c
        if not c.testiosad:
            c.testiosad = {}
        testid = []
        if isinstance(testiosad_id, int):
            # viimane, testiosade kaupa
            testiosad_id = [testiosad_id]
        for testiosa_id in testiosad_id or []:
            label = c.testiosad.get(testiosa_id)
            if not label:
                q = (model.Session.query(model.Testiosa.test_id, model.Testiosa.tahis, model.Test.testityyp)
                     .filter(model.Testiosa.id==testiosa_id)
                     .join(model.Testiosa.test)
                     )
                r = q.first()
                if r:
                    t_id, o_tahis, tyyp = r
                    if tyyp == const.TESTITYYP_EKK:
                        label = f'{t_id}-{o_tahis}'
                    else:
                        label = f'{t_id}'
                    c.testiosad[testiosa_id] = label
                else:
                    continue
            testid.append(label)
        return testid
