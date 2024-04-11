from .ainepdf import *
from .aspektihindemarkus import *
from .aspektihinne import *
#from .alatestisooritus import *
from .erikomplekt import *
from .erivajadus import *
from .hindamine import *
from .hindamisolek import *
from .hindamisprotokoll import *
#from .integritysig import *
from .kandideerimiskoht import *
from .khstatistika import *
from .kriteeriumihinne import *
from .kriteeriumivastus import *
from .ksmarkus import *
from .kvskann import *
from .kvstatistika import *
from .kysimusehindemarkus import *
from .kysimusehinne import *
from .kysimusestatistika import *
from .labivaatus import *
from .labiviija import *
from .labiviijaklass import *
from .labiviijaylesanne import *
from .nimekiri import *
from .nousolek import *
from .oppekoht import *
from .piirkond_kord import *
from .regkoht_kord import *
from .sooritaja import *
from .sooritus import *
from .sooritajalogi import *
from .soorituslogi import *
from .ruumifail import *
from .sisestuslogi import *
from .sisestusolek import *
from .skannfail import *
from .statistikaraport import *
from .statvastus_t import *
from .tagastusymbrik import *
from .tagastusymbrikuliik import *
from .tagastusymbrikuliik_hk import *
from .testiarvuti import *
from .testikoht import *
from .testikonsultatsioon import *
from .testimiskord import *
from .testiopetaja import *
from .testipakett import *
from .testiparoolilogi import *
from .testiprotokoll import *
from .testiruum import *
from .testitunnistus import *
from .toimumisaeg import *
from .toimumisaeg_komplekt import *
from .toimumispaev import *
from .toimumisprotokoll import *
from .toovaataja import *
from .tunnistusekontroll import *
from .tunnistus import *
from .turvakott import *
from .vaie import *
from .vaideallkiri import *
from .vaidefail import *
from .vaidelogi import *
from .valjastusymbrik import *
from .valjastusymbrikuliik import *
from .vastusaspekt import *
from .ylesandehindemarkus import *
from .ylesandehinne import *
from .ylesandestatistika import *

