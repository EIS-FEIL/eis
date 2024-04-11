# -*- coding: utf-8 -*-
"Ülesandekogu"
import mimetypes
from eis.model.ylesanne import *
from eis.model.test import *
from .ylesandekogulogi import Ylesandekogulogi
_ = usersession._

class Ylesandekogu(EntityHelper, Base):
    """Ülesandekogu
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(256)) # ülesandekogu nimetus
    staatus = Column(Integer) # olek: 0 - kehtetu, 1 - kasutusel
    aine_kood = Column(String(10)) # õppeaine, klassifikaator AINE
    seotud_ained = Column(postgresql.ARRAY(String(10))) # seotud õppeainete koodid (kui põhiaine on üldõpetus)
    ainevald_kood = Column(String(10)) # õppeaine ainevaldkond (üldõpetuse korral seotud ainete valdkond, kui neil on ühine valdkond)
    oskus_kood = Column(String(10)) # osaoskus, klassifikaator OSKUS
    keeletase_kood = Column(String(10)) # keeleoskuse tase, klassifikaator KEELETASE
    aste_mask = Column(Integer) # kooliastmed/erialad kodeeritud bittide summana; biti järjekorranumber on astme kood (või vaikimisi astmete korral 0 - I aste; 1 - II aste; 2 - III aste; 3 - gümnaasium)
    aste_kood = Column(String(10)) # peamine kooliaste
    klass = Column(String(10)) # klass
    kogufail = relationship('Kogufail', uselist=False, back_populates='ylesandekogu')
    koguteemad = relationship('Koguteema', order_by='Koguteema.id', back_populates='ylesandekogu') # kogu valdkonnad ja teemad
    koguylesanded = relationship('Koguylesanne', order_by='Koguylesanne.id', back_populates='ylesandekogu')
    kogutestid = relationship('Kogutest', order_by='Kogutest.id', back_populates='ylesandekogu')
    tkylesanded = relationship('Tkylesanne', order_by='Tkylesanne.ylesanne_id', back_populates='ylesandekogu')
    tktestid = relationship('Tktest', order_by='Tktest.test_id', back_populates='ylesandekogu')    
    ylesandekogulogid = relationship('Ylesandekogulogi', order_by=sa.desc(sa.text('Ylesandekogulogi.id')), back_populates='ylesandekogu')

    def delete_subitems(self):
        r = self.kogufail
        if r:
            r.delete()
        self.delete_subrecords(['koguteemad',
                                'koguylesanded',
                                'kogutestid',
                                'ylesandekogulogid',
                                ])

    @classmethod
    def opt_kogud(cls, aine_kood, avalik_y=None, pedagoog=None):
        from .koguylesanne import Koguylesanne
        from .kogutest import Kogutest
        q = SessionR.query(Ylesandekogu.id, Ylesandekogu.nimi)
        if aine_kood:
            q = q.filter(Ylesandekogu.aine_kood==aine_kood)
        if avalik_y:
            # kogu peab olema avalik
            q = q.filter(Ylesandekogu.staatus==const.YK_STAATUS_AVALIK)
            # otsime ainult neid kogusid, kus on mõni avalik ylesanne
            if pedagoog:
                # võivad olla pedagoogile mõeldud ylesanded
                q = q.filter(Ylesandekogu.koguylesanded.any(
                    Koguylesanne.ylesanne.has(
                        Ylesanne.staatus.in_((const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG))
                        )))
            else:
                q = q.filter(Ylesandekogu.koguylesanded.any(
                    Koguylesanne.ylesanne.has(
                        Ylesanne.staatus==const.Y_STAATUS_AVALIK
                        )))
        return q.order_by(Ylesandekogu.nimi, Ylesandekogu.id)

    @property
    def kooliastmed(self):
        "Leiame astmete koodid"
        astmed = []
        if self.aste_kood:
            astmed = [self.aste_kood]
        mask = self.aste_mask or 0
        return self._get_kooliastmed(astmed, mask)
    
    def _get_kooliastmed(self, astmed, mask):
        opt = usersession.get_opt()
        for r in opt.astmed(self.aine_kood):
            aste_kood = r[0]
            if aste_kood not in astmed:
                bit = opt.aste_bit(aste_kood, self.aine_kood)
                if bit and mask and (bit & mask):
                    astmed.append(aste_kood)
        return astmed

    @property
    def aste_nimed(self):
        li = []
        for kood in self.kooliastmed:
            li.append(Klrida.get_str('ASTE', kood))
        return ', '.join(li)

    @property
    def teemad2(self):
        return [r.teema_kood + (r.alateema_kood and ('.' + r.alateema_kood) or '') \
                for r in self.koguteemad]

    @property
    def staatus_nimi(self):
        opt = usersession.get_opt()
        return opt.YK_STAATUS.get(self.staatus)

    @property
    def ylesannete_arv(self):
        from .koguylesanne import Koguylesanne
        if self.id:
            q = (SessionR.query(sa.func.count(Koguylesanne.id))
                 .filter_by(ylesandekogu_id=self.id))
            return q.scalar()
        else:
            return 0
        
    @property
    def testide_arv(self):
        from .kogutest import Kogutest
        if self.id:
            q = (SessionR.query(sa.func.count(Kogutest.id))
                 .filter_by(ylesandekogu_id=self.id))
            return q.scalar()
        else:
            return 0
        
    @property
    def max_pallid(self):
        from .koguylesanne import Koguylesanne
        if self.id:
            q = (SessionR.query(sa.func.sum(Ylesanne.max_pallid))
                 .join(Ylesanne.koguylesanded)
                 .filter(Koguylesanne.ylesandekogu_id==self.id))
            y_pallid = q.scalar() or 0
            return y_pallid
        else:
            return 0

    def has_permission(self, permission, perm_bit, lang=None, user=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud kogus
        """
        if not user:
            user = usersession.get_user()
        if not user:
            return False

        kasutaja = user.get_kasutaja()
        if not kasutaja:
            return False

        # ylesandekogu õigusi kontrollitakse ainult Innove vaates
        rc = kasutaja.has_permission(permission, 
                                     perm_bit,
                                     koht_id=const.KOHT_EKK, 
                                     aine_kood=self.aine_kood)
        # if not rc:
        #     # kas kasutajal on ainespetsialisti õigus 
        #     # kõigile selle aine avaliku vaate kogudele
        #     ained = kasutaja.get_ained(permission, perm_bit)
        #     rc = self.aine_kood in ained
        #     log.debug('%s in (%s) = %s' % (self.aine_kood, ained, rc))
        return rc

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        if liik and len(liik) > 256:
            liik = liik[:256]
        if not self.id:
            return
        logi = Ylesandekogulogi(ylesandekogu_id=self.id,
                                kasutaja_id=usersession.get_user().id,
                                liik=liik,
                                vanad_andmed=vanad_andmed,
                                uued_andmed=uued_andmed)
        self.ylesandekogulogid.append(logi)

    def log_delete(self):
        # logimist ei toimu
        pass

    def _ser_log_keyvalue(self, v):
        "Siin saab määrata, kuidas mingi väli logitakse"
        key = v[0]
        value = v[1]
        if key == 'aste_mask':
            value = ','.join(self._get_kooliastmed([], value))
        return key, value
