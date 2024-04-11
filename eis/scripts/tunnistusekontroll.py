"""
Eksamitulemuste auditeerimine tunnistuste PDFis olevate eksamitulemuste alusel

Käivitada crontabist regulaarselt

python -m eis.scripts.tunnistusekontroll
"""
import io
from zipfile import ZipFile, ZIP_STORED
from pypdf import PdfReader
from datetime import datetime, timedelta
from .scriptuser import *

def usage():
    print('Kasuta kujul:')
    print('   python -m eis.scripts.tunnistusekontroll [-f KONFIFAIL]')
    print()
    sys.exit(0)

def kontroll(tunnistus, dirname):
    err = None
    bdoc = tunnistus.filedata
    filename = tunnistus.filename
    mimetype = tunnistus.mimetype
    if mimetype not in (const.CONTENT_TYPE_BDOC, const.CONTENT_TYPE_ASICE):
        err = 'Fail pole BDOC'
    else:
        pdfdata, err = bdoc_to_pdf(bdoc)
        if not err:
            info = get_pdf_info(pdfdata)
            err = kontroll_info(tunnistus, info)
            if not err:
                err = digidoc_validate(bdoc, dirname, tunnistus.fileext)
                
    ktr = tunnistus.tunnistusekontroll
    if not ktr:
        ktr = model.Tunnistusekontroll()
        tunnistus.tunnistusekontroll = ktr
    ktr.seisuga = datetime.now()
    ktr.korras = not err
    ktr.viga = err
    return ktr.korras, ktr.viga

def kontroll_info(tunnistus, info):
    ver = info.get('/ExamDataVer')
    if not ver:
        return 'PDF ei sisalda metainfot ExamDataVer'
    examdata = info.get('/ExamData')
    if not examdata:
        return 'PDF ei sisalda metainfot ExamData' 
    isikukood = synnikpv = None
    if ver == '1':
        try:
            ik, items = examdata.split(';', 1)
            li_items = items.split(';')
        except:
            return 'Vigased andmed: %s' % item

        if not len(li_items):
            return 'Tunnistusel pole ühegi eksami tulemust'

        for tt in tunnistus.testitunnistused:
            item = model.Tunnistusekontroll.encode_sooritaja(tt.sooritaja)
            try:
                li_items.remove(item)
            except ValueError:
                return 'Tulemus "%s" puudub tunnistuselt (%s)' % (item, items)
        if len(li_items):
            return 'Andmebaasis pole tulemusi: %s' % (';'.join(li_items))
    else:
        return 'Tundmatu versioon %s' % ver

    kasutaja = tunnistus.kasutaja
    if '.' in ik:
        synnikpv = kasutaja.synnikpv and kasutaja.synnikpv.strftime('%d.%m.%Y') or ''
        if synnikpv != ik:
            return 'Sünnikuupäev erineb: tunnistusel %s, andmebaasis %s' % (ik, synnikpv)
    else:
        if ik != kasutaja.isikukood:
            return 'Isikukood erineb: tunnistusel %s, andmebaasis %s' % (ik, kasutaja.isikukood)
    
def bdoc_to_pdf(doc_data):
    f_in = io.BytesIO(doc_data)
    zf_in = ZipFile(f_in, mode='r')
    pdfdata = err = None
    for zfile in zf_in.namelist():
        if zfile.endswith('.pdf'):
            pdfdata = zf_in.read(zfile)
    zf_in.close()
    if not pdfdata:
        err = 'PDF puudub BDOCist'
    return pdfdata, err

def get_pdf_info(pdfdata):
    fpdf = io.BytesIO(pdfdata)
    reader = PdfReader(fpdf)
    info = reader.metadata
    fpdf.close()
    return info

def digidoc_validate(bdoc, dirname, ext):
    allowed_signer = registry.settings.get('sk.signer')
    if not allowed_signer:
        # allkirja valideerimist ei toimu
        return
    
    fname = dirname + '/tunnistus.%s' % ext
    f = open(fname, 'w')
    f.write(bdoc)
    f.close()
    tool = registry.settings.get('sk.digidoc-tool', 'digidoc-tool')    
    cmd = '"%s" open %s' % (tool, fname)
    
    fn_output = '%s/output' % (dirname)
    fn_error = '%s/error' % (dirname)
    cmd += '> %s 2>%s' % (fn_output, fn_error)
    log.debug(cmd)
    returncode = os.system(cmd)
    output = open(fn_output,'r').read()
    error = open(fn_error, 'r').read()
    if returncode or error:
        return 'Viga %s digidoc-tool kasutamisel: %s' % (returncode, error)

    in_signature = False
    signer = validation = None
    for line in output.splitlines():
        if line.startswith('  Signature '):
            in_signature = True
            signer = validation = None            
        elif in_signature:
            if line.startswith('    Signing cert:'):
                signer = line.split(':', 1)[1].strip()
            elif line.startswith('    Validation:'):
                validation = line.split(':', 1)[1].strip()

    if not signer:
        return 'Allkiri puudub'
    if validation != 'OK':
        return 'Allkiri ei kehti: %s' % validation
    if signer != allowed_signer:
        return 'Allkirjastanud "%s", oodatud "%s"' % (signer, allowed_signer)

def run():
    alates = datetime.now() - timedelta(minutes=1)
    prev_id = 0
    max_cnt = 10
    total = 0
    errors = list()

    dirname = '/srv/eis/var/data/tunnistusekontroll'
    try:
        os.stat(dirname)
    except:
        os.mkdir(dirname)
        
    while True:
        q = (model.Tunnistus.query
             .filter(model.Tunnistus.staatus==const.N_STAATUS_AVALDATUD)
             .filter(model.Tunnistus.fileversion!=None)
             .filter(~ model.Tunnistus.tunnistusekontroll.has(
                 model.Tunnistusekontroll.seisuga>alates))
             .filter(model.Tunnistus.id>prev_id)
             .order_by(model.Tunnistus.id)
             )
        cnt = 0
        for tunnistus in q.all():
            log.info('Tunnistus %s' % tunnistus.tunnistusenr)
            rc, err = kontroll(tunnistus, dirname)
            if not rc:
                errors.append('%s: %s' % (tunnistus.tunnistusenr, err)) 
            prev_id = tunnistus.id
            cnt += 1
            total += 1
            if cnt > max_cnt:
                break
        if cnt:
            model.Session.commit()
        else:
            break
        
    err_cnt = len(errors)
    buf = 'Kontrollitud %d tunnistust, leiti %d viga' % (total, err_cnt)
    log.info(buf)
    if err_cnt:
        msg = 'Leiti %s viga\n%s' % (err_cnt, '\n'.join(errors))
        script_error('Veateade (tunnistusekontroll)', None, msg)
        sys.exit(1)
        
if __name__ == '__main__':
    fn_lock = '/srv/eis/log/tunnistusekontroll.lock'
    with FileLock(fn_lock) as lock:
        if not lock:
            log.info('Protsess juba käib (fail %s on lukus)' % fn_lock)
            sys.exit(0)
        run()
    
