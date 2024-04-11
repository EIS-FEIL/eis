# -*- coding: utf-8 -*-
"Ülesande andmemudel"
import pickle
from eis.model_s.entityhelper import *
import eiscore.const as const
from .meta import Base, DBSession
from .tempvastus import Tempvastus

_ = usersession._

class Esitlus(EntityHelper, Base):
    """Ülesande sisu laaditakse põhiaknas oleva IFRAME sisse.
    - Kui on antud kasutaja_id, siis kirje luuakse (testi) põhilehe genereerimisel
    ning on kasutusel selleks, et IFRAME laadimisel veenduda ülesande vaatamise
    õiguse olemasolus ning määrata ülesande kuvamise parameetrid.
    Ülesande sisu genereeritakse sel juhul IFRAME laadimisel ning seda ei salvestata.
    - Kui kasutaja_id=NULL ja ettetehtud=true, siis on ette valmis genereeritud sisu,
    mis kuvatakse kõigile testisooritajatele, kes alustavad ülesande lahendamist,
    et süsteem ei peaks iga testisooritaja jaoks eraldi sisu genereerima hakkama.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesanne_id = Column(Integer, nullable=False) # viide ülesandele
    #ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id) 
    kasutaja_id = Column(Integer, index=True) # viide kasutajale
    #kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id) 
    sisu = Column(Text) # IFRAME sisu (ettetehtud esitluse korral)
    lang = Column(String(2)) # esitluse keel
    oige_nahtav = Column(Boolean) # kas kasutaja tohib vaadata õiget vastust
    hindaja = Column(Boolean) # kas kasutaja on hindaja (hindaja näeb näidisvastuseid)
    hindamine_id = Column(Integer) # kui kasutaja on hindaja, siis hindamise id
    lahendaja = Column(Boolean) # kas saab vastata
    ettetehtud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas esitlus on ettetehtud kõigile sooritajatele (ettetehtud esitlus on genereeritud ülesande koostamisel, et testisooritamisel ei peaks kõigile sooritajatele eraldi genereerima)
    sooritus_id = Column(Integer) # viide testiosa soorituse kirjele (kui on < 0, siis on TempSooritus)
    ylesandevastus_id = Column(Integer) # viide vastusele (kui on < 0, siis on TempYlesandevastus)
    valitudylesanne_id = Column(Integer, index=True) # viide valitud ülesande kirjele
    #valitudylesanne = relationship('Valitudylesanne', foreign_keys=valitudylesanne_id)    

    __table_args__ = (
        sa.Index('ix_esitlus_ylesanne_ette',
                 ylesanne_id,
                 ettetehtud,
                 lang
                 ),
        )

    @classmethod
    def get(cls, id):
        if id:
            return DBSession.query(cls).filter_by(id=id).first()

    def get_sooritus(self, handler, model):
        if self.sooritus_id:
            if not is_temp_id(self.sooritus_id):
                # püsiv vastus on salvestatud andmebaasi
                return model.Sooritus.get(self.sooritus_id)
            else:
                # ajutine eelvaate vastus TempVastus ja viide on seansi andmete seas
                request = handler.request
                li = request.session.get('tempsooritus') or []
                for s_id, tv_id in li:
                    if s_id == self.sooritus_id:
                        tv = Tempvastus.get(tv_id)
                        if tv:
                            return pickle.loads(tv.filedata)

    def get_ylesandevastus(self, handler, model, sooritus):
        #from eis.model.testimine.ylesandevastus import Ylesandevastus
        yv = None
        kehtiv = not self.lahendaja
        muudetav = not kehtiv
        yv_id = self.ylesandevastus_id
        if yv_id:
            if not is_temp_id(yv_id):
                # püsiv vastus on salvestatud andmebaasi
                yv = model.Ylesandevastus.get(yv_id)
            else:
                # ajutine vastus on kasutaja seansi andmete seas
                if sooritus:
                    li = sooritus.ylesandevastused
                    for yv2 in li:
                        if yv2.id == yv_id and \
                               (not muudetav or yv2.muudetav) and (not kehtiv or yv2.kehtiv):
                            yv = yv2
                            break
                else:
                    yv = Tempvastus.get_temp(handler, yv_id)
        else:
            vy_id = self.valitudylesanne_id
            if sooritus and vy_id:
                yv = sooritus.get_ylesandevastus_by_vy(vy_id, muudetav=muudetav, kehtiv=kehtiv)
        #log.debug('esitlus.id=%s s_id=%s yv_id=%s yv=%s' % \
        #          (self.id, self.sooritus_id, self.ylesandevastus_id, yv))
        return yv

    @classmethod
    def get_ette_esitlus(cls, ylesanne, lang):
        "Leiame ylesande ettetehtud esitluse"
        q = (DBSession.query(Esitlus)
             .filter(Esitlus.ylesanne_id==ylesanne.id)
             .filter(Esitlus.ettetehtud==True)
             .filter(Esitlus.kasutaja_id==None)
             .filter(Esitlus.lang==lang)
             .order_by(sa.desc(Esitlus.id))
             )
        return q.first()

    @classmethod
    def disable_ette_esitlused(cls, ylesanne):
        q = (DBSession.query(Esitlus)
             .filter(Esitlus.ylesanne_id==ylesanne.id)
             .filter(Esitlus.ettetehtud==True)
             .filter(Esitlus.kasutaja_id==None)
             .filter(Esitlus.sisu!=None)
             )
        for r in q.all():
            r.sisu = None
        DBSession.flush()
        
    @classmethod
    def give_ette_esitlus(cls, ylesanne, lang):
        "Loome ettetehtud esitluse kirje"
        if not lang:
            # kui keel pole antud, kasutame põhikeelt
            lang = ylesanne.lang
        rcd = cls.get_ette_esitlus(ylesanne, lang)
        if not rcd:
            rcd = cls(kasutaja_id=None,
                      ylesanne_id=ylesanne.id,
                      lang=lang,
                      ettetehtud=True,
                      hindaja=False,
                      lahendaja=True,
                      oige_nahtav=False)
            DBSession.add(rcd)
            DBSession.flush()
        return rcd

    @classmethod
    def create_kasutaja_esitlus(cls, ylesanne, vy, lang, handler, sooritus, ylesandevastus):
        "Luuakse kasutaja oma esitluse kirje"
        c = handler.c
        olen_hindaja = bool(c.hindaja or c.hindamised or c.on_hindamine)
        if not lang:
            # kui keel pole antud, kasutame põhikeelt            
            lang = ylesanne.lang
        esitlus = cls(kasutaja_id=c.user.id,
                      sisu=None,
                      ylesanne_id=ylesanne.id,
                      lang=lang,
                      hindaja=olen_hindaja,
                      hindamine_id=c.hindamine and c.hindamine.id or None,
                      lahendaja=not c.read_only,
                      oige_nahtav=bool(c.prepare_correct)
                      )
        if sooritus:
            esitlus.sooritus_id = sooritus.id
        if ylesandevastus:
            esitlus.ylesandevastus_id = ylesandevastus.id
        if vy:
            esitlus.valitudylesanne_id = vy.id
        #log.debug('CREATE esitlus hindaja=%s oige=%s, yv_id=%s' % (olen_hindaja, c.prepare_correct, esitlus.ylesandevastus_id))

        DBSession.add(esitlus)
        DBSession.flush()
        return esitlus

    def kasutaja_urlid(self, c):
        task_url = "esitlus/%s/%s/show" % (self.id, self.ylesanne_id)
        if not c.read_only and not c.preview and self.sooritus_id and self.valitudylesanne_id:
            # käib testi sooritamine
            task_url += "?tos_id=%s&vy_id=%s" % (self.sooritus_id, self.valitudylesanne_id)
        correct_url = 'esitlus/%s/%s/correct' % (self.id, self.ylesanne_id)
        return task_url, correct_url
