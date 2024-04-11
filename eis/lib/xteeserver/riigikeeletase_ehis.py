"""
Teenus EHISele riigikeele taseme pärimiseks.

Teenus on loodud selleks, et EHIS saaks pärida õpetajate riigikeeleoskuse tasemeid.
Teenus otsib sisendis olevate isikukoodidega isikute testisooritused, mis on andnud riigikeele oskuse taseme (tasemeeksamid, riigieksamid ja põhikooli lõpueksamid ainetes eesti keel teise keelena või riigikeel). 
Kui sisendis on antud ajavahemiku alguse või lõpu aeg, siis antakse isiku kohta andmeid välja ainult juhul, kui isikul leidub mõni selline riigikeele oskust mõõtev testisooritus, mille tulemust on antud ajavahemikul muudetud.
Iga isiku kohta leitakse kõrgeim saadud riigikeeleoskuse tase. Varem kasutatud tasemed väljastatakse uue taseme koodiga: kõrgtaseme asemel näidatakse tasemeks C1, kesktaseme asemel B2, algtaseme asemel B1.
Leitud andmed väljastatakse ZIP-pakitud CSV-failina (väljade eraldaja semikoolon), milles on:
•	isikukood;
•	tulemuse viimase muutmise kuupäev;
•	tunnistuse väljastamise kuupäev;
•	tunnistuse number.
Tulemuse viimase muutmise kuupäev kirjeldab selle testisoorituse tulemuse viimase muutmise kuupäeva, millest saadi kõrgeim tase. See ei pruugi olla isiku viimane keeleoskuse taseme muutmise kuupäev (nt võib isik olla mõnel hilisemal eksamil saanud kõrgema taseme, mis on hiljem tühistatud). Kui tunnistust ei ole avaldatud, siis on tunnistuse väljastamise kuupäev ja tunnistuse numbrid tühjad.
Kui sisendi isikukoode ei ole palju, siis on võimalik need esitada ka ilma manust kasutamata, elemendi „isikukoodid“ tekstilise väärtusena (sel juhul ilma ZIP-pakkimiseta).

"""
from datetime import datetime
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
import re
from eis import model
from eis.model import const
from eis.lib.xtee.xroad import *
from eis.lib.pyxadapterlib import attachment
from eis.lib.inmemoryzip import InMemoryZip

def serve(paring, header=None, attachments=[], context=None):
    err = None

    model.Paring_logi.log(header)
    
    alates, err1 = get_datetime_err(paring, 'alates')
    kuni, err2 = get_datetime_err(paring, 'kuni')
    err = err1 or err2

    isikukoodid = get_text(paring, 'isikukoodid')
    if attachments:
        att = attachments[0]
        try:
            for fname, fdata in InMemoryZip(att.data).extract():
                isikukoodid = fdata.decode('utf-8')
                break
        except Exception as ex:
            err = 'ZIP-manuse lahtipakkimine ei õnnestunud'
        
    paringuaeg = datetime.now()
    data = ''
    if not err and not isikukoodid:
        err = 'Andmeid ei väljastata, sest sisendis puuduvad isikukoodid'

    attachments = []

    res = E.response(E.paringuaeg(_set_datetime(paringuaeg)))
    if not err:
        re_ik = re.compile('[0-9]{11}$')
        isikukoodid = isikukoodid.split()
        for ik in isikukoodid:
            if not re_ik.match(ik):
                err = 'Andmeid ei väljastata, kuna sisendist leiti ilmselt vigane isikukood (%s)' % (ik)
    if not err:
        chunk_size = 500
        for i in range(0, len(isikukoodid), chunk_size):
            chunk = isikukoodid[i:i+chunk_size]
            results = _get_isikud(chunk, alates, kuni)
            for row in results:
                # isiku keeletase on muutunud
                isikukood, keeletase, tulemus_aeg, valjastamisaeg, tunnistusenr = row
                #if is_live:
                model.Paring_logi.log(header, isikukood)
                item = '%s;%s;%s;%s;%s\n' % (isikukood,
                                             keeletase,
                                             _set_date(tulemus_aeg) or '',
                                             _set_date(valjastamisaeg) or '',
                                             tunnistusenr or '')
                data += item
        if not err and data:
            filename = 'data.csv'
            zipdata = InMemoryZip().append(filename, data).close().read()
            att = attachment.Attachment(zipdata, use_gzip=False)
            zipfilename = 'data.zip'
            att.filename = zipfilename
            content_id = att.gen_content_id()
            attachments = [att]
            res.append(E.data('', href='cid:%s' % content_id, filename=zipfilename))
    if err:
        res.append(E.veateade(err))
            
    return res, attachments

