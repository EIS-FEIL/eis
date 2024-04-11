import eiscore.const as const
from .tunnused1 import FeedbackDgmTunnused1
from .tunnused2 import FeedbackDgmTunnused2
from .tunnused3 import FeedbackDgmTunnused3
from .klassyl import FeedbackDgmKlassyl
from .hinnang import FeedbackDgmHinnang
from .barnp import FeedbackDgmBarnp
from .gtbl import FeedbackDgmGtbl
from .ktbl import FeedbackDgmKtbl
from .opyltbl import FeedbackDgmOpyltbl

def get_feedbackdgm(dname):
    if dname == const.DGM_TUNNUSED1:
        # 2018 õpilase tunnuste diagramm
        return FeedbackDgmTunnused1
    elif dname == const.DGM_TUNNUSED2:
        # 2018 rühma tunnuste diagramm
        return FeedbackDgmTunnused2    
    elif dname == const.DGM_TUNNUSED3:
        # 2021 klasside taseme tunnuste diagramm
        return FeedbackDgmTunnused3
    elif dname == const.DGM_HINNANG:
        # küsitluse vastuste diagramm rühmas
        return FeedbackDgmHinnang
    elif dname == const.DGM_KLASSYL:
        # klassi tulemuste diagramm ylesannete kaupa
        return FeedbackDgmKlassyl 
    elif dname == const.DGM_BARNP:
        # lintdiagramm 
        return FeedbackDgmBarnp
    elif dname == const.DGM_GTBL:
        # tabel
        return FeedbackDgmGtbl
    elif dname == const.DGM_KTBL:
        # tabel
        return FeedbackDgmKtbl        
    elif dname == const.DGM_OPYLTBL:
        # tabel
        return FeedbackDgmOpyltbl        

