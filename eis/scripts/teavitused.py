"""
Teavituste saatmine
Käivitada crontabist hommikupoole ööd!
"""
from datetime import date, datetime, timedelta, time
from eis.scripts.scriptuser import *
from eis.lib.utils import add_working_days
from eis.lib.helpers import str_from_date
import sqlalchemy as sa
from pyramid.renderers import render
from eis.handlers.avalik.korraldamine.testikohad import (
    tkoht_on_ruumid,
    tkoht_on_labiviijad,
    tkoht_on_hindajad
    )
from eis.handlers.admin.ehisopetajad import uuenda_pedagoogid
from eis.handlers.avalik.khindamine.hindamiskogumid import HindamisteArv
_ = i18n._
nosend = False

def usage():
    print(_("Kasuta kujul:"))
    print('   python -m eis.scripts.teavitused [-f KONFIFAIL] [-op {h|k}] [-nosend]')
    sys.exit(0)

def poll_korraldamata():
    # ES-2551
    # Saata kirjad kooli, kui testini on kuni 2 päeva ja on kooli poolt korraldamata.
    # Ei arvesta ilma sooritajateta soorituskohti (ES-2711).
    
    # Meeldetuletuse saatmise tingimused:
    # koolis toimub test, millel mõnel testiosal on sisse lülitatud,
    # et soorituskoht saab määrata ruume ja läbiviijaid.
    # Toimumisaeg on määramata (kellaaeg on vaikimisi tühi) või
    # on kohustuslik määrata testi administraator, komisjoni liige või hindaja.
    # Soorituskohas on mõni sooritajatega ruum,
    # kus pole ühtki testi administraatorit või komisjoni liiget (kui on kohustuslik)
    # või mõnele hindamiskogumile ei ole määratud ühtki hindajat.

    # ES-3423
    # Saata koolile teavitusi komisjoniliikmete määramise tähtaja kohta,
    # kui komisjoni määramise tähtajani on vähem kui 3 pv ja pole määratud.
    
    today = date.today()
    now = datetime.combine(today, time(0))
    until_date = add_working_days(today, 3)

    q = (model.Session.query(model.Testikoht,
                             model.Toimumisaeg)
         .join(model.Testikoht.toimumisaeg)
         .join(model.Toimumisaeg.testimiskord)
         .filter(model.Testimiskord.korraldamata_teated==True)
         # eesolevad testid
         .filter(model.Testikoht.testiruumid.any(model.Testiruum.algus >= now))
         # testi alguseni on 3 pv või komisjoni määramise tähtajani on 3 pv
         .filter(sa.or_(
             model.Testikoht.testiruumid.any(
                sa.and_(model.Testiruum.algus >= now, model.Testiruum.algus < until_date)),
             model.Toimumisaeg.komisjon_maaramise_tahtaeg < until_date))
         .filter(sa.or_(model.Testikoht.meeldetuletus==None,
                        model.Testikoht.meeldetuletus<now))
         .filter(model.Testikoht.sooritused.any())
         .order_by(model.Testikoht.id)
         )
    cnt = q.count()
    log.info(_("Korraldamise kontroll {n} testikohas...").format(n=cnt))
    # leiame kõik testikohad, kus lähema 3 päeva jooksul toimub test
    # või on vaja komisjoniliikmete määramisest teavitada
    for testikoht, toimumisaeg in q.all():
        # kontrollime, kas on korraldatud
        _check_korraldamata(testikoht, toimumisaeg)


def _check_korraldamata_ruumid(testiosa, toimumisaeg, testikoht):
    "Kontrollitakse, kas ruumid on määratud (e-testis)"
    errs = []
    on_ruumid = tkoht_on_ruumid(testiosa, toimumisaeg, testikoht, True)
    if on_ruumid == False:
        errs.append(_("Testiruumid on määramata. "))
    return errs

