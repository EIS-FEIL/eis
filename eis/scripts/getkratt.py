"Krati vastuste tõmbamine krati serverist"

from eis.scripts.scriptuser import *
from eis.lib.examsaga import ExamSaga

def run():
    q = (model.Session.query(model.Sooritus)
         .filter_by(klastrist_toomata=True))
    total = q.count()
    log.info(f'Klastrist toomata {total}\n')
    if total:
        cnt = 0
        saga = ExamSaga(handler)
        while True:
            sooritus = q.order_by(model.Sooritus.id).first()
            if not sooritus:
                break
            sooritaja = sooritus.sooritaja
            exapi_host = model.Klaster.get_host(sooritaja.klaster_id)
            if exapi_host:
                cnt += 1
                log.info(f'{cnt} / {total} #{sooritus.id} {exapi_host}')            
                lang = sooritaja.lang
                test = sooritaja.test
                testiosa = sooritus.testiosa
                toimumisaeg = sooritus.toimumisaeg
                saga.from_examdb(exapi_host, sooritus, sooritaja, test, testiosa, toimumisaeg, lang, False)
                # funktsiooni sees tehti ka commit
        log.info(f'Toodud {cnt}')
             
if __name__ == '__main__':
    run()
