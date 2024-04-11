# -*- coding: utf-8 -*- 
# $Id: osaoskused.py 544 2016-04-01 09:07:15Z ahti $

import pickle
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class OsaoskusedController(BaseResourceController):
    """Osaoskuste (alatestideta testiosade ja alatestide) võrdlus,
    mille tulemuste erinevus on suur (ühe isiku piires)
    """
    _permission = 'aruanded-osaoskused'
    _INDEX_TEMPLATE = 'ekk/statistika/osaoskused.mako'
    _LIST_TEMPLATE = 'ekk/statistika/osaoskused_list.mako'
    _DEFAULT_SORT = 'sooritaja.id'
    _ignore_default_params = ['csv']

    def _query(self):
        return 

    def _search(self, q1):

        # koostame valitud testi struktuurile vastava andmete väljastamise päringu

        if not self.c.test_id or not self.c.erinevus:
            if self.c.otsi:
                self.error(_("Palun valida test"))
            return 
        test = model.Test.get(self.c.test_id)

        join_tables = []
        headers = [('kasutaja.isikukood', _("Isikukood")),]
        select_fields = [model.Sooritaja.id, model.Kasutaja.isikukood, model.Kasutaja.synnikpv]

        n_sooritus = 0
        n_alatest = 0
        staatus_jrk = {}
        for testiosa in test.testiosad:
            n_sooritus += 1
            name = 'sooritus_%d' % n_sooritus
            Sooritus = sa.orm.aliased(model.Sooritus, name=name)
            join_tables.append((Sooritus,
                                sa.and_(Sooritus.testiosa_id==testiosa.id,
                                        Sooritus.sooritaja_id==model.Sooritaja.id)))

            if n_sooritus == 1:
                select_fields.append(Sooritus.algus)
                headers.append(('%s.algus' % name, _("Kuupäev")))

            select_fields.append(Sooritus.tahised)
            select_fields.append(Sooritus.staatus)
            testiosa_staatus_jrk = len(select_fields)

            headers.append(('%s.tahised' % name, _("Soorituse kood") + ' (%s)' % testiosa.nimi))            
            if testiosa.on_alatestid:
                for alatest in testiosa.alatestid:
                    n_alatest += 1
                    name = 'alatest_%d' % n_alatest
                    Alatestisooritus = sa.orm.aliased(model.Alatestisooritus, name=name)
                    join_tables.append((Alatestisooritus,
                                        sa.and_(Alatestisooritus.alatest_id==alatest.id,
                                                Alatestisooritus.sooritus_id==Sooritus.id)))
                    headers.append(('%s.pallid' % name, '%s' % alatest.nimi))                    
                    select_fields.append(Alatestisooritus.staatus)

                    # alatesti staatuse välja jrk nr-ile vastab alatesti väljade arv 2
                    staatus_jrk[len(select_fields)] = 2
                    select_fields.append(Alatestisooritus.pallid)
                    select_fields.append(Alatestisooritus.tulemus_protsent)
            else:
                headers.append(('%s.pallid' % name, '%s' % testiosa.nimi))
                select_fields.append(Sooritus.pallid)
                select_fields.append(Sooritus.tulemus_protsent)

            # staatuse välja jrk nr-ile vastab selle staatusega testiosa väljade arv
            staatus_jrk[testiosa_staatus_jrk] = len(select_fields) - testiosa_staatus_jrk
            
        if n_sooritus <= 1 and n_alatest <= 1:
            # test koosneb yhestainsast testiosast/alatestist
            # jätame alles ainult soorituse koodi
            select_fields = select_fields[:3]
            headers = headers[:1]
        
        headers.append(('sooritaja.pallid', _("Testi tulemus")))
        select_fields += [model.Sooritaja.pallid,
                          model.Sooritaja.tulemus_protsent]

        self.c.staatus_jrk = staatus_jrk
        self.c.headers = headers
        q = model.SessionR.query(*select_fields).\
            filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).\
            filter(model.Sooritaja.hindamine_staatus!=const.H_STAATUS_TOOPUUDU).\
            join(model.Sooritaja.kasutaja)
        if self.c.testimiskord_id:
            q = q.filter(model.Sooritaja.testimiskord_id==self.c.testimiskord_id)
        else:
            q = q.filter(model.Sooritaja.test_id==self.c.test_id)
        for join in join_tables:
            q = q.join(join)


        # koostame filtri, mis leiab need sooritajad, mille osade tulemuste erinevus on suur

        sql = """SELECT DISTINCT j.id 
         FROM sooritaja j
         JOIN v_alaosatulemused v1 ON v1.sooritaja_id=j.id
         JOIN v_alaosatulemused v2 ON v2.sooritaja_id=j.id
         WHERE ABS(v1.pallid-v2.pallid) >= :erinevus 
         AND v1.staatus=%s AND v2.staatus=%s""" % (const.S_STAATUS_TEHTUD, const.S_STAATUS_TEHTUD)
        params = {'erinevus': self.c.erinevus}    
        if self.c.testimiskord_id:
            sql += ' AND j.testimiskord_id=:testimiskord_id '
            params['testimiskord_id'] = self.c.testimiskord_id
        else:
            sql += ' AND j.test_id=:test_id '
            params['test_id'] = self.c.test_id
        li = model.SessionR.execute(sa.text(sql), params)
        q = q.filter(model.Sooritaja.id.in_([r[0] for r in li]))

        if self.c.csv:
            return self._index_csv(q)
        return q

    def _index_csv(self, q):
        c = self.c

        # tabeli päis
        names = [r[1] for r in self.c.headers]

        # tabeli sisu
        items = []
        for rcd in q.all():

            row = self._prepare_row(rcd)
            items.append(row)

        buf = ''
        for r in [names] + items:
            buf += ';'.join([str(v) for v in r]) + '\n'

        buf = utils.encode_ansi(buf)
        response = Response(buf) 
        response.content_type = 'text/csv'
        response.content_disposition = 'attachment;filename=osalemine.csv'
        return response

    def _prepare_row(self, rcd):
        "Tabeli ühe rea väljade kokkupanek"
        c = self.c
        h = self.h

        row = []
        n=2
        while n < len(rcd):
            if n == 2:
                r = rcd[1] or h.str_from_date(rcd[2]) # isikukood v synnikpv
            else:
                r = rcd[n] 
            n += 1
            if n not in c.staatus_jrk:
                if isinstance(r, float):
                    row.append(h.fstr(r,1))
                    n += 1
                elif n==4:
                    row.append(h.str_from_date(r))
                else:
                    row.append(r)

            elif r != const.S_STAATUS_TEHTUD:
                ignore = c.staatus_jrk[n] 
                colspan = int((ignore - len([k for k in range(n+1, n+ignore+1) if k in c.staatus_jrk]))/2)
                n += ignore
                row.extend([c.opt.S_STAATUS.get(r)]*colspan)
        return row