def _check_korraldamata_labiviijad(testiosa, toimumisaeg, testikoht):
    "Kontrollitakse, kas läbiviijad on määratud"
    errs = []
    today = date.today()
    mta_grupid = tkoht_on_labiviijad(testiosa, toimumisaeg, testikoht, True)
    if mta_grupid:
        grupid = {const.GRUPP_KOMISJON_ESIMEES: _("komisjoni esimees"),
                  const.GRUPP_KOMISJON: _("komisjoni liikmed"),
                  const.GRUPP_T_ADMIN: _("testi administraator"),
                  }
        li = []
        for g_id, cnt in mta_grupid:
            buf = grupid.get(g_id)
            if g_id == const.GRUPP_KOMISJON and cnt:
                buf += ' (%s)' % _("lisaks esimehele on vaja määrata {n} liiget)").format(n=cnt)
            li.append(buf)
        s_grupid = _listand(li)
        buf = _("Testile on määramata {groups}. ").format(groups=s_grupid)

        # Kui komisjoniliikmed on määramata, siis teavitame ka määramise tähtaja
        mta_grupid_id = [r[0] for r in mta_grupid]
        komisjon_kp = toimumisaeg.komisjon_maaramise_tahtaeg
        if komisjon_kp and \
          (const.GRUPP_KOMISJON_ESIMEES in mta_grupid_id or \
           const.GRUPP_KOMISJON in mta_grupid_id):
            s_kp = str_from_date(komisjon_kp)
            if komisjon_kp < today:
                buf += _("Eksamikomisjoni liikmete määramise tähtaeg oli {s_kp}. ").format(s_kp=s_kp)
            else:
                buf += _("Eksamikomisjoni liikmete määramise tähtaeg on {s_kp}. ").format(s_kp=s_kp)
        errs.append(buf)
    return errs

def _check_korraldamata_hindajad(testiosa, toimumisaeg, testikoht):
    "Kontrollitakse, kas hindajad on määratud (e-testis)"
    errs = []
    mta_hk = tkoht_on_hindajad(testiosa, toimumisaeg, testikoht, True)
    if mta_hk:
        li = []
        for hk_tahis, liik, valimis in mta_hk:
            if not valimis and hk_tahis:
                li.append(hk_tahis)
        if li:
            sbuf = _listand(li)
            if len(li) == 1:
                errs.append(_("Määramata on hindaja hindamiskogumis {sbuf}. ").format(sbuf=sbuf))
            elif len(li) == 0:
                errs.append(_("Määramata on hindaja. "))
            else:
                errs.append(_("Määramata on hindaja hindamiskogumites {sbuf}. ").format(sbuf=sbuf))

        li = []
        for hk_tahis, liik, valimis in mta_hk:
            if valimis and hk_tahis:
                li.append(hk_tahis)
        if li:
            sbuf = _listand(li)
            if len(li) == 1:
                errs.append(_("Määramata on valimi hindaja hindamiskogumis {sbuf}. ").format(sbuf=sbuf))
            elif len(li) == 0:
                errs.append(_("Määramata on valimi hindaja. "))
            else:
                errs.append(_("Määramata on valimi hindaja hindamiskogumites {sbuf}. ").format(sbuf=sbuf))
    return errs

def _check_korraldamata(testikoht, toimumisaeg):
    errs = []
    today = date.today()
    until_date = utils.add_working_days(today, 3)
    until_time = datetime.combine(until_date, time(0))
        
    testikoht_id = testikoht.id
    toimumisaeg_id = toimumisaeg.id
    testiosa = toimumisaeg.testiosa
    vastvorm_e = (const.VASTVORM_KE,
                  const.VASTVORM_SE,
                  const.VASTVORM_I,
                  const.VASTVORM_SH)
    on_etest = testiosa.vastvorm_kood in vastvorm_e

    # e-testi ruumide määramise kontroll
    if on_etest:
        errs.extend(_check_korraldamata_ruumid(testiosa, toimumisaeg, testikoht))

    # läbiviijate määramise kontroll
    # komisjoniliikmete korral komisjoniliikmete määramise tähtaja järgi
    # testi administraatoril testi alguse järgi
    errs.extend(_check_korraldamata_labiviijad(testiosa, toimumisaeg, testikoht))
    
    # hindajate määramise kontroll
    if on_etest and testikoht.alates < until_time:
        errs.extend(_check_korraldamata_hindajad(testiosa, toimumisaeg, testikoht))

    log.info(f'Kontrollitud {testikoht.tahised} #{testikoht.id}: {not errs}')
    if errs:
        # midagi on korraldamata
        testiosa = toimumisaeg.testiosa
        test = testiosa.test
        t_nimi = test.nimi
        millal = testikoht.millal
        koht = testikoht.koht
        
        id_host = registry.settings.get('eis.pw.url')
        k_url = f'{id_host}/eis/korraldamised/{testikoht.id}' # FIXURL
        lnk = f'<a href="{k_url}">{t_nimi}</a>'
        
        intro = [_("Hea kooli administraator. "),
                 _("Tuletame meelde, et teie koolis ({s}) toimub {when} {lnk}.").format(s=koht.nimi, when=millal, lnk=lnk)]

        body = '\n'.join(intro + errs)
        _send_korraldamata(testikoht, toimumisaeg, koht, body)
        
