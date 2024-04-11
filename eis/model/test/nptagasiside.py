"Tagasiside diagnoosivas testis"
from eis.model.entityhelper import *
_ = usersession._
from .normipunkt import Normipunkt

class Nptagasiside(EntityHelper, Base):
    """Ülesandegrupi tingimus ja tagasiside tekst diagnoosivas testis või ülesandes
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    normipunkt_id = Column(Integer, ForeignKey('normipunkt.id'), index=True, nullable=False) # viide alatesti või testiülesandega seotud normipunkti tüübi kirjele
    normipunkt = relationship('Normipunkt', back_populates='nptagasisided')
    seq = Column(Integer, nullable=False) # tingimuse järjekorranumber (normipunktis)
    ahel_testiylesanne_id = Column(Integer, ForeignKey('testiylesanne.id'), index=True) # varasemate ülesannete ahelas olev ülesanne - kui tingimus kehtib ainult juhul, kui varasemas ahelas on teatud ülesanne
    ahel_testiylesanne = relationship('Testiylesanne', foreign_keys=ahel_testiylesanne_id, back_populates='ahel_nptagasisided')
    tingimus_tehe = Column(String(2)) # tingimuses kasutatav tehe <, <=, ==, >=, >
    tingimus_vaartus = Column(Float) # tingimuse võrdluse parema poole väärtus
    tingimus_valik = Column(String(100)) # tingimuse võrdluse paremal poolel olev valiku kood, kui vasakul on valikküsimuse kood (ülesande tagasiside korral)
    tagasiside = Column(Text) # sooritajale kuvatava tagasiside tekst
    op_tagasiside = Column(Text) # õpetajale kuvatava tagasiside tekst
    stat_tagasiside = Column(Text) # statistikas kasutatav tagasiside (grupi kohta)
    jatka = Column(Boolean) # kas peale lahendamist tuleb jätkata sama ülesannet (ülesande tagasiside korral - kui soovitakse lasta ülesannet lahendada seni, kuni vastab õigesti)
    uus_testiylesanne_id = Column(Integer, ForeignKey('testiylesanne.id'), index=True) # viide ülesandele, millele tingimuse täidetuse korral edasi minnakse, peab olema samas alatestis (diagnoosiva testi korral)
    uus_testiylesanne = relationship('Testiylesanne', foreign_keys=uus_testiylesanne_id, back_populates='uus_nptagasisided')        
    nsgrupp_id = Column(Integer, ForeignKey('nsgrupp.id'), index=True) # viide tagasiside grupile
    nsgrupp = relationship('Nsgrupp', back_populates='nptagasisided')
    trans = relationship('T_Nptagasiside', cascade='all', back_populates='orig')

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        if self.logging:
            np = self.normipunkt or self.normipunkt_id and Normipunkt.get(self.normipunkt_id)
            if np:
                np.logi('Tagasiside %s %s' % (self.id or '', liik), vanad_andmed, uued_andmed, logitase)
    
    @classmethod
    def opt_tehe(cls):
        return (('>', '>'),
                ('>=', '≥'),
                ('==', '='),
                ('<=', '≤'),
                ('<', '<'))

    @property
    def tingimus_tehe_ch(self):
        for r in Nptagasiside.opt_tehe():
            if r[0] == self.tingimus_tehe:
                return r[1]
    
    def copy(self, ignore=[], **di):
        cp = EntityHelper.copy(self, ignore=ignore, **di)
        self.copy_subrecords(cp, ['trans'])
        return cp

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        for rcd in self.trans:
            li.extend(rcd.pack(delete, modified))
        return li

    def delete_subitems(self):    
        from eis.model.eksam.npvastus import Npvastus
        q = Session.query(Npvastus).filter_by(nptagasiside_id=self.id)
        for r in q.all():
            r.nptagasiside_id = None
        Session.flush()
