# -*- coding: utf-8 -*-
"Ülesande andmemudel"
from eis.model.entityhelper import *

class Valikvastus(EntityHelper, Base):
    """Andmed valikvastuse koodi seostamiseks valiku kirjega, 
    et statistikutel oleks lihtsam vastuste sisu lugeda.
    Valikvastused on tabelites kvsisu ja hindamismaatriks esitatud koodide abil.
    Käesolevas tabelis kirjeldatakse, millise küsimuse valikute seast on vaja neid koode otsida.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    tulemus_id = Column(Integer, ForeignKey('tulemus.id'), index=True) # viide tulemuse kirjele
    tulemus = relationship('Tulemus', foreign_keys=tulemus_id, back_populates='valikvastused')
    maatriks = Column(Integer, nullable=False) # mitmes hindamismaatriks (üldjuhul alati 1, aga kolme hulgaga sobitamisel on olemas ka 2 ja 3)
    valik1_kysimus_id = Column(Integer, ForeignKey('kysimus.id'), index=True) # kysimus_id, mille järgi leida tabelist Valik kvsisu.kood1 kirje
    valik1 = relationship('Kysimus', foreign_keys=valik1_kysimus_id, back_populates='valikvastused2')
    valik2_kysimus_id = Column(Integer, ForeignKey('kysimus.id'), index=True) # kysimus_id, mille järgi leida tabelist Valik kvsisu.kood2 kirje    
    valik2 = relationship('Kysimus', foreign_keys=valik2_kysimus_id, back_populates='valikvastused2')
    vahetada = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas statistikute vaates statvastus vahetada valik1 ja valik2 omavahel
    statvastuses = Column(Boolean, sa.DefaultClause('true'), nullable=False) # kas vastust näidata statistikutele statvastuse vaates
    mittevastus = Column(Boolean) # kas vastused kuvada Exceli väljavõttes: null - kuvada; true - kuvada ainult punktid, mitte vastused
    sisujarjestus = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas on järjestuse tüüpi küsimus (kvsisu.sisu on moodustatud valik1 koodide järjestusena, semikoolonitega eraldatult)
    paarina = Column(Boolean) # NULL - vastus pole paar; false - vastus on paar, aga kuvatakse mitme eraldi küsimusena; true - vastus on paar ja kuvatakse paarina
    analyys1 = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas statvastuses kasutada kvsisu analyysikirjet ning arvestada max_vastus=1
    _parent_key = 'tulemus_id'
    __table_args__ = (
        sa.UniqueConstraint('tulemus_id','maatriks'),
        )
    
    logging = False

    @classmethod
    def get_by_tulemus(cls, tulemus_id, maatriks):
        q = (Session.query(Valikvastus)
             .filter_by(tulemus_id=tulemus_id)
             .filter_by(maatriks=maatriks)
             )
        return q.first()

    def get_selgitus(self, kst):
        # selgituse leidmine kysimusestatistika põhjal
        from .valik import Valik
        from .hindamismaatriks import Hindamismaatriks

        def get_v(kysimus_id, kood):
            return (Session.query(Valik)
                    .filter_by(kysimus_id=kysimus_id)
                    .filter_by(kood=kood)
                    .first())
        
        value = None
        if self.sisujarjestus:
            sisu = kst.sisu
            if sisu:
                li = []
                koodid = sisu.split(';')
                for kood in koodid:
                    v1jrk = get_v(self.valik1_kysimus_id, kood)
                    if v1jrk:
                        li.append(v1jrk.selgitus or '')
                if li:
                    value = '; '.join(li)

        elif self.valik1_kysimus_id or self.valik2_kysimus_id:
            li = []
            if self.valik1_kysimus_id:
                v = get_v(self.valik1_kysimus_id, kst.kood1)
                if v and v.selgitus:
                    li.append(v.selgitus)
            if self.valik2_kysimus_id:
                v = get_v(self.valik2_kysimus_id, kst.kood2)
                if v and v.selgitus:
                    li.append(v.selgitus)
            if li:
                value = '; '.join(li)

        elif kst.hindamismaatriks_id:
            hm = Hindamismaatriks.get(kst.hindamismaatriks_id)
            if hm:
                value = hm.selgitus
        return value