def delete_test_sooritajad(test_id):
    "Testi kõigi sooritajate kiire kustutamine (tehtud eeltestide jaoks)"

    from eis.model.eksam import Kysimusevastus, Ylesandevastus, delete_eksam_test_sooritajad
    
    assert isinstance(test_id, int), 'vale test_id'
    testiosad_id = [r[0] for r in Session.query(Testiosa.id).filter_by(test_id=test_id).all()]
    if testiosad_id:
        li_stmt = (
            Sisestuslogi.__table__.delete().where(
                Sisestuslogi.hindamine_id.in_(
                    sa.select(Hindamine.id)
                    .join(Hindamine.hindamisolek)
                    .join(Hindamisolek.sooritus)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id)))
                ),
            Ksmarkus.__table__.delete().where(
                Ksmarkus.kysimusevastus_id.in_(
                    sa.select(Kysimusevastus.id)
                    .join(Kysimusevastus.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Kysimusehindemarkus.__table__.delete().where(
                Kysimusehindemarkus.kysimusehinne_id.in_(
                    sa.select(Kysimusehinne.id)
                    .join(Kysimusehinne.ylesandehinne)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Kysimusehinne.__table__.delete().where(
                Kysimusehinne.ylesandehinne_id.in_(
                    sa.select(Ylesandehinne.id)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Aspektihindemarkus.__table__.delete().where(
                Aspektihindemarkus.aspektihinne_id.in_(
                    sa.select(Aspektihinne.id)
                    .join(Aspektihinne.ylesandehinne)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Aspektihinne.__table__.delete().where(
                Aspektihinne.ylesandehinne_id.in_(
                    sa.select(Ylesandehinne.id)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Ylesandehindemarkus.__table__.delete().where(
                Ylesandehindemarkus.ylesandehinne_id.in_(
                    sa.select(Ylesandehinne.id)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Ylesandehinne.__table__.delete().where(
                Ylesandehinne.ylesandevastus_id.in_(
                    sa.select(Ylesandevastus.id)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Kvskann.__table__.delete().where(
                Kvskann.kysimusevastus_id.in_(
                    sa.select(Kysimusevastus.id)
                    .join(Kysimusevastus.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Vastusaspekt.__table__.delete().where(
                Vastusaspekt.ylesandevastus_id.in_(
                    sa.select(Ylesandevastus.id)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Labivaatus.__table__.delete().where(
                Labivaatus.hindamine_id.in_(
                    sa.select(Hindamine.id)
                    .join(Hindamine.hindamisolek)
                    .join(Hindamisolek.sooritus)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Hindamine.__table__.delete().where(
                Hindamine.hindamisolek_id.in_(
                    sa.select(Hindamisolek.id)
                    .join(Hindamisolek.sooritus)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Hindamisolek.__table__.delete().where(
                Hindamisolek.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Erikomplekt.__table__.delete().where(
                Erikomplekt.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Erivajadus.__table__.delete().where(
                Erivajadus.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Sisestusolek.__table__.delete().where(
                Sisestusolek.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            Soorituslogi.__table__.delete().where(
                Soorituslogi.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.testiosa_id.in_(testiosad_id))
                    )
                ),
            )
        log.info('Delete1 sooritajad, test %s, testiosa %s' % (test_id, testiosad_id))
        for ind, stmt in enumerate(li_stmt):
            log.debug(str(stmt))
            res = Session.execute(stmt)
            if res.rowcount:
                log.info('%s: deleted %d rows' % (stmt.table.name, res.rowcount))

        delete_eksam_test_sooritajad(test_id)
        
        li_stmt = (
            Sooritus.__table__.delete().where(
                Sooritus.testiosa_id.in_(testiosad_id)
                ),
            Sooritajakiri.__table__.delete().where(
                Sooritajakiri.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.test_id==test_id)
                    )
                ),
            Toovaataja.__table__.delete().where(
                Toovaataja.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.test_id==test_id)
                    )
                ),
            Sooritajalogi.__table__.delete().where(
                Sooritajalogi.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.test_id==test_id)
                    )
                ),
            Kandideerimiskoht.__table__.delete().where(
                Kandideerimiskoht.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.test_id==test_id)
                    )
                ),
            Oppekoht.__table__.delete().where(
                Oppekoht.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.test_id==test_id)
                    )
                ),
            Kandideerimiskoht.__table__.delete().where(
                Kandideerimiskoht.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.test_id==test_id)
                    )
                ),
            Testiopetaja.__table__.delete().where(
                Testiopetaja.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.test_id==test_id)
                    )
                ),
            Testiparoolilogi.__table__.delete().where(
                Testiparoolilogi.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.test_id==test_id)
                    )
                ),
            Sooritaja.__table__.delete().where(
                Sooritaja.test_id==test_id),
            )
        log.info('Delete2 sooritajad, test %s, testiosa %s' % (test_id, testiosad_id))
        for ind, stmt in enumerate(li_stmt):
            log.debug(str(stmt))
            res = Session.execute(stmt)
            if res.rowcount:
                log.info('%s: deleted %d rows' % (stmt.table.name, res.rowcount))

def delete_testimiskord_sooritajad(kord_id):
    "Testimiskorra kõigi sooritajate kiire kustutamine"
    from eis.model.eksam import Kysimusevastus, Ylesandevastus, delete_eksam_testimiskord_sooritajad
    
    assert isinstance(kord_id, int), 'vale kord_id'
    toimumisajad_id = [r[0] for r in Session.query(Toimumisaeg.id).filter_by(testimiskord_id=kord_id).all()]
    if toimumisajad_id:
        li_stmt = (
            Sisestuslogi.__table__.delete().where(
                Sisestuslogi.hindamine_id.in_(
                    sa.select(Hindamine.id)
                    .join(Hindamine.hindamisolek)
                    .join(Hindamisolek.sooritus)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))
                )
            ),
            Ksmarkus.__table__.delete().where(
                Ksmarkus.kysimusevastus_id.in_(
                    sa.select(Kysimusevastus.id)
                    .join(Kysimusevastus.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))
                )
            ),
            Kysimusehindemarkus.__table__.delete().where(
                Kysimusehindemarkus.kysimusehinne_id.in_(
                    sa.select(Kysimusehinne.id)
                    .join(Kysimusehinne.ylesandehinne)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                        
                )
            ),
            Kysimusehinne.__table__.delete().where(
                Kysimusehinne.ylesandehinne_id.in_(
                    sa.select(Ylesandehinne.id)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                            
                    )
                ),
            Aspektihindemarkus.__table__.delete().where(
                Aspektihindemarkus.aspektihinne_id.in_(
                    sa.select(Aspektihinne.id)
                    .join(Aspektihinne.ylesandehinne)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                            
                    )
                ),
            Aspektihinne.__table__.delete().where(
                Aspektihinne.ylesandehinne_id.in_(
                    sa.select(Ylesandehinne.id)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                                                
                    )
                ),
            Ylesandehindemarkus.__table__.delete().where(
                Ylesandehindemarkus.ylesandehinne_id.in_(
                    sa.select(Ylesandehinne.id)
                    .join(Ylesandehinne.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Ylesandehinne.__table__.delete().where(
                Ylesandehinne.ylesandevastus_id.in_(
                    sa.select(Ylesandevastus.id)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                    
                    )
                ),
            Kvskann.__table__.delete().where(
                Kvskann.kysimusevastus_id.in_(
                    sa.select(Kysimusevastus.id)
                    .join(Kysimusevastus.ylesandevastus)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Vastusaspekt.__table__.delete().where(
                Vastusaspekt.ylesandevastus_id.in_(
                    sa.select(Ylesandevastus.id)
                    .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                        
                    )
                ),
            Labivaatus.__table__.delete().where(
                Labivaatus.hindamine_id.in_(
                    sa.select(Hindamine.id)
                    .join(Hindamine.hindamisolek)
                    .join(Hindamisolek.sooritus)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                            
                    )
                ),
            Hindamine.__table__.delete().where(
                Hindamine.hindamisolek_id.in_(
                    sa.select(Hindamisolek.id)
                    .join(Hindamisolek.sooritus)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                            
                    )
                ),
            Hindamisolek.__table__.delete().where(
                Hindamisolek.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                            
                    )
                ),
            Erikomplekt.__table__.delete().where(
                Erikomplekt.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                            
                    )
                ),
            Erivajadus.__table__.delete().where(
                Erivajadus.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                            
                    )
                ),
            Sisestusolek.__table__.delete().where(
                Sisestusolek.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                            
                    )
                ),
        )
        log.info('Delete1 sooritajad, testimiskord %s, toimumisajad %s' % (kord_id, toimumisajad_id))
        for ind, stmt in enumerate(li_stmt):
            log.debug(str(stmt))
            res = Session.execute(stmt)
            if res.rowcount:
                log.info('%s: deleted %d rows' % (stmt.table.name, res.rowcount))

        delete_eksam_testimiskord_sooritajad(kord_id)
                
        li_stmt = (
            Soorituslogi.__table__.delete().where(
                Soorituslogi.sooritus_id.in_(
                    sa.select(Sooritus.id)
                    .filter(Sooritus.toimumisaeg_id.in_(toimumisajad_id))                                                            
                    )
                ),
            Sooritus.__table__.delete().where(
                Sooritus.toimumisaeg_id.in_(toimumisajad_id)
                ),
            Sooritajakiri.__table__.delete().where(
                Sooritajakiri.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.testimiskord_id==kord_id)
                    )
                ),
            Toovaataja.__table__.delete().where(
                Toovaataja.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.testimiskord_id==kord_id)
                    )
                ),
            Sooritajalogi.__table__.delete().where(
                Sooritajalogi.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.testimiskord_id==kord_id)
                    )
                ),
            Kandideerimiskoht.__table__.delete().where(
                Kandideerimiskoht.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.testimiskord_id==kord_id)
                    )
                ),
            Oppekoht.__table__.delete().where(
                Oppekoht.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.testimiskord_id==kord_id)
                    )
                ),
            Testiopetaja.__table__.delete().where(
                Testiopetaja.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.testimiskord_id==kord_id)
                    )
                ),
            Testiparoolilogi.__table__.delete().where(
                Testiparoolilogi.sooritaja_id.in_(
                    sa.select(Sooritaja.id)
                    .filter(Sooritaja.testimiskord_id==kord_id)
                    )
                ),
            Sooritaja.__table__.delete().where(
                Sooritaja.testimiskord_id==kord_id),
            )
        log.info('Delete2 sooritajad, testimiskord %s, toimumisajad %s' % (kord_id, toimumisajad_id))
        for ind, stmt in enumerate(li_stmt):
            log.debug(str(stmt))
            res = Session.execute(stmt)
            if res.rowcount:
                log.info('%s: deleted %d rows' % (stmt.table.name, res.rowcount))

