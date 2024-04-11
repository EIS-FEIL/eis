"JSON teenuse osutamine"

from datetime import date, datetime
from webob import Response
from eis.handlers.adapter import AdapterHandler
from eis.model_log import Logi_adapter
import logging
log = logging.getLogger(__name__)

class BadParameter(Exception):
    def __init__(self, name, error=None):
        self.name = name
        self.error = error
        
def serve_json(request, service_name, f_args, f_run):
    "JSON teenuse osutamine"
    started = datetime.now()    
    status_code = 400 # bad request
    error = res = None
    try:
        args = f_args(request)
        status_code = 500
        res = f_run(args)
    except BadParameter as ex:
        log.error(ex)
        error = f'bad parameters: {ex.name}'
    except Exception as ex:
        handler = AdapterHandler(request)
        handler._error(ex, str(ex))
        if status_code == 400:
            error = 'bad parameters'
        else:
            error = 'error occurred'
    if error:
        request.response.status_code = status_code
        res = {'error': error}
    log_msg(service_name, None, res, started, request)
    return Response(json_body=res)

def log_msg(service, input_json, output_json, started, request):
    "Sisendi ja väljundi logimine"
    headers = request.headers
    client_str = headers.get('X-Road-Client')
    userid = headers.get('X-Road-UserId') or None
    input_data = input_json and str(input_json) or None
    output_data = output_json and str(output_json) or None
    tyyp = Logi_adapter.TYYP_JSON
    Logi_adapter.add(client_str, userid, service, input_data, output_data, started, request, tyyp)

def jsondate(obj):
    "Kuupäeva teisendamine JSONi jaoks tekstiks"
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
