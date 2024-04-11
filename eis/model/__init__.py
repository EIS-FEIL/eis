"EISi andmemudel"

from eis.model import meta
Session = meta.Session
SessionR = meta.SessionR

def Session_begin():
    #Session.begin()
    pass

def initialize_sql(engine):
    # primary, read-write transaktsioonidele
    meta.Session.configure(bind=engine)

def initialize_read_sql(engine):
    # read-only replica
    meta.SessionR.configure(bind=engine)

from . import usersession
from .klassifikaator import *
from .opt import *
from .abiinfo import *
from .avaleheinfo import *
from .avaleheinfologi import *
from .avalehepilt import *
from .kasutaja import *
from .koht import *
from .ylesanne import *
from .test import *
from .arvutusprotsess import *
from .rveksam import *
from .testimine import *
from .kogu import *
from .deletefile import *
from .deletelog import *
from .testfail import *
from .eksam import *
from .seade import *
#from .potext import *
