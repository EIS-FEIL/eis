# -*- coding: utf-8 -*-
"PostgreSQLi kommentaaridest dokumentatsiooni genereerimine"
# python gen_gruppoigus.py > ../sql/init/kasutajagrupp_oigus.sql

from eis.scripts.scriptuser import *

import sqlalchemy as sa
import re

def gen():
    print("SELECT pg_catalog.set_config('search_path', 'public', false);")
    q = model.Kasutajagrupp_oigus.query.\
        order_by(model.Kasutajagrupp_oigus.kasutajagrupp_id,
                 model.Kasutajagrupp_oigus.nimi)
    for rcd in q.all():
        buf = 'INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,\n' +\
        ' kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) \n' +\
        " SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,\n" +\
        " g.id, o.id, o.nimi, g.tyyp, g.staatus, %d\n" % (rcd.bitimask) +\
        " FROM kasutajagrupp g, kasutajaoigus o \n"+\
        " WHERE g.id=%d AND o.nimi='%s';\n" % (rcd.kasutajagrupp_id, rcd.kasutajaoigus.nimi)

        print(buf)
   
if __name__ == '__main__':
    gen()