def _get_isikud(isikukoodid, alates, kuni):
    # leiame isiku kõrgeima riigikeeloskuse taseme, kui see on antud ajavahemikul muutunud 
    q = (model.Session.query(model.Kasutaja.isikukood,
                             model.Sooritaja.keeletase_kood,
                             model.Sooritaja.tulemus_aeg,
                             model.Sooritaja.staatus,
                             model.Sooritaja.hindamine_staatus,
                             model.Tunnistus.valjastamisaeg,
                             model.Tunnistus.tunnistusenr)
         .join(model.Sooritaja.kasutaja)
         .filter(model.Kasutaja.isikukood.in_(isikukoodid))
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood.in_((const.TESTILIIK_TASE,
                                                const.TESTILIIK_RIIGIEKSAM,
                                                const.TESTILIIK_POHIKOOL)))
         .filter(model.Test.aine_kood.in_((const.AINE_ET2, const.AINE_RK)))
         .filter(model.Sooritaja.tulemus_aeg!=None)
         .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
         .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
         .join(model.Sooritaja.testitunnistused)
         .join((model.Tunnistus, model.sa.and_(model.Tunnistus.id==model.Testitunnistus.tunnistus_id,
                                               model.Tunnistus.staatus==const.N_STAATUS_AVALDATUD)))
         .order_by(model.Kasutaja.isikukood, model.Sooritaja.id, model.Tunnistus.id)
         )
    #model.log_query(q)
    results = []
    def _yield_isik(li_isik):
        # vanad tasemed:
        # algtase - vastab B1 tasemele
        # kesktase - vastab B2 tasemele
        # kõrgtase - vastab C1 tasemele
        vmap = {const.KEELETASE_KORG: const.KEELETASE_C1,
                const.KEELETASE_KESK: const.KEELETASE_B2,
                const.KEELETASE_ALG: const.KEELETASE_B1}
        li = []
        for r in li_isik:
            isikukood, keeletase, tulemus_aeg, staatus, h_staatus, valjastamisaeg, tunnistusenr = r
            if keeletase:
                keeletase = vmap.get(keeletase) or keeletase
                li.append((isikukood, keeletase, tulemus_aeg, valjastamisaeg, tunnistusenr))
        if li:
            for r in sorted(li, key=lambda r: r[1], reverse=True):
                results.append(r)
                break
            
    prev_ik = None
    is_modified = False
    isik = []
    for r in q.all():
        isikukood = r[0]
        tulemus_aeg = r[2]
        if isikukood == prev_ik:
            isik.append(r)
        else:
            if is_modified and isik:
                _yield_isik(isik)
            isik = [r]
            prev_ik = isikukood
            is_modified = False
        if (not alates or alates <= tulemus_aeg) and (not kuni or kuni >= tulemus_aeg):
            is_modified = True
    if is_modified and isik:
        _yield_isik(isik)
    
    return results

def _set_date(item):
    if item:
        return item.strftime('%Y-%m-%d')

def _set_datetime(item):
    if item:
        return item.strftime('%Y-%m-%dT%H:%M:%S')

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    # kasuta kujul: python riigikeeletase_ehis.py -admin TEGIJAKOOD "ISIKUKOOD1 ISIKUKOOD2"
    # kasuta kujul: python riigikeeletase_ehis.py -admin TEGIJAKOOD -gen N
    gen_cnt = named_args.get('gen')
    if gen_cnt:
        # leiame andmebaasist isikukoodid ja paneme manusesse
        LIMIT = int(gen_cnt)
        q = (model.Session.query(model.Kasutaja.isikukood).distinct()
             .filter(model.Kasutaja.isikukood!=None)
             .join(model.Kasutaja.sooritajad)
             .join(model.Sooritaja.test)
             .filter(model.Test.testiliik_kood.in_((const.TESTILIIK_TASE,
                                                    const.TESTILIIK_RIIGIEKSAM,
                                                    const.TESTILIIK_POHIKOOL)))
             .filter(model.Test.aine_kood.in_((const.AINE_ET2, const.AINE_RK)))
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
             .filter(model.Sooritaja.keeletase_kood!=None)
             )
        li = []
        for ik, in q.order_by(model.sa.desc(model.Sooritaja.id)).limit(LIMIT).all():
            li.append(ik)
        data = '\n'.join(li)

        filename = 'isikukoodid.txt'
        zipdata = InMemoryZip().append(filename, data).close().read()
        att = attachment.Attachment(zipdata, use_gzip=False)
        zipfilename = 'isikukoodid.zip'
        att.filename = zipfilename
        content_id = att.gen_content_id()
        attachments = [att]
        with open('/tmp/%s' % zipfilename, 'wb') as f:
            f.write(att.data)
        attnode = E.isikukoodid('', href='cid:%s' % content_id, filename=zipfilename)
    else:
        # ei kasuta sisendis manust
        isikukoodid = noname_args[0]
        attnode = E.isikukoodid(isikukoodid)
        attachments = []

    paring = E.request(E.alates(_set_datetime(datetime(2001,0o1,0o2))),
                       attnode)
    res, attachments = test_me(serve, 'riigikeeletase_ehis.v1', paring, named_args, attachments=attachments)
    for att in attachments:
        with open('/tmp/%s' % att.filename, 'wb') as f:
            f.write(att.data)