def _send_korraldamata(testikoht, toimumisaeg, koht, body):
    "Kiri kooli administraatorile ja koolijuhile"
    # EHISe päring ei tööta
    tahised = testikoht.tahised
    
    emails = []
    kasutajad = []
    for kasutaja in koht.get_admin():
        epost = kasutaja.epost
        if epost:
            if not is_live and not kasutaja.on_kehtiv_ametnik:
                log.error(_('Testkeskkonnas ei saada kirja kasutajale {epost}').format(epost=epost))
            else:
                emails.append(epost)
                kasutajad.append(kasutaja)

    if not emails:
        log.error(_("Kooli {s} aadresse pole").format(s=koht.nimi))
        return

    saajad = ', '.join(emails)
    if nosend:
        log.info(f'EI SAADA: {tahised} meeldetuletus {koht.nimi}: {saajad}\n{body}')
        return
    body = Mailer.replace_newline(body)
    subject = _("Meeldetuletus")
    try:

        ml = Mailer(handler)
        ml.send_ex(emails, subject, body)
    except Exception as e:
        script_error(_('Ei saa kirja saata'), e)
    else:
        log.info(f'{tahised} meeldetuletus saadetud {koht.nimi}: {saajad}')

        testikoht.meeldetuletus = datetime.now()
        kiri = model.Kiri(tyyp=model.Kiri.TYYP_KORRALDAMATA,
                          teema=subject,
                          sisu=ml.body,
                          teatekanal=const.TEATEKANAL_EPOST)
        for k in kasutajad:
            ks = model.Kirjasaaja(kasutaja_id=k.id,
                                  epost=k.epost,
                                  koht_id=koht.id)
            kiri.kirjasaajad.append(ks)
        model.Session.commit()


def poll_hindamata():
    # ES-2552
    # Kui tähtaeg on määratud, saadab süsteem automaatselt
    # hindajatele meeldetuletuse 2 p enne hindamise lõppu,
    # 1p enne lõppu kuni hinnatud või
    # kuni hindamine on Harno poolt lukku pandud.

    today = date.today()
    now = datetime.combine(today, time(0))
    until_date = add_working_days(today, 3)    
    q = (model.Session.query(model.Toimumisaeg.id)
         .filter(model.Toimumisaeg.hindamise_tahtaeg < until_date)
         .filter(model.Toimumisaeg.tulemus_kinnitatud==False)
         )
    toimumisajad_id = [ta_id for ta_id, in q.all()]
    cnt = len(toimumisajad_id)
    log.info(_('Hindamise kontroll {cnt} toimumisajal...').format(cnt=cnt))
    
    for ta_id in toimumisajad_id:
        _check_hindamata(ta_id)

def _check_hindamata(ta_id):

    grupid_id = (const.GRUPP_HINDAJA_S,
                 const.GRUPP_HINDAJA_K)
    ta = model.Toimumisaeg.get(ta_id)
    if not ta.on_hindamise_luba:
        # kui veel ei või hinnata, siis ei saada teateid
        return
    s_tahtaeg = str_from_date(ta.hindamise_tahtaeg)
    testiosa = ta.testiosa

    data = {}
    # leiame hindajad, kelle planeeritud tööde arv on määramata
    # või pole midagi veel hinnanud
    # või on hinnanud vähem kui planeeritud
    # või kellel on pooleli hindamisi
    qlv = (model.Session.query(model.Labiviija, model.Hindamiskogum.tahis)
           .filter(model.Labiviija.toimumisaeg_id==ta_id)
           .filter(model.Labiviija.kasutaja_id!=None)
           .filter(model.Labiviija.kasutajagrupp_id.in_(grupid_id))
           .filter(model.Labiviija.liik.in_((const.HINDAJA1, const.HINDAJA2)))
           .filter(sa.or_(model.Labiviija.hinnatud_toode_arv==None,
                          model.Labiviija.planeeritud_toode_arv==None,
                          model.Labiviija.hinnatud_toode_arv<model.Labiviija.planeeritud_toode_arv,
                          model.Labiviija.hinnatud_toode_arv<model.Labiviija.toode_arv))
           .join(model.Labiviija.hindamiskogum)
           .order_by(model.Hindamiskogum.tahis)
           )
    for (lv, hk_tahis) in qlv.all():
        li = []
        ha = HindamisteArv(lv, ta)
        if ha.lv_hindamata:
            li.append(_("hindamata {n} tööd").format(n=ha.lv_hindamata))
        if ha.lv_pooleli:
            li.append(_("pooleli {n} tööd").format(n=ha.lv_pooleli))
        if ha.lv_valmis:
            li.append(_("kinnitamata {n} tööd").format(n=ha.lv_valmis))
        if ha.alustamata:
            li.append(_("alustamata {s} tööd").format(s=ha.alustamata))
        if li:
            h_url = _get_hindamine_url(testiosa, ta, lv)
            if lv.valimis:
                label = _('hindamiskogumis {hk} valimis').format(hk=hk_tahis)
            else:
                label = _('hindamiskogumis {hk}').format(hk=hk_tahis)
            lnk = h_url and f'<a href="{h_url}">{label}</a>' or label
            buf = _("Teil on {lnk} {todolist}.").format(lnk=lnk, todolist=_listand(li))
            kasutaja_id = lv.kasutaja_id
            if kasutaja_id not in data:
                data[kasutaja_id] = {'labiviijad':[], 'bufs': []}
            data[kasutaja_id]['labiviijad'].append(lv)
            data[kasutaja_id]['bufs'].append(buf)
            
    if data:
        test = testiosa.test
        t_nimi = f'<i>{test.nimi}</i>'
        if len(test.testiosad) > 1:
            t_nimi += ' %s <i>%s</i>' % (_("testiosa"), testiosa.nimi)
        for kasutaja_id, r in data.items():
            bufs = r['bufs']
            labiviijad = r['labiviijad']
            kasutaja = model.Kasutaja.get(kasutaja_id)
            if kasutaja.epost:
                nimi = kasutaja.nimi
                body = _("Lp {nimi}!").format(nimi=nimi) + "\n\n"
                body += _("Olete testi {t_nimi} hindaja.").format(t_nimi=t_nimi) + " \n" + \
                        '\n'.join(bufs)
                if s_tahtaeg:          
                    body += '\n' + _("Hindamise tähtaeg:") + ' ' + s_tahtaeg + '.'                                                             
                body = Mailer.replace_newline(body)
                _send_hindamata(ta, kasutaja, body, labiviijad)
                
