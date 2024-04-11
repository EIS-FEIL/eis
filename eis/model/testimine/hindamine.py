"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

from .kriteeriumihinne import Kriteeriumihinne
#from .ylesandevastus import Ylesandevastus
from .ylesandehinne import Ylesandehinne
#from kysimusevastus import Kysimusevastus
from .labivaatus import Labivaatus

_ = usersession._

class Hindamine(EntityHelper, Base):
    """Soorituse ja hindamiskogumi hindamine ja/või sisestamine.
    Iga soorituse, hindamisliigi ja sisestuse kohta on üks kirje, 
    mida erinevad sisestajad võivad sisestada, 
    välja arvatud eksperthindamise korral, kus on igal eksperdil oma kirje.
    Kui on p-test, siis on kahekordne sisestamine.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hindamisolek_id = Column(Integer, ForeignKey('hindamisolek.id'), index=True, nullable=False) # viide soorituse hindamiskogumi hindamisolekule
    hindamisolek = relationship('Hindamisolek', foreign_keys=hindamisolek_id, back_populates='hindamised')
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # hindamise/sisestamise olek: 0=const.H_STAATUS_HINDAMATA - hindamata; 1=const.H_STAATUS_POOLELI - hindamisel; 2=const.H_STAATUS_LYKATUD - tagasi lükatud; 4=const.H_STAATUS_SUUNATUD - ümber suunatud; 6=const.H_STAATUS_HINNATUD - hinnatud (hindaja poolt kinnitatud)
    tyhistatud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas hindamine on tühistatud (sama soorituse sama liigiga tühistamata hindamise kirjeid ei saa olla rohkem kui üks)
    sisestatud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas kõigi ülesannete hinded on sisestatud

    # hindamise andmed
    
    liik = Column(Integer, nullable=False) # hindamise liik (kui hindamisprotokoll on olemas, siis sama, mis hindamisprotokollis): 1=const.HINDAJA1 - I hindamine; 2=const.HINDAJA2 - II hindamine ; 3=const.HINDAJA3 - III hindamine; 4=const.HINDAJA4 - eksperthindamine; 5=const.HINDAJA5 - vaide korral hindamine; 6=const.HINDAJA6 - kohtuhindamine
    hindaja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide hindaja kasutajale (igasuguse hindamise korral)
    hindaja_kasutaja = relationship('Kasutaja', foreign_keys=hindaja_kasutaja_id, back_populates='hindamised')
    labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True) # viide hindajale (puudub vaide korral hindamisel)
    labiviija = relationship('Labiviija', foreign_keys=labiviija_id, back_populates='hindamised')
    kontroll_labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True) # viide teisele hindajale objektiivhinnatava p-testi korral, kui üks hindaja hindab ja teine kontrollib
    kontroll_labiviija = relationship('Labiviija', foreign_keys=kontroll_labiviija_id)
    ekspertmuutis = Column(Boolean) # eksperthindamise korral märge, kas kehtivaid palle muudeti
    intervjuu_labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True) # viide intervjueerijale (p-testi korral, kui intervjueerija sisestatakse hindamise protokollilt)
    intervjuu_labiviija = relationship('Labiviija', foreign_keys=intervjuu_labiviija_id)
    ylesandehinded = relationship('Ylesandehinne', back_populates='hindamine')
    kriteeriumihinded = relationship('Kriteeriumihinne', back_populates='hindamine')    
    hindamisprotokoll_id = Column(Integer, ForeignKey('hindamisprotokoll.id'), index=True) # viide hindamisprotokollile (hindamisprotokollilt sisestamise korral
    hindamisprotokoll = relationship('Hindamisprotokoll', foreign_keys=hindamisprotokoll_id, back_populates='hindamised')
    lykkamispohjus = Column(Text) # kirjaliku soorituse korral hindaja põhjendus, kui ta hindamise tagasi lükkas
    hindamispohjus = Column(Text) # VI hindamise korral hindamise alus ja põhjendus, miks tulemust muudetakse
    uus_hindamine_id = Column(Integer, ForeignKey('hindamine.id'), index=True) # kirjaliku soorituse korral uue hindaja hindamise kirje, kui antud hindaja lükkas soorituse hindamise tagasi ja määrati uus hindaja
    uus_hindamine = relationship('Hindamine', foreign_keys=uus_hindamine_id, remote_side=id)
    pallid = Column(Float) # hindamise hindepallide summa
    loplik = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas hindamine on lõplik
    ksm_naeb_hindaja = Column(Boolean) # kas märkused on nähtavad teistele hindajatele
    ksm_naeb_sooritaja = Column(Boolean) # kas märkused on nähtavad sooritajale
    on_probleem = Column(Boolean) # kas hindaja on märkinud töö probleemseks
    probleem_sisu = Column(Text) # kui hindaja on märkinud töö probleemseks, siis probleemi sisu
    probleem_varv = Column(String(7)) # probleemse töö värv (#rrggbb või #rgb)
    unikaalne = Column(Boolean, sa.DefaultClause('1'), nullable=False) # True - hindamiskogumiga hindamise korral, piirang ei luba mitut sama liiki hindamist; False - avaliku vaate hindamiskogumita hindamise korral, kus võib olla mitu hindajat, iga hindab oma ylesannet
    
    # sisestamise andmed

    komplekt_id = Column(Integer, ForeignKey('komplekt.id'), index=True) # viide komplektile (väärtus peaks olema sama kui hindamisoleku tabelis olev komplekt, aga on siin tabelis vajalik mitmekordse sisestamise võimaldamiseks)
    komplekt = relationship('Komplekt', foreign_keys=komplekt_id)
    sisestuserinevus = Column(Boolean) # kas I ja II sisestus erinevad (p-testi hindamisprotokolli sisestamise korral)
    sisestus = Column(Integer, sa.DefaultClause('1'), nullable=False) # mitmes sisestamine (p-testi hindamisprotokolli kahekordse sisestamise korral on sisestused 1 ja 2, muidu ainult 1)
    sisestaja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # sisestaja kasutaja (ainult sisestamise korral, e-hindamise korral puudub)
    sisestaja_kasutaja = relationship('Kasutaja', foreign_keys=sisestaja_kasutaja_id, back_populates='hindamised')
    sisestuslogid = relationship('Sisestuslogi', order_by=sa.desc(sa.text('Sisestuslogi.id')), back_populates='hindamine')
    labivaatused = relationship('Labivaatus', order_by='Labivaatus.id', back_populates='hindamine')
    __table_args__ = (
        sa.UniqueConstraint('hindamisolek_id','liik','uus_hindamine_id','sisestus', 'hindaja_kasutaja_id'),
        )
    _parent_key = 'hindamisolek_id'

    @property
    def liik_nimi(self):
        return usersession.get_opt().HINDAJA.get(self.liik)

    @property
    def staatus_nimi(self):
        if self.staatus == const.H_STAATUS_POOLELI and self.sisestatud:
            return _("Kinnitamiseks valmis")
        return usersession.get_opt().H_STAATUS.get(self.staatus)

    def default(self):
        if self.ksm_naeb_hindaja is None:
            self.ksm_naeb_hindaja = True
        if self.ksm_naeb_sooritaja is None:
            self.ksm_naeb_sooritaja = True            

    def get_vy_by_ty(self, ty):
        """Leitakse, milline valitudylesanne on antud testiylesande kohta 
        selles sisestamises salvestatud.
        """
        if self.id:
            q = (Session.query(Valitudylesanne)
                 .filter(Valitudylesanne.testiylesanne_id==ty.id)
                 .join(Valitudylesanne.ylesandehinded)
                 .filter(Ylesandehinne.hindamine_id==self.id))
            return q.first()

    def get_vy_ylesandehinne(self, vy_id):
        """Leitakse hinde kirje valitudylesande id kaudu.
        """
        if self.id:
            q = (Session.query(Ylesandehinne)
                 .filter(Ylesandehinne.hindamine==self)
                 .filter(Ylesandehinne.valitudylesanne_id==vy_id))
            return q.first()
        # else:
        #     for yh in self.ylesandehinded:
        #         if yh.valitudylesanne_id == vy_id:
        #             return yh

    def get_ylesandehinne(self, ylesandevastus):
        """Leitakse hinde kirje ylesandevastuse kirje kaudu.
        """
        for rcd in self.ylesandehinded:
            if rcd.ylesandevastus == ylesandevastus:
                return rcd

    def give_ylesandehinne(self, ylesandevastus, vy):
        rcd = self.get_ylesandehinne(ylesandevastus)
        if not vy:
            vy = ylesandevastus.valitudylesanne
        if rcd and vy and rcd.valitudylesanne != vy:
            rcd.valitudylesanne = vy
        if not rcd:
            rcd = Ylesandehinne(ylesandevastus=ylesandevastus,
                                valitudylesanne=vy,
                                hindamine=self)
            self.ylesandehinded.append(rcd)

        return rcd

    def get_kriteeriumihinne(self, kriteerium_id):
        """Leitakse hinde kirje 
        """
        for rcd in self.kriteeriumihinded:
            if rcd.hindamiskriteerium_id == kriteerium_id:
                return rcd

    def give_kriteeriumihinne(self, kriteerium_id):
        rcd = self.get_kriteeriumihinne(kriteerium_id)
        if not rcd:
            rcd = Kriteeriumihinne(hindamiskriteerium_id=kriteerium_id,
                                   hindamine=self)
            self.kriteeriumihinded.append(rcd)
        return rcd

    def get_labivaatus(self, ekspert_labiviija_id):
        for rcd in self.labivaatused:
            if rcd.ekspert_labiviija_id == ekspert_labiviija_id:
                return rcd

    def give_labivaatus(self, ekspert_labiviija_id):
        rcd = self.get_labivaatus(ekspert_labiviija_id)
        if not rcd:
            rcd = Labivaatus(hindamine=self,
                             ekspert_labiviija_id=ekspert_labiviija_id)
            self.labivaatused.append(rcd)
        return rcd

    def delete_subitems(self):    
        self.delete_subrecords(['ylesandehinded',
                                'kriteeriumihinded',
                                'sisestuslogid',
                                'labivaatused',
                                ])
