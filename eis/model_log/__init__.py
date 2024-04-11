# -*- coding: utf-8 -*-
"Logi andmebaas"

from eis.model_log import meta
DBSession = meta.DBSession

def initialize_sql(engine):
    meta.DBSession.configure(bind=engine)

from .logi import Logi
from .logi_adapter import Logi_adapter
from .ltest import Ltest
from .taralog import Taralog
from .haridlog import Haridlog