def _get_hindamine_url(testiosa, ta, lv):
    id_host = registry.settings.get('eis.pw.url')
    url = None
    if testiosa.vastvorm_kood == const.VASTVORM_SH:
        testiruum_id = lv.testiruum_id
        if testiruum_id:
            url = f'{id_host}/eis/shindamine/{testiruum_id}/vastajad' # FIXURL
    else:
        url = f'{id_host}/eis/khindamine/{ta.id}/hindaja/{lv.id}/vastajad' # FIXURL
    return url

def _send_hindamata(ta, kasutaja, body, labiviijad):
    "Kiri hindajale"

    tahised = ta.tahised
    epost = kasutaja.epost
    if not is_live and not kasutaja.on_kehtiv_ametnik:
        log.error(f'Testkeskkonnas ei saada kirja kasutajale {epost}')

    if nosend:
        log.info(f'EI SAADA: {tahised} hindamine meeldetuletus {kasutaja.nimi}: {epost}')
        return
    subject = "Meeldetuletus"
    try:
        ml = Mailer(handler)
        ml.send_ex(epost, subject, body)
    except Exception as e:
        script_error(_('Ei saa kirja saata'), e)
    else:
        log.info(f'{tahised} hindamise meeldetuletus saadetud {kasutaja.nimi}: {epost}')

        kiri = model.Kiri(tyyp=model.Kiri.TYYP_HINDAMATA,
                          teema=subject,
                          sisu=ml.body,
                          teatekanal=const.TEATEKANAL_EPOST)
        ks = model.Kirjasaaja(kasutaja_id=kasutaja.id,
                              epost=epost)
        kiri.kirjasaajad.append(ks)
        for lv in labiviijad:
            model.Labiviijakiri(kiri=kiri, labiviija_id=lv.id)
        model.Session.commit()

def _listand(li):
    buf = sep = ''
    for w in reversed(li):
        buf = w + sep + buf
        if not sep:
            sep = ' ja '
        else:
            sep = ', '
    return buf

def _error(exc, msg=''):
    script_error(_('Veateade') + ' (teavitused)', exc, msg)
    sys.exit(1)   
       
if __name__ == '__main__':
    fn_lock = '/srv/eis/log/teavitused.lock'
    op = named_args.get('op')
    nosend = named_args.get('nosend')
    with FileLock(fn_lock) as lock:
        if not lock:
            log.info(_('Protsess juba käib (fail {fn} on lukus)').format(fn=fn_lock))
            sys.exit(0)

        if not op or op == 'k':
            try:
                poll_korraldamata()
            except Exception as e:
                _error(e, str(e))

        if not op or op == 'h':
            try:
                poll_hindamata()
            except Exception as e:
                _error(e, str(e))            

