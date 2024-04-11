"""
Plankide mooduli aruannete teavituste saatmine ES-2387
Plankide kasutamise aruande tähtaja saabumisel (11. oktoober) saadab
süsteem automaatselt teavituse (e-kirja) kõikidele kooli plankide
haldajatele ja üldaadressitele ning edaspidi (peale 1.novembrit)
iga nädal (nt esmaspäeval) ainult nendele koolidele,
kes pole endiselt aruannet esitanud. 
"""
from datetime import date, datetime, timedelta, time
from eis.scripts.scriptuser import *
import eis_plank.model as model
import eis_plank.model.const as const
from eis_plank.handlers.plangid.aruanded import get_aruandelised
import sqlalchemy as sa
from pyramid.renderers import render

nosend = False

def usage():
    print('Kasuta kujul:')
    print('   python -m eis.scripts.plank_aruanne [-f KONFIFAIL] -op {a1|a2} [-nosend]')
    sys.exit(0)

def p_notices():
    "11. okt saadetakse teade kõigile plankide haldajatele"

    tyyp = model.Kiri.TYYP_PLANK_A1

    # leiame käesoleva aruandeperioodi, mille aruanne ei pea veel olema esitatud
    dt = date.today()
    aasta = dt.month < 11 and dt.year or dt.year + 1
    periood = (model.Session.query(model.Aruandeperiood)
               .filter_by(aasta=aasta)
               .first())

    # leiame aruandekohuslased koolid
    q = get_aruandelised(periood)
    # ei jäta välja neid koole, kes on juba aruande esitanud, sest isegi kui kool 
    # on aruande esitanud, ei pruugi ta olla saatnud meile mahakantud planke
    q = q.order_by(model.Koht.nimi)

    kohad_id = [k.id for k in q.all()]
    log.info('Saata teated %d koolile (periood %s-%s)' % \
             (len(kohad_id), str_date(periood.alates), str_date(periood.kuni)))
    
    for k_id in kohad_id:
        koht = model.Koht.get(k_id)
        addresses = get_addresses(koht)
        _send_mail(koht, addresses, tyyp)

def p_reminders():
    "Alates 1.nov igal esmaspäeval saadetakse kiri neile, kes pole aruannet kinnitanud"
    # käivitada järgmise aruandeperioodi kestel, st peale 1.nov

    tyyp = model.Kiri.TYYP_PLANK_A2

    # leiame viimase aruandeperioodi, mille aruanne peab olema esitatud
    dt = date.today()
    aasta = dt.month < 11 and dt.year - 1 or dt.year
    periood = (model.Session.query(model.Aruandeperiood)
          .filter_by(aasta=aasta)
          .first())

    # leiame aruandekohuslased koolid
    q = get_aruandelised(periood)
    # jätame välja need koolid, kes on juba aruande esitanud
    q = q.filter(~ sa.exists().where(
        sa.and_(model.Perioodiaruanne.koht_id==model.Koht.id,
                model.Perioodiaruanne.aruandeperiood_id==periood.id,
                model.Perioodiaruanne.staatus>=const.AR_STAATUS_KINNITATUD)
        ))
    q = q.order_by(model.Koht.nimi)

    kohad_id = [k.id for k in q.all()]
    log.info('Saata meeldetuletused %d koolile (periood %s-%s)' % \
             (len(kohad_id), str_date(periood.alates), str_date(periood.kuni)))
    if not is_live:
        log.info('not live')
    for k_id in kohad_id:
        koht = model.Koht.get(k_id)
        addresses = get_addresses(koht)
        _send_mail(koht, addresses, tyyp)
        
def _send_mail(koht, addresses, tyyp):
    "Teade saatmine"
    if not addresses:
        log.info(f'POLE AADRESSI: {koht.nimi}')
        return

    emails = [email for (email, k_id) in addresses]
    saajad = ', '.join(emails)
    if nosend:
        log.info(f'EI SAADA: {tyyp} {koht.nimi}: {saajad}')
        return

    if tyyp == model.Kiri.TYYP_PLANK_A1:
        # teade
        template = 'mail/plank.aruanne_teade.mako'
    else:
        # meeldetuletus
        template = 'mail/plank.aruanne_meeldetuletus.mako'
        
    template = 'mail/plank.aruanne_teade.mako'
    subject, body = handler.render_mail(template, {})
    body = Mailer.replace_newline(body)
    try:
        ml = Mailer(handler)
        ml.send_ex(emails, subject, body)
    except Exception as e:
        script_error('Ei saa kirja saata', e)
    else:
        log.info(f'teade saadetud {koht.nimi}: {saajad}')
        kiri = model.Kiri(tyyp=tyyp,
                          teema=subject,
                          sisu=ml.body,
                          teatekanal=const.TEATEKANAL_EPOST)
        for email, k_id in addresses:
            ks = model.Kirjasaaja(kasutaja_id=k_id,
                                  epost=email)
            kiri.kirjasaajad.append(ks)
        model.Session.commit()

def get_addresses(koht):
    "Leitakse soorituskoha plankide haldurite e-posti aadressid"
    emails = []
    for k in get_plangiadmin(koht.id):
        if not is_live and not k.on_kehtiv_ametnik:
            # testkeskkonnas ei saada
            continue
        if k.epost:
            emails.append((k.epost, k.id))

    # lisame kooli yldaadressi juhul, kui on live ja
    # kooli yldaadress pole adminide aadresside seas
    if koht.epost and is_live and (koht.epost not in emails):
        emails.append((koht.epost, None))
    return emails

def get_plangiadmin(koht_id):
    "Leitakse soorituskoha plankide haldurid"
    now = datetime.now()
    q = (model.Session.query(model.Kasutaja)
         .filter(model.Kasutaja.kasutajarollid.any(
             sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_K_PLANK,
                     model.Kasutajaroll.koht_id==koht_id,
                     model.Kasutajaroll.kehtib_alates<=now,
                     model.Kasutajaroll.kehtib_kuni>=now)
             ))
         )
    return q.all()

def str_date(dd):
    return dd.strftime('%d.%m.%Y')

def _error(exc, msg=''):
    script_error('Veateade (plank_aruanne)', exc, msg)
    sys.exit(1)   
       
if __name__ == '__main__':
    fn_lock = '/srv/eis/log/plank_aruanne.lock'
    op = named_args.get('op')
    nosend = named_args.get('nosend')
    with FileLock(fn_lock) as lock:
        if not lock:
            log.info('Protsess juba käib (fail %s on lukus)' % fn_lock)
            sys.exit(0)

        if op == 'a1':
            # teadet saatmine
            try:
                p_notices()
            except Exception as e:
                _error(e, str(e))

        if op == 'a2':
            # meeldetuletuste saatmine
            try:
                p_reminders()
            except Exception as e:
                _error(e, str(e))
