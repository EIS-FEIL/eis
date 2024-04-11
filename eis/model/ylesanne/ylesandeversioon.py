# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from eis.model.entityhelper import *
from .t_ylesanne import t_meta_fields

class Ylesandeversioon(EntityHelper, Base):
    """Ülesande versioonid
    """
    __table_args__ = (
        sa.UniqueConstraint('ylesanne_id','seq'),
        )
    id = Column(Integer, primary_key=True, autoincrement=True)    
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='ylesandeversioonid')
    seq = Column(Integer, nullable=False) # versiooni järjekorranumber ülesande sees

    t_ylesanded = relationship('T_Ylesanne', cascade='all', back_populates='ylesandeversioon')
    t_lahendusjuhised = relationship('T_Lahendusjuhis', cascade='all', back_populates='ylesandeversioon')
    t_hindamisaspektid = relationship('T_Hindamisaspekt', cascade='all', back_populates='ylesandeversioon')
    t_sisuplokid = relationship('T_Sisuplokk', cascade='all', back_populates='ylesandeversioon')
    t_sisuobjektid = relationship('T_Sisuobjekt', cascade='all', back_populates='ylesandeversioon')
    t_ylesandefailid = relationship('T_Ylesandefail', cascade='all', back_populates='ylesandeversioon')
    t_kysimused = relationship('T_Kysimus', cascade='all', back_populates='ylesandeversioon')
    t_valikud = relationship('T_Valik', cascade='all', back_populates='ylesandeversioon')
    t_hindamismaatriksid = relationship('T_Hindamismaatriks', cascade='all', back_populates='ylesandeversioon')

    logging = True
    _flush_on_delete = True
    _parent_key = 'ylesanne_id'
            
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .ylesanne import Ylesanne
        parent = self.ylesanne or self.ylesanne_id and Ylesanne.get(self.ylesanne_id)
        if parent:        
            parent.logi('Ülesande versioon [%s]' % (self.seq), vanad_andmed, uued_andmed, logitase)

    @classmethod
    def add(self, ylesanne):
        "Lisame tõlketabelitesse uue versiooni kõigist tekstidest"
        
        versioon = Ylesandeversioon(ylesanne_id=ylesanne.id)
        #ylesanne.ylesandeversioonid.append(versioon)
        Session.flush()
        versioon_id = versioon.id
        lang = ylesanne.lang
        def t_copy(src, dest):
            is_file = False
            for column in dest.__table__.columns:
                name = column.name
                if name == 'fileversion':
                    is_file = True
                elif name not in t_meta_fields:
                    dest.__setattr__(name, src.__getattr__(name))
            if is_file:
                dest.copy_file(src)

        def add_copy(src):
            # põhikeelse kirje versioon
            dest = src.give_tran(None, versioon_id)
            t_copy(src, dest)
            # tõlgete versioonid
            for t_src in list(src.trans):
                if not t_src.ylesandeversioon_id:
                    t_dest = src.give_tran(t_src.lang, versioon_id)
                    t_copy(t_src, t_dest)
        
        add_copy(ylesanne)
        if ylesanne.lahendusjuhis:
            add_copy(ylesanne.lahendusjuhis)
        for r in ylesanne.hindamisaspektid:
            add_copy(r)
        for r in ylesanne.sisuplokid:
            add_copy(r)
            for robj in list(r.sisuobjektid):
                add_copy(robj)
            for robj in r.kysimused:
                add_copy(robj)
                for rv in robj.valikud:
                    add_copy(rv)
        for r in ylesanne.ylesandefailid:
            add_copy(r)
        for r in ylesanne.tulemused:
            for robj in r.hindamismaatriksid:
                add_copy(robj)

        return versioon

    def revert(self, sisuplokk_id=None):
        "Versiooni tekstid taastatakse ylesande jooksva seisuna"
        versioon_id = self.id
        
        def t_copy(src, dest):
            is_file = False
            for column in src.__table__.columns:
                name = column.name
                if name == 'fileversion':
                    is_file = True
                if name not in t_meta_fields:
                    dest.__setattr__(name, src.__getattr__(name))
            if is_file:
                dest.copy_file(src)
                
        def to_current(t_list):
            for tran_vers in t_list:
                # leiame jooksva versiooni
                tran = tran_vers.orig.tran(tran_vers.lang)
                if tran:
                    # kui on jooksev versioon olemas, siis kanname sinna andmed
                    t_copy(tran_vers, tran)

        def from_version(c_list):
            for c_orig in c_list:
                for t_vers in list(c_orig.trans):
                    if t_vers.ylesandeversioon_id == versioon_id:
                        # t_vers on antud versiooni kirje
                        # leiame versiooni kirjega sama keele jooksva kirje
                        if not t_vers.lang:
                            # jooksev kirje põhikeeles
                            c_tran = c_orig
                        else:
                            # jooksev tõlge
                            c_tran = c_orig.give_tran(t_vers.lang)
                        t_copy(t_vers, c_tran)
                    elif not t_vers.ylesandeversioon_id:
                        # t_vers on jooksev tõlge
                        t_tran = c_orig.tran(t_vers.lang, versioon_id)
                        if not t_tran:
                            # meie versioonis seda tõlget pole
                            t_vers.delete()
                        
        if sisuplokk_id:
            # soovitakse taastada ainult yhe sisuploki andmed
            for sisuplokk in self.ylesanne.sisuplokid:
                if sisuplokk.id == int(sisuplokk_id):
                    break
                else:
                    sisuplokk = None
            if sisuplokk:
                from_version([sisuplokk])
                from_version(sisuplokk.sisuobjektid)
                for k in sisuplokk.kysimused:
                    from_version([k])
                    from_version(k.valikud)
                    tulemus = k.tulemus
                    if tulemus:
                        from_version(tulemus.hindamismaatriksid)
        else:
            # soovitakse kogu ylesande andmed taastada
            to_current(self.t_ylesanded)
            to_current(self.t_lahendusjuhised)
            to_current(self.t_hindamisaspektid)
            to_current(self.t_sisuplokid)
            to_current(self.t_sisuobjektid)
            to_current(self.t_kysimused)
            to_current(self.t_valikud)
            to_current(self.t_ylesandefailid)
            to_current(self.t_hindamismaatriksid)
