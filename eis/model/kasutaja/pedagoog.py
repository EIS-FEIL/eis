# -*- coding: utf-8 -*-
from eis.model.entityhelper import *
from eis.model.koht import Koht
from .ainepedagoog import Ainepedagoog

log = logging.getLogger(__name__)

class Pedagoog(EntityHelper, Base):
    """Õppeasutuste töötajate andmed, kopeeritakse EHISest
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukood = Column(String(50), index=True) # isikukood
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # kasutaja
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='pedagoogid')
    eesnimi = Column(String(50)) # eesnimi
    perenimi = Column(String(50)) # perekonnanimi
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # õppeasutus (puudub siis, kui EISis on koolide andmed uuendamata ja vahepeal on EHISesse uus kool lisatud
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='pedagoogid') 
    kool_id = Column(Integer) # kooli ID EHISes (puudub siis, kui kool ei ole EHISes - seda võib juhtuda ainult juhul, kui ka töötamise andmed ei ole võetud EHISest, vaid sisestatud käsitsi)
    seisuga = Column(DateTime) # viimane EHISest andmete kontrollimise aeg (sellise päringuga, mis ei tehtud kindla kooliastme ega õppeaine järgi)
    kehtib_kuni = Column(Date) # rolli kehtivuse lõppkuupäev (EISis käsitsi lisatud rolli korral)
    kasutajagrupp_id = Column(Integer, ForeignKey('kasutajagrupp.id'), index=True) # viide kasutajagrupile: 56=const.GRUPP_K_JUHT - koolijuht (soorituskoha admin, foreign_keys=kasutajagrupp_id); 25=const.GRUPP_OPETAJA - tavaline õpetaja
    kasutajagrupp = relationship('Kasutajagrupp', foreign_keys=kasutajagrupp_id, back_populates='pedagoogid')
    on_ehisest = Column(Boolean, sa.DefaultClause('1')) # kas andmed on pärit EHISest (kui pole, siis seda kirjet EHISe päringu tulemuse põhjal ei kustutata)
    ainepedagoogid = relationship('Ainepedagoog', back_populates='pedagoog')
    
    __table_args__ = (
        sa.UniqueConstraint('kasutaja_id', 'kool_id', 'koht_id'),
        )

    @property
    def nimi(self):
        return ('%s %s' % (self.eesnimi or '', self.perenimi or '')).strip()

    def has_permission(self, permission, perm_bit):
        """Kas kasutajal on õigus?
        """
        return self.kasutajagrupp and \
            self.kasutajagrupp.has_permission(permission, perm_bit) or False

    def get_str(self):
        li = []
        if self.kasutajagrupp_id == const.GRUPP_K_JUHT:
            li.append('Koolijuht')
        elif self.kasutajagrupp_id == const.GRUPP_OPETAJA:
            li.append('Pedagoog')
        koht = Koht.get(self.koht_id)
        if koht:
            li.append(koht.nimi)
        if self.kehtib_kuni and self.kehtib_kuni < const.MAX_DATE:
            li.append('kuni %s' % self.kehtib_kuni.strftime('%d.%m.%Y'))
        return ', '.join(li)

    def update_from_ehis(self, rcd, taielik=True):
        """Pedagoogi ametikohad uuendatakse EHISest küsitud andmetega.
        taielik - kas isiku kohta on kõik andmed kaasas
        (kui EHISe päring tehti kindla aine, astme või kooli kohta,
        siis ei ole täielik)
        """
        now = datetime.now()
        kool_id = int(rcd.koolId)
        koolijuht = _xbool(rcd.koolijuht)
        
        # muudame andmed
        self.on_ehisest = True
        self.kehtib_kuni = None
        if koolijuht:
            self.kasutajagrupp_id = const.GRUPP_K_JUHT
        else:
            self.kasutajagrupp_id = const.GRUPP_OPETAJA
                
        self.eesnimi = rcd.eesnimi
        self.perenimi = rcd.perenimi
        self.koht = (Koht.query
                     .filter_by(kool_id=kool_id)
                     .filter_by(staatus=const.B_STAATUS_KEHTIV)
                     .first())
        if not self.koht:
            log.error('EHISe ametikohtade paringu vastuses on kool %d, mida meile tuntud kehtivate koolide hulgas pole' % kool_id)

        # restruktureerime ainete/astmete info paarideks (aine, aste)
        oppeained = []
        for r1 in rcd.find('oppeained/oppeaine') or []:
            astmed = r1.kooliaste
            if astmed:
                for aste in astmed:
                    oppeained.append((r1.kood, aste))

        # leiame olemasolevad ained
        for ap in list(self.ainepedagoogid):
            kood = ap.ehis_aine_kood
            kooliaste = ap.ehis_aste_kood
            found = False
            for r1 in oppeained:
                if r1[0] == kood and r1[1] == kooliaste:
                    # leitud
                    ap.seisuga = now
                    oppeained.remove(r1)
                    found = True
                    break
            if not found and taielik:
                ap.delete()

        # lisame uued ained
        for r1 in oppeained:
            ap = Ainepedagoog(ehis_aine_kood=r1[0],
                              ehis_aste_kood=r1[1],
                              seisuga=now)
            self.ainepedagoogid.append(ap)

    def delete_subitems(self):    
        self.delete_subrecords(['ainepedagoogid',
                                ])

def _xbool(node):
    """X-tee päringu vastuses oleva boolean välja dekodeerimine
    """
    value = str(node)
    if value in ('true','1','t'):
        return True
    elif value in ('false','0','f'):
        return False
    else:
        return None
