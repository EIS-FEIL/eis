"Andmeklasside ühised omadused"

import eiscore.const as const
from eiscore.entitybase import *
from eis.model_log import DBSession, meta
import  eis.model.usersession as usersession
session = meta.DBSession

_ = usersession._
Base = declarative_base()
log = logging.getLogger(__name__)
    
class EntityHelper(EntityBase):
    """Andmeklasside olemite baasklass, mis lisab ühised meetodid
    """

    def get_userid(self):
        return usersession.get_userid()
