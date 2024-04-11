"Eksamisoorituste andmebaas"

from eis.model import meta
Session = meta.Session

import eis.model.usersession as usersession
from .alatestisooritus import *
from .alatestisoorituslogi import *
from .helivastusfail import *
from .helivastus import *
from .kvsisu import *
from .kysimusevastus import *
from .loendur import *
from .npvastus import *
from .seblog import *
from .sisuvaatamine import *
from .soorituskomplekt import *
from .ylesandevastus import *
from .proctoriolog import *
from .verifflog import *

from eis.model.testimine import Sooritus, Sooritaja

def delete_eksam_test_sooritajad(test_id):
    "Testi kõigi sooritajate kiire kustutamine (tehtud eeltestide jaoks)"
    assert isinstance(test_id, int), 'vale test_id'
    li_stmt = (
        Sisuvaatamine.__table__.delete().where(
            Sisuvaatamine.ylesandevastus_id.in_(
                sa.select(Ylesandevastus.id)
                .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)
            )
        ),
        Kvsisu.__table__.delete().where(
            Kvsisu.kysimusevastus_id.in_(
                sa.select(Kysimusevastus.id)
                .join(Kysimusevastus.ylesandevastus)
                .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)
            )
        ),
        Kysimusevastus.__table__.delete().where(
            Kysimusevastus.ylesandevastus_id.in_(
                sa.select(Ylesandevastus.id)
                .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)
            )
        ),
        Loendur.__table__.delete().where(
            Loendur.ylesandevastus_id.in_(
                sa.select(Ylesandevastus.id)
                .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)
            )
        ),
        Npvastus.__table__.delete().where(
            Npvastus.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)                
            )
        ),
        Ylesandevastus.__table__.delete().where(
            Ylesandevastus.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)                                
            )
        ),
        Helivastus.__table__.delete().where(
            Helivastus.sooritus_id.in_(
                sa.select(Sooritus.id)
                .filter(Sooritus.testiosa_id.in_(testiosad_id))
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)                                                
            )
        ),
        Alatestisoorituslogi.__table__.delete().where(
            Alatestisoorituslogi.alatestisooritus_id.in_(
                sa.select(Alatestisooritus.id)
                .join(Sooritus, Alatestisooritus.sooritus_id==Sooritus.id)
            )
        ),
        Alatestisooritus.__table__.delete().where(
            Alatestisooritus.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)                                                                    
            )
        ),
        Seblog.__table__.delete().where(
            Seblog.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)
            )
        ),
        Soorituskomplekt.__table__.delete().where(
            Soorituskomplekt.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.test_id==test_id)
            )
        ),
    )
    log.info(f'Delete sooritajad, test {test_id}')
    rowcount = 0
    for ind, stmt in enumerate(li_stmt):
        log.debug(str(stmt))
        res = Session.execute(stmt)
        rowcount = res.rowcount
        if rowcount:
            log.info('%s: deleted %d rows' % (stmt.table.name, rowcount))

    # tagastame kustutatud sooritaja-kirjete arvu
    return rowcount

def delete_eksam_testimiskord_sooritajad(kord_id):
    "Testimiskorra kõigi sooritajate kiire kustutamine"
    assert isinstance(kord_id, int), 'vale kord_id'
    li_stmt = (
        Sisuvaatamine.__table__.delete().where(
            Sisuvaatamine.ylesandevastus_id.in_(
                sa.select(Ylesandevastus.id)
                .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)
            )
        ),
        Kvsisu.__table__.delete().where(
            Kvsisu.kysimusevastus_id.in_(
                sa.select(Kysimusevastus.id)
                .join(Kysimusevastus.ylesandevastus)
                .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)
            )
        ),
        Kysimusevastus.__table__.delete().where(
            Kysimusevastus.ylesandevastus_id.in_(
                sa.select(Ylesandevastus.id)
                .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)
            )
        ),
        Loendur.__table__.delete().where(
            Loendur.ylesandevastus_id.in_(
                sa.select(Ylesandevastus.id)
                .join(Sooritus, Sooritus.id==Ylesandevastus.sooritus_id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)
            )
        ),
        Npvastus.__table__.delete().where(
            Npvastus.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)                
            )
        ),
        Ylesandevastus.__table__.delete().where(
            Ylesandevastus.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)                
            )
        ),
        Helivastus.__table__.delete().where(
            Helivastus.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)                
            )
        ),
        Alatestisoorituslogi.__table__.delete().where(
            Alatestisoorituslogi.alatestisooritus_id.in_(
                sa.select(Alatestisooritus.id)
                .join(Sooritus, Alatestisooritus.sooritus_id==Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)                
            )
        ),
        Alatestisooritus.__table__.delete().where(
            Alatestisooritus.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)                
            )
        ),
        Seblog.__table__.delete().where(
            Seblog.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)                
            )
        ),
        Soorituskomplekt.__table__.delete().where(
            Soorituskomplekt.sooritus_id.in_(
                sa.select(Sooritus.id)
                .join(Sooritaja, Sooritaja.id==Sooritus.sooritaja_id)
                .filter(Sooritaja.testimiskord_id==kord_id)                
            )
        ),
    )
    log.info(f'Delete sooritajad testimiskord {kord_id}')
    rowcount = 0
    for ind, stmt in enumerate(li_stmt):
        log.debug(str(stmt))
        res = Session.execute(stmt)
        rowcount = res.rowcount
        if rowcount:
            log.info('%s: deleted %d rows' % (stmt.table.name, rowcount))

    # tagastame kustutatud sooritaja-kirjete arvu
    return rowcount
