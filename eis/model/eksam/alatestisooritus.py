"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from .ylesandevastus import Ylesandevastus
from .alatestisoorituslogi import Alatestisoorituslogi

_ = usersession._

class Alatestisooritus(EntityHelper, Base):
    """Piirajaga alatesti sooritamine
    """
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, index=True, nullable=False) # viide sooritusele
    alatest_id = Column(Integer, index=True, nullable=False) # viide alatestile
    algus = Column(DateTime) # soorituse esimese seansi algus
    lopp = Column(DateTime) # soorituse viimase seansi lõpp
    seansi_algus = Column(DateTime) # soorituse viimase seansi algus
    lisaaeg = Column(Integer) # sooritajale antud lisaaeg, lisandub testiosa piirajale
    ajakulu = Column(Integer) # kulutatud sekundite arv kõigi lõpetatud seansside peale kokku
    staatus = Column(Integer, nullable=False) # olek: 3=const.S_STAATUS_REGATUD - registreeritud; 5=const.S_STAATUS_ALUSTAMATA - alustamata; 6=const.S_STAATUS_POOLELI - pooleli; 7=const.S_STAATUS_KATKESTATUD - katkestatud; 8=const.S_STAATUS_TEHTUD - tehtud; 9=const.S_STAATUS_EEMALDATUD - eemaldatud; 10=const.S_STAATUS_PUUDUS - puudus; 11=const.S_STAATUS_VABASTATUD - vabastatud
    yl_arv = Column(Integer) # ülesannete arv alatestis sooritaja poolt valitud komplektis
    tehtud_yl_arv = Column(Integer) # ülesannete arv, milles on vähemalt mõnele küsimusele vastatud
    lopetatud_yl_arv = Column(Integer) # ülesannete arv, milles on kõigile küsimustele kohustuslik arv vastuseid antud
    pallid = Column(Float) # saadud hindepallid
    pallid_enne_vaiet = Column(Float) # hindepallid enne vaidlustamist
    tulemus_protsent = Column(Float) # saadud hindepallid protsentides suurimast võimalikust tulemusest
    max_pallid = Column(Float) # max pallid (lõdva struktuuri korral sõltub valitud komplektist)
    oigete_arv = Column(Integer) # õigete vastuste arv (koolipsühholoogitesti jaoks)
    valede_arv = Column(Integer) # valede vastuste arv (koolipsühholoogitesti jaoks)
    valimata_valede_arv = Column(Integer) # valimata valede vastuste arv, sisaldub õigete arvus (koolipsühholoogitesti jaoks)
    valimata_oigete_arv = Column(Integer) # valimata valede vastuste arv, sisaldub valede arvus (koolipsühholoogitesti jaoks)    
    oigete_suhe = Column(Float) # õigete vastuste suhe kõikidesse vastustesse (koolipsühholoogitesti jaoks)
    viimane_valitudylesanne_id = Column(Integer, index=True) # viimane vaadatud valitudylesanne
    viimane_testiylesanne_id = Column(Integer, index=True) # viimane vaadatud testiylesanne
    valikujrk = Column(ARRAY(Integer)) # ülesannete järjekord antud alatestisoorituses (kui on juhusliku järjekorraga alatest)
    alatestisoorituslogid = relationship('Alatestisoorituslogi', order_by='Alatestisoorituslogi.created', back_populates='alatestisooritus')
    __table_args__ = (
        sa.UniqueConstraint('sooritus_id','alatest_id'),
        )

    _parent_key = 'sooritus_id'
    _logi = None # jooksva tegevuse logikirje
    
    @property
    def staatus_nimi(self):
        return usersession.get_opt().S_STAATUS.get(self.staatus)

    @property
    def alatest(self):
        from eis.model.test.alatest import Alatest
        return Alatest.get(self.alatest_id)
        
    def get_tulemus(self, max_pallid=None, digits=3):
        if self.pallid is not None:
            pallid = self.pallid
            max_p = self.max_pallid
            if not max_p:
                return fstr(self.pallid, digits)
            return _('{p1}p {p2}-st, {p3}%').format(
                p1=fstr(pallid, digits), 
                p2=fstr(max_p, digits), 
                p3=fstr(pallid*100/max_p, digits))
        
    def delete_subitems(self):    
        self.delete_subrecords(['alatestisoorituslogid',
                                ])
    def log_update(self):
        log_fields = ('staatus',
                      'pallid')
        old_values, new_values = self._get_changed_values()
        if new_values:
            fields = [r[0] for r in new_values]
            found = False
            for key in log_fields:
                if key in fields:
                    found = True
                    break
            if found:
                self.add_soorituslogi()
                
    def log_insert(self):
        self.add_soorituslogi()

    def add_soorituslogi(self):
        request = usersession.get_request()
        if request:
            environ = request.environ
            remote_addr = request.remote_addr
        else:
            environ = {}
            remote_addr = None
        server_addr = environ.get('HOSTNAME') or environ.get('SERVER_ADDR')
        if self._logi:
            self._logi.staatus = self.staatus
            self._logi.pallid = self.pallid
        else:
            self._logi = \
                Alatestisoorituslogi(alatestisooritus=self,
                                     staatus=self.staatus,
                                     pallid=self.pallid,
                                     url=request and request.url[:100] or None,                            
                                     remote_addr=remote_addr,
                                     server_addr=server_addr)