def delete_test_statistika(test_id):
    "Testi statistika kiire kustutamine"
    assert isinstance(test_id, int), 'vale test_id'
    testiosad_id = [r[0] for r in Session.query(Testiosa.id).filter_by(test_id=test_id).all()]
    if testiosad_id:
        li_stmt = (
            Khstatistika.__table__.delete().where(
                Khstatistika.kysimusestatistika_id.in_(
                    sa.select(Kysimusestatistika.id)
                    .filter(Kysimusestatistika.testiosa_id.in_(testiosad_id))
                    )
                ),
            Kvstatistika.__table__.delete().where(
                Kvstatistika.kysimusestatistika_id.in_(
                    sa.select(Kysimusestatistika.id)
                    .filter(Kysimusestatistika.testiosa_id.in_(testiosad_id))
                    )
                ),
            Kysimusestatistika.__table__.delete().where(
                Kysimusestatistika.testiosa_id.in_(testiosad_id)
                ),
            Ylesandestatistika.__table__.delete().where(
                Ylesandestatistika.valitudylesanne_id.in_(
                    sa.select(Valitudylesanne.id)
                    .join(Valitudylesanne.testiylesanne)
                    .filter(Testiylesanne.testiosa_id.in_(testiosad_id))
                    )
                )
            )
        for ind, stmt in enumerate(li_stmt):
            log.debug(str(stmt))
            res = Session.execute(stmt)
            if res.rowcount:
                log.info('%s: deleted %d rows' % (stmt.table.name, res.rowcount))            

