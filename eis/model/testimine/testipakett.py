"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Testipakett(EntityHelper, Base):
    """Testisoorituspakett
    Üldjuhul on iga testikoha ja keele kohta on üks pakett.
    Erandiks on seaduse tundmise eksam ja riigikeele tasemeeksam, 
    kus on iga testiruumi kohta oma pakett.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    testikoht_id = Column(Integer, ForeignKey('testikoht.id'), index=True, nullable=False) # viide testikohale
    testikoht = relationship('Testikoht', foreign_keys=testikoht_id, back_populates='testipaketid')
    testiruum_id = Column(Integer, ForeignKey('testiruum.id'), index=True) # viide testiruumile, on olemas ainult siis, kui igal testiruumil on oma testipakett ehk SE ja TE liiki testide korral
    testiruum = relationship('Testiruum', foreign_keys=testiruum_id, back_populates='testipaketid')
    lang = Column(String(2), nullable=False) # soorituskeel (klassifikaator SOORKEEL)
    toodearv = Column(Integer) # sooritajate arv (ei arvestata lisatöid)
    valjastuskottidearv = Column(Integer) # väljastuskottide arv
    valjastusymbrikearv = Column(Integer) # testiruumide igat liiki väljastusümbrike arv kokku
    tagastuskottidearv = Column(Integer) # tagastuskottide arv
    tagastusymbrikearv = Column(Integer) # testiruumide igat liiki tagastusümbrike arv kokku
    erivajadustoodearv = Column(Integer) # erivajadustega tööde arv
    testiprotokollid = relationship('Testiprotokoll', order_by='Testiprotokoll.tahis', back_populates='testipakett')
    turvakotid = relationship('Turvakott', order_by='Turvakott.id', back_populates='testipakett')
    valjastusymbrikud = relationship('Valjastusymbrik', back_populates='testipakett')
    tagastusymbrikud = relationship('Tagastusymbrik', back_populates='testipakett')
    _parent_key = 'testikoht_id'

    # testikohal (SE,TE korral testiruumil) on iga keele kohta täpselt üks testipakett
    __table_args__ = (
        sa.UniqueConstraint('testikoht_id','lang','testiruum_id'),
        )

    @property
    def valjastuskotid(self):
        return [r for r in self.turvakotid if r.suund == const.SUUND_VALJA]

    @property
    def tagastuskotid(self):
        return [r for r in self.turvakotid if r.suund == const.SUUND_TAGASI]

    @property
    def lang_nimi(self):
        if self.lang:
            return Klrida.get_lang_nimi(self.lang)

    @property
    def toimumisprotokoll(self):
        return self.testikoht.get_toimumisprotokoll(self.lang, self.testiruum_id)

    def get_peaymbrik(self):
        for rcd in self.tagastusymbrikud:
            if rcd.tagastusymbrikuliik_id == None:
                return rcd

    def give_peaymbrik(self):
        from .tagastusymbrik import Tagastusymbrik
        rcd = self.get_peaymbrik()
        if not rcd:
            rcd = Tagastusymbrik(testiprotokoll_id=None,
                                 testipakett=self,
                                 tahised=self.testikoht.tahised,#'%s-%s' % (self.testikoht.tahised, self.lang.upper()),
                                 tagastusymbrikuliik_id=None)
        return rcd

    def give_valjastusymbrik(self, valjastusymbrikuliik_id, kursus):
        for ymbrik in self.valjastusymbrikud:
            if ymbrik.valjastusymbrikuliik_id == valjastusymbrikuliik_id and \
               ymbrik.testiruum_id == None and \
               ymbrik.kursus_kood == kursus:
                return ymbrik
            
        from .valjastusymbrik import Valjastusymbrik
        ymbrik = Valjastusymbrik(valjastusymbrikuliik_id=valjastusymbrikuliik_id,
                                 testipakett=self,
                                 kursus_kood=kursus)
        return ymbrik
    
    def get_kursused(self):
        kursused = set([tpr.kursus_kood for tpr in self.testiprotokollid if tpr.kursus_kood])
        return kursused
    
    def calc_tehtud_toodearv(self):
        """Tehtud tööde arv arvutatakse üle:
        - osalemise protokolli kinnitamisel;
        - valimi laadimisel.
        """
        # salvestame tehtud tööde arvu, seda kasutatakse hindajatele ümbrike väljastamisel
        for tpr in self.testiprotokollid:
            tpr.tehtud_toodearv = len([r for r in tpr.sooritused \
                                       if r.staatus==const.S_STAATUS_TEHTUD])
            for hpr in tpr.hindamisprotokollid:
                hpr.calc_tehtud_toodearv(tpr.id)

    def delete_subitems(self):    
        for r in self.valjastusymbrikud:
            if not r.testiruum_id:
                r.delete()
        # testiruumiga seotud väljastusümbrikud eemaldati testiruumi kaudu
        # (testiruumid peavad olema juba varem eemaldatud)

        pea = self.get_peaymbrik()
        if pea:
            pea.delete()
        # muud tagastusümbrikud peale peaümbriku eemaldatakse testiprotokolli kaudu
            
        self.delete_subrecords(['valjastuskotid',
                                'tagastuskotid',
                                'testiprotokollid',
                                ])
