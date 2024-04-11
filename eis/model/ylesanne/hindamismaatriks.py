"Ülesande andmemudel"

import re
import math
from eis.model.entityhelper import *
_ = usersession._
from . import util

class Hindamismaatriks(EntityHelper, Base):
    """Hindamismaatriksi rida, 
    QTI vaste: mapping/mapEntry või mapping/areaMapEntry või mapping/correctResponse/value
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kood1 = Column(String(2000)) # hinnatav väärtus (QTI mapKey) või selle esimene osa
    kood2 = Column(String(256)) # hinnatava väärtuse (QTI mapKey) teine osa (kasutatakse siis, kui baastyyp on pair või directedPair)
    oige = Column(Boolean) # kas on märgitud õigeks vastuseks (QTI correctResponse)
    kujund = Column(String(10)) # hinnatava kujundi liik (QTI shape, areaMapEntry korral)
    koordinaadid = Column(Text) # hinnatava kujundi koordinaadid (QTI coords, areaMapEntry korral; jrk nr lüngata panga ja kirjavahemärgi lisamise korral)
    selgitus = Column(String(255)) # selgitus    
    jrk = Column(Integer) # ridade järjestus (saab määrata ainult otse andmebaasis, kasutajaliidese kaudu ei saa)
    pallid = Column(Float, sa.DefaultClause('1'), nullable=False) # hinnatava väärtuse eest antavad toorpunktid (QTI mappedValue, nende valikute eest saadud punktid)
    sallivus = Column(Integer) # joonistamise sisuploki korral maksimaalne lubatud kaugus pikslites lahendaja tõmmatud joone ja koostaja antud õige joone vahel (koostamise vaates pool joone laiusest)
    tulemus_id = Column(Integer, ForeignKey('tulemus.id'), index=True) # viide tulemuse kirjele
    tulemus = relationship('Tulemus', foreign_keys=tulemus_id, back_populates='hindamismaatriksid')
    maatriks = Column(Integer, sa.DefaultClause('1'), nullable=False) # mitmes hindamismaatriks (üldjuhul alati 1, aga kolme hulgaga sobitamisel on olemas ka 2)
    tahis = Column(String(25)) # tabamuste loenduri tähis (loendur suureneb ühe võrra, kui sooritaja vastust hinnatakse sellel hindamismaatriksi real)
    tabamuste_arv = Column(Integer) # täpne tabamuste arv, mille korral antakse punkte (kui on tühi, siis korduvaid tabamusi ei arvestata, st punkte annab ainult esimene tabamus)
    tingimus = Column(String(256)) # lisatingimuse valem, mis võib sõltuda teistest vastustest - kui valem on antud ja valemi väärtus pole tõene, siis see maatriksirida ei anna tabamust
    valem = Column(Boolean) # kas vastuse võrdlemisel võtta hindamismaatriksi vastust valemina (matemaatika korral, muudes sisuplokkides kasutatakse tabelis Tulemus olevat märget)
    teisendatav = Column(Boolean) # kas vastuse võrdlemisel vastust (nii maatriksi vastust kui ka sooritaja vastust) lihtsustatakse (matemaatika korral)
    vrd_tekst = Column(Boolean) # kas vastuse võrdlemisel võrreldakse ainult tekstina (matemaatilist tähendust ei arvestata, matemaatika korral)
    trans = relationship('T_Hindamismaatriks', cascade='all', back_populates='orig')
    _parent_key = 'tulemus_id'
    logging = True
    
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .tulemus import Tulemus

        parent = self.tulemus or self.tulemus_id and Tulemus.get(self.tulemus_id)
        if parent:
            parent.logi('Hindamismaatriks %s %s %s %s' % ((self.kood1 or '')[:10], (self.kood2 or '')[:10], self.id or '', liik), vanad_andmed, uued_andmed, logitase)

    @property
    def korduv_tabamus(self):
        "Korduvaid tabamusi arvestatakse parajasti siis, kui on antud tabamuste arv"
        return self.tabamuste_arv is not None

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        for rcd in self.trans:
            li.extend(rcd.pack(delete, modified))
        return li

    def get_pallid(self):
        if self.pallid is None and self.oige:
            return 1
        elif self.pallid and self.tabamuste_arv:
            # real olev pallide arv on mitme tabamuse peale kokku
            # leiame yksikvastuse pallide arvu
            return float(self.pallid) / self.tabamuste_arv
        else:
            return self.pallid

    @property
    def is_correct(self):
        # kas on correctResponse/value
        return self.oige is True

    @property
    def is_mapEntry(self):
        # kas on mapEntry
        return self.pallid is not None and self.kood1 is not None \
            and (self.koordinaadid is None or self.kood2 is not None)

    @property
    def is_areaMapEntry(self):
        # kas on areaMapEntry
        return self.koordinaadid is not None and self.kood2 is None

    def num_kood1(self, e_locals, lang=None, valem=False):
        """Õigete vastuste näitamisel kasutatav kood1 väärtus.
        Erineb päris kood1 väärtusest arvude vahemiku korral.
        Kasutada ainult siis, kui on baastyyp arvuline.
        """
        t = self.tulemus
        baastyyp = t.baastyyp
        t_valem = t.valem
        tran = self.tran(lang)
        kuni = None
        alates, err0, err, buf1 = eval_formula(tran.kood1, e_locals, comma=not t_valem)
        if isinstance(alates, str):
            try:
                alates = float(alates)
            except:
                alates = None
        if alates is None:
            return None, ''
        if tran.kood2:
            # 3 kohta peale koma, aga ilma nullideta peale koma
            kuni, err0, err, buf1 = eval_formula(tran.kood2, e_locals, comma=True)
            if isinstance(kuni, str):
                try:
                    kuni = float(kuni)
                except:
                    kuni = None
            if kuni is None:
                return None, ''
            f = (alates + kuni)/2.
            buf = '%s – %s' % (fstr(alates), fstr(kuni))
        else:
            f = alates
            buf = fstr(alates)

        if baastyyp == const.BASETYPE_INTEGER:
            value = round(f)
        else:
            value = f
        return value, buf

    def matches(self, response, hm_pos, basetype=None, lang=None, f_locals={}, partvalue=None):
        """Leitakse vastusele vastavad punktid
        response - klassi QResponse või Kvsisu objekt, mille atribuut maatriks
        võrdub antud kirje välja maatriks väärtusega.
        """
        rc = False
        correct = None
        points = None
        sbuf = ''
        buf = ''
        rbuf = ''
        
        tulemus = self.tulemus
        kysimus = None
        for kysimus in tulemus.kysimused:
            break
        if not basetype:
            basetype = tulemus.baastyyp

        def _ymard_float(txt):
            # vastuse tekst muudetakse floatiks ja leitakse komakohtade arv
            svalue = txt.strip().replace(',','.')
            value = float(svalue)
            # leiame, mitu komakohta on kasutatud
            li = svalue.split('.')
            komakohad = len(li) > 1 and len(li[1]) or 0
            return value, komakohad

        def match_number(response):
            # BASETYPE_INTEGER, BASETYPE_FLOAT
            rc = False
            alates = kuni = h_ymard = None
            if self.kood2:
                buf = ' "%s ... %s"' % (self.kood1, self.kood2)
            else:
                buf = ' "%s"' % (self.kood1)

            if self.kood1 == '':
                # tyhi vastus
                alates = ''

            elif tulemus.valem:
                # valem, mis arvutab õige vastuse ylejäänud vastuste põhjal
                # arvutame valemiga, et leida maatriksi reaga määratud õige vastus
                alates, err0, err, buf1 = eval_formula(self.kood1, f_locals)
                if not err and not err0 and alates and not isinstance(alates, (int, float)):
                    err = 'Vigane valem, arvutustulemus ei ole arv (%s)' % alates
                if not err and not err0 and self.kood2:
                    kuni, err0, err, buf1 = eval_formula(self.kood2, f_locals)
                    if not err and not err0 and kuni and not isinstance(kuni, (int, float)):
                        err = 'Vigane valem, arvutustulemus ei ole arv (%s)' % kuni                        
                if err0 or err:
                    buf += err0 or err
                    alates = kuni = None
            else:
                # pole valemit, lihtsalt arvud
                try:
                    alates, a_ymard = _ymard_float(self.kood1)
                    if self.kood2:
                        kuni, k_ymard = _ymard_float(self.kood2)
                        h_ymard = max(a_ymard, k_ymard)
                    else:
                        h_ymard = a_ymard
                except ValueError:
                    alates = kuni = None

            cmp_response = response.sisu or ''

            if kysimus and kysimus.rtf:
                # eemaldame HTML sildid
                cmp_response = html_as_string(cmp_response).replace(' ', '')
                
            if alates == '':
                rc = cmp_response == ''
            elif cmp_response and alates is not None:
                try:
                    value, r_ymard = _ymard_float(cmp_response)
                except:
                    value = None
                    rc = False
                else:
                    ymard = tulemus.ymard_komakohad
                    ymardet = tulemus.ymardet
                    if ymard is None:
                        # ymardamise komakohti pole antud, lahendaja ei või ymardada
                        if ymardet and h_ymard is not None:
                            # maatriksis on ymardatud vastus, lahendaja ei või rohkem ymardada
                            # ymardame lahendaja vastuse sama palju kui maatriksis on ymardatud
                            ymard = h_ymard
                        else:
                            # maatriksis on täpne vastus
                            ymard = None
                    else:
                        # koostaja on ette andnud, mitme komakohani on lubatud ymardada
                        if h_ymard is not None and h_ymard < r_ymard:
                            # lahendaja on andnud täpsema arvu kui on maatriksis
                            if ymardet:
                                # maatriksis olev arv on ymardatud
                                # kui vastuses on komakohti rohkem kui maatriksis,
                                # siis peab saama ymardada maatriksis olevaks arvuks
                                ymard = h_ymard
                            else:
                                # maatriksis olev arv on täpne ja peab võrduma vastusega
                                ymard = None
                        else:
                            # lahendaja vastus ei ole täpsem kui on maatriksis
                            # maatriksi arvu ymardamine vastuse moodi (aga mitte vähem kui lubatud komakohtade arv)
                            # peab andma sama arvu, mis on vastuseks
                            if ymard < r_ymard:
                                ymard = r_ymard

                    diff = 1e-12
                    if ymard is None:
                        # kontroll, kas vastus value vastab täpselt hindamismaatriksi vahemikule
                        if kuni is None:
                            rc = alates - diff <= value <= alates + diff
                        else:
                            rc = alates - diff <= value <= kuni + diff
                    else:
                        # võrdleme ymardatud arve
                        frm = '%%.%df' % (ymard)
                        if kuni is None:
                            # stringide võrdlus
                            # lisame diff, kuna '%.0f' % .5 = '0'
                            v1 = frm % (alates + diff)
                            v2 = frm % (value + diff)
                            rc = v1 == v2
                            buf += '(%s vs %s)' % (v1, v2)
                        else:
                            # vahemikuga võrdlus
                            ymard_alates = float(frm % (alates + diff))
                            ymard_kuni = float(frm % (kuni + diff))
                            rc = ymard_alates - diff/2 <= value <= ymard_kuni + diff

                    slp = tulemus.sallivusprotsent
                    if not rc and slp:
                        alates1 = alates*(100-slp)/100.
                        if kuni is None:
                            kuni1 = alates*(100+slp)/100.
                        else:
                            kuni1 = kuni*(100+slp)/100.
                        rc = alates1 - diff <= value <= kuni1 + diff
                        if rc:
                            buf += ' (± %s%%) ' % slp
                                
            elif cmp_response and alates is None and self.kood1 is not None:
                # erijuht reaalarvu jaoks, mis pole reaalarvu syntaksiga, aga klapib maatriksiga (nt |15|)
                rc = cmp_response == self.kood1
            return rc, buf

        def match_math(response, partvalue):
            # BASETYPE_MATH
            rc = False
            if lang:
                # võib olla tõlgitud
                kood1 = self.tran(lang).kood1
            else:
                kood1 = self.kood1
            buf = ' "%s"' % (kood1)
            if partvalue is not None:
                # võrdusmärk eraldab vastused
                # vastuse osad on juba eraldatud
                cmp_response = partvalue
            else:
                cmp_response = response.sisu or ''

            def _latex2sympy(value):
                "LaTeX-tekstist sympy objekti loomine"
                try:
                    log.debug('PROCESS:%s' % value)
                    return process_sympy(value)
                except Exception as e:
                    log.debug('process_sympy error: %s' % str(e))
                        
            def _evalsympy(value):
                try:
                    if value.is_Equality:
                        # võrrandi korral võrdleme võrrandi vastuseid
                        # näiteks samaväärsed on:
                        # \frac{x^2-x+2}{4}=\frac{x+3}{5}
                        # 5x^2-5x+10=4x+12
                        # 5x^2-9x-2=0
                        v1 = sympy.solve(value)
                    else:
                        # arvutame avaldise väärtuse
                        v1 = value.evalf()
                except AttributeError:
                    # process_sympy('1=1')==True
                    # 'BooleanTrue' object has no attribute 'evalf'
                    v1 = value
                except Exception as e:
                    log.debug('_evalsympy error: %s' % str(e))
                    v1 = None
                return v1

            def _simplifytxt(value):
                # eemaldame nullid koma tagant
                v2 = re.sub(r'\.([0-9]*[1-9])0*([^0-9]|$)', '.\\1\\2', str(value))
                v3 = re.sub(r'\.0*([^0-9]|$)', '\\1', v2)
                return v3

            math_kood1 = latex_kood1 = None
            if self.valem:
                # kood1 ei ole matemaatika, vaid pythoni valem (mis võib välja arvutada matemaatika)
                # lahendaja vastus on matemaatika
                cmp_kood1, err0, err, buf1 = eval_formula(kood1, f_locals, is_sympy=True)
                if err0 or err:
                    buf += ' ' + (err0 or err)
                    cmp_kood1 = None
                else:
                    buf += ' (arvutatud: "%s")' % _simplifytxt('%s' % cmp_kood1)
                # cmp_kood1 võib juba olla matemaatika, aga võib olla ka arv
                if isinstance(cmp_kood1, sympy.Basic):
                    math_kood1 = cmp_kood1
                else:
                    latex_kood1 = cmp_kood1
            else:
                if not tulemus.tyhikud:
                    kood1 = kood1.replace('\\ ', '').rstrip('\\')
                latex_kood1 = fixlatex(kood1)
                buf = ' "%s"' % (latex_kood1)

            if not tulemus.tyhikud:
                # ei arvestata tyhikuid
                # tyhikute eemaldamine teha enne fixlatex() kasutamist!
                cmp_response = cmp_response.replace('\\ ', '').rstrip('\\')
            latex_response = fixlatex(cmp_response)

            if latex_kood1 == latex_response:
                # võivad olla tyhjad
                rc = True
            elif (latex_kood1 is not None and latex_kood1 != '' or math_kood1 is not None) and cmp_response:
                # kontrolli ei toimu, kui valem arvutas None või tyhja stringi
                rc = False
                if tulemus.ladinavene and isinstance(latex_kood1, str) and isinstance(latex_response, str):
                    # loeme samaväärseks need ladina ja vene tähed,
                    # mis näevad samamoodi välja
                    latex_kood1, latex_response = replace_ru_latin(latex_kood1, latex_response)
                    
                if latex_kood1 is not None:
                    # kui hindamismaatriksi vastus ei ole juba matemaatika, siis võrdleme esmalt stringe
                    rc = latex_kood1 == latex_response
                    
                # kui veel pole õigeks loetud ja ei nõuta ainult teksti võrdlemist,
                # või kui teksti ei saa võrrelda, sest valem arvutas juba matemaatika välja,
                # siis võrdleme matemaatilist tähendust
                if not rc and (not self.vrd_tekst or latex_kood1 is None):
                    # võrdleme matemaatilisi avaldisi
                    math_response = _latex2sympy(latex_response)
                    if math_kood1 is None:
                        math_kood1 = _latex2sympy(latex_kood1)
                    if math_response is not None and math_kood1 is not None and math_response != '':
                        rc = math_response == math_kood1
                        if not rc:
                            try:
                                rc = str(math_response) == str(math_kood1)
                            except:
                                # RuntimeError: maximum recursion depth exceeded while calling a Python object
                                # kui math_response = 'lllllllllllllllllllllllllllllllllllllll'
                                pass
                        if rc:
                            buf += ' (matemaatiliselt: "%s", vastatud: "%s)' % (math_kood1, math_response)
                        if not rc and self.teisendatav:
                            # stringid erinevad, aga lubatud on teisendamine
                            # lihtsustame mõlemad avaldised ja võrdleme siis
                            me_response = _evalsympy(math_response)
                            me_kood1 = _evalsympy(math_kood1)
                            
                            s_response = _simplifytxt(me_response)
                            s_kood1 = _simplifytxt(me_kood1)
                                
                            rbuf = '(%s)' % s_response
                            buf += ' (lihtsustatud: "%s", vastatud: "%s")' % (s_kood1, s_response)
                            if me_response is not None and me_response != '' and s_response != '':
                                rc = me_kood1 == me_response or s_kood1 == s_response

                        try:
                            # kui seni ei hinnatud, siis kas on vaja võrrelda arvudena
                            is_cmp_n = not rc and math_response.is_number and math_kood1.is_number
                        except AttributeError as ex:
                            # avaldis on nt list ja tal pole atribuuti is_number
                            is_cmp_n = False
                        if is_cmp_n:
                            # kasutame arvude võrdlust
                            try:
                                value = float(math_response)
                                alates = float(math_kood1)
                            except:
                                pass
                            else:
                                # nii vastus kui ka hindamismaatriksi kood1 on arvud
                                diff = 1e-12
                                kuni = None
                                # võrdlus vahemikus
                                if self.kood2:
                                    try:
                                        kuni, k_ymard = _ymard_float(self.kood2)
                                    except:
                                        pass
                                    else:
                                        rc = alates - diff <= value <= kuni + diff
                                        if rc:
                                            buf += ' (lubatud vahemikus) '
                                # võrdlus protsentidega
                                slp = tulemus.sallivusprotsent
                                if not rc and slp:
                                    alates1 = alates*(100-slp)/100.
                                    if kuni is None:
                                        kuni1 = alates*(100+slp)/100.
                                    else:
                                        kuni1 = kuni*(100+slp)/100.
                                    rc = alates1 - diff <= value <= kuni1 + diff
                                    if rc:
                                        buf += ' (± %s%%) ' % slp
            return rc, buf

        def match_mathml(response):
            # BASETYPE_MATHML
            rc = False
            if lang:
                # võib olla tõlgitud
                kood1 = self.tran(lang).kood1
            else:
                kood1 = self.kood1
            buf = ' "%s"' % (kood1)

            cmp_response = response.sisu or ''

            if tulemus.valem:
                # valem, mis arvutab õige vastuse ylejäänud vastuste põhjal
                # arvutame valemiga, et leida maatriksi reaga määratud õige vastus
                cmp_kood1, err0, err, buf1 = eval_formula(kood1, f_locals)
                if err0 or err:
                    buf += err0 or err
                    cmp_kood1 = None
            else:
                cmp_kood1 = kood1

            if isinstance(cmp_kood1, str):
                # kontrolli ei toimu, kui valem arvutas None või mitte-stringi
                if not tulemus.tostutunne:
                    cmp_kood1 = cmp_kood1.lower()
                    cmp_response = cmp_response.lower()
                    
                def _simplifytxt(value):
                    # eemaldame tyhikud
                    return value.replace('&#xa0;','').replace('<mo></mo>','')
                
                cmp_kood1 = _simplifytxt(cmp_kood1)
                cmp_response = _simplifytxt(cmp_response)

                if tulemus.ladinavene:
                    # loeme samaväärseks need ladina ja vene tähed,
                    # mis näevad samamoodi välja
                    cmp_kood1, cmp_response = replace_ru_latin(cmp_kood1, cmp_response)
                    
                rc = cmp_kood1 == cmp_response
                log.info('\nV:%s\nH:%s' % (cmp_kood1, cmp_response))
            return rc, buf

        def match_boolean(response):
            buf = ' "%s"' % (self.kood1)
            def _str_to_bool(value):
                return value and value.lower() not in ('false', '0')
                    
            if self.tulemus.valem:
                # arvutame valemiga, et leida maatriksi reaga määratud õige vastus
                is_true, err0, err, buf1 = eval_formula(self.kood1, f_locals)
                if err0 or err:
                    buf += err0 or err
                    is_true = None
            else:
                # pole valemit
                is_true = _str_to_bool(self.kood1)

            cmp_response = _str_to_bool(response.sisu or '')
            rc = cmp_response == is_true
            return rc, buf

        def match_string(response):
            # BASETYPE_STRING, BASETYPE_POSSTRING
            rc = False
            if lang:
                # võib olla tõlgitud
                kood1 = self.tran(lang).kood1
            else:
                kood1 = self.kood1

            buf = ' "%s"' % (kood1)

            cmp_response = response.sisu or ''

            if tulemus.valem:
                # valem, mis arvutab õige vastuse ylejäänud vastuste põhjal
                # arvutame valemiga, et leida maatriksi reaga määratud õige vastus
                cmp_kood1, err0, err, buf1 = eval_formula(kood1, f_locals)
                if err0 or err:
                    buf += err0 or err
                    cmp_kood1 = None
            else:
                cmp_kood1 = kood1

            if basetype == const.BASETYPE_POSSTRING:
                try:
                    nseq = int(self.koordinaadid)
                    rseq = int(response.koordinaat)
                except Exception as ex:
                    log.error(ex)
                    nseq = rseq = None

                if rseq is None or rseq != nseq:
                    # see kirje ei hinda seda vastust, sest pole sama lynga kirje
                    cmp_kood1 = None
                    
            if isinstance(cmp_kood1, str):
                # kontrolli ei toimu, kui valem arvutas None või mitte-stringi
                if not tulemus.tostutunne:
                    cmp_kood1 = cmp_kood1.lower()
                    cmp_response = cmp_response.lower()

                if kysimus and kysimus.rtf:
                    # eemaldame HTML sildid, teisendame tyhikud jms
                    cmp_kood1 = html_as_string(cmp_kood1)
                    cmp_response = html_as_string(cmp_response)

                if not tulemus.tyhikud:
                    cmp_kood1 = cmp_kood1.replace(' ', '')
                    cmp_response = cmp_response.replace(' ', '')
                    
                if tulemus.ladinavene:
                    # loeme samaväärseks need ladina ja vene tähed,
                    # mis näevad samamoodi välja
                    cmp_kood1, cmp_response = replace_ru_latin(cmp_kood1, cmp_response)
                        
                if tulemus.regavaldis or tulemus.regavaldis_osa:
                    try:
                        cmp_response = cmp_response.replace('\n','')
                        if tulemus.regavaldis_osa:
                            # alamteksti vastavus avaldisele
                            buf += _(" (regulaaravaldis tekstiosale)")
                            rc = re.search(cmp_kood1, cmp_response)
                        else:
                            # kogu vastuse vastavus avaldisele
                            buf += _(" (regulaaravaldis kogu tekstile)")
                            cmp_kood1 += '$'
                            rc = re.match(cmp_kood1, cmp_response)
                    except:
                        rc = False
                else:
                    rc = cmp_kood1 == cmp_response
            return rc, buf

        def match_point(response):
            rc = False
            buf = ' "%s:%s"' % (self.kujund, self.koordinaadid)
            #li = response.split(',')
            #x = float(response[0])
            #y = float(response[1])
            punkt = response.punkt
            if punkt:
                x, y = punkt
                if util.point_in_shape(x, y, self.koordinaadid, self.kujund):
                    rc = True
            return rc, buf

        def match_polyline(response):
            rc = False
            buf = ' "%s:%s"' % (self.kujund, self.koordinaadid)
            koordinaadid = response.koordinaadid
            if (response.kujund == 'ray' and self.kujund != 'ray'):
                # kui vastus on kiir, siis peab ka maatriksis kiir olema
                # kui maatriksis on kiir, siis võib vastata ka joonega
                #if (self.kujund == 'ray') != (response.kujund == 'ray'):
                # hm on kiir ja vastus mitte, või vastus on kiir ja hm mitte
                buf += " (%s)" % _("erinev kujundi tüüp")
            elif koordinaadid:
                if self.kujund == 'ray':
                    r_koordinaadid = response.koordinaadid
                    rc, buf2 = self._rays_match(r_koordinaadid)
                    if not rc and response.kujund == 'line':
                        # vastati joonega, proovime vastust teises suunas kiirena
                        r_koordinaadid2 = [r_koordinaadid[1], r_koordinaadid[0]]
                        rc, buf3 = self._rays_match(r_koordinaadid2)
                        buf2 = (buf2 or '') + (buf3 or '')
                else:
                    rc, buf2 = self._polylines_match(response.koordinaadid)
                if not rc:
                    buf = '%s (%s)' % (buf, buf2)
            return rc, buf
        
        cond_valid, buf1 = self._check_condition(f_locals)
        sbuf += buf1
        
        if not cond_valid:
            # kuna tingimus ei kehti, siis hindamismaatriksi rida ei arvestata
            sbuf += _("Tingimus pole täidetud") + '\n'
            
        elif self.is_mapEntry or (self.is_correct and not self.is_areaMapEntry):
            if basetype == const.BASETYPE_PAIR:
                buf = ' "%s, %s"' % (self.kood1, self.kood2)
                rc = self.kood1 == response.kood1 and self.kood2 == response.kood2 \
                     or self.kood1 == response.kood2 and self.kood2 == response.kood1

            elif basetype == const.BASETYPE_DIRECTEDPAIR:
                buf = ' "%s, %s"' % (self.kood1, self.kood2)
                if response.sisu and self.koordinaadid:
                    # lynkadeta pank
                    nseq = self.koordinaadid
                    buf += ' (%s)' % nseq
                    rc = self.kood1 == response.kood1 and nseq == response.sisu
                else:
                    rc = self.kood1 == response.kood1 and self.kood2 == response.kood2

            elif basetype == const.BASETYPE_IDENTIFIER:
                buf = ' "%s"' % (self.kood1)
                rc = self.kood1 == response.kood1

            elif basetype == const.BASETYPE_INTEGER or basetype == const.BASETYPE_FLOAT:
                rc, buf = match_number(response)
                
            elif basetype == const.BASETYPE_MATH:
                rc, buf = match_math(response, partvalue)

            elif basetype == const.BASETYPE_MATHML:
                rc, buf = match_mathml(response)
                                    
            elif basetype == const.BASETYPE_BOOLEAN:                
                rc, buf = match_boolean(response)
                
            elif basetype == const.BASETYPE_IDLIST:
                # trail
                buf = ' "%s"' % (self.kood1)
                idlist = response.sisu
                if idlist:
                    rc = self.kood1.strip(';') == idlist.strip(';')
                else:
                    rc = False
            else:
                # BASETYPE_STRING, BASETYPE_POSSTRING
                rc, buf = match_string(response)
                    
        elif self.is_areaMapEntry:
            if basetype == const.BASETYPE_POINT:            
                rc, buf = match_point(response)
                    
            elif basetype == const.BASETYPE_POLYLINE:
                rc, buf = match_polyline(response)
            else:
                buf = _(" (vale baastüübiga {s})").format(s=basetype)

        if rc:
            points = self.get_pallid()
            if self.tahis:
                buf = '%s (%s)' % (buf, self.tahis)
            sbuf += _("Maatriksi {n}. rida {s} annab sellise vastuse eest {p} punkti").format(n=hm_pos, s=buf, p=fstr(points))
            sbuf += '\n'
        return rc, points, sbuf, rbuf

    def matches_identifier(self, kood, f_locals):
        """Leitakse basetype="identifier" korral valitud vastusele vastavad punktid.
        Seda funktsiooni kasutatakse järjestamisülesande korral.
        """
        rc = False
        points = None
        buf = sbuf = ''

        cond_valid, buf1 = self._check_condition(f_locals)
        sbuf += buf1
        if not cond_valid:
            sbuf += _("Tingimus pole täidetud") + '\n'
            
        elif self.kood1 and self.kood2:
            # seostamine pildil koos valevastuste loenduriga
            buf = ' "%s-%s"' % (self.kood1, self.kood2)
            try:
                kood1, kood2 = kood.split('-')
            except:
                rc = False
            else:
                rc = kood1 == self.kood1 and kood2 == self.kood2 or \
                     kood1 == self.kood2 and kood2 == self.kood1
        else:
            # järjestamine
            buf = ' "%s"' % (self.kood1)
            rc = self.kood1 == kood

        if rc:
            points = self.pallid
            if points is None:
                points = 1
                    
        if rc:
            sbuf += _("Maatriksi rida {s} annab sellise vastuse eest {p} punkti").format(s=buf, p=points) + '\n'
        else:
            sbuf += _("Maatriksi rida {s} selle vastuse eest punkte ei anna").format(s=buf) + '\n'
        #log.debug(buf)
        return rc, points, sbuf

    def _check_condition(self, f_locals):
        "Kontrollitakse, kas hindamismaatriksi tingimus kehtib"
        rc = True
        buf = ''
        if self.tingimus:
            # real on antud tingimus, mis peab kehtima, et rida arvestataks
            cond_valid, err0, err, buf1 = eval_formula(self.tingimus, f_locals)
            rc = bool(cond_valid)
            buf = '%s %s=%s (%s)\n' % (_("Tingimus"), self.tingimus, cond_valid,
                                       rc and _("Kehtiv") or _("Kehtetu"))
        return rc, buf

    @property
    def cx(self):
        return util.cx(self.koordinaadid, self.kujund)
    
    @property
    def cy(self):
        return util.cy(self.koordinaadid, self.kujund)
        
    def _rays_match(self, points1):
        """Leitakse, kas parameetriga antud kiir vastab maatriksis olevale kiirele
        """
        if len(points1) < 2:
            return False, _("vastus on punkt")
        points2 = eval(self.koordinaadid)

        # kas alguspunkt on piisavalt lähedal?
        if abs(points2[0][0] - points1[0][0]) > self.sallivus or \
           abs(points2[0][1] - points1[0][1]) > self.sallivus:
            return False, _("alguspunktid erinevad")

        # kas suund on sama?
        angle2 = math.atan2(points2[1][1] - points2[0][1], points2[1][0] - points2[0][0])
        angle1 = math.atan2(points1[1][1] - points1[0][1], points1[1][0] - points1[0][0])
        min_angle = min((angle1, angle2))
        max_angle = max((angle1, angle2))
        diff = max_angle - min_angle
        if diff > math.pi:
            # yks on  < -90 kraadi, teine on > 90 kraadi
            min_angle += 2 * math.pi
            diff = min_angle - max_angle
        ANGLE_TOLERANCE = .314 # 18 kraadi
        if diff > ANGLE_TOLERANCE:
            return False, _("suund erineb: maatriksis {n1} kraadi, vastuses on {n2} kraadi").format(
                n1=int(math.degrees(angle2)), n2=int(math.degrees(angle1)))

        # kas vastus jääb maatriksis oleva kiire sisse
        pt = self._polyline_in_polyline(points1, points2, self.sallivus)
        if pt:
            # kui ei jää, siis võib olla vastuse kiir pikem kui maatriksi kiir
            # kontrollime, kas maatriksi kiir jääb vastuse kiire sisse
            pt = self._polyline_in_polyline(points2, points1, self.sallivus)
            if pt:
                # need on erinevad kiired
                return False, _("kiired erinevad")
        return True, None

    def _polylines_match(self, points1):
        """Leitakse, kas parameetriga points antud murdjoone iga punkt on
        piisavalt lähedal kirjega määratud õige murdjoone mõne punktiga
        ja vastupidi.
        Kui ei ole lähedal, siis tagastatakse False ja selgitav tekst
        """
        points2 = eval(self.koordinaadid)
        # Ühe murdjoone mingi punkt on teise murdjoone lähedal parajasti siis,
        # kui punkti ümbritseva ruudu mõni serv lõikub teise murdjoone mõne lõiguga

        # Punktide lähedust kontrollitakse
        #  1. vastuse murdjoone iga nurgapunkti korral
        #  2. vastuse murdjoone iga lõigu keskpunkti korral
        #  3. maatriksi murdjoone iga nurgapunkti korral
        #  4. maatriksi murdjoone iga lõigu keskpunkti korral
        pt = self._polyline_in_polyline(points1, points2, self.sallivus)
        if pt:
            return False, _("vastuse murdjoone punkt ({x},{y}) on teisest murdjoonest kaugel").format(x=pt[0],y=pt[1])
        pt = self._polyline_in_polyline(points2, points1, self.sallivus)
        if pt:
            return False, _("maatriksi murdjoone punkt ({x},{y}) on teisest murdjoonest kaugel").format(x=pt[0],y=pt[1])
        return True, None
    
    def _polyline_in_polyline(self, points1, points2, sallivus):
        """Tagastab ühe murdjoone points1 punkti, mis on rohkem kui sallivuse kaugusel
        murdjoonest points2.
        Kui murdjoon points1 on üleni murdjoone points2 lähedal, siis tagastatakse None.
        """
        prev = None
        for pt in points1:
            # murdjoone iga punkti korral kontrollime selle kaugust teisest murdjoonest
            if not self._point_near_polyline(pt[0], pt[1], sallivus, points2):
                return pt[0], pt[1]
            #log.debug(u'punkt (%d,%d) on sobivas kauguses murdjoonest %s' % (pt[0],pt[1],str(points2)))
            if prev:
                # leiame viimase lõigu keskpunkti
                cx = prev[0] + (pt[0] - prev[0])/2
                cy = prev[1] + (pt[1] - prev[1])/2
                if not self._point_near_polyline(cx, cy, sallivus, points2):
                    return cx, cy

            prev = pt
        return None

    def _point_near_polyline(self, x, y, sallivus, points):
        for n in range(len(points)-1):
            if self._intersect_circle_line(x, y, sallivus,
                                           points[n][0], points[n][1],
                                           points[n+1][0], points[n+1][1]):
                return True
        return False

    def _intersect_circle_line(self, cx, cy, r, x1, y1, x2, y2):
        # kas punkti (cx,cy) ümbritseva ruudu mõni serv lõikub lõiguga [(x1,y1),(x2,y2)] 
        a  = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)
        b  = 2 * ( (x2 - x1) * (x1 - cx) + (y2 - y1) * (y1 - cy)   )
        cc = cx*cx + cy*cy + x1*x1 + y1*y1 - 2 * (cx * x1 + cy * y1) - r*r
        deter = b*b - 4*a*cc

        rc = None
        if deter < 0:
            #log.debug('outside')
            rc = False
        elif deter == 0:
            #log.debug('tangent')
            rc = False
        else:
            e  = math.sqrt(deter)
            u1 = ( -b + e ) / ( 2*a )
            u2 = ( -b - e ) / ( 2*a )

            if ( (u1 < 0 or u1 > 1) and (u2 < 0 or u2 > 1) ):
                if ( (u1 < 0 and u2 < 0) or (u1 > 1 and u2 > 1) ):
                    #log.debug('outside')
                    rc = False
                else:
                    #log.debug('inside')
                    rc = True
            else:
                #log.debug('intersection')
                rc = True
        #log.debug('kas punkti (%s,%s) ümbritseva ruudu mõni serv lõikub lõiguga [(%s,%s),(%s,%s)]? %s' % (cx, cy, x1, y1, x2, y2, rc))
        return rc
    
    def copy(self, ignore=[], **di):
        cp = EntityHelper.copy(self, ignore=ignore, **di)
        self.copy_subrecords(cp, ['trans',])
        return cp

def fstr(f):
    return re.sub(r'\,?0+$', '', (('%.3f') % f).replace('.',','))

def replace_ru_latin(v1, v2):
    # loeme samaväärseks need ladina ja vene tähed,
    # mis näevad samamoodi välja
    chars_l = 'aeopcyxABEKMHOPCTX'
    chars_r = 'аеорсухАВЕКМНОРСТХ'
    tra = str.maketrans(chars_r, chars_l)
    if v1:
        v1 = v1.translate(tra)
    if v2:
        v2 = v2.translate(tra)
    return v1, v2
