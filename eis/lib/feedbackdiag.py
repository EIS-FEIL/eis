"Koolipsühholoogi testi tulemuste tagasiside"
import pickle
from itertools import groupby
import random
from eis.lib.base import *
_ = i18n._

class FeedbackDiag:
    _STUDENT_TEMPLATE = '/avalik/tagasiside/sooritustagasiside.diag2.mako'
    _GROUP_TEMPLATE = '/avalik/tagasiside/grupptagasiside.diag2.mako'

    def __init__(self, handler):
        self.handler = handler
        self.h = handler.h
        self.request = handler.request
        self.lang = handler.c.lang
        
    def gen_opilane(self, sooritaja):
        "Õpilase tagasiside genereerimine"
        template = self._STUDENT_TEMPLATE
        c = self.handler.c
        c.sooritaja = sooritaja
        c.pickle_dumps = lambda data: pickle.dumps(data, 0).hex()
        test = sooritaja.test
        sooritus = list(sooritaja.sooritused)[0]
        lang = sooritaja.lang
        tts = test.testitagasiside
        c.diag_data = self._gen_opilane_data(tts, sooritus, lang)
        data = self.handler.render(template)
        return data

    def _gen_opilane_data(self, tts, sooritus, lang):
        testiosa = sooritus.testiosa
        nslist = [] 
        nvlist = []
        
        nv_by_np = {}
        for npv in sooritus.npvastused:
            if npv.normipunkt_id not in nv_by_np:
                nv_by_np[npv.normipunkt_id] = [npv]
            else:
                nv_by_np[npv.normipunkt_id].append(npv)

        # järjestame tagasiside normipunktide kirjeldamise järjekorras    
        for np in testiosa.normipunktid:
            for npv in nv_by_np.get(np.id) or []:
                #log.debug('  npv %s' % npv.id)
                ns = npv.nptagasiside
                if ns:
                    txt = ns.tran(lang).tagasiside
                    if txt:
                        # tagasiside teksti on olemas
                        if np.ylesandegrupp_id:
                            nslist.append((txt, np.ylesandegrupp_id, ns.nsgrupp_id))
                        elif tts and tts.ylgrupp_kuva and np.testiylesanne_id:
                            for vy in np.testiylesanne.valitudylesanded:
                                for gy in vy.grupiylesanded:
                                    nslist.append((txt, gy.ylesandegrupp_id, ns.nsgrupp_id))
                        else:
                            nslist.append((txt, None, ns.nsgrupp_id))

        data = self._gen_opilane_display(tts, testiosa, nslist, lang)
        return data
    
    def _gen_opilane_display(self, tts, testiosa, nslist, lang):

        class CellD:
            is_celld = True
            is_cellh = False
            
            def __init__(self, value):
                self.value = value

            def __repr__(self):
                return 'CellD(%s)' % self.value
            
        class CellH:
            is_cellh = True
            is_celld = False

            def __init__(self, value):
                self.value = value        

            def __repr__(self):
                return 'CellH(%s)' % self.value
            
        def _nslist_to_txt(tts, nslist):
            if not nslist:
                buf = ''
            elif tts and tts.ts_loetelu:
                buf = '<ul>' + '\n'.join(['<li class="body16">' + r[0] + '</li>' for r in nslist]) + '</ul>'
            else:
                buf = '<br/>\n'.join([r[0] for r in nslist])
            return buf

        nsgrupid = list(testiosa.nsgrupid)
        # vaikimisi on yl-grupid järjestatud gruppide kirjeldamise järjekorras
        ylgrupid = list(testiosa.ylesandegrupid)
        data = []
        
        if not tts or tts.ylgrupp_kuva == const.KUVA_EI:
            row = []
            if not tts or tts.nsgrupp_kuva == const.KUVA_EI:
                row.append(CellD(_nslist_to_txt(tts, nslist)))
            elif tts.nsgrupp_kuva == const.KUVA_VER:
                data2 = []
                for grupp2 in nsgrupid:
                    nslist2 = [r for r in nslist if r[2] == grupp2.id]
                    row2 = []
                    if tts.nsgrupp_nimega:
                        row2.append(CellH(grupp2.tran(lang).nimi))
                    row2.append(CellD(_nslist_to_txt(tts, nslist2)))
                    data2.append(row2)
                row.append(data2)
            elif tts.nsgrupp_kuva == const.KUVA_HOR:
                if tts.nsgrupp_nimega:
                    row = []
                    for grupp2 in nsgrupid:
                        row.append(CellD(grupp2.tran(lang).nimi))
                    data.append(row)
                row = []
                for grupp2 in nsgrupid:
                    nslist2 = [r for r in nslist if r[2] == grupp2.id]
                    row.append(CellD(_nslist_to_txt(tts, nslist2)))
            data.append(row)
            
        elif tts.ylgrupp_kuva == const.KUVA_VER and tts.nsgrupp_kuva == const.KUVA_EI:
            data = []
            for grupp in ylgrupid:
                nslist1 = [r for r in nslist if r[1] == grupp.id]
                if nslist1:
                    row = []
                    if tts.ylgrupp_nimega:
                        row.append(CellH(grupp.tran(lang).nimi))
                    row.append(CellD(_nslist_to_txt(tts, nslist1)))
                    data.append(row)

        elif tts.ylgrupp_kuva == const.KUVA_VER and tts.nsgrupp_kuva == const.KUVA_VER:
            data = []
            for grupp in ylgrupid:
                nslist1 = [r for r in nslist if r[1] == grupp.id]
                if nslist1:
                    row = []
                    if tts.ylgrupp_nimega:
                        row.append(CellH(grupp.tran(lang).nimi))
                    data2 = []
                    for grupp2 in nsgrupid:
                        nslist2 = [r for r in nslist1 if r[2] == grupp2.id]
                        row2 = []
                        if tts.nsgrupp_nimega:
                            row2.append(CellH(grupp2.tran(lang).nimi))
                        row2.append(CellD(_nslist_to_txt(tts, nslist2)))
                        data2.append(row2)
                    row.append(data2)
                    data.append(row)

        elif tts.ylgrupp_kuva == const.KUVA_VER and tts.nsgrupp_kuva == const.KUVA_HOR:
            data = []
            if tts.nsgrupp_nimega:
                row = []
                if tts.ylgrupp_nimega:
                    row.append(CellH(''))
                for grupp2 in nsgrupid:
                    row.append(CellH(grupp2.tran(lang).nimi))
                data.append(row)

            for grupp in ylgrupid:
                nslist1 = [r for r in nslist if r[1] == grupp.id]
                if nslist1:
                    row = []
                    if tts.ylgrupp_nimega:
                        row.append(CellH(grupp.tran(lang).nimi))

                    for grupp2 in nsgrupid:
                        nslist2 = [r for r in nslist1 if r[2] == grupp2.id]
                        row.append(CellD(_nslist_to_txt(tts, nslist2)))
                    data.append(row)

        elif tts.ylgrupp_kuva == const.KUVA_HOR and tts.nsgrupp_kuva == const.KUVA_VER:
            data = []
            if tts.ylgrupp_nimega:
                row = []
                if tts.nsgrupp_nimega:
                    row.append(CellH(''))
                for grupp2 in ylgrupid:
                    row.append(CellH(grupp2.tran(lang).nimi))
                data.append(row)

            for grupp in nsgrupid:
                nslist1 = [r for r in nslist if r[2] == grupp.id]
                if nslist1:
                    row = []
                    if tts.nsgrupp_nimega:
                        row.append(CellH(grupp.tran(lang).nimi))

                    for grupp2 in ylgrupid:
                        nslist2 = [r for r in nslist1 if r[1] == grupp2.id]
                        row.append(CellD(_nslist_to_txt(tts, nslist2)))
                    data.append(row)

        elif tts.ylgrupp_kuva == const.KUVA_HOR and (tts.nsgrupp_kuva == const.KUVA_EI or \
                                                     tts.nsgrupp_kuva == const.KUVA_HOR):
            # see on nsgrupp_kuva == KUVA_EI jaoks
            # KUVA_HOR jaoks ei ole tehtud
            data = []
            for grupp in nsgrupid:
                nslist1 = [r for r in nslist if r[2] == grupp.id]
                if nslist1:
                    row = []
                    if tts.nsgrupp_nimega:
                        row.append(CellH(grupp.tran(lang).nimi))
                    row.append(CellD(_nslist_to_txt(tts, nslist1)))
                    data.append(row)

        return data
    
    def gen_grupp(self, tts, stat):
        "Grupi tagasiside genereerimine"
        template = self._GROUP_TEMPLATE
        c = self.handler.c
        c.tts = tts
        c.test = stat.test
        if c.ekk_preview_rnd:
            # juhuslikult genereeritav eelvaade (tagasiside koostajale)
            c.cnt_pooleli = random.randint(1, 8)
            c.cnt_alustamata = random.randint(1, 8)
            c.millal = self.h.str_from_date(date.today())

            # testiosade keskmine ajakulu
            sum_ajakulu = 0
            if c.test.ajakulu_naitamine in (const.AJAKULU_OSA, const.AJAKULU_KOIK):
                c.avg_osa_ajakulu = []
                for osa in c.test.testiosad:
                    ajakulu = random.randint(4, 60)
                    sum_ajakulu += ajakulu
                    c.avg_osa_ajakulu.append((osa.nimi, ajakulu))

            # testi keskmine ajakulu
            if c.test.ajakulu_naitamine in (const.AJAKULU_TEST, const.AJAKULU_KOIK):
                c.avg_ajakulu = sum_ajakulu or random.randint(4,70)

            c.cnt_tehtud = random.randint(8,20)
        else:
            # tagasiside tegelike andmete põhjal
            q = model.SessionR.query(model.Sooritaja)
            q = self._group_filter(q, stat)
            if not stat.valimis:
                c.sooritajad = q.order_by(model.Sooritaja.eesnimi, model.Sooritaja.perenimi).all()

            c.cnt_tehtud = q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).count()
            c.cnt_pooleli = q.filter(model.Sooritaja.staatus==const.S_STAATUS_POOLELI).count()
            c.cnt_alustamata = q.filter(model.Sooritaja.staatus.in_(
                (const.S_STAATUS_ALUSTAMATA, const.S_STAATUS_REGATUD))
                                        ).count()
            q = q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
            
            # sooritamise kuupäev
            algus, lopp = (q.with_entities(sa.func.min(model.Sooritaja.algus),
                                           sa.func.max(model.Sooritaja.algus))
                           .first())
            if algus and lopp:
                s_algus = self.h.str_from_date(algus)
                s_lopp = self.h.str_from_date(lopp)
                if s_algus != s_lopp:
                    c.millal = '%s-%s' % (s_algus, s_lopp)
                else:
                    c.millal = s_algus

            # testi keskmine ajakulu
            if c.test.ajakulu_naitamine in (const.AJAKULU_TEST, const.AJAKULU_KOIK):
                q = q.with_entities(sa.func.avg(model.Sooritaja.ajakulu))
                avg_ajakulu = q.scalar()
                if avg_ajakulu is not None:
                    c.avg_ajakulu = int(round(float(avg_ajakulu) / 60.))

            # testiosade keskmine ajakulu
            if c.test.ajakulu_naitamine in (const.AJAKULU_OSA, const.AJAKULU_KOIK):
                c.avg_osa_ajakulu = []
                for osa in c.test.testiosad:
                    if osa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
                        q1 = (q.with_entities(sa.func.avg(model.Sooritus.ajakulu))
                             .join(model.Sooritaja.sooritused)
                             .filter(model.Sooritus.testiosa_id==osa.id)
                             )
                        avg_ajakulu = q1.scalar()
                        if avg_ajakulu is not None:
                           ajakulu = int(round(float(avg_ajakulu) / 60.))
                           c.avg_osa_ajakulu.append((osa.nimi, ajakulu))

        # kogutakse andmebaasist päris andmed
        items_tbl = self.diag_group_items_tbl(tts, stat)

        # grupeerime tabeli read ylesandegrupi id järgi (esimene element tuples)
        c.items_tbl = []
        for ylgrupp_id, li_yg in groupby(items_tbl, lambda r: r[0]):
            yg_items = []
            yg_cnt = 0
            # ylesandegrupi sees grupeerime read nsgrupi järgi (teine element)
            for nsgrupp_id, li_ng in groupby(li_yg, lambda r: r[1]):
                rows = list(li_ng)
                ng_cnt = len(rows)
                yg_items.append((nsgrupp_id, ng_cnt, rows))
                yg_cnt += ng_cnt
            c.items_tbl.append((ylgrupp_id, yg_cnt, yg_items))

        data = self.handler.render(template)            
        return data

    def gen_valim(self, tts, stat):
        "Valimi tagasiside kuvamine"
        self.handler.c.stat_valimis = True
        return self.gen_grupp(tts, stat)
        
    def gen_riiklik(self, tts, stat):
        "Riikliku tagasiside kuvamine"
        self.handler.c.stat_riiklik = True
        return self.gen_grupp(tts, stat)
        
    def diag_group_items_tbl(self, tts, stat):
        "Tagasiside tekstide tabel bugzilla 624 formaadis"
        c = self.handler.c
        c.level_YG = c.level_NG = False
        items = []
        c.test = stat.test
        q = (model.SessionR.query(model.Ylesandegrupp.id,
                                 model.Nsgrupp.id,
                                 model.Nptagasiside)
             .filter(model.Nptagasiside.op_tagasiside!=None)
             .filter(model.Nptagasiside.op_tagasiside!='')
             .join(model.Nptagasiside.normipunkt)
             .join(model.Normipunkt.testiosa)
             .filter(model.Testiosa.test_id==c.test.id)
             )
        li_sort = []

        if tts and tts.ylgrupp_kuva and tts.ylgrupp_nimega:
            # leiame ylesandegrupid
            c.level_YG = True
            q = q.join((model.Ylesandegrupp,
                        sa.or_(model.Normipunkt.ylesandegrupp_id==model.Ylesandegrupp.id,
                               sa.exists().where(
                                   sa.and_(
                                       model.Normipunkt.testiylesanne_id==model.Valitudylesanne.testiylesanne_id,
                                       model.Valitudylesanne.id==model.Grupiylesanne.valitudylesanne_id,
                                       model.Grupiylesanne.ylesandegrupp_id==model.Ylesandegrupp.id))
                               )
                        ))
            li_sort.append(model.Ylesandegrupp.seq)
        else:
            q = q.outerjoin(model.Normipunkt.ylesandegrupp)

        if tts and tts.nsgrupp_kuva and tts.nsgrupp_nimega:
            # leiame tagasisidegrupid
            c.level_NG = True
            q = q.join(model.Nptagasiside.nsgrupp)
            li_sort.append(model.Nsgrupp.seq)
        else:
            q = q.outerjoin(model.Nptagasiside.nsgrupp)

        li_sort.extend([model.Normipunkt.seq, model.Nptagasiside.seq])
        q = q.order_by(*li_sort)

        for ylgrupp_id, nsgrupp_id, npts in q.all():
            txt = npts.tran(self.lang).op_tagasiside or npts.op_tagasiside
            if c.ekk_preview_rnd:
                # eelvaade juhuslike andmetega
                # sooritajate arv
                cnt_m = random.randint(0,5)
                cnt_n = random.randint(0,5)
                cnt = cnt_m + cnt_n
                # sooritajate loetelu
                if c.stat_valimis or c.stat_riiklik:
                    sooritajad = []
                else:
                    sooritajad = [(_("Eesnimi"), _("Perekonnanimi"), 0, 0, None, None)] * cnt
            else:
                # päris soorituste andmed
                if c.stat_valimis or c.stat_riiklik:
                    # valimi tagasisidesse leiame ainult sooritajate arvu
                    selects = [sa.func.count(model.Sooritaja.id)]
                else:
                    # grupi tagasisidesse leiame sooritajate loetelu
                    selects = [model.Sooritaja.eesnimi,
                               model.Sooritaja.perenimi,
                               model.Sooritaja.id,
                               model.Sooritus.id,
                               model.Sooritaja.testimiskord_id,
                               model.Sooritaja.kursus_kood]
                if tts and tts.ts_sugu:
                    selects.append(model.Kasutaja.sugu)
                q1 = (model.SessionR.query(*selects)
                      .join(model.Sooritaja.sooritused)
                      .join((model.Npvastus, model.Npvastus.sooritus_id==model.Sooritus.id))
                      .filter(model.Npvastus.nptagasiside_id==npts.id)
                      .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
                      .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)              
                      )
                q1 = self._group_filter(q1, stat)

                if tts and tts.ts_sugu:
                    q1 = q1.join(model.Sooritaja.kasutaja)
                if c.stat_valimis or c.stat_riiklik:
                    sooritajad = []
                    if tts and tts.ts_sugu:
                        # valimi tagasisidesse leiame sooritajate arvu soo kaupa
                        cnt_m = cnt_n = 0
                        for _cnt, sugu in q1.group_by(model.Kasutaja.sugu).all():
                            if sugu == const.SUGU_M:
                                cnt_m = _cnt
                            else:
                                cnt_n = _cnt
                        cnt = cnt_m + cnt_n
                    else:
                        # valimi tagasisidesse leiame ainult sooritajate arvu
                        cnt = q1.scalar()
                        cnt_m = cnt_n = None
                else:
                    # grupi tagasisidesse leiame sooritajate loetelu
                    q1 = q1.order_by(model.Sooritaja.eesnimi, model.Sooritaja.perenimi)
                    sooritajad = list(q1.all())
                    if tts and tts.ts_sugu:
                        cnt = cnt_m = cnt_n = 0
                        for r in sooritajad:
                            if r[6] == const.SUGU_M:
                                cnt_m += 1
                            else:
                                cnt_n += 1
                        cnt = cnt_m + cnt_n
                    else:
                        cnt = len(sooritajad)
                        cnt_m = cnt_n = None
            np = npts.normipunkt
            if not c.level_YG:
                ylgrupp_id = None
            if not c.level_NG:
                nsgrupp_id = None
            item = (ylgrupp_id, nsgrupp_id, np, txt, cnt, cnt_m, cnt_n, sooritajad)
            items.append(item)
        return items

    def _group_filter(self, q, stat):
        if stat.kool_koht_id:
            q = q.filter(model.Sooritaja.kool_koht_id==stat.kool_koht_id)
        if stat.kand_koht_id:
            q = q.filter(model.Sooritaja.kandideerimiskohad.any(
                model.Kandideerimiskoht.koht_id==stat.kool_koht_id))
        if stat.valimis:
            if stat.sis_valim_tk_id:
                # testimiskorra sisene valim
                tk_id = stat.sis_valim_tk_id
                q = q.filter(model.Sooritaja.testimiskord_id==tk_id)
                q = q.filter(model.Sooritaja.valimis==True)
            elif stat.valimid_tk_id:
                # eraldatud valimi testimiskord
                if len(stat.valimid_tk_id) == 1:
                    q = q.filter(model.Sooritaja.testimiskord_id==stat.valimid_tk_id[0])
                else:
                    q = q.filter(model.Sooritaja.testimiskord_id.in_(stat.valimid_tk_id))
            else:
                # valim puudub
                q = q.filter(model.Sooritaja.testimiskord_id==-1)
        else:
            # algse testimiskorra tulemused
            if stat.testimiskord_id:
                q = q.filter(model.Sooritaja.testimiskord_id==stat.testimiskord_id)
            elif stat.testimiskorrad_id:
                q = q.filter(model.Sooritaja.testimiskord_id.in_(stat.testimiskorrad_id))
        if stat.klass:
            q = q.filter(model.Sooritaja.klass==stat.klass)
        if stat.paralleel:
            q = q.filter(model.Sooritaja.paralleel==stat.paralleel)
        if stat.sooritajad_id:
            q = q.filter(model.Sooritaja.id.in_(stat.sooritajad_id))
        if stat.testiruum_id:
            q = q.filter(model.Sooritaja.sooritused.any(
                model.Sooritus.testiruum_id==stat.testiruum_id))
        if stat.nimekiri_id:
            q = q.filter(model.Sooritaja.nimekiri_id==stat.nimekiri_id)            
        return q
