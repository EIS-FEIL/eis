"""Tagasisidevormi diagramm
"""
from collections import defaultdict   
import sqlalchemy as sa
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.lib.block import _outer_xml

from .feedbackdgm import FeedbackDgm

log = logging.getLogger(__name__)
_ = i18n._

class FeedbackDgmGtbl(FeedbackDgm):
    "Õpilaste tulemuste tabel"
    is_html = True
    foot_msg = []
    
    def data_by_params(self, data):
        avg_row = data.get('avg_row') or []
        tcol = data.get('tcol')
        self.heading = data.get('heading')
        return self.data(tcol, avg_row)

    def data(self, tcol, avg_row):
        g_filter = self.stat.g_filter
        is_pdf = self.stat.is_pdf
        is_xls = self.stat.is_xls
        is_preview = self.handler.c.is_preview
        h = self.handler.h

        def applicable_columns(tcol, test, tk, v_avaldet):
            # jätame välja need veerud, mille andmed pole avaldatud            
            tcol2 = []
            for item in tcol:
                expr = item['expr']
                dpt = item['displaytype']
                cat, fld = expr.split('.', 1)
                if tk:
                    if cat == const.FBC_ALATEST and not \
                           (tk.alatestitulemused_avaldet \
                            or v_avaldet.alatestitulemused_avaldet):
                        log.debug('gtbl: ei kuva alatesti veergu, sest alatestitulemused avaldamata')
                        continue
                    elif cat == const.FBC_YLESANNE and not \
                             (tk.ylesandetulemused_avaldet \
                              or v_avaldet.ylesandetulemused_avaldet):
                        log.debug('gtbl: ei kuva ylesande veergu, sest ylesandetulemused avaldamata')
                        continue
                    elif cat == const.FBC_ASPEKT and not \
                             (tk.aspektitulemused_avaldet \
                              or v_avaldet.aspektitulemused_avaldet):
                        continue
                epallid = (const.FBC_ALATEST,
                           const.FBC_YLESANNE,
                           const.FBC_ASPEKT,
                           const.FBC_TESTIOSA,
                           const.FBC_TEST)
                if test.pallideta and dpt == const.FBD_TULEMUS and cat in epallid:
                    log.debug('gtbl: ei kuva palle, sest test on pallideta')
                    continue
                if test.protsendita and dpt in (const.FBD_PROTSENT, const.FBD_G_PROTSENT):
                    log.debug('gtbl: ei kuva protsente, sest test on protsentideta')
                    continue
                log.debug(f'gtbl: kuvatakse {item}')
                tcol2.append(item)
            return tcol2
                
        # jätame välja need veerud, mille andmed pole avaldatud
        test = self.stat.test
        tk = self.stat.testimiskord
        is_valim = self.stat.valimid_tk_id and True or False
        tcol = applicable_columns(tcol, test, tk, self.stat.v_avaldet)
        if not tcol:
            # pole veerge, mida saaks kuvada
            log.debug(f'gtbl: pole veerge, mida kuvada')
            return
        if const.FBR_SOORITAJA in avg_row:
            # lisada iga sooritaja kohta rida
            items = self._data_individual(tcol, is_valim)
        else:
            items = []

        # lisada keskmiste read
        total_items = self._data_group(tcol, avg_row, is_valim)
        items.extend(total_items)

        # tabeli päis
        header = [(None, _("Jrk nr")),
                  (None, _("Õpilane"))] + \
                  [(f'flt{ind}', r['name']) for (ind,r) in enumerate(tcol)]
        return header, items, tcol
    
    def _data_individual(self, tcol, is_valim):
        g_filter = self.stat.g_filter
        is_pdf = self.stat.is_pdf
        is_xls = self.stat.is_xls
        is_preview = self.handler.c.is_preview
        h = self.handler.h

        class TQuery:
            def __init__(self, valimis=None):
                # kas arvestada ainult valimi sooritusi
                self.valimis = valimis
                # tabelis kuvatavad väärtused
                self.values = {}
                
            # päringud kategooriate kaupa
            def query_testiosa(self, expr, osa_seq, dpt):
                q = (model.Session.query(model.Sooritus.sooritaja_id,
                                         model.Sooritus.pallid,
                                         model.Sooritus.tulemus_protsent,
                                         model.Sooritus.ajakulu)
                     .join(model.Sooritus.sooritaja)
                     .join(model.Sooritus.testiosa)
                     .filter(model.Testiosa.seq==osa_seq)
                     )
                q = g_filter(q, valimis=self.valimis, mittestat=True)
                for r in q.all():
                    j_id, pallid, prot, ajakulu = r
                    if dpt == const.FBD_AJAKULU:
                        value = h.strh_from_time(ajakulu)
                    elif dpt == const.FBD_TULEMUS:
                        value = pallid
                    else:
                        value = prot
                    self.values[j_id, expr, dpt] = value

            def query_alatest(self, expr, fid, dpt, kursus):
                osa_seq, alatest_seq = map(int, fid.split('_'))
                q = (model.Session.query(model.Sooritus.sooritaja_id,
                                         model.Alatestisooritus.pallid,
                                         model.Alatestisooritus.tulemus_protsent)
                     .join(model.Sooritus.sooritaja)
                     .join(model.Sooritus.testiosa)
                     .join((model.Alatestisooritus, model.Alatestisooritus.sooritus_id==model.Sooritus.id))
                     .join((model.Alatest, model.Alatest.id==model.Alatestisooritus.alatest_id))
                     .filter(model.Testiosa.seq==osa_seq)
                     .filter(model.Alatest.seq==alatest_seq)
                     )
                if kursus:
                    # alatest_seq on sama erinevatel kursustel
                    q = q.filter(model.Alatest.kursus_kood==kursus)                
                q = g_filter(q, valimis=self.valimis, mittestat=True)
                for r in q.all():
                    j_id, pallid, prot = r
                    if dpt == const.FBD_TULEMUS:
                        value = pallid
                    else:
                        value = prot
                    self.values[j_id, expr, dpt] = value
                
            def query_ylesanne(self, expr, fid, dpt):
                li = list(map(int, fid.split('_')))
                if len(li) == 3:
                    osa_seq, alatest_seq, ty_seq = li
                else:
                    osa_seq, ty_seq = li
                    alatest_seq = None

                if dpt == const.FBD_TULEMUS:
                    q = model.Session.query(model.Sooritus.sooritaja_id,
                                            model.Ylesandevastus.pallid,
                                            model.Ylesandevastus.toorpunktid)
                else:
                    q = model.Session.query(model.Sooritus.sooritaja_id,
                                            model.Ylesandevastus.pallid,
                                            model.Ylesandevastus.toorpunktid,
                                            model.Testiylesanne.max_pallid,
                                            model.Ylesanne.max_pallid)
                q = (q.join(model.Sooritus.sooritaja)
                     .join(model.Sooritus.testiosa)
                     .join((model.Ylesandevastus,
                            model.Ylesandevastus.sooritus_id==model.Sooritus.id))
                     .join((model.Testiylesanne,
                            model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
                     .filter(model.Testiosa.seq==osa_seq)
                     )
                if ty_seq == 'Q':
                    q = q.filter(model.Testiylesanne.liik==const.TY_LIIK_K)
                else:
                    q = (q.filter(model.Testiylesanne.seq==ty_seq)
                         .filter(model.Testiylesanne.alatest_seq==alatest_seq)
                         )
                if dpt != const.FBD_TULEMUS:
                    q = (q.join((model.Valitudylesanne,
                                 model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
                         .join(model.Valitudylesanne.ylesanne)
                         )
                q = g_filter(q, valimis=self.valimis, mittestat=True)

                for r in q.all():
                    value = None
                    if dpt == const.FBD_TULEMUS:
                        j_id, pallid, toorp = r
                        value = pallid
                    else:
                        j_id, pallid, toorp, ty_max_p, y_max_p = r
                        if ty_max_p is None:
                            max_p = y_max_p
                        else:
                            max_p = ty_max_p
                        if max_p and pallid is not None:
                            value = pallid * 100 / max_p
                    self.values[j_id, expr, dpt] = value

            def query_aspekt(self, expr, fid, dpt):
                li = fid.split('_')
                aspekt_kood = li.pop()
                li = list(map(int, li))
                if len(li) == 3:
                    osa_seq, alatest_seq, ty_seq = li
                else:
                    osa_seq, ty_seq = li
                    alatest_seq = None

                if dpt == const.FBD_TULEMUS:
                    # kui on vaja ainult palle
                    q = model.Session.query(model.Sooritus.sooritaja_id,
                                            model.Vastusaspekt.pallid,
                                            model.Vastusaspekt.toorpunktid)
                else:
                    # kui on vaja protsent arvutada
                    q = model.Session.query(model.Sooritus.sooritaja_id,
                                            model.Vastusaspekt.pallid,
                                            model.Vastusaspekt.toorpunktid,
                                            model.Hindamisaspekt.max_pallid)
                q = (q.join(model.Sooritus.sooritaja)
                     .join(model.Sooritus.testiosa)
                     .join((model.Ylesandevastus,
                            model.Sooritus.id==model.Ylesandevastus.sooritus_id))
                     .join((model.Testiylesanne,
                            model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
                     .join(model.Ylesandevastus.vastusaspektid)
                     .join(model.Vastusaspekt.hindamisaspekt)
                     .filter(model.Testiosa.seq==osa_seq)
                     .filter(model.Hindamisaspekt.aspekt_kood==aspekt_kood)
                     )
                if ty_seq == 'Q':
                    q = q.filter(model.Testiylesanne.liik==const.TY_LIIK_K)
                else:
                    q = (q.filter(model.Testiylesanne.seq==ty_seq)
                         .filter(model.Testiylesanne.alatest_seq==alatest_seq)
                         )
                q = g_filter(q, valimis=self.valimis, mittestat=True)

                for r in q.all():
                    value = None
                    if dpt == const.FBD_TULEMUS:
                        j_id, pallid, toorp = r
                        value = pallid
                    else:
                        j_id, pallid, toorp, max_p = r
                        if max_p and toorp is not None:
                            value = toorp * 100 / max_p
                    self.values[j_id, expr, dpt] = value

            def query_np(self, expr, np_kood, dpt):
                q = (model.Session.query(model.Sooritus.sooritaja_id,
                                         model.Npvastus.nvaartus,
                                         model.Npvastus.svaartus,
                                         model.Normipunkt.max_vaartus,
                                         model.Nptagasiside.tagasiside,
                                         model.Nptagasiside.op_tagasiside)
                     .join((model.Npvastus,
                            model.Npvastus.sooritus_id==model.Sooritus.id))
                     .join(model.Sooritus.sooritaja)
                     .join((model.Normipunkt,
                            model.Normipunkt.id==model.Npvastus.normipunkt_id))
                     .filter(model.Normipunkt.kood==np_kood)
                     .outerjoin((model.Nptagasiside,
                                 model.Nptagasiside.id==model.Npvastus.nptagasiside_id))
                     )
                q = g_filter(q, valimis=self.valimis, mittestat=True)
                for r in q.all():
                    value = None
                    j_id, nv, sv, max_nv, txt, op_txt = r
                    if dpt == const.FBD_TEKST:
                        value = op_txt or txt
                    elif dpt == const.FBD_TULEMUS:
                        if nv is None:
                            value = sv
                        else:
                            value = nv
                    else:
                        if max_nv and nv is not None:
                            value = nv * 100 / max_nv
                    self.values[j_id, expr, dpt] = value

            def get_row_data(self, tcol, li_tk_id, avaldet):
                "Kogutakse rea kõik väärtused"
                for item in tcol:
                    expr = item['expr']
                    dpt = item['displaytype']
                    cat, fld = expr.split('.', 1)

                    if cat == const.FBC_TESTIOSA:
                        self.query_testiosa(expr, fld, dpt)
                    elif cat == const.FBC_ALATEST:
                        if not li_tk_id or avaldet.alatestitulemused_avaldet:
                            self.query_alatest(expr, fld, dpt, kursus)
                    elif cat == const.FBC_YLESANNE:
                        if not li_tk_id or avaldet.ylesandetulemused_avaldet:
                            self.query_ylesanne(expr, fld, dpt)
                    elif cat == const.FBC_ASPEKT:
                        if not li_tk_id or avaldet.ylesandetulemused_avaldet:
                            self.query_aspekt(expr, fld, dpt)                            
                    elif cat == const.FBC_NP:
                        self.query_np(expr, fld, dpt)
                    elif cat != const.FBC_TEST:
                        # testi kogutulemus saadakse koos sooritajate loeteluga
                        raise Exception('tundmatu kategooria %s' % cat)
                return self.values

        def get_map_valim():
            "Leitakse valimi ja mittevalimi sooritajate vastavus"
            # eri testimiskordade kirjete seostamiseks leiame kasutaja_id
            q = model.Session.query(model.Sooritaja.kasutaja_id,
                                    model.Sooritaja.id)
            # siin arvestatakse ka mittearvestatavaid valimeid
            q = g_filter(q, valimis=True, mittestat=True)
            map_v1 = defaultdict(list)
            for k_id, j_id in q.all():
                map_v1[k_id].append(j_id)

            q = model.Session.query(model.Sooritaja.kasutaja_id,
                                    model.Sooritaja.id)
            q = g_filter(q, valimis=None)
            li = [(k_id, j_id) for (k_id, j_id) in q.all()]
            # map mittevalimi sooritaja.id > valimi sooritaja.id
            map_v = {j_id: map_v1.get(k_id) for (k_id, j_id) in li}
            return map_v

        def get_value_v(map_v, values_v, j_id, expr, dpt):
            "Leitakse kogutud andmetest valimi tulemus"
            li = []
            for j_v_id in map_v.get(j_id) or []:
                if expr == TEST_EXPR:
                    # testi kogutulemus
                    r = (model.Session.query(model.Sooritaja.pallid)
                         .filter_by(id=j_v_id)
                         .first())
                    value_v = r and r[0] or None
                else:
                    # ylesande või osa või alatesti tulemus
                    value_v = values_v.get((j_v_id, expr, dpt))
                if value_v is not None:
                    li.append(value_v)
            return li
            
        def format_value_v(value, li_value_v, is_xls):
            "Mitte-valimi väärtusele lisatakse valimi väärtus"
            is_diff = False
            li_diff = []
            if li_value_v:
                # valimi väärtused on olemas
                if value is None:
                    # mittevalimi tulemust ei olegi
                    value = li_value_v[0]
                # leiame erinevad valimi tulemused
                for value_v in li_value_v:
                    if value_v != value:
                        li_diff.append(fstr(value_v, 1))
            if value is None:
                value = ''
            else:
                value = fstr(value,1)
            if li_diff:
                # mitte-valimi ja valimi tulemused erinevad
                # mitte-valimi tulemuse järel sulgudes kuvatakse valimi tulemus
                is_diff = True
                value_v = ', '.join(li_diff)
                if is_xls:
                    value = '%s (%s)' % (value, value_v)
                else:
                    value = '%s <font class="v-mv-diff">(%s)</font>' % (value, value_v)
            return value, is_diff
        
        test = self.stat.test
        tk = self.stat.testimiskord
        kursus = self.stat.kursus
        
        # kogume kõik väärtused
        qry = TQuery(None)
        li_tk_id = tk and [tk.id] or []
        avaldet = self.stat.new_avaldet().from_tk(tk)
        values = qry.get_row_data(tcol, li_tk_id, avaldet)

        # kui valim on olemas, siis võrreldakse valimiga
        map_v = defaultdict(list)
        if is_valim:
            # kui peab valimiga võrdlema, siis kogume kõik valimi väärtused
            qry_v = TQuery(True) # sh mittestat
            values_v = qry_v.get_row_data(tcol, self.stat.valimid_tk_id, self.stat.v_avaldet)
            # valimi ja mittevalimi soorituste vastavus
            map_v = get_map_valim()
                
        # sooritajate loetelu ja kogutulemuse päring
        q = model.Session.query(model.Sooritaja.id,
                                model.Sooritaja.staatus,
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Sooritaja.klass,
                                model.Sooritaja.paralleel,
                                model.Sooritaja.pallid,
                                model.Sooritaja.tulemus_protsent,
                                model.Sooritaja.keeletase_kood)
        q = g_filter(q)
        q = q.order_by(model.Sooritaja.eesnimi, model.Sooritaja.perenimi)

        items = []
        TEST_EXPR = '%s.' % const.FBC_TEST
        for ind, r in enumerate(q.all()):
            j_id, st, eesnimi, perenimi, klass, paralleel, pallid, prot, tase = r
            nimi = f'{eesnimi} {perenimi}'
            if (st == const.S_STAATUS_TEHTUD) and tk and not is_pdf and not is_xls and not is_preview:
                if model.Sooritaja.has_permission_ts(j_id, tk):
                    # on individuaalse tagasiside vaatamise õigus
                    # (kooli admin või õpilase testi admin või õpilase aineõpetaja)
                    url = f"opetajatulemused/{j_id}/"
                    nimi = f'<a href="{url}">{nimi}</a>'
            row = [ind + 1, nimi]
            tr_cls = ''
            for item in tcol:
                expr = item['expr']
                dpt = item['displaytype']
                if expr == TEST_EXPR:
                    if dpt == const.FBD_TASE:
                        value = tase
                    elif dpt == const.FBD_TULEMUS:
                        value = pallid
                    else:
                        value = prot
                else:
                    value = values.get((j_id, expr, dpt))

                if is_valim and map_v and dpt == const.FBD_TULEMUS:
                    # kui on olemas vastavus valimi sooritustega
                    # ja tulemus kuvatakse pallides,
                    # siis võrdleme tulemust valimi tulemusega
                    li_value_v = get_value_v(map_v, values_v, j_id, expr, dpt)
                    value, is_diff = format_value_v(value, li_value_v, is_xls)
                    if is_diff:
                        # mitte-valimi ja valimi tulemuse erinemise korral kuvatakse rida punasel taustal
                        tr_cls = 'v-mv-diff'
                        msg = _("Sulgudes on Harno sisestatud punktid, kui need erinevad kooli sisestatud punktidest.")
                        self.foot_msg.append(msg)

                row.append(value)
            items.append((row, {'type': None, 'class': tr_cls}))

        return items
    
    def _data_group(self, tcol, avg_row, is_valim):
        "Kokku-ridade koostamine"
        h = self.handler.h
        stat = self.stat
        g_filter = self.stat.g_filter
        
        class GroupQuery:
            # päringud kategooriate kaupa grupi kohta

            def __init__(self, group_type, valimis):
                self.group_type = group_type
                self.valimis = valimis

            def is_any(self):
                "Kas leidub sooritajaid"
                q = model.Session.query(model.Sooritaja.id)
                q = g_filter(q, self.group_type, self.valimis)
                for r in q.limit(1):
                    return True
                return False
                
            def query_test(self, dpt):
                "Testi tulemuse leidmine"
                q = model.Session.query(sa.func.avg(model.Sooritaja.pallid),
                                        sa.func.avg(model.Sooritaja.tulemus_protsent)
                                        )
                q = g_filter(q, self.group_type, self.valimis)
                for r in q.all():
                    pallid, prot = r
                    if dpt == const.FBD_TASE:
                        # keskmist taset ei arvuta
                        value = None
                    elif dpt == const.FBD_TULEMUS:
                        value = pallid
                    else:
                        value = prot
                    return value
                
            def query_testiosa(self, expr, osa_seq, dpt):
                "Testiosa tulemuse leidmine"
                q = (model.Session.query(sa.func.avg(model.Sooritus.pallid),
                                         sa.func.avg(model.Sooritus.tulemus_protsent),
                                         sa.func.avg(model.Sooritus.ajakulu))
                     .join(model.Sooritus.sooritaja)
                     .join(model.Sooritus.testiosa)
                     .filter(model.Testiosa.seq==osa_seq)
                     )
                q = g_filter(q, self.group_type, self.valimis)
                for r in q.all():
                    pallid, prot, ajakulu = r
                    if dpt == const.FBD_AJAKULU:
                        value = h.strh_from_time(ajakulu)
                    elif dpt == const.FBD_TULEMUS:
                        value = pallid
                    else:
                        value = prot
                    return value

            def query_alatest(self, expr, fid, dpt, kursus):
                "Alatesti tulemuse leidmine"
                osa_seq, alatest_seq = map(int, fid.split('_'))
                q = (model.Session.query(sa.func.avg(model.Alatestisooritus.pallid),
                                         sa.func.avg(model.Alatestisooritus.tulemus_protsent))
                     .join(model.Sooritus.sooritaja)
                     .join(model.Sooritus.testiosa)
                     .join((model.Alatestisooritus, model.Alatestisooritus.sooritus_id==model.Sooritus.id))
                     .join((model.Alatest, model.Alatest.id==model.Alatestisooritus.alatest_id))
                     .filter(model.Testiosa.seq==osa_seq)
                     .filter(model.Alatest.seq==alatest_seq)
                     )
                if kursus:
                    # alatest_seq on sama erinevatel kursustel
                    q = q.filter(model.Alatest.kursus_kood==kursus)
                q = g_filter(q, self.group_type, self.valimis)
                for r in q.all():
                    pallid, prot = r
                    if dpt == const.FBD_TULEMUS:
                        value = pallid
                    else:
                        value = prot
                    return value

            def query_ylesanne(self, expr, fid, dpt):
                "Ülesande tulemuse leidmine"
                li = list(map(int, fid.split('_')))
                if len(li) == 3:
                    osa_seq, alatest_seq, ty_seq = li
                else:
                    osa_seq, ty_seq = li
                    alatest_seq = None

                if dpt == const.FBD_TULEMUS:
                    q = model.Session.query(sa.func.avg(model.Ylesandevastus.pallid),
                                            sa.func.avg(model.Ylesandevastus.toorpunktid))
                else:
                    q = model.Session.query(sa.func.avg(model.Ylesandevastus.pallid),
                                            sa.func.avg(model.Ylesandevastus.toorpunktid),
                                            sa.func.avg(model.Testiylesanne.max_pallid),
                                            sa.func.avg(model.Ylesanne.max_pallid))
                q = (q.join(model.Sooritus.sooritaja)
                     .join(model.Sooritus.testiosa)
                     .join((model.Ylesandevastus,
                            model.Ylesandevastus.sooritus_id==model.Sooritus.id))
                     .join((model.Testiylesanne,
                            model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
                     .filter(model.Testiosa.seq==osa_seq)
                     )
                if ty_seq == 'Q':
                    q = q.filter(model.Testiylesanne.liik==const.TY_LIIK_K)
                else:
                    q = (q.filter(model.Testiylesanne.seq==ty_seq)
                         .filter(model.Testiylesanne.alatest_seq==alatest_seq)
                         )                    
                if dpt != const.FBD_TULEMUS:
                    q = (q.join((model.Valitudylesanne,
                                 model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
                         .join(model.Valitudylesanne.ylesanne)
                         )
                q = g_filter(q, self.group_type, self.valimis)
                for r in q.all():
                    value = None
                    if dpt == const.FBD_TULEMUS:
                        pallid, toorp = r
                        value = pallid
                    else:
                        pallid, toorp, ty_max_p, y_max_p = r
                        if ty_max_p is None:
                            max_p = y_max_p
                        else:
                            max_p = ty_max_p
                        if max_p and pallid is not None:
                            value = pallid * 100 / max_p
                    return value

            def query_aspekt(self, expr, fid, dpt):
                "Ülesande hindamisaspekti tulemuse leidmine"
                li = fid.split('_')
                aspekt_kood = li.pop()
                li = list(map(int, li))
                if len(li) == 3:
                    osa_seq, alatest_seq, ty_seq = li
                else:
                    osa_seq, ty_seq = li
                    alatest_seq = None

                if dpt == const.FBD_TULEMUS:
                    q = model.Session.query(sa.func.avg(model.Vastusaspekt.pallid),
                                            sa.func.avg(model.Vastusaspekt.toorpunktid))
                else:
                    q = model.Session.query(sa.func.avg(model.Vastusaspekt.pallid),
                                            sa.func.avg(model.Vastusaspekt.toorpunktid),
                                            sa.func.avg(model.Hindamisaspekt.max_pallid))
                q = (q.join(model.Sooritus.sooritaja)
                     .join(model.Sooritus.testiosa)
                     .join((model.Ylesandevastus,
                            model.Ylesandevastus.sooritus_id==model.Sooritus.id))
                     .join((model.Testiylesanne,
                            model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
                     .join(model.Ylesandevastus.vastusaspektid)
                     .join(model.Vastusaspekt.hindamisaspekt)
                     .filter(model.Testiosa.seq==osa_seq)
                     .filter(model.Hindamisaspekt.aspekt_kood==aspekt_kood)
                     )
                if ty_seq == 'Q':
                    q = q.filter(model.Testiylesanne.liik==const.TY_LIIK_K)
                else:
                    q = (q.filter(model.Testiylesanne.seq==ty_seq)
                         .filter(model.Testiylesanne.alatest_seq==alatest_seq)
                         )                    
                q = g_filter(q, self.group_type, self.valimis)
                for r in q.all():
                    value = None
                    if dpt == const.FBD_TULEMUS:
                        pallid, toorp = r
                        value = pallid
                    else:
                        pallid, toorp, max_p = r
                        if max_p and toorp is not None:
                            value = toorp * 100 / max_p
                    return value

            def query_np(self, expr, np_kood, dpt):
                "Tagasiside tunnuse väärtuse leidmine"
                q = (model.Session.query(sa.func.avg(model.Npvastus.nvaartus),
                                         sa.func.max(model.Normipunkt.max_vaartus))
                     .join((model.Sooritus,
                            model.Sooritus.id==model.Npvastus.sooritus_id))
                     .join(model.Sooritus.sooritaja)
                     .join((model.Normipunkt,
                            model.Normipunkt.id==model.Npvastus.normipunkt_id))
                     .filter(model.Normipunkt.kood==np_kood)
                     )
                q = g_filter(q, self.group_type, self.valimis)
                for r in q.all():
                    value = None
                    nv, max_nv = r
                    if dpt == const.FBD_TULEMUS:
                        if nv is not None:
                            value = nv
                    else:
                        if max_nv and nv is not None:
                            # max_nv on decimal
                            value = nv * 100 / float(max_nv)
                    return value

        def get_kov_koolide_arv(valimis):
            "Leitakse, mitmest minu KOVi koolist testist osa võeti"
            q = model.Session.query(sa.func.count(model.Sooritaja.kool_koht_id.distinct()))
            q = g_filter(q, const.FBR_LINN, valimis)
            return q.scalar()
            
        kursus = self.stat.kursus
        TEST_EXPR = '%s.' % const.FBC_TEST

        def gen_row(group_type, label, valimis):
            # kui on protsentide rida, siis on kõik väljad protsentides
            is_pr_row = False
            if group_type == const.FBR_GRUPP_PR:
                group_type = const.FBR_GRUPP
                is_pr_row = True
            elif group_type == const.FBR_RIIK_PR:
                group_type = const.FBR_RIIK
                is_pr_row = True

            qry = GroupQuery(group_type, valimis)
            if valimis and self.stat.valimid_tk_id:
                li_tk_id = self.stat.valimid_tk_id
                avaldet = self.stat.v_avaldet
            elif self.stat.testimiskord:
                li_tk_id = [self.stat.testimiskord.id]
                avaldet = self.stat.new_avaldet().from_tk(self.stat.testimiskord)
            else:
                li_tk_id = []
                avaldet = self.stat.new_avaldet()

            row = ['', label]
            is_any = False
            for item in tcol:
                value = None
                expr = item['expr']
                dpt = item['displaytype']
                if is_pr_row and dpt == const.FBD_TULEMUS:
                    # kogu rida on protsentides
                    dpt = const.FBD_PROTSENT
                if expr == TEST_EXPR:
                    # kogu testi tulemus
                    if not li_tk_id or avaldet.koondtulemus_avaldet:
                        value = qry.query_test(dpt)
                else:
                    cat, fld = expr.split('.', 1)
                    if cat == const.FBC_TESTIOSA:
                        if not li_tk_id or avaldet.koondtulemus_avaldet:                        
                            value = qry.query_testiosa(expr, fld, dpt)
                    elif cat == const.FBC_ALATEST:
                        if not li_tk_id or avaldet.alatestitulemused_avaldet:
                            value = qry.query_alatest(expr, fld, dpt, kursus)
                    elif cat == const.FBC_YLESANNE:
                        if not li_tk_id or avaldet.ylesandetulemused_avaldet:
                            value = qry.query_ylesanne(expr, fld, dpt)
                    elif cat == const.FBC_ASPEKT:
                        if not li_tk_id or avaldet.ylesandetulemused_avaldet:
                            value = qry.query_aspekt(expr, fld, dpt)
                    elif cat == const.FBC_NP:
                        if not li_tk_id or avaldet.koondtulemus_avaldet:                        
                            value = qry.query_np(expr, fld, dpt)
                row.append(value)
                if value is not None:
                    is_any = True
            if is_any:
                return row

        koht_id = stat.kool_koht_id or stat.kand_koht_id
        koht = koht_id and model.Koht.get(koht_id)
        aadress = koht and koht.aadress
        stat.maakond_kood = aadress and aadress.kood1
        stat.linn_kood = aadress and aadress.kood2
        
        valim_types = (const.FBR_LINN, const.FBR_MAAKOND, const.FBR_RIIK, const.FBR_RIIK_PR)
        items = []
        for group_type in (avg_row or []):
            valimis = is_valim and group_type in valim_types
            label = ''
            if group_type == const.FBR_GRUPP:
                label = _("Grupi keskmine")
            elif group_type == const.FBR_GRUPP_PR:
                label = _("Grupi keskmine %")
            elif group_type == const.FBR_KOOL:
                label = koht and koht.nimi
            elif group_type == const.FBR_LINN:
                if aadress:
                    n = get_kov_koolide_arv(valimis)
                    # KOV rida kuvada ainult juhul, kui KOVis
                    # võttis testist osa enam kui 2 kooli
                    if n > 2:
                        label = aadress.vald
                    msg = _("Kohaliku omavalitsuse koondrida kuvatakse tabelis juhul, kui test sooritati vähemalt kolmes selle omavalitsuse koolis.")
                    self.foot_msg.append(msg)
                    
            elif group_type == const.FBR_MAAKOND:
                if aadress:
                    label = aadress.maakond
            elif group_type == const.FBR_RIIK:
                label = _("Eesti kokku")
            elif group_type == const.FBR_RIIK_PR:
                label = _("Eesti kokku %")                

            if label:
                if valimis:
                    label += " (%s)" % _("valim")
                row = gen_row(group_type, label, valimis)
                if row:
                    items.append((row, {'type': group_type}))
        return items
    
    def draw_html(self, data, fbd_id, body_only=False):
        header, items, tcol = data

        # filtrist jätame välja esimesed 2 veergu (jrk nr ja õpilase nimi)
        flt_header = [('',''),('','')] + header[2:]
        div_filter = self.tbl_col_filter(flt_header)
        div_body = self.draw_html_body(header, items, tcol)
        if self.heading:
            el_heading = f'<h3>{self.heading}</h3>'
        else:
            el_heading = ''
        buf = f'<div class="fbtbl fbtbl-gtbl" id="{fbd_id}">' +\
              el_heading +\
              div_filter + \
              '<div style="overflow-x:auto;position:relative;" class="fbtbl-body">' +\
              div_body +\
              '</div></div>'
        return buf
    
    def draw_html_body(self, header, items, tcol):
        h = self.handler.h
        fstr = h.fstr
        def fstrpr(value):
            if value is not None:
                return fstr(value, 0) + '%'

        buf = '<table class="table table-striped tablesorter">' +\
              '<thead><tr>'
        for ind, (key, name) in enumerate(header):
            buf += f'<th class="fbcol-{key}">{name}</th>'

        n_prot = [n for (n,v) in enumerate(tcol) if v['displaytype'] == const.FBD_PROTSENT]
        n_g_prot = [n for (n,v) in enumerate(tcol) if v['displaytype'] == const.FBD_G_PROTSENT]

        buf += '</tr></thead>\n<tbody>'

        # eristame õpilaste read ja kokku-read
        tbody_items = []
        tfoot_items = []
        for row, attrs in items:
            group_type = attrs.get('type')
            if group_type:
                tfoot_items.append((row, attrs))
            else:
                tbody_items.append((row, attrs))

        # õpilaste read
        for row, attrs in tbody_items:
            tr_cls = attrs.get('class') or ''
            buf += f'<tr class="{tr_cls}">'
            for ind, value in enumerate(row):
                cl = ''
                key = header[ind][0]
                if key:
                    cl = f'fbcol-{key}'
                # arvestame jrk nr ja nime veerge
                n = ind - 2
                if n in n_g_prot:
                    cl += ' pc-circle'
                    value = fstrpr(value)
                elif n in n_prot:
                    value = fstrpr(value)
                if isinstance(value, float):
                    value = fstr(value,1)
                if value is None:
                    value = ''
                buf += '<td class="%s">%s</td>' % (cl, value)
            buf += '</tr>\n'

        buf += '</tbody><tfoot>\n'

        # read, millel kõik tulemused on protsentides
        PR_ROWS = (const.FBR_GRUPP_PR, const.FBR_RIIK_PR)

        # kokku-read
        for row, attrs in tfoot_items:
            group_type = attrs.get('type')
            buf += '<tr class="total-row">'
            for ind, value in enumerate(row):
                key = header[ind][0]
                cl = f'fbcol-{key}'
                # arvestame jrk nr ja nime veerge
                n = ind - 2
                if n in n_g_prot:
                    cl += ' pc-circle'
                    value = fstrpr(value)
                elif n in n_prot:
                    value = fstrpr(value)
                elif group_type in PR_ROWS and isinstance(value, (float,int)):
                    # tulemuse veerg protsentide real
                    #cl += ' pc-circle'
                    value = fstrpr(value)                    

                if isinstance(value, float):
                    value = fstr(value,1)
                if value is None:
                    value = ''
                buf += '<td class="%s">%s</td>' % (cl, value)
                    
            buf += '</tr>\n'
        buf += '</tfoot></table>'

        # märkus
        if self.foot_msg:
            for msg in set(self.foot_msg):
                buf += '<div>' + msg + '</div>'
        return buf
    
    @classmethod
    def get_opt_expr(cls, handler, test, kursus):
        "Tabeli veergude allikate valik"
        def add_p(label, max_pallid):
            if not test.pallideta and max_pallid:
                label += ' (%sp)' % fstr(max_pallid, 1)
            return label

        def add_asp(key, label, ty):
            "Aspektide leidmine"
            li = []
            # leiame ylesande aspektid
            q = (model.Session.query(model.Hindamisaspekt.aspekt_kood,
                                     model.Hindamisaspekt.aine_kood,
                                     model.Hindamisaspekt.max_pallid)
                 .join((model.Valitudylesanne,
                        model.Valitudylesanne.ylesanne_id==model.Hindamisaspekt.ylesanne_id))
                 .filter(model.Valitudylesanne.testiylesanne_id==ty.id)
                 .order_by(model.Hindamisaspekt.seq))
            # eemaldame korduvad ja leiame aspekti nimetuse
            aspektid = []
            for aspekt_kood, aine_kood, ha_max_p in q.all():
                if (aspekt_kood, aine_kood) not in aspektid:
                    aspektid.append((aspekt_kood, aine_kood))
                    ha_key = f'{const.FBC_ASPEKT}.{key}_{aspekt_kood}'
                    ha_label = label + ' ' + model.Klrida.get_str('ASPEKT', aspekt_kood, aine_kood) or aspekt_kood
                    ha_label = add_p(ha_label, ha_max_p)
                    li.append((ha_key, ha_label))
            return li

        def add_ty(tykood, ty):
            li = []
            key = f'{const.FBC_YLESANNE}.{tykood}'
            label = '%s %s' % (_("Ül"), ty.tahis or '')
            label_ty = add_p(label, ty.max_pallid)
            # lisame ylesande veeru
            li.append((key, label_ty))
            # lisame ylesande aspektide veerud
            li.extend(add_asp(tykood, label, ty))                    
            return li
        
        key = '%s.' % (const.FBC_TEST)
        label = _("Testi tulemus")
        label = add_p(label, test.max_pallid)
        li = [(key, _("Testi tulemus"))]
        for osa in test.testiosad:
            key = '%s.%d' % (const.FBC_TESTIOSA, osa.seq)
            label = '%s: %s' % (_("Testiosa"), osa.nimi)
            label = add_p(label, osa.max_pallid)
            li.append((key, label))
            alatestid = list(osa.alatestid)
            for alatest in alatestid:
                if kursus and alatest.kursus_kood != kursus:
                    continue
                alatest_li = []
                for ty in alatest.testiylesanded:
                    if ty.liik == const.TY_LIIK_Y:
                        tykood = f'{osa.seq}_{ty.alatest_seq}_{ty.seq}'
                        alatest_li.extend(add_ty(tykood, ty))
                    else:
                        continue

                if alatest_li:
                    # kui alatestil on ülesandeid
                    key = f'{const.FBC_ALATEST}.{osa.seq}_{alatest.seq}'
                    label = '%s: %s' % (_("Alatest"), alatest.nimi)
                    label = add_p(label, alatest.max_pallid)
                    li.append((key, label))
                    li.extend(alatest_li)

            if not alatestid:
                for ty in osa.testiylesanded:
                    if ty.liik == const.TY_LIIK_Y:
                        tykood = f'{osa.seq}_{ty.seq}'
                        li.extend(add_ty(tykood, ty))
                    else:
                        continue

            for np in osa.normipunktid:
                key = '%s.%s' % (const.FBC_NP, np.kood)
                label = '%s: %s' % (_("Tagasiside tunnus"), np.kood)
                li.append((key, label))
        return li
