"""
Teenus võimaldab riigieksamite tulemusi puhverdada riigiportaalis. Teenuse kirjeldus asub eraldi dokumendis.
"""
from datetime import datetime
from eis.lib.pyxadapterlib.xutils import *
from eis import model
import eiscore.const as const
from eis.lib.pyxadapterlib import attachment
from eis.lib.xtee.xroad import *

# arv, millest rohkem me kunagi korraga kirjeid ei väljasta
MAX_CNT = 1000

def serve(paring, header=None, attachments=[], context=None):
    error = None
    out_attachments = []
    model.Paring_logi.log(header)

    q, max_cnt, error = _compose_query(paring)
    if error:
        res = E.response(E.veateade(error))
    else:
        praegu = datetime.now()
        buf, cnt, jaanud_arv, jargmine_id = _run_query(q, max_cnt)     
        
        res = E.response(E.aeg(praegu.isoformat()),
                         E.valjastatud_arv(str(cnt)),
                         E.jaanud_arv(str(jaanud_arv)))
        if jargmine_id:
            res.append(E.jargmine_id(str(jargmine_id)))
                        
        if buf:
            att = attachment.Attachment(buf, use_gzip=True)
            att.filename = 'data.txt.gz'
            content_id = att.gen_content_id()
            out_attachments = [att]
            res.append(E.manus('', href='cid:%s' % content_id))

    return res, out_attachments

def _compose_query(paring):
    q = error = max_arv = None

    alates, error = get_datetime_err(paring, 'alates')
    if not error:
        aasta, error = get_int_err(paring, 'aasta')
    if not error:
        alates_id, error = get_int_err(paring, 'alates_id')
    if not error:
        max_arv, error = get_int_err(paring, 'max_arv')
        if max_arv is None or max_arv > MAX_CNT:
            max_arv = MAX_CNT
        
    if not error:
        q = model.Session.query(model.Sooritaja,
                                model.Kasutaja.isikukood,
                                model.Test.nimi,
                                model.Test.aine_kood,
                                model.Test.max_pallid).\
            join(model.Sooritaja.kasutaja).\
            join(model.Sooritaja.testimiskord).\
            join(model.Sooritaja.test).\
            filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM).\
            filter(model.Testimiskord.koondtulemus_avaldet==True)

        if alates:
            q = q.filter(model.sa.or_(model.Sooritaja.modified>=alates,
                                      model.Sooritaja.sooritused.any(model.Sooritus.modified>=alates)))
        if aasta:
            q = q.filter(model.Testimiskord.aasta==aasta)
        if alates_id:
            q = q.filter(model.Sooritaja.id>alates_id)

    return q, max_arv, error

def _run_query(q, max_cnt):
    buf = ''
    cnt = jaanud_arv = 0
    jargmine_id = None
    for rcd in q.order_by(model.Sooritaja.id).all():
        sooritaja, isikukood, test_nimi, aine_kood, max_pallid = rcd
        if cnt >= max_cnt:
            # korraga väljastamise limiit on väiksem kui kirjete koguarv
            # jätame meelde, kus väljastamine pooleli jäi ja mitu on jäänud
            jargmine_id = sooritaja.id
            jaanud_arv = q.filter(model.Sooritaja.id>=jargmine_id).count()
            break
        cnt += 1
        pallid = sooritaja.pallid
        tulemus_protsent = sooritaja.tulemus_protsent
        if sooritaja.staatus != const.S_STAATUS_TEHTUD:
            pallid = tulemus_protsent = ''
        data = [str(sooritaja.id),
                isikukood,
                sooritaja.eesnimi,
                sooritaja.perenimi,
                test_nimi,
                aine_kood,
                model.Klrida.get_str('AINE', aine_kood),
                const.S_STAATUS.get(sooritaja.staatus),
                fstr(pallid),
                fstr(max_pallid),
                fstr(tulemus_protsent),
                sooritaja.keeletase_kood,
                ]
        buf += _to_line(data, 'S')

        for r in sooritaja.get_osasooritused():
            alasooritus, alaosa, tos = r
            if not alasooritus:
                continue
            if not tos:
                # alatestideta testiosa sooritus
                linetype = 'O' # testiosa
                tos = alasooritus
            else:
                linetype = 'A' # alatest
                
            kpv = tos.algus or tos.kavaaeg
            kpv = kpv and kpv.strftime('%Y-%m-%d') or ''

            koht = tos.testikoht and tos.testikoht.koht
            if koht and tos.staatus <= const.S_STAATUS_REGATUD and not tos.toimumisaeg.kohad_avalikud:
                # on määratud soorituskohta, kuid see pole veel kindel
                koht = None
            aadress = koht and koht.aadress
            staatus = alasooritus.staatus
            pallid = alasooritus.pallid
            protsent = alasooritus.tulemus_protsent

            if staatus != const.S_STAATUS_TEHTUD:
                pallid = protsent = ''

            data = [str(alasooritus.id),
                    alaosa.nimi,
                    kpv,
                    koht and koht.nimi,
                    koht and koht.tais_aadress or '',
                    const.S_STAATUS.get(staatus),
                    fstr(pallid),
                    fstr(protsent),
                    fstr(alasooritus.max_pallid),
                    ]
            buf += _to_line(data, linetype)
    return buf.encode('utf-8'), cnt, jaanud_arv, jargmine_id

def _to_line(data, linetype):
    line = linetype
    for value in data:
        if value is None:
            value = ''
        value = value.replace('|', ' ')
        line += '|%s' % value
    return line + '\n'

if __name__ == '__main__':
    from eis.scripts.scriptuser import *

    if named_args.get('list'):
        for aasta in range(1999, 2014):
            paring = E.request(E.aasta(str(aasta)))
            q, error = _compose_query(paring)
            print(aasta, q.count())
        sys.exit(0)

    # kasuta kujul: python tulemused_riigiportaali.py -admin TEGIJAKOOD [-aasta AASTA] [-alates ALATES] [-v4 true]
    paring = E.request(E.alates(named_args.get('alates') or ''),
                       E.alates_id(named_args.get('alates_id') or ''),
                       E.max_arv(named_args.get('max_arv') or ''),
                       E.aasta(named_args.get('aasta') or ''))
    res, att = test_me(serve, 'tulemused_riigiportaali.v1', paring, named_args)
    if att:
        data = attachment.encode('<BODY></BODY>', att)
        f = open('tmp.data', 'w')
        f.write(data)
        f.close()
