"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.model.kasutaja import Kasutaja
from eis.model.test import Test
from .labiviija import Labiviija
from .testiruum import Testiruum

class Nimekiri(EntityHelper, Base):
    """Testile registreeritute nimekiri.
    Kui õpetaja kasutab sama avaliku vaate testi mitmes klassis, 
    siis ta teeb iga klassi jaoks oma nimekirja.
    Avaliku vaate testidel testimiskord puudub.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(100)) # nimekirja nimetus
    esitaja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # nimekirja esitaja
    esitaja_kasutaja = relationship('Kasutaja', foreign_keys=esitaja_kasutaja_id, back_populates='esitaja_nimekirjad')
    esitaja_koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # õppeasutus, nimekirja esitaja
    esitaja_koht = relationship('Koht', foreign_keys=esitaja_koht_id)
    sooritajad = relationship('Sooritaja', order_by='Sooritaja.id', back_populates='nimekiri')
    test_id = Column(Integer, ForeignKey('test.id'), index=True) # viide testile, millele registreeritakse (kui on ühe testi jaoks koostatud nimekiri)
    test = relationship('Test', foreign_keys=test_id)
    #test = relationship('Test', foreign_keys=test_id, back_populates='nimekirjad')
    testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True) # viide testimiskorrale, millele registreeritakse (kui on ühe testimiskorra jaoks koostatud nimekiri)
    testimiskord = relationship('Testimiskord', foreign_keys=testimiskord_id, back_populates='nimekirjad')
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # olek
    testiruumid = relationship('Testiruum', back_populates='nimekiri')
    alates = Column(Date) # varaseim lahendamise kuupäev (jagatud töö korral ja kutseeksami korral)
    kuni = Column(Date) # hiliseim lahendamise kuupäev (jagatud töö korral)
    pedag_nahtav = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas nimekiri on nähtav teistele sama kooli õpetajatele
    tulemus_nahtav = Column(Boolean) # kas oma tulemus on sooritajale nähtav (kutseeksami korral koondtulemus)
    alatestitulemus_nahtav = Column(Boolean) # kas oma alatestide tulemused on sooritajale nähtavad (kutseeksami korral)
    vastus_peidus = Column(Boolean) # kas oma tehtud töö on sooritajale mittenähtav (kutseeksami korral)
    stat_arvutatud = Column(DateTime) # millal on arvutatud viimati nimekirja statistika
        
    @property
    def sooritajate_arv(self):
        return len(self.sooritajad)

    @classmethod
    def lisa_nimekiri(cls, user, regviis_kood, test, testimiskord_id=None, pedag_nahtav=None):
        test_id = test and test.id or None
        if test and test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
            pedag_nahtav = False
        elif pedag_nahtav is None:
            pedag_nahtav = True
        tulemus_nahtav = not testimiskord_id and True or None
        rcd = Nimekiri(test_id=test_id,
                       testimiskord_id=testimiskord_id, 
                       nimi='Nimekiri',
                       esitaja_kasutaja_id=user.id,
                       esitaja_koht_id=user.koht_id or None,
                       staatus=const.B_STAATUS_KEHTIV,
                       pedag_nahtav=pedag_nahtav,
                       tulemus_nahtav=tulemus_nahtav)
        return rcd

    @classmethod
    def give_nimekiri(cls, koht_id, test, testimiskord_id):
        rcd = (Nimekiri.query
               .filter_by(esitaja_koht_id=koht_id or None)
               .filter(Nimekiri.testimiskord_id==testimiskord_id)
               .filter(Nimekiri.test_id==test.id)
               .first())
        if not rcd:
            if test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
                pedag_nahtav = False
            else:
                pedag_nahtav = True
            rcd = Nimekiri(test_id=test.id,
                           testimiskord_id=testimiskord_id, 
                           nimi='Nimekiri',
                           esitaja_koht_id=koht_id or None,
                           staatus=const.B_STAATUS_KEHTIV,
                           pedag_nahtav=pedag_nahtav)
        return rcd

    @classmethod
    def get_esitajad_opt(cls, koht_id):
        q = Kasutaja.query.filter(Kasutaja.esitaja_nimekirjad.any(Nimekiri.esitaja_koht_id==koht_id)).\
            order_by(Kasutaja.perenimi,Kasutaja.eesnimi).all()
        li = [(o.id, o.nimi) for o in q]
        return li

    def delete(self, *args, **kwargs):
        from .sooritus import Sooritus
        from .sooritaja import Sooritaja
        q = (Session.query(Sooritus.testiruum_id).distinct()
             .join(Sooritus.sooritaja)
             .filter(Sooritaja.nimekiri_id==self.id)
             .filter(Sooritus.testiruum_id!=None))
        testiruumid_id = [r_id for r_id, in q.all()]

        EntityHelper.delete(self, *args, **kwargs)

        Session.flush()
        for testiruum_id in testiruumid_id:
            Testiruum.get(testiruum_id).set_sooritajate_arv()
        
    def delete_subitems(self):    
        self.delete_subrecords(['sooritajad',
                                ])

    def has_permission(self, permission, perm_bit, user=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud nimekirjas
        """
        rc = False
        if not user:
            user = usersession.get_user()
        if not user:
            return rc

        test = self.test
        if (self.esitaja_kasutaja_id == user.id or user.on_pedagoog) and user.koht_id == self.esitaja_koht_id:
            # olen nimekirja esitaja või pedagoog selles koolis, kust nimekiri esitati
            testimiskord = self.testimiskord
            if testimiskord:
                # kontrollime, et koolil on registreerimise aeg
                tk = self.testimiskord
                dt = date.today()
                reg_kool = tk.reg_kool_eis or \
                           tk.reg_kool_valitud and user and tk.on_regkoht(user.koht_id)                
                if reg_kool and tk.reg_kool_alates and tk.reg_kool_kuni and \
                       tk.reg_kool_alates<=dt and tk.reg_kool_kuni>=dt:
                    rc = True
                elif reg_kool and testimiskord.on_eeltest and \
                  (not tk.reg_kool_alates or tk.reg_kool_alates<=dt) and \
                  (not tk.reg_kool_kuni or tk.reg_kool_kuni>=dt):
                    # eeltestile võib määrata ka siis, kui kuupäevadega pole piiratud
                    rc = True
                else:
                    log.debug(f'test {test.id} tk {tk.tahis} koolis reg aeg on läbi {tk.reg_kool_alates}-{tk.reg_kool_kuni}')

            elif self.pedag_nahtav or self.esitaja_kasutaja_id == user.id:
                # pedagoogid saavad oma kooli nimekirjadele ligi
                rc = True
            else:
                log.debug(f'nimekiri pole pedag_nahtav')
        else:
            log.debug('nimekirja %s esitaja %s, koht %s, kasutaja %s, kasutaja koht %s' % \
                      (self.id, self.esitaja_kasutaja_id, self.esitaja_koht_id, user.id, user.koht_id))
        
        if test:
            # välja arvatud koolipsyhholoogi testidele, millele saavad ligi ainult koolipsyhholoogid
            if test.avaldamistase == const.AVALIK_LITSENTS:
                if test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
                    if user.on_koolipsyh and self.esitaja_kasutaja_id == user.id:
                        rc = True
                    else:
                        log.debug('teise psyhholoogi test')
                        rc = False
                elif test.testiliik_kood == const.TESTILIIK_LOGOPEED:
                    if user.on_logopeed and self.esitaja_kasutaja_id == user.id:
                        rc = True
                    else:
                        log.debug('teise logopeedi test')
                        rc = False

            if self.esitaja_kasutaja_id != user.id:
                # pole mulle määratud nimekiri 
                # kas on hindamine ja olen määratud hindajaks?
                olen_hindaja = False
                if permission == 'thindamine':
                    # kas olen määratud hindajaks?
                    for testiruum in self.testiruumid:
                        if testiruum.get_labiviija(const.GRUPP_HINDAJA_K, user.id):
                            olen_hindaja = True
                            rc = True
                            break

                if not olen_hindaja:
                    if not self.pedag_nahtav or (perm_bit & const.BT_MODIFY and test.testiliik_kood != const.TESTILIIK_KUTSE):
                        # pole teistele nähtav või tahan muuta
                        # kutseeksami korral võivad teised sama kooli õpetajad ka nimekirja muuta
                        log.debug('määratud nimekiri, teine õpetaja')
                        rc = False

            # kui kontrollitakse muutmisõigust, siis peab olema test hetkel avalik
            if perm_bit & const.BT_MODIFY:
                if test.avaldamistase not in (const.AVALIK_SOORITAJAD,
                                              const.AVALIK_OPETAJAD,
                                              const.AVALIK_MAARATUD,
                                              const.AVALIK_LITSENTS):
                    # test pole enam avalik
                    log.debug('Test %s pole avalik' % test.id)
                    rc = False
                else:
                    dt = date.today()
                    if test.avalik_alates and test.avalik_alates > dt or \
                       test.avalik_kuni and test.avalik_kuni < dt:
                        # pole enam avalik test
                        log.info('Test %s pole enam avalik' % test.id)
                        rc = False
        return rc

    @property
    def testiruum1(self):
        "Avaliku vaate testi korral nimekirja esimene testiruum"
        for r in self.testiruumid:
            return r

    def give_avalik_testiruum(self, testikoht):
        """Luuakse testiruumi kirje - avaliku vaate testi korral.
        """
        for testiruum in self.testiruumid:
            if testiruum.testikoht == testikoht:
                return testiruum
        tahis = testikoht.gen_testiruum_tahis()
        testiruum = Testiruum(testikoht=testikoht,
                              arvuti_reg=const.ARVUTI_REG_POLE,
                              tahis=tahis,
                              ruum_id=None)
        self.testiruumid.append(testiruum)
        return testiruum

    @classmethod
    def kuujagamised(cls, kasutaja_id, kpv):
        "Õpetaja töölaual ühe kuu jagamiste kuvamiseks"
        algus = date(kpv.year, kpv.month, 1)
        if kpv.month == 12:
            lopp = date(kpv.year+1, 1, 1)
        else:
            lopp = date(kpv.year, kpv.month+1, 1)
        q = (Nimekiri.query
             .filter_by(esitaja_kasutaja_id=kasutaja_id)
             .filter(Nimekiri.alates>=algus)
             .filter(Nimekiri.alates<lopp)
             .order_by(Nimekiri.alates)
             )
        return q.all()
