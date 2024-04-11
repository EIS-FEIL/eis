

from eis.scripts.scriptuser import *
from eis.lib.examsaga import ExamSaga
from eis.lib.examclient import ExamClient
from eis.lib.blockresponse import kratt_download

def get_exam():
    """Pooleli jäänud testisoorituste sooritusandmete tõmbamine eksamiklastritest põhibaasi,
    (et testi oleks vajadusel võimalik jätkata mõnes teises eksamiklastris)
    """
    q = (model.Session.query(model.Sooritus)
         .filter_by(klastrist_toomata=True))
    total = q.count()
    log.info(f'Klastrist toomata {total}')
    if total:
        cnt = 0
        min_id = 0
        saga = ExamSaga(handler)
        while True:
            sooritus = q.filter(model.Sooritus.id>min_id).order_by(model.Sooritus.id).first()
            if not sooritus:
                break
            min_id = sooritus.id
            sooritaja = sooritus.sooritaja
            exapi_host = model.Klaster.get_host(sooritaja.klaster_id)
            log.info(f'exam {cnt} / {total} #{sooritus.id} {exapi_host or "------"}')            
            if exapi_host:
                cnt += 1
                lang = sooritaja.lang
                test = sooritaja.test
                testiosa = sooritus.testiosa
                toimumisaeg = sooritus.toimumisaeg
                saga.from_examdb(exapi_host, sooritus, sooritaja, test, testiosa, toimumisaeg, lang, False)
                # funktsiooni sees tehti ka commit
        log.info(f'Toodud {cnt}')

def get_kratt():
    "Krati nende vastuste tõmbamine, mida kasutajaliidese tegevuste kaudu pole veel vaja olnud tõmmata"
    q = (model.Session.query(model.Kvsisu,
                             model.Sooritus.staatus,
                             model.Sooritaja.klaster_id)
         .join(model.Kvsisu.kysimusevastus)
         .filter(model.Kysimusevastus.sptyyp == const.INTER_KRATT)
         .filter(model.Kvsisu.koordinaat != None)
         .filter(model.Kvsisu.fileversion == None)
         .filter(sa.or_(model.Kvsisu.sisu == None, model.Kvsisu.sisu == ''))
         .join(model.Kysimusevastus.ylesandevastus)
         .join((model.Sooritus, model.Sooritus.id==model.Ylesandevastus.sooritus_id))
         .join(model.Sooritus.sooritaja)
         )
    total = q.count()
    log.info(f'Krati vastus toomata {total}')
    if total:
        cnt = 0
        min_id = 0
        while True:
            r = q.filter(model.Kvsisu.id > min_id).order_by(model.Kvsisu.id).first()
            if not r:
                break
            ks, staatus, klaster_id = r
            min_id = ks.id
            if ks.koordinaat and not ks.has_file:
                cnt += 1
                rc = kratt_download(handler, ks)
                log.info(f'kratt {cnt} / {total} ks {ks.id} st={staatus} - {rc}')
                if rc:
                    if klaster_id and staatus in (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD):
                        # uuendame ka klastris
                        klaster_id, host = model.Klaster.get_klaster(klaster_id)
                        if host:
                            # klaster on veel aktiivne
                            dks = RecordWrapper.create_from_dict(ks.pack_row(False))
                            ExamClient(handler, host).update_ks(dks)
                    model.Session.commit()
         
if __name__ == '__main__':
    op = named_args.get('op')
    if op == 'exam' or not op:
        get_exam()
    if op == 'kratt' or not op:
        get_kratt()
        