def delete_testimiskord_statistika(kord_id):
    "Testimiskorra statistika kiire kustutamine"
    assert isinstance(kord_id, int), 'vale kord_id'
    toimumisajad_id = [r[0] for r in Session.query(Toimumisaeg.id).filter_by(testimiskord_id=kord_id).all()]
    if toimumisajad_id:
        li_stmt = (
            Khstatistika.__table__.delete().where(
                Khstatistika.kysimusestatistika_id.in_(
                    sa.select(Kysimusestatistika.id)
                    .filter(Kysimusestatistika.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Kvstatistika.__table__.delete().where(
                Kvstatistika.kysimusestatistika_id.in_(
                    sa.select(Kysimusestatistika.id)
                    .filter(Kysimusestatistika.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Kysimusestatistika.__table__.delete().where(
                Kysimusestatistika.toimumisaeg_id.in_(toimumisajad_id)
                ),
            
            Ylesandestatistika.__table__.delete().where(
                Ylesandestatistika.toimumisaeg_id.in_(toimumisajad_id)
                )
            )

        for ind, stmt in enumerate(li_stmt):
            log.debug(str(stmt))
            res = Session.execute(stmt)
            if res.rowcount:
                log.info('%s: deleted %d rows' % (stmt.table.name, res.rowcount))            

def delete_test_testikohad(test_id):
    "Testi soorituskohtade kiire kustutamine (eeldusel, et sooritajad on juba kustutatud)"
    assert isinstance(test_id, int), 'vale test_id'
    testiosad_id = [r[0] for r in Session.query(Testiosa.id).filter_by(test_id=test_id).all()]
    if testiosad_id:
        li_stmt = (
            Ruumifail.__table__.delete().where(
                Ruumifail.toimumisprotokoll_id.in_(
                    sa.select(Toimumisprotokoll.id)
                    .join(Toimumisprotokoll.testikoht)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Toimumisprotokoll.__table__.delete().where(
                Toimumisprotokoll.testikoht_id.in_(
                    sa.select(Testikoht.id)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Turvakott.__table__.delete().where(
                Turvakott.testipakett_id.in_(
                    sa.select(Testipakett.id)
                    .join(Testipakett.testikoht)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Valjastusymbrik.__table__.delete().where(
                Valjastusymbrik.testipakett_id.in_(
                    sa.select(Testipakett.id)
                    .join(Testipakett.testikoht)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Tagastusymbrik.__table__.delete().where(
                Tagastusymbrik.testipakett_id.in_(
                    sa.select(Testipakett.id)
                    .join(Testipakett.testikoht)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Testiprotokoll.__table__.delete().where(
                Testiprotokoll.testiruum_id.in_(
                    sa.select(Testiruum.id)
                    .join(Testiruum.testikoht)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Testipakett.__table__.delete().where(
                Testipakett.testikoht_id.in_(
                    sa.select(Testikoht.id)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Labiviijakiri.__table__.delete().where(
                Labiviijakiri.labiviija_id.in_(
                    sa.select(Labiviija.id)
                    .join(Labiviija.testikoht)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Labiviija.__table__.delete().where(
                Labiviija.testikoht_id.in_(
                    sa.select(Testikoht.id)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Testiarvuti.__table__.delete().where(
                Testiarvuti.testiruum_id.in_(
                    sa.select(Testiruum.id)
                    .join(Testiruum.testikoht)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Testiruum.__table__.delete().where(
                Testiruum.testikoht_id.in_(
                    sa.select(Testikoht.id)
                    .filter(Testikoht.testiosa_id.in_(testiosad_id))
                    )
                ),
            Testikoht.__table__.delete().where(
                Testikoht.testiosa_id.in_(testiosad_id),
                )
            )
        for ind, stmt in enumerate(li_stmt):
            log.debug(str(stmt))
            res = Session.execute(stmt)
            if res.rowcount:
                log.info('%s: deleted %d rows' % (stmt.table.name, res.rowcount))            
            
            
def delete_testimiskord_testikohad(kord_id):
    "Testi soorituskohtade kiire kustutamine (eeldusel, et sooritajad on juba kustutatud)"
    assert isinstance(kord_id, int), 'vale kord_id'
    toimumisajad_id = [r[0] for r in Session.query(Toimumisaeg.id).filter_by(testimiskord_id=kord_id).all()]
    if toimumisajad_id:
        li_stmt = (
            Ruumifail.__table__.delete().where(
                Ruumifail.toimumisprotokoll_id.in_(
                    sa.select(Toimumisprotokoll.id)
                    .join(Toimumisprotokoll.testikoht)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Toimumisprotokoll.__table__.delete().where(
                Toimumisprotokoll.testikoht_id.in_(
                    sa.select(Testikoht.id)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Testiprotokoll.__table__.delete().where(
                Testiprotokoll.testiruum_id.in_(
                    sa.select(Testiruum.id)
                    .join(Testiruum.testikoht)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Turvakott.__table__.delete().where(
                Turvakott.testipakett_id.in_(
                    sa.select(Testipakett.id)
                    .join(Testipakett.testikoht)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Valjastusymbrik.__table__.delete().where(
                Valjastusymbrik.testipakett_id.in_(
                    sa.select(Testipakett.id)
                    .join(Testipakett.testikoht)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Tagastusymbrik.__table__.delete().where(
                Tagastusymbrik.testipakett_id.in_(
                    sa.select(Testipakett.id)
                    .join(Testipakett.testikoht)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Testipakett.__table__.delete().where(
                Testipakett.testikoht_id.in_(
                    sa.select(Testikoht.id)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))

                    )
                ),
            Labiviijakiri.__table__.delete().where(
                Labiviijakiri.labiviija_id.in_(
                    sa.select(Labiviija.id)
                    .join(Labiviija.testikoht)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Labiviija.__table__.delete().where(
                Labiviija.testikoht_id.in_(
                    sa.select(Testikoht.id)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Testiarvuti.__table__.delete().where(
                Testiarvuti.testiruum_id.in_(
                    sa.select(Testiruum.id)
                    .join(Testiruum.testikoht)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Testiruum.__table__.delete().where(
                Testiruum.testikoht_id.in_(
                    sa.select(Testikoht.id)
                    .filter(Testikoht.toimumisaeg_id.in_(toimumisajad_id))
                    )
                ),
            Testikoht.__table__.delete().where(
                Testikoht.toimumisaeg_id.in_(toimumisajad_id),
                )
            )
        for ind, stmt in enumerate(li_stmt):
            log.debug(str(stmt))
            res = Session.execute(stmt)
            if res.rowcount:
                log.info('%s: deleted %d rows' % (stmt.table.name, res.rowcount))            
            
            
            
    
