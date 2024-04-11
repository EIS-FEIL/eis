import requests
import os
import uuid
from datetime import datetime
import eiscore.const as const
import eis.model_log as model_log
import logging
log = logging.getLogger(__name__)

def log_add(handler,
            tyyp,
            sisu,
            param, 
            kontroller=None,
            tegevus=None,
            isikukood=None,
            user=None,
            oppekoht_id=None,
            testiosa_id=None,
            kestus=None,
            url=None,
            method=None):
    #if tyyp != const.LOG_ERROR:
    #    return
    c = handler.c
    user = user or c and c.user or None
    if not isikukood and user:
        isikukood = user.isikukood

    koht_id = user and user.koht_id or None
    request = handler.request
    environ = request.environ
    log_uuid = uuid.uuid4().hex
    request_id = request.__hash__()
    data = dict(uuid=log_uuid,
                request_id=request_id,
                aeg=datetime.now(),
                isikukood=isikukood,
                kontroller=kontroller or c and c.controller,
                tegevus=tegevus or c and c.action,
                param=param,
                sisu=sisu,
                tyyp=tyyp,
                koht_id=koht_id,
                oppekoht_id=oppekoht_id,
                testiosa_id=testiosa_id,
                kestus=kestus,
                remote_addr=request.remote_addr,
                url=url or request.url,
                path=request.path,
                meetod=method or request.method,
                server_addr=os.getenv('HOSTNAME'),
                user_agent=environ.get('HTTP_USER_AGENT'),
                app=c.app_name)
    handler.request.logrows.append(data)
    return log_uuid

def flush_log(request):
    "Logikirjete salvestamine logibaasi pöördumise lõppedes"
    dt = datetime.now()
    # järjestame aja järgi, kuna ErrorController korral ei ole kirjed ajalises järjekorras
    for data in sorted(request.logrows, key=lambda r: r.get('aeg')):
        model_log.Logi.add_logrow(data)
    request.logrows = []
    model_log.DBSession.flush()
    model_log.DBSession.close()
    
    dt1 = datetime.now()
    d = (dt1-dt).total_seconds()
    if d > .1:
        log.debug(f'logimiseks {d}s')

