# -*- coding: utf-8 -*-
# $Id: boot.py 635 2010-05-10 05:05:00Z eeahtkeld $
"Arenduskeskkonnas kasutatav kood püsiandmete laadimiseks"

# andmebaasiühenduse loomine
from eis.config import connection
from eis import model

connection.CONF_FILE_NAME = 'development.ini'
connection.open()

# debug info
#model.metadata.bind.echo = True

#init()

def init():
    # andmete laadimine
    import eis.initdata as initdata
    initdata.insert_klassifikaator()
    model.Session.commit()
    model.Session.close()

