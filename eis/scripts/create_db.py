"""Andmebaasi loomine
   Kasuta kujul:

   python -m eis.scripts.create_db tmp/development.dbg.ini
   python create_db.py ../../tmp/development.dbg.ini
"""
import logging.config
import os
import sys
import transaction
from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

import eis.model as model
import eis.model_s as model_s
import eis.model_log as model_log
try:
    import eis.model.plank
except:
    pass
from eis.lib.user import User
from . import initdata

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m eis.scripts.create_db INI_FILE")

    config_uri = sys.argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    model.Session.configure(bind=engine)
    model.Base.metadata.create_all(engine)
    if model.Session.query(model.Klrida).count() == 0:
        model.usersession.set_user(AdminUser())
        initdata.insert()
        model.Session.flush()
        model.Session.commit()
        
    engine_s = engine_from_config(settings, 'sqlalchemy_s.')
    model_s.DBSession.configure(bind=engine_s)
    model_s.meta.Base.metadata.create_all(engine_s)

    engine_log = engine_from_config(settings, 'sqlalchemy_log.')
    model_log.DBSession.configure(bind=engine_log)
    model_log.meta.Base.metadata.create_all(engine_log)

class AdminUser(User):
    def __init__(self):
        self.isikukood = 'ADMIN'  
        self.id = 1
        self.app_ekk = True

if __name__ == "__main__":  
    main()
