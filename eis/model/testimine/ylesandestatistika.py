# -*- coding: utf-8 -*-
"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Ylesandestatistika(EntityHelper, Base):
    """Ülesande statistika toimumisaja piires.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    valitudylesanne_id = Column(Integer, ForeignKey('valitudylesanne.id'), index=True) # viide testi valitud ülesandele, mille kohta statistika käib
    valitudylesanne = relationship('Valitudylesanne', foreign_keys=valitudylesanne_id)
    #valitudylesanne = relationship('Valitudylesanne', foreign_keys=valitudylesanne_id, back_populates='ylesandestatistikad')
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele, mille kohta statistika käib
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id)    
    tkorraga = Column(Boolean, nullable=False, index=True) # kas on testimiskorraga soorituste statistika (või avaliku testi statistika)
    valimis = Column(Boolean) # NULL - valim ja mitte-valim koos; true - valimi statistika; false - mitte-valimi statistika
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True) # viide toimumisajale (testimiskorraga testi statistika korral)
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id)
    testiruum_id = Column(Integer, ForeignKey('testiruum.id'), index=True) # viide nimekirjale (avaliku vaate testi statistika korral)
    testiruum = relationship('Testiruum', foreign_keys=testiruum_id)
    testikoht_id = Column(Integer, ForeignKey('testikoht.id'), index=True) # viide soorituskohale
    testikoht = relationship('Testikoht', foreign_keys=testikoht_id)
    kool_koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # viide õppimiskohale
    kool_koht = relationship('Koht', foreign_keys=kool_koht_id)
    sooritajate_arv = Column(Integer) # sooritajate arv
    keskmine = Column(Float) # keskmine tulemus toorpunktides
    lahendatavus = Column(Float) # keskmine lahendusprotsent, keskmise tulemuse ja maksimaalse võimaliku tulemuse suhe protsentides (EIS arvutab)
    rit = Column(Float) # korrelatsioonikordaja ülesande punktide ja testi kogutulemuse vahel, ülesande eristusjõu näitaja: corr(yv.pallid, sooritaja.pallid)
    rir = Column(Float) # korrelatsioonikordaja ülesande punktide ja testi ülejäänud ülesannete punktide vahel: corr(yv.pallid, sooritaja.pallid-yv.pallid)
    #raskus = Column(Float) # raskus, -4..4 (statistik sisestab andmebaasi)
    #eristusindeks = Column(Float) # eristusindeks, -1..1 (statistik sisestab andmebaasi)
    #arvamisindeks = Column(Float) # äraarvamisindeks, 0..1 (vastuse juhusliku äraarvamise tõenäosus) (statistik sisestab andmebaasi)
    aeg_avg = Column(Integer) # keskmine lahendusaeg sekundites (koolipsühholoogi testi korral)
    aeg_min = Column(Integer) # min lahendusaeg sekundites (koolipsühholoogi testi korral)
    aeg_max = Column(Integer) # max lahendusaeg sekundites (koolipsühholoogi testi korral)
    __table_args__ = (
        sa.UniqueConstraint('valitudylesanne_id', 'ylesanne_id', 'toimumisaeg_id', 'testiruum_id', 'testikoht_id', 'kool_koht_id'),
        )

    @classmethod
    def get_by_keys(cls, vy_id, ylesanne_id, tkorraga, toimumisaeg_id, testiruum_id=None, testikoht_id=None, kool_koht_id=None, valimis=None):
        q = (cls.query
             .filter_by(valitudylesanne_id=vy_id)
             .filter_by(tkorraga=tkorraga)
             .filter_by(valimis=valimis))
        if ylesanne_id:
            q = q.filter_by(ylesanne_id=ylesanne_id)
        if testiruum_id:
            # avaliku vaate test
            q = (q.filter_by(testiruum_id=testiruum_id)
                 .filter_by(toimumisaeg_id=None))
        else:
            # ekk vaate test
            q = (q.filter_by(toimumisaeg_id=toimumisaeg_id)
                 .filter_by(testiruum_id=None)
                 .filter_by(testikoht_id=testikoht_id)
                 .filter_by(kool_koht_id=kool_koht_id))
        return q.first()

    @classmethod
    def give_by_keys(cls, vy_id, ylesanne_id, tkorraga, toimumisaeg_id, testiruum_id=None, testikoht_id=None, kool_koht_id=None, valimis=None):
        rcd = cls.get_by_keys(vy_id, ylesanne_id, tkorraga, toimumisaeg_id, testiruum_id, testikoht_id, kool_koht_id, valimis)
        if not rcd:
            #log.info('CREATE vy_id=%s, ta_id=%s, tr_id=%s, tk_id=%s, kk_id=%s' % \
            #         (vy_id, toimumisaeg_id, testiruum_id, testikoht_id, kool_koht_id))
            rcd = cls(valitudylesanne_id=vy_id,
                      ylesanne_id=ylesanne_id,
                      tkorraga=tkorraga,
                      valimis=valimis,
                      toimumisaeg_id=toimumisaeg_id or None,
                      testiruum_id=testiruum_id or None,
                      testikoht_id=testikoht_id or None,
                      kool_koht_id=kool_koht_id or None)
            rcd.flush()
        return rcd
