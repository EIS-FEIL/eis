# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

STEP_DAY = 1
STEP_7DAYS = 7
STEP_MONTH = 30
STEP_TOTAL = 100
TOTAL_KEY = 'total'

class KasutajatearvController(BaseResourceController):
    """Kasutajate arvu statistika
    """
    _permission = 'admin'
    _INDEX_TEMPLATE = 'ekk/otsingud/kasutajatearv.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/kasutajatearv_list.mako'
    _SEARCH_FORM = forms.ekk.otsingud.KasutajatearvForm 
    _ignore_default_params = ['csv','otsi']
    _actions = 'index'
    _no_paginate = True
    
    def _query(self):
        return 

    def _search_default(self, q):
        self.c.alates = date.today() - timedelta(days=1)
        self.c.kuni = None

    def _search(self, q):
        c = self.c
        if not c.otsi and not c.page and not c.csv:
            return
        
        if not self._has_search_params():
            self._search_default(q)

        if not c.alates:
            c.alates = date.today() - timedelta(days=1)
        kuni1 = c.kuni and c.kuni + timedelta(days=1)
        kuni0 = c.kuni or date.today()

        h = self.h

        def _get_monday(dt):
            return dt - timedelta(days=dt.weekday())

        def _get_sunday(dt):
            return dt + timedelta(days=6-dt.weekday())

        if c.step == STEP_TOTAL:
            # ei toimu grupeerimist
            fgroups = lambda fld: []
            maxk = kuni0
        elif c.step == STEP_MONTH:
            # kuukaupa
            fgroups = lambda fld: [sa.func.date_part('year', fld),
                                  sa.func.date_part('month', fld)]
            fkey = lambda year, month: '%s-%s' % (int(year), int(month))
            maxk1 = utils.add_months(c.alates, 20)
            maxk = date(maxk1.year, maxk1.month, 1) - timedelta(days=1)
        elif c.step == STEP_7DAYS:
            # 7 päeva kaupa
            week_start = c.alates.weekday()
            fgroups = lambda fld: [sa.func.date_part('week', fld - sa.cast('%d days' % week_start, sa.dialects.postgresql.INTERVAL))]
            fkey = lambda week: int(week)
            maxk = c.alates + timedelta(days=7*20-1)
        else:
            # päevakaupa
            fgroups = lambda fld: [sa.func.date(fld),]
            fkey = lambda dt: h.str_from_date(dt)
            maxk = c.alates + timedelta(days=19)

        if kuni0 > maxk:
            self.error(_("Liiga pikk periood, kuvame kuni 20 rida"))
            c.kuni = kuni0 = maxk
            kuni1 = kuni0 + timedelta(days=1)

        def _get_kokku_testisooritused(alates, kuni1):
            # testisoorituste arv
            groups = fgroups(model.Sooritaja.algus)
            q = (model.Session.query(*groups,
                                     sa.func.count(model.Sooritaja.id))
                 .join(model.Sooritaja.test)
                 .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_EKK)))
                 .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_POOLELI,
                                                      const.S_STAATUS_KATKESTATUD,
                                                      const.S_STAATUS_KATKESPROT,
                                                      const.S_STAATUS_TEHTUD,
                                                      const.S_STAATUS_EEMALDATUD)))
                 )
            if kuni1:
                q = q.filter(sa.and_(model.Sooritaja.algus >= alates,
                                     model.Sooritaja.algus < kuni1))
            else:
                q = q.filter(model.Sooritaja.algus >= alates)

            if groups:
                q = q.group_by(*groups)
            data = {}
            #model.log_query(q)
            for r in q.all():
                if c.step == STEP_TOTAL:
                    cnt, = r
                    sdt = TOTAL_KEY
                elif c.step in (STEP_DAY, STEP_7DAYS):
                    dt, cnt = r
                    sdt = fkey(dt)
                else:
                    year, month, cnt = r
                    sdt = fkey(year, month)
                data[sdt] = cnt
            return data

        def _get_e_testisooritused(alates, kuni1):
            # testisoorituste arv
            groups = fgroups(model.Sooritus.seansi_algus)
            q = (model.Session.query(*groups,
                                     sa.func.count(sa.distinct(model.Sooritaja.id)))
                 .join(model.Sooritus.sooritaja)
                 .join(model.Sooritaja.test)
                 .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_EKK)))
                 .filter(model.Sooritus.seansi_algus >= alates)
                 )
            if kuni1:
                q = q.filter(model.Sooritus.seansi_algus < kuni1)
            if groups:
                q = q.group_by(*groups)
            #model.log_query(q)
            data = {}
            for r in q.all():
                if c.step == STEP_TOTAL:
                    cnt, = r
                    sdt = TOTAL_KEY
                elif c.step in (STEP_DAY, STEP_7DAYS):
                    dt, cnt = r
                    sdt = fkey(dt)
                else:
                    year, month, cnt = r
                    sdt = fkey(year, month)
                data[sdt] = cnt
            return data

        def _get_toosooritused(alates, kuni1):
            # jagatud tööde soorituste arv
            groups = fgroups(model.Sooritus.seansi_algus)
            q = (model.Session.query(*groups,
                                     sa.func.count(sa.distinct(model.Sooritaja.id)))
                 .join(model.Sooritus.sooritaja)
                 .join(model.Sooritaja.test)
                 .filter(model.Test.testityyp==const.TESTITYYP_TOO)
                 .filter(model.Sooritus.seansi_algus >= alates)
                 )
            if kuni1:
                q = q.filter(model.Sooritus.seansi_algus < kuni1)
            if groups:
                q = q.group_by(*groups)
            data = {}
            for r in q.all():
                if c.step == STEP_TOTAL:
                    cnt,  = r
                    sdt = TOTAL_KEY
                elif c.step in (STEP_DAY, STEP_7DAYS):
                    dt, cnt = r
                    sdt = fkey(dt)
                else:
                    year, month, cnt = r
                    sdt = fkey(year, month)
                data[sdt] = cnt
            return data

            # select sooritaja.test_id from sooritaja, sooritus where sooritaja_id=sooritaja.id and sooritus.seansi_algus>'2020-02-28' and seansi_algus<'2020-02-29'

            # select date(ylesandevastus.lopp), count(ylesandevastus.id) from ylesandevastus, sooritus, sooritaja, test
            # where ylesandevastus.lopp >= '2020-02-28'
            # and ylesandevastus.sooritus_id=sooritus.id
            # and sooritus.sooritaja_id=sooritaja.id
            # and sooritaja.test_id=test.id
            # and test.testityyp=3
            # group by date(ylesandevastus.lopp)
            # order by date(ylesandevastus.lopp)


        def _get_pankyl(alates, kuni1):
            # ylesandepangas lahendamiste arv
            groups = fgroups(model_log.Logi.aeg)
            q = (model_log.DBSession.query(*groups,
                                           sa.func.count(model_log.Logi.id))
                 .filter(model_log.Logi.tyyp==const.LOG_USER)
                 .filter(model_log.Logi.aeg >= alates)
                 .filter(model_log.Logi.meetod=='GET')
                 )
            flt_uus = model_log.Logi.path.like('/eis/lahendamine/%/edittask')
            flt_vana = model_log.Logi.path.like('/eis/lahendamine/%/')
            if alates >= date(2021,4,1):
                q = q.filter(flt_uus)
            elif kuni1 and kuni1 < date(2021,3,1):
                q = q.filter(flt_vana)
            else:
                q = q.filter(sa.or_(flt_uus, flt_vana))
                
            if kuni1:
                q = q.filter(model_log.Logi.aeg < kuni1)
            if groups:
                q = q.group_by(*groups)
            data = {}
            for r in q.all():
                if c.step == STEP_TOTAL:
                    cnt, = r
                    sdt = TOTAL_KEY
                elif c.step in (STEP_DAY, STEP_7DAYS):
                    dt, cnt = r
                    sdt = fkey(dt)
                else:
                    year, month, cnt = r
                    sdt = fkey(year, month)
                data[sdt] = cnt
            #model.log_query(q)
            return data

        def _get_tooyl(alates, kuni1):
            # jagatud tööde koosseisus ülesannete lahendamiste arv
            groups = fgroups(model.Ylesandevastus.lopp)
            q = (model.Session.query(*groups,
                                     sa.func.count(model.Ylesandevastus.id))
                 .join((model.Sooritus, model.Sooritus.id==model.Ylesandevastus.sooritus_id))
                 .join(model.Sooritus.sooritaja)
                 .join(model.Sooritaja.test)
                 .filter(model.Test.testityyp==const.TESTITYYP_TOO)
                 .filter(model.Ylesandevastus.lopp >= alates))
            if kuni1:
                q = q.filter(model.Ylesandevastus.lopp < kuni1)
            if groups:
                q = q.group_by(*groups)
            data = {}
            for r in q.all():
                if c.step == STEP_TOTAL:
                    cnt, = r
                    sdt = TOTAL_KEY
                elif c.step in (STEP_DAY, STEP_7DAYS):
                    dt, cnt = r
                    sdt = fkey(dt)
                else:
                    year, month, cnt = r
                    sdt = fkey(year, month)
                data[sdt] = cnt
            return data

        def _get_users(alates, kuni1):
            # kasutajate arv
            groups = fgroups(model_log.Logi.aeg)
            q = (model_log.DBSession.query(*groups,
                                           sa.func.count(model_log.Logi.id),
                                           sa.func.count(sa.distinct(model_log.Logi.isikukood)))
                 .filter(model_log.Logi.tyyp==const.LOG_LOGIN)
                 .filter(model_log.Logi.aeg >= alates)
                 )
            if kuni1: 
                q = q.filter(model_log.Logi.aeg < kuni1)
            if groups:
                q = q.group_by(*groups)
            logins = {}
            users = {}
            for r in q.all():
                if c.step == STEP_TOTAL:
                    cnt1, cnt2 = r
                    sdt = TOTAL_KEY
                elif c.step in (STEP_DAY, STEP_7DAYS):
                    dt, cnt1, cnt2 = r
                    sdt = fkey(dt)
                else:
                    year, month, cnt1, cnt2 = r
                    sdt = fkey(year, month)
                logins[sdt] = cnt1
                users[sdt] = cnt2
            return logins, users

        def _get_pedagoogid(alates, kuni1):
            # õpetajate ja nende koolide arv
            groups = fgroups(model_log.Logi.aeg)            
            q = (model_log.DBSession.query(*groups,
                                           sa.func.count(sa.distinct(model_log.Logi.isikukood)),
                                           sa.func.count(sa.distinct(model_log.Logi.koht_id)))
                 .filter(model_log.Logi.tyyp.in_((const.LOG_LOGIN, const.LOG_KOHT)))
                 .filter(model_log.Logi.koht_id!=None)
                 .filter(model_log.Logi.aeg >= alates)
                 )
            if kuni1: 
                q = q.filter(model_log.Logi.aeg < kuni1)
            if groups:
                q = q.group_by(*groups)
            pedag = {}
            pedag_koolid = {}
            for r in q.all():
                if c.step == STEP_TOTAL:
                    cnt1, cnt2 = r
                    sdt = TOTAL_KEY
                elif c.step in (STEP_DAY, STEP_7DAYS):
                    dt, cnt1, cnt2 = r
                    sdt = fkey(dt)
                else:
                    year, month, cnt1, cnt2 = r
                    sdt = fkey(year, month)
                pedag[sdt] = cnt1
                pedag_koolid[sdt] = cnt2
            return pedag, pedag_koolid

        def _get_opilased(alates, kuni1):
            # õpilaste ja nende koolide arv
            groups = fgroups(model_log.Logi.aeg)                        
            q = (model_log.DBSession.query(*groups,
                                           sa.func.count(sa.distinct(model_log.Logi.isikukood)),
                                           sa.func.count(sa.distinct(model_log.Logi.oppekoht_id)))
                 .filter(model_log.Logi.tyyp==const.LOG_LOGIN)
                 .filter(model_log.Logi.oppekoht_id!=None)
                 .filter(model_log.Logi.aeg >= alates)
                 )
            if kuni1: 
                q = q.filter(model_log.Logi.aeg < kuni1)
            if groups:
                q = q.group_by(*groups)
            opil = {}
            opil_koolid = {}
            for r  in q.all():
                if c.step == STEP_TOTAL:
                    cnt1, cnt2 = r
                    sdt = TOTAL_KEY
                elif c.step in (STEP_DAY, STEP_7DAYS):
                    dt, cnt1, cnt2 = r
                    sdt = fkey(dt)
                else:
                    year, month, cnt1, cnt2 = r
                    sdt = fkey(year, month)
                opil[sdt] = cnt1
                opil_koolid[sdt] = cnt2
            return opil, opil_koolid

        class Prfcls:
            buf = '\n'
            def __init__(self):
                self.ts1 = round(datetime.now().timestamp() * 1000)
            def prf(self, label):
                self.ts2 = round(datetime.now().timestamp() * 1000)
                self.buf += '%s - %s\n' % (label, self.ts2-self.ts1)
                self.ts1 = self.ts2
        p = Prfcls()
        if c.b_kokku_sooritused:
            kokku_sooritused = _get_kokku_testisooritused(c.alates, kuni1)
        if c.b_e_sooritused:
            e_sooritused = _get_e_testisooritused(c.alates, kuni1)        
            p.prf('testisooritused')
        if c.b_toosooritused:
            toosooritused = _get_toosooritused(c.alates, kuni1)
            p.prf('toosooritused')
        if c.b_pankyl:
            pankyl = _get_pankyl(c.alates, kuni1)
            p.prf('pankyl')
        if c.b_tooyl:
            tooyl = _get_tooyl(c.alates, kuni1)
            p.prf('tooyl')
        if c.b_users:
            logins, users = _get_users(c.alates, kuni1)
            p.prf('users')
        if c.b_pedag:
            pedag, pedag_koolid = _get_pedagoogid(c.alates, kuni1)
            p.prf('pedag')
        if c.b_opil:
            opil, opil_koolid = _get_opilased(c.alates, kuni1)
            p.prf('opil')
        log.info(p.buf)
        
        days = [_("Esmaspäev"),
                _("Teisipäev"),
                _("Kolmapäev"),
                _("Neljapäev"),
                _("Reede"),
                _("Laupäev"),
                _("Pühapäev")]
        months = [_("Jaanuar"),
                  _("Veebruar"),
                  _("Märts"),
                  _("Aprill"),
                  _("Mai"),
                  _("Juuni"),
                  _("Juuli"),
                  _("August"),
                  _("September"),
                  _("Oktoober"),
                  _("November"),
                  _("Detsember")]
        rows = []
        dt = c.alates
        while dt <= kuni0:
            if c.step == STEP_TOTAL:
                key = TOTAL_KEY
                title1 = self.h.str_from_date(c.alates)
                title2 = self.h.str_from_date(kuni0)
            elif c.step == STEP_DAY:
                weekday = dt.weekday()
                key = fkey(dt)
                title1 = days[weekday]
                title2 = self.h.str_from_date(dt)
            elif c.step == STEP_7DAYS:
                week = int(model.Session.query(sa.func.date_part('week', dt)).scalar())
                key = fkey(week)
                title1 = str(dt.year)
                title2 = '%s - %s' % (h.str_from_date(dt),
                                      h.str_from_date(dt + timedelta(days=6)))
            else:
                key = fkey(dt.year, dt.month)
                title1 = str(dt.year)
                title2 = months[dt.month-1]
                if dt.day > 1:
                    title2 = title2 + ' (alates %s)' % h.str_from_date(dt)

            item = [dt,
                    title1,
                    title2]
            if c.b_users:
                item.append(logins.get(key))
                item.append(users.get(key))
            if c.b_kokku_sooritused:
                item.append(kokku_sooritused.get(key))
            if c.b_e_sooritused:
                item.append(e_sooritused.get(key))
            if c.b_toosooritused:
                item.append(toosooritused.get(key))
            if c.b_pankyl:
                item.append(pankyl.get(key))
            if c.b_tooyl:
                item.append(tooyl.get(key))
            if c.b_pedag:
                item.append(pedag.get(key))
                item.append(pedag_koolid.get(key))
            if c.b_opil:
                item.append(opil.get(key))
                item.append(opil_koolid.get(key))
                    
            rows.append(item)
            if c.step == STEP_TOTAL:
                break
            elif c.step == STEP_DAY:
                dt += timedelta(days=1)
            elif c.step == STEP_7DAYS:
                dt += timedelta(days=7)
            else:
                # leiame kuupäeva järgmisel kuul
                dt1 = date(dt.year, dt.month, 1) + timedelta(days=20)
                if dt1.month == dt.month:
                    dt1 = dt1 + timedelta(days=20)
                # leiame järgmise kuu esimese päeva
                dt = date(dt1.year, dt1.month, 1)
        c.prepare_header = self._prepare_header
        c.prepare_item = self._prepare_item
        if c.csv:
            # väljastame CSV
            return self._index_csv(rows)
        return rows

    def _paginate(self, q):
        return q

    def _prepare_header(self):
        c = self.c
        if c.step == STEP_TOTAL:
            header = [_("Alates"),_("Kuni")]
        elif c.step == STEP_MONTH:
            header = [_("Aasta"), _("Kuu")]
        elif c.step == STEP_7DAYS:
            header = [_("Aasta"), _("Ajavahemik")]
        else:
            header = [_("Nädalapäev"),
                      _("Kuupäev"),
                      ]
        if c.b_users:
            header.append(_("Sisselogimiste arv"))
            header.append(_("Erinevate sisseloginud kasutajate arv"))
        if c.b_kokku_sooritused:
            header.append(_("Testisoorituste arv (e-testid ja p-testid)"))
        if c.b_e_sooritused:
            header.append(_("Lahendatud e-testide arv"))
        if c.b_toosooritused:
            header.append(_("Lahendatud iseseisvate tööde arv"))
        if c.b_pankyl:
            header.append(_("Lahendatud e-ülesannete arv ülesandepangas"))
        if c.b_tooyl:
            header.append(_("Lahendatud e-ülesannete arv iseseisvate tööde koosseisus"))
        if c.b_pedag:
            header.append(_("Sisseloginud õpetajate arv"))
            header.append(_("Õpetajate koolide arv"))
        if c.b_opil:
            header.append(_("Sisseloginud õpilaste arv"))
            header.append(_("Õpilaste koolide arv"))
        return header

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        return rcd[1:]

    def _prepare_items(self, rows):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        header = self._prepare_header()
        items = [self._prepare_item(rcd, n) for n, rcd in enumerate(rows)]
        return header, items

    def _order(self, q, sort=None):
        return q
