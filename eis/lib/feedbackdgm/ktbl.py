"""Klasside tulemuste tabel tagasisidevormil
"""
from chameleon import PageTemplate
import sqlalchemy as sa
import decimal
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.lib.block import _outer_xml

from .feedbackdgm import FeedbackDgm

log = logging.getLogger(__name__)
_ = i18n._

class FeedbackDgmKtbl(FeedbackDgm):
    "Klasside tulemuste tabel"
    is_html = True
    foot_msg = []
    
    def data_by_params(self, data):
        # keskmiste read
        avg_row = data.get('avg_row')
        # tagasisidemalliga määratud veerud
        tcol = data.get('tcol2')
        # dynaamilised veerud ja grupeerimistingimused
        gargs = data.get('gargs')
        return self.data(tcol, avg_row, gargs)

    def data(self, tcol, avg_row, gargs):
        g_filter = self.stat.g_filter
        is_pdf = self.stat.is_pdf
        is_preview = self.handler.c.is_preview
        stat = self.stat
          
        # tabelis kuvatavad väärtused
        values = {}

        # dynaamiliste väljade parameetrid
        try:
            alla = int(gargs['alla'])
        except:
            alla = 20
        try:
            yle = int(gargs['yle'])
        except:
            yle = 80

        def applicable_columns(tcol, test, stat, gargs):
            "Jätame välja need veerud, mille andmeid ei saa kuvada"
            tcol2 = []
            if gargs:
                # lisame dynaamilised parameetrid
                for key in ('sugu','lng'):
                    if gargs.get(key):
                        # soovitakse grupeerida
                        if key not in tcol:
                            # grupeerimistingimused lisame ette
                            tcol.insert(0, key)
                    else:
                        # ei soovita grupeerida
                        if key in tcol:
                            tcol.remove(key)
            on_valim = None
            for expr in tcol:
                if test.pallideta and expr in ('avgp','v_avgp','med'):
                    continue
                if test.protsendita and expr in ('avgpr','v_avgpr','alla20','alla20pr','yle80','yle80pr'):
                    continue
                if expr in ('v_avgp','v_avgpr') and not stat.valimid_tk_id:
                    # valimi veerge ei kuva, kui valim puudub
                    continue
                    
                tcol2.append(expr)
            return tcol2

        class TQuery:
            def __init__(self, q, groupkeys):
                if 'sugu' in groupkeys:
                    q = q.filter(model.Kasutaja.sugu==groupkeys['sugu'])
                if 'lng' in groupkeys:
                    q = q.filter(model.Sooritaja.lang==groupkeys['lng'])
                if 'klass' in groupkeys:
                    q = q.filter(model.Sooritaja.klass==groupkeys['klass'])
                    q = q.filter(model.Sooritaja.paralleel==groupkeys['paralleel'])
                if 'opetaja_id' in groupkeys:
                    value = groupkeys['opetaja_id']
                    q = q.filter(model.Sooritaja.testiopetajad.any(
                        model.Testiopetaja.opetaja_kasutaja_id==value))
                self.q = q
                
            def query_max_pall(self, protsent):
                "Vähemalt etteantud arvu punkti saanute arv"
                diff = 1e-12
                select_fields = [sa.func.count(model.Sooritaja.id)]
                q = (self.q.with_entities(sa.func.count(model.Sooritaja.id))
                
                     .filter(model.Sooritaja.tulemus_protsent > protsent - diff)
                     )
                return q.scalar()

            def query_min_pall(self):
                "Min punktide saajate arv"
                diff = 1e-12
                select_fields = [sa.func.count(model.Sooritaja.id)]        
                q = (self.q.with_entities(*select_fields)
                     .filter(model.Sooritaja.pallid < diff)
                     )
                return q.scalar()       

            def query_max(self, protsent, total):
                "Vähemalt etteantud protsendi saanute arv"
                diff = 1e-12
                select_fields = [sa.func.count(model.Sooritaja.id)]
                q = (self.q.with_entities(*select_fields)
                     .filter(model.Sooritaja.tulemus_protsent > protsent - diff)
                     )
                cnt = q.scalar()
                cntpr = None
                if cnt is not None and total:
                    cntpr = cnt * 100./total        
                return cnt, cntpr

            def query_min(self, protsent, total):
                "Kuni etteantud protsendi saanute arv"
                diff = 1e-12
                select_fields = [sa.func.count(model.Sooritaja.id)]
                q = (self.q.with_entities(*select_fields)
                     .filter(model.Sooritaja.tulemus_protsent < protsent + diff)
                     )
                cnt = q.scalar()
                cntpr = None
                if cnt is not None and total:
                    cntpr = cnt * 100. / total        
                return cnt, cntpr

            def query_mediaan(self):
                "Tulemuse mediaan"
                # alates PostgreSQL v9.4 on olemas percentile_cont()
                select_fields = [model.Sooritaja.pallid]        
                q = self.q.with_entities(*select_fields)
                sql = "WITH t(value) AS (" + model.str_query(q) + ") SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY value) FROM t"
                #log.info(sql)
                qm = model.SessionR.execute(sa.text(sql))
                return qm.scalar()

            def query_tase_pr(self, tase, total):
                "Antud keeletaseme saajate %"
                select_fields = [sa.func.count(model.Sooritaja.id)]
                q = (self.q.with_entities(sa.func.count(model.Sooritaja.id))
                     .filter(model.Sooritaja.keeletase_kood==tase)
                     )
                cnt = q.scalar()
                if cnt is not None and total:
                    return cnt * 100. / total

            def query_avg(self):
                q = self.q.with_entities(sa.func.avg(model.Sooritaja.pallid),
                                         sa.func.avg(model.Sooritaja.tulemus_protsent))
                avgp, avgpr = q.first()
                return avgp, avgpr
            
        def get_fields(tcol):
            "Päringu tulemuste väljade leidmine"
            # päringu tulemused
            fields = []
            # grupeerimistingimused
            groups = []
            # päringu tulemuse väljade nimetused
            indexes = {}
            
            # koostame päritavate väljade loetelu
            # (need väärtused, mille jaoks pole vaja omaette päringut)
            n_fld = 0
            for expr in tcol:
                if expr == 'lng':
                    fields.append(model.Sooritaja.lang)
                    groups.append(model.Sooritaja.lang)
                elif expr == 'sugu':
                    fields.append(model.Kasutaja.sugu)
                    groups.append(model.Kasutaja.sugu)
                elif expr == 'cnt':
                    fields.append(sa.func.count(model.Sooritaja.id))
                elif expr == 'ajakulu':
                    fields.append(sa.func.avg(model.Sooritaja.ajakulu))
                elif expr == 'avgp':
                    fields.append(sa.func.avg(model.Sooritaja.pallid))
                elif expr == 'avgpr':
                    fields.append(sa.func.avg(model.Sooritaja.tulemus_protsent))
                elif expr == 'v_avgp':
                    fields.append(sa.func.avg(model.Sooritaja.pallid))
                elif expr == 'v_avgpr':
                    fields.append(sa.func.avg(model.Sooritaja.tulemus_protsent))
                else:
                    # väljad, mis arvutatakse hiljem eraldi päringuga
                    continue
                # jätame meelde veeru asukoha selles jrk-s, mis on päringus
                indexes[expr] = n_fld
                n_fld += 1

            if 'cnt' not in indexes:
                # sooritajate arvu väljundisse ei soovitud,
                # aga meil on seda vaja
                fields.append(sa.func.count(model.Sooritaja.id))
                indexes['cnt'] = n_fld
            return fields, groups, indexes

        def get_kov_koolide_arv():
            "Leitakse, mitmest minu KOVi koolist testist osa võeti"
            q = model.SessionR.query(sa.func.count(model.Sooritaja.kool_koht_id.distinct()))
            q = g_filter(q, const.FBR_LINN)
            return q.scalar()

        def gen_qry(group_type, fields, groups, indexes, valimis):
            # koostame päringu
            q = (model.SessionR.query(sa.func.count(model.Sooritaja.id))
                 .join(model.Sooritaja.kasutaja)
                 )
            Opetaja = sa.orm.aliased(model.Kasutaja)

            # päringu tingimused grupile
            q = g_filter(q, group_type, valimis)
            if group_type == const.FBR_KLASS:
                # klasside read
                extra = [model.Sooritaja.klass,
                         model.Sooritaja.paralleel]

            elif group_type == const.FBR_OPETAJA:
                # õpetajate read
                extra = [Opetaja.nimi, Opetaja.id]
            else:
                extra = []

            _fields = fields + extra
            _groups = groups + extra

            q1 = q.with_entities(*_fields)

            if group_type == const.FBR_OPETAJA:
                # õpetaja seos
                q1 = (q1.join(model.Sooritaja.testiopetajad)
                      .join((Opetaja,
                             Opetaja.id==model.Testiopetaja.opetaja_kasutaja_id))
                      )
            qbase = q1
            if _groups:
                q1 = q1.group_by(*_groups)
            return qbase, q1

        h = self.handler.h
        fstr = h.fstr
        def fstrpr(value):
            if value is not None:
                return fstr(value,0) + '%'

        def gen_label(rcd, indexes, group_type):
            # groupkeys on rida identifitseerivad parameetrid
            groupkeys = {}
            n_lng = indexes.get('lng')
            if n_lng is not None:
                lng = rcd[n_lng]
                groupkeys['lng'] = lng
            n_sugu = indexes.get('sugu')
            if n_sugu is not None:
                groupkeys['sugu'] = rcd[n_sugu]

            if group_type == const.FBR_LINN:
                label = model.Aadresskomponent.get_str_by_tase_kood(2, stat.linn_kood)
            elif group_type == const.FBR_MAAKOND:
                label = model.Aadresskomponent.get_str_by_tase_kood(1, stat.maakond_kood)
            elif group_type == const.FBR_KOOL:
                koht_id = stat.kool_koht_id or stat.kand_koht_id
                label = koht_id and model.Koht.get(koht_id).nimi or None
            elif group_type == const.FBR_KLASS:
                klass, paralleel = rcd[-2:]
                groupkeys['klass'] = klass
                groupkeys['paralleel'] = paralleel
                if paralleel:
                    label = f'{klass}.{paralleel} klass'
                elif klass:
                    label = f'{klass}. klass'
                else:
                    label = ''
            elif group_type == const.FBR_OPETAJA:
                label, opetaja_id = rcd[-2:]
                label = _("Õpetaja {opetaja} õpilased").format(opetaja=label)
                groupkeys['opetaja_id'] = opetaja_id
            elif group_type == const.FBR_RIIK:
                label = _("Eesti keskmine")
            else:
                label = None
            return label, groupkeys

        def gen_row(rcd, indexes, group_type, qbase, v_qbase, groupkeys, valimis):

            def get_rowquery_val(expr):
                "Leitakse veeru väärtus rea põhipäringu tulemustest"
                n_fld = indexes.get(expr)
                if n_fld is None:
                    log.error(f'vigane fld {expr}')
                    return ''
                value = rcd[n_fld]
                if expr == 'ajakulu':
                    # teisendame varem leitud suuruse formaadi
                    if isinstance(value, decimal.Decimal):
                        # ajakulu sekundites (decimal.Decimal tyypi)
                        value = int(value)
                    value = h.strh_from_time(value) or ''
                elif expr == 'lng':
                    value = model.Klrida.get_lang_nimi(value).lower()
                return value

            # valimi päringu tulemused
            class ValimVal:
                v_avgp = None
                v_avgpr = None
            
                def get_valim_val(self, expr):
                    "Leitakse valimi veeru väärtus"
                    # valimi keskmine (punktid või %)
                    if valimis and expr == 'v_avgp' and 'avgp' in indexes:
                        # rea päring sisaldab sama väärtust, ei pea uuesti pärima
                        value = get_rowquery_val('avgp')
                    elif valimis and expr == 'v_avgpr' and 'avgpr' in indexes:
                        # rea päring sisaldab sama väärtust, ei pea uuesti pärima
                        value = get_rowquery_val('avgpr')
                    elif not v_qry:
                        # valim puudub, ei saa valimi päringut teha
                        value = None
                    else:
                        # tehakse valimi päring, kui veel pole tehtud
                        if self.v_avgp is None:
                            self.v_avgp, self.v_avgpr = v_qry.query_avg()
                        if expr == 'v_avgp':
                            value = fstr(self.v_avgp, 1)
                        elif expr == 'v_avgpr':
                            value = fstr(self.v_avgpr, 1)
                    return value

            vval = ValimVal()
                
            # tulemuse tabeli rea väärtused
            row = []
            # päringu tulemustes sooritajate koguarvu indeks
            n_total = indexes.get('cnt')
            # sooritajate koguarv
            total = rcd[n_total]
            # eraldi päritavate veergude päring
            qry = TQuery(qbase, groupkeys)
            # eraldi päritavate veergude päring valimist
            if v_qbase:
                v_qry = TQuery(v_qbase, groupkeys)
            else:
                # valimi päringut ei ole (valim puudub või on kogu rida valim)
                v_qry = None

            for expr in tcol:
                if expr == 'med':
                    value = qry.query_mediaan()
                elif expr == 'cnt_min':
                    value = qry.query_min_pall()
                elif expr == 'cnt_max':
                    value = qry.query_max_pall(100)
                elif expr == 'alla20':
                    val, valpr = qry.query_min(alla, total)
                    value = fstr(val,1)
                elif expr == 'alla20pr':
                    val, valpr = qry.query_min(alla, total)
                    value = fstrpr(valpr)
                elif expr == 'yle80':
                    val, valpr = qry.query_max(yle, total)
                    value = fstr(val,1)
                elif expr == 'yle80pr':
                    val, valpr = qry.query_max(yle, total)
                    value = fstrpr(valpr)
                elif expr.startswith('tase_pr_'):
                    tase = expr[8:]
                    value = qry.query_tase_pr(tase, total)
                elif expr in ('v_avgp','v_avgpr'):
                    value = vval.get_valim_val(expr)
                else:
                    # väljad, mis on juba põhipäringuga kätte saadud
                    if valimis and \
                      (expr == 'avgpr' and 'v_avgpr' in indexes or \
                       expr == 'avgp' and 'v_avgp' in indexes):
                        # kui kogu rida ongi valim, siis jätame need veerud tühjaks,
                        # mille jaoks on eraldi valimi veerg olemas
                        value = None
                    else:
                        value = get_rowquery_val(expr)
                row.append(value)

            return row

        def gen_row_group(group_type, fields, groups, indexes):
            items = []
            valim_types = (const.FBR_LINN, const.FBR_MAAKOND, const.FBR_RIIK, const.FBR_RIIK_PR)
            valimid_tk_id = stat.valimid_tk_id
            is_valim = valimid_tk_id and True or False
            if is_valim:
                # valimi read valimist, muud read mittevalimist
                valimis = group_type in valim_types
            else:
                # päring üle kõigi (valim + mittevalim)
                valimis = None # False
            if valimis and valimid_tk_id:
                if not stat.v_avaldet.koondtulemus_avaldet:
                    # valimi koondtulemus pole avaldatud
                    return items
            elif stat.testimiskord:
                if not stat.testimiskord.koondtulemus_avaldet:
                    return items
            
            if group_type == const.FBR_LINN:
                # omavalitsuse rida kuvada ainult juhul, kui omavalitsuses
                # võttis testist osa rohkem kui 2 kooli
                msg = _("Kohaliku omavalitsuse koondrida kuvatakse tabelis juhul, kui test sooritati vähemalt kolmes selle omavalitsuse koolis.")
                self.foot_msg.append(msg)
                n = get_kov_koolide_arv()
                if n <= 2:
                    return items
                
            # päringu tingimused grupile
            qbase, q1 = gen_qry(group_type, fields, groups, indexes, valimis)
            if is_valim:
                # eraldi valimi veergude päring, kui reas on muud väljad mitte-valimist
                v_qbase, v_q1 = gen_qry(group_type, fields, groups, indexes, True)
            else:
                v_qbase = None

            # tabeli read
            for rcd in q1.all():
                rcd = list(rcd)
                label, groupkeys = gen_label(rcd, indexes, group_type)
                if label:
                    row = gen_row(rcd, indexes, group_type, qbase, v_qbase, groupkeys, valimis)
                    attrs = {'type': group_type,
                             'groupkeys': groupkeys,
                            }
                    items.append(([label, *row], attrs))
            return items

        # leiame maakonna ja linna
        koht_id = stat.kool_koht_id or stat.kand_koht_id
        
        koht = koht_id and model.Koht.get(koht_id)
        aadress = koht and koht.aadress
        stat.maakond_kood = aadress and aadress.kood1
        stat.linn_kood = aadress and aadress.kood2
        
        # jätame välja need veerud, mille andmed pole avaldatud
        test = stat.test
        tcol = applicable_columns(tcol, test, stat, gargs)

        fields, groups, indexes = get_fields(tcol)

        # tabeli read
        items = []
        
        # yle kõigi ridade liikide
        for group_type in avg_row:
            g_items = gen_row_group(group_type, fields, groups, indexes)
            items.extend(g_items)

        # koostame päiserea andmed
        opt_expr = self.get_opt_expr(self.handler, test, alla, yle)
        di_expr = {key: value for (key, value) in opt_expr}
        header = [('','')]
        for ind, key in enumerate(tcol):
            if key.startswith('tase_pr_'):
                tase = key[8:]
                label = _("{s} taseme saajate %").format(s=tase)
            else:
                label = di_expr.get(key) or ''
            header.append((key, label))
            
        return header, items, tcol
    
    def draw_html(self, data, fbd_id, body_only=False):
        header, items, tcol = data

        div_body = self.draw_html_body(header, items, tcol)

        if body_only:
            # brauserist saadeti päring ainult tabeli sisu uuendamiseks
            return div_body
        else:
            # kogu tagasisidevormi genereerimine
            
            # filtris võimalik peita kõiki veerge peale keele ja soo,
            # sest need on grupeerimistingimused
            div_filter = self.tbl_col_filter(header)
            
            buf = f'<div class="fbtbl fbtbl-ktbl" id="{fbd_id}">' +\
                  div_filter +\
                  '<div style="overflow-x:auto;position:relative;" class="fbtbl-body">' +\
                  div_body +\
                  '</div></div>'
            return buf

    def draw_html_body(self, header, items, tcol):
        buf = '<table class="table table-striped tablesorter">' +\
                   '<thead><tr>'
        for ind, (key, name) in enumerate(header):
            buf += f'<th class="fbcol-{key}">{name}</th>'
        buf += '</tr>\n'

        # enne klasside ja õpetajate ridu ilmuv kooli koondrida on thead sees
        # klasside ja õpetajate read on tbody ja need read alluvad veergude järjestamisele
        # peale klasse tulevad koondread on tfoot
        curr_tag = 'thead' 
        for row, attrs in items:
            group_type = attrs.get('type')
            if group_type in (const.FBR_KLASS, const.FBR_OPETAJA):
                new_tag = 'tbody'
                tr_cls = ''
            else:
                new_tag = curr_tag == 'tbody' and 'tfoot' or curr_tag
                tr_cls = 'total-row'
            if new_tag != curr_tag:
                buf += f'</{curr_tag}><{new_tag}>\n'
                curr_tag = new_tag
            buf += f'<tr class="{tr_cls}">'

            for ind, value in enumerate(row):
                if isinstance(value, decimal.Decimal):
                    # ajakulu sekundites (decimal.Decimal tyypi)
                    value = int(value)
                elif isinstance(value, float):
                    value = self.handler.h.fstr(value,1)
                if value is None:
                    value = ''
                key = header[ind][0]
                buf += f'<td class="fbcol-{key}">'
                if group_type in (const.FBR_KLASS, const.FBR_OPETAJA) and ind == 0:
                    # klassi nimetus või õpetaja nimi 
                    arg = ''
                    if group_type == const.FBR_KLASS:
                        groupkeys = attrs['groupkeys']
                        klass = groupkeys.get('klass')
                        paralleel = groupkeys.get('paralleel')
                        klass_id = model.KlassID(klass, paralleel).id
                        arg = f'klassid_id={klass_id}'
                    elif group_type == const.FBR_OPETAJA:
                        groupkeys = attrs['groupkeys']
                        op_id = groupkeys.get('opetaja_id')
                        arg = f'op_id={op_id}'
                    buf += f'<a class="lnk-opilased" data-arg="{arg}">{value}</a>'
                else:
                    buf += f'{value}'
                buf += f'</td>'
            buf += '</tr>\n'
        buf += f'</{curr_tag}></table>\n'

        # märkus
        if self.foot_msg:
            for msg in set(self.foot_msg):
                buf += '<div>' + msg + '</div>'
            
        return buf

    def tbl_col_filter_items(self, header):
        "Tabeli väljade valimise märkeruudud"
        h = self.handler.h
        keys = [key for (key, label) in header]

        # grupeerimisvalikud, alati valitavad
        items = []
        g_opt = (('lng', _("Keel")),
                 ('sugu', _("Sugu")))
        # grupeerimisvalikud on esimesed 2 items elementi
        cnt_g = 2
        for (key, label) in g_opt:
            # dynaamilised parameetrid, vajalik päring serverist
            cb = h.checkbox1(key,
                             1,
                             checked=key in keys,
                             label=label,
                             class_='fbtbl-srv-filter',
                             ronly=False)
            buf = '<div>' + str(cb) + '</div>'
            items.append(buf)

        # koostaja määratud valikud
        items2 = []
        for (ind, (key, label)) in enumerate(header):
            if key in ('lng','sugu','alla20','alla20pr','yle80','yle80pr'):
                # lng,sugu on eespool juba lisatud
                # alla-yle lisame hiljem lõppu, sest vaja on tekstivälja
                continue
            if label:
                # filter olemasoleva veeru peitmiseks
                cb = h.checkbox1(key,
                                 1,
                                 checked=True,
                                 label=label,
                                 class_='fbtbl-hide-filter',
                                 ronly=False)
                buf = '<div>' + str(cb) + '</div>'
                items.append(buf)

        # jagame veergudesse
        buf = self.tbl_col_filter_layout(items, cnt_g)

        # lisame alla-yle väljad
        buf_extra = self.tbl_col_filter_extra(keys)

        wrapper = '<div class="d-flex flex-wrap">' + buf + buf_extra + '</div>'
        return wrapper
    
    def tbl_col_filter_extra(self, keys):
        h = self.handler.h
        items = []
        if 'alla20' in keys or 'alla20pr' in keys:
            inp = str(h.posfloat('alla', 20, size=3, maxvalue=100,
                                 class_="fbtbl-srv-filter",
                                 ronly=False))
            buf = '<div>' +\
                  _("Kuni {p}% pallidest").format(p=inp)
            if 'alla20' in keys:
                buf += '<br/>' +\
                        str(h.checkbox('alla20',
                                       1,
                                       checked=False,
                                       label=_("sooritajate arv"),
                                       class_="fbtbl-hide-filter",
                                       ronly=False))
            if 'alla20pr' in keys:
                buf += '<br/>' +\
                       str(h.checkbox('alla20pr',
                                      1,
                                      checked=False,
                                      label=_("sooritajate protsent"),
                                      class_="fbtbl-hide-filter",
                                      ronly=False))
            buf += '</div>\n'
            items.append(buf)
            
        if 'yle80' in keys or 'yle80pr' in keys:
            inp = str(h.posfloat('yle', 80, size=3, maxvalue=100,
                                 class_="fbtbl-srv-filter",
                                 ronly=False))
            buf = '<div>' +\
                  _("Vähemalt {p}% pallidest").format(p=inp)
            if 'yle80' in keys:
                buf += '<br/>' +\
                       str(h.checkbox('yle80',
                                      1,
                                      checked=False,
                                      label=_("sooritajate arv"),
                                      class_="fbtbl-hide-filter",
                                      ronly=False))
            if 'yle80pr' in keys:
                buf += '<br/>' +\
                       str(h.checkbox('yle80pr',
                                      1,
                                      checked=False,
                                      label=_("sooritajate protsent"),
                                      class_="fbtbl-hide-filter",
                                      ronly=False))
            buf += '</div>\n'
            items.append(buf)

        buf = ''
        for item in items:
            buf += '<div class="pr-2">' + item + '</div>'
        return buf

    @classmethod
    def get_opt_expr(cls, handler, test, alla=20, yle=80):
        "Tabeli veergude allikate valik"

        li = [('lng', _("Soorituskeel")),
              ('sugu', _("Sugu")),
              ('cnt', _("Sooritajate arv")),
              ('ajakulu', _("Kasutatud aeg")),
              ('avgp', _("Keskmine (punktid)")),
              ('avgpr', _("Keskmine (%)")),
              ('v_avgp', _("Valimi keskmine (punktid)")),
              ('v_avgpr', _("Valimi keskmine (%)")),
              ('med', _("Mediaan")),
              ('cnt_min', _("Min punktide saajate arv")),
              ('cnt_max', _("Max punktide saajate arv")),
              ('alla20', _("Kuni {n}% saajate arv").format(n=alla)),
              ('alla20pr', _("Kuni {n}% saajate %").format(n=alla)),
              ('yle80', _("Vähemalt {n}% saajate arv").format(n=yle)),
              ('yle80pr', _("Vähemalt {n}% saajate %").format(n=yle)),
              ]

        # keeleoskuse taseme saajate protsent
        for tt in test.testitasemed:
            tase = tt.keeletase_kood
            key = f'tase_pr_{tase}'
            label = _("{s} taseme saajate %").format(s=tase)
            li.append((key, label))

        # jätame välja need veerud, mis antud testis ei kohaldu
        remove = []
        # ajakulu on ainult kirjaliku e-testi korral
        q = (model.SessionR.query(sa.func.count(model.Testiosa.id))
             .filter_by(test_id=test.id)
             .filter(model.Testiosa.vastvorm_kood.in_((const.VASTVORM_KE, const.VASTVORM_SE)))
             )
        if q.scalar() == 0:
            remove.append('ajakulu')
        li = [r for r in li if r[0] not in remove]
        return li
    
