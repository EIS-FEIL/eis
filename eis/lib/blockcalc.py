"""Automaatne hindamine
"""
import html
from eis.lib.base import *
from eis.lib.helpers import fstr
from eis.lib.formulaenv import FormulaEnv
from eiscore.recordwrapper import RecordWrapper
log = logging.getLogger(__name__)
_ = i18n._

class BlockCalc(object):
    "Automaatne hindamine"
    
    def __init__(self, handler):
        self.handler = handler
        self.request = handler and handler.request or None

    # calculate_auto
    def calculate_temp(self, item, responses, lang, temp_yv):
        "Tulemuse arvutamine ainult arvutihinnatavate küsimuste põhjal, ilma testita lahendamisel"
        jatka = False
        total, arvuti, kasitsi, max_pallid, buf, on_arvuti, on_kasitsi, f_locals = \
               self.calculate(item, responses, lang, temp_yv, oige=False, koefitsient=1, testiosa=None)

        if not on_kasitsi:
            kasitsi = None
        elif on_arvuti:
            total = None
        else:
            total = None
            arvuti = None
        temp_yv.toorpunktid = total
        temp_yv.pallid_arvuti = arvuti
        temp_yv.pallid_kasitsi = kasitsi
        msg, jatka = self.gen_res_msg(temp_yv, item, max_pallid, on_arvuti, on_kasitsi, lang)
        buf += '<p><b>' + msg + '</b></p>'
        return total, arvuti, kasitsi, max_pallid, msg, buf, jatka

    def gen_res_msg(self, yv, item, max_pallid, on_arvuti, on_kasitsi, lang):
        "Tulemuse arvutamine ainult arvutihinnatavate küsimuste põhjal, ilma testita lahendamisel"
        from eis.lib.npcalc import Npcalc
        jatka = False
        if item.on_tagasiside:
            #if not on_kasitsi and item.on_tagasiside:
            # kui on tagasisidega ylesanne, siis antakse tagasiside
            npc = Npcalc(self.handler, None, None, None, None)
            msg, jatka = npc.calc_ylesanne_tagasiside(yv, item, lang, True)
            kasitsi = None
        elif not on_kasitsi:
            total = yv.toorpunktid
            msg = _("Tulemus: {p1} punkti {p2}-st võimalikust").format(p1=fstr(total), p2=fstr(max_pallid))
            kasitsi = None
        elif on_arvuti:
            total = None
            arvuti = yv.pallid_arvuti
            kasitsi = yv.pallid_kasitsi
            msg = model.Ylesandevastus.get_tulemus_eraldi_(max_pallid, arvuti, kasitsi, total)
        else:
            msg = _("Ülesanne ei ole arvutihinnatav")
            total = None
            arvuti = None

        return msg, jatka

    def calculate(self, item, responses, lang, yv, oige=False, koefitsient=1, testiosa=None, yhinne=None):
        """Hindepallide arvutamine
        item - ylesanne
        responses - dict, milles iga kysimuse koodi kohta on key ja sellele vastab kv sarnane MemKV
        oige - kas hinnata õige/vale järgi
        koefitsient - vy.koefitsient, millega korrutatakse toorpunktid, et saada pallid
        yhinne - hindaja hindamine (kui puudub, siis arvestatakse kehtivaid punkte)
        """
        max_pallid = item.max_pallid

        # arvutatakse arvutihinnatavate kysimuste tulemused
        # vastamise vormid, mille korral ei ole andmebaasis vastuseid
        p_vormid = (const.VASTVORM_KP, const.VASTVORM_SP, const.VASTVORM_SH)
        on_ptest = testiosa and testiosa.vastvorm_kood in p_vormid or False
        buf, on_arvuti, on_kasitsi, f_locals = \
             self._calculate_kysimused(item, responses, lang, yv, oige, koefitsient, on_ptest)

        total, arvuti, kasitsi, sp_buf = self._blocks_total(responses, yhinne, yv)
        # arvuti, kasitsi - arvuti või käsitsi antud punktid
        # kui käsitsi on hindamata, siis kasitsi=None
        buf += sp_buf

        if total:
            if item.ymardamine:
                diff = 1e-12
                rtotal = round(total + diff)
                if rtotal != total:
                    buf += _("Punktide arv {p} ümardatakse").format(p=fstr(total)) + '\n'
                    total = rtotal

            if total < 0:
                ## ylesande tulemus võib olla negatiivne ainult siis, kui test_id=2044 (EH-237)
                #if not testiosa or testiosa.test_id != 2044:
                buf += _("Negatiivne punktide arv {p} muudetakse 0-ks").format(p=fstr(total)) + '\n'
                total = 0

        if yv:
            yv.arvutuskaik = buf
        return total, arvuti, kasitsi, max_pallid, buf, on_arvuti, on_kasitsi, f_locals
    
    def _calculate_kysimused(self, item, responses, lang, ylesandevastus, oige, koefitsient, on_ptest):
        """Hindepallide arvutamine
        item - ylesanne
        responses - dict, milles iga kysimuse koodi kohta on key ja sellele vastab kv
        oige - kas hinnata õige/vale järgi
        koefitsient - vy.koefitsient, millega korrutatakse toorpunktid, et saada pallid
        #yhinded - hindajate poolt antud kehtivad hinded, 
        #millest võtta mitte-arvutihinnatavate kysimuste tulemused
        """
        buf = ''
        on_arvuti = False # kas on mõni arvutihinnatav küsimus
        on_kasitsi = False # kas on mõni käsitsihinnatav küsimus
        on_vastus = False # kas on mõnele küsimusele vastatud
        # kogume kasutaja antud vastused lokaalmuutujateks
        f_locals = self._calc_formula_locals(item, responses)

        formulas = list() # valemid (teise raundi kysimused-vastused)
        kood_list = [kood for kood in responses.keys() if kood]
        kood_list.sort()

        # tabamusega hindamismaatriksiridade tähiste loendurid
        q = (model.SessionR.query(model.Hindamismaatriks.tahis).distinct()
             .filter(model.Hindamismaatriks.tahis!=None)
             .join(model.Hindamismaatriks.tulemus)
             .filter(model.Tulemus.ylesanne_id==item.id))
        loendurid = {tahis: 0 for tahis, in q.all() if tahis}
        oigsus_kv_k = {}
        
        # märgime kysimused, mis on vastuseta
        if not on_ptest:
            for kood in kood_list:
                kv = responses[kood]
                kysimus = model.Kysimus.get(kv.kysimus_id)
                if not kysimus:
                    log.error('kysimus {k_id} puudub'.format(k_id=kv.kysimus_id))
                    continue
                tulemus = kysimus.tulemus
                # kas on vastuseta
                kv_vastuseta = True
                for ks in get_kvsisud(kv.kvsisud):
                    if not ks.on_vastuseta(tulemus):
                        kv_vastuseta = False
                        on_vastus = True
                        break
                kv.vastuseta = kv_vastuseta

        class AspInfo:
            _on_aspektid = None
            def on_aspektid(self):
                if self._on_aspektid is None:
                    self._on_aspektid = False
                    for ha in item.hindamisaspektid:
                        self._on_aspektid = True
                        break
                return self._on_aspektid
        aspinfo = AspInfo()
        for kood in kood_list:
            kv = responses[kood]
            kysimus = model.Kysimus.get(kv.kysimus_id)
            tulemus = kysimus and kysimus.tulemus
            if not tulemus:
                # pseudokysimused mingite hindamiseks mitte mõeldud andmete
                # hoidmiseks, nt alusteksti kommentaar
                continue

            if kysimus.sisuplokk.tyyp == const.BLOCK_FORMULA:
                formulas.append((kv, kysimus, tulemus))
            else:
                kv_arvutihinnatud = False
                buf += '<b>%s: %s </b>' % (_("Küsimuse ID"), kood)
                if tulemus:
                    buf += ' (%s, %s, ' % (tulemus.kardinaalsus, tulemus.baastyyp)
                    buf += _("võimalik max {p} punkti").format(p=fstr(tulemus.get_max_pallid()) or 0) + ')'
                buf += '\n'

                if tulemus:
                    # kas on arvutihinnatav kysimus?
                    on_ah = tulemus.arvutihinnatav or tulemus.hybriidhinnatav or oige
                    if not on_ah and (tulemus.get_max_pallid() == 0):
                        # kui kysimus pole märgitud arvutihinnatavaks, aga annab 0p
                        # ja ei hinnata aspekte, siis arvutihinnatakse 0p
                        on_ah = not aspinfo.on_aspektid()
                    if on_ah:    
                        # arvutihindamine või hybriidhindamine
                        buf += self._calculate_kysimus(kv, kysimus, tulemus, lang, oige, koefitsient, f_locals, loendurid)
                        if tulemus.arvutihinnatav or kv.arvutihinnatud:
                            on_arvuti = True
                        kv_arvutihinnatud = kv.arvutihinnatud

                if not kv_arvutihinnatud:
                    # käsitsihindamine või hybriidhindamine, mida ei saanud arvutiga hinnata
                    kv_mittekasitsi = kv.vastuseta
                    if kv_mittekasitsi:
                        # kui vastuseta kysimuse juures hinnatakse mitut kysimust
                        # ja mõni neist on vastatud, siis on käsitsi hindamine
                        for t2 in kysimus.oigsus_tulemused:
                            kv2 = responses.get(t2.kood)
                            if kv2 and not kv2.vastuseta:
                                kv_mittekasitsi = False
                                break

                    try:
                        kv_pallid = kv.pallid
                    except AttributeError:
                        kv_pallid = kv.pallid = None
                    # kysimused, millele pole vastatud, saavad automaatselt 0p
                    if kv_mittekasitsi and (kv_pallid is None or kv_pallid == 0 and kv.arvutihinnatud):
                        # vastamata kysimus
                        buf += _("Ei ole vastatud") + '\n'
                        kv.toorpunktid = 0
                        kv.pallid = 0
                        on_arvuti = kv.arvutihinnatud = True
                    else:
                        # käsitsi hinnatav kysimus
                        buf += _("Küsimus {s} pole arvutihinnatav").format(s=kood) + '\n'
                        on_kasitsi = True
                        kv.arvutihinnatud = False

            # jätame meelde, milliste kysimuste õigsuse see kysimus määrab
            li = []
            for t in kysimus.oigsus_tulemused:
                for k in t.kysimused:
                    li.append(k)
            if li:
                oigsus_kv_k[kv] = li

        # lisame tabamuste loendurid, neid kasutatakse:
        # - siinsamas arvutatud väärtuste valemites;
        # - hiljem diagnoosiva testi reeglites
        fenv = FormulaEnv(self.handler)
        f_locals.update(fenv.formula_funcs(responses, loendurid))
        if loendurid:
            buf += '\n<b>' + _("Tabamuste loendurid") + '</b>\n'
            for key in sorted(loendurid.keys()):
                buf += '%s=%s\n' % (key, loendurid[key])
            # lisame kasutatud hindamismaatriksite tähised
            f_locals.update(loendurid)

        # lisame sisuplokkide vaatamiste andmete funktsioonid bvcount, bvtime
        f_locals.update(fenv.get_sisuvaatamised(item, ylesandevastus.sisuvaatamised))
       
        if formulas:
            buf += '\n<b>' + _("Arvutatud väärtused") + '</b>\n'

            # arvutame arvutatavad vastused peale hindamist, round 2 hindamine
            #log.debug('F_LOCALS:%s' % f_locals)
            buf += 'Muutujad: %s\n' % str({key: value for (key, value) in list(f_locals.items()) if not callable(value)})
            for kv, kysimus, tulemus in formulas:
                buf += '<b>%s: %s </b>\n' % (_("Küsimuse ID"), kysimus.kood)
                # arvutame valemite väärtused
                # (võivad sõltuda round 1 hindamisel tekkinud loenduritest)
                buf += self._calc_formula_response(kv, kysimus, f_locals)
                # hindame valemid
                buf += self._calculate_kysimus(kv, kysimus, tulemus, lang, oige, koefitsient, f_locals, loendurid)

        if isinstance(ylesandevastus, model.EntityHelper):
            dloendurid = {l.tahis: l for l in ylesandevastus.loendurid}
            for key, value in loendurid.items():
                l = dloendurid.get(key)
                if l:
                    l.tabamuste_arv = value
                else:
                    l = model.Loendur(tahis=key, tabamuste_arv=value, ylesandevastus=ylesandevastus)
        else:
            ylesandevastus.loendurid = []
            for key, value in loendurid.items():
                r = RecordWrapper(tahis=key, tabamuste_arv=value)
                ylesandevastus.loendurid.append(r)

        # kysimused, mis määravad teiste kysimuste vastuste õigsuse
        responses = {kv.kysimus_id: kv for kv in ylesandevastus.kysimusevastused}
        for kv, kysimused in oigsus_kv_k.items():
            ks_oige = None
            for ks in kv.kvsisud:
                ks_oige = ks.oige
                break
            for k in kysimused:
                kv = responses.get(k.id)
                if kv:
                    for ks in kv.kvsisud:
                        #log.debug('  SET %s=%s' % (k.kood, ks_oige))
                        ks.oige = ks_oige

        ylesandevastus.vastuseta = not on_vastus
        ylesandevastus.mittekasitsi = not on_kasitsi
        return buf, on_arvuti, on_kasitsi, f_locals       

    def _calculate_kysimus(self, kv, kysimus, tulemus, lang, oige, koefitsient, f_locals, loendurid):
        """Arvutame kysimuse arvutihinnatava tulemuse
        
        f_locals on dict, mis sisaldab:
        - kysimuse kood (mitte arvutatud väärtus, baastyyp: INTEGER, FLOAT):
          vastus (kood1 või sisu) arvuna või None
          (kui kysimuse kardinaalsus on MULTIPLE, siis on väärtus list)          
        - kysimuse kood (mitte arvutatud väärtus, baastyyp: STRING, IDENTIFIER):
          vastus (kood1 või sisu) tekstina
          (kui kysimuse kardinaalsus on MULTIPLE, siis on väärtus list)
        - tabamuste loenduri kood:
          vastava tähisega hindamismaatriksiridade tabamuste arv
        - pt:
          funktsioon, mille argument on kysimuse kood (või reg av) ning tagastab kysimuse eest antud punktid
        - val:
          funktsioon, mille argument on kysimuse kood (või reg av) ning tagastab väärtuste listi
          (skalaarid, arvulise baastüübi korral arvud, muidu stringid)
        - uncover_help_cnt:
          funktsioon, mille argument on kysimuse kood (või reg av) ning tagastab pildi avamise abinupu kasutamise arvu
        """
        kood = kysimus.kood
        points = 0
        buf = ''
        sisuplokk = None
        
        # algväärtustame tabamuste loendurid
        for hm in tulemus.hindamismaatriksid:
            if hm.tahis and hm.tahis not in loendurid:
                loendurid[hm.tahis] = 0
                
        # leiame hindepallid
        if kv:
            sisuplokk = kysimus.sisuplokk
            # is_ordered - kysimuse kõik vastused on yhe Kvsisu kirje sisse pakitud
            is_ordered = sisuplokk.tyyp in (const.INTER_ORDER, const.INTER_GR_ORDER, const.INTER_GR_ORDASS)
            if oige is None:
                # hinnatakse sisestatud vastuste järgi
                # vastused on sisestatud siis, kui sisuplokk on sisestatav
                k_oige = not sisuplokk.on_sisestatav
            else:
                # on selgelt ette antud, kas hinnata õige/vale või vastuse järgi
                k_oige = oige

            # arvutame punktid
            if is_ordered:
                # järjestamine, pildil järjestamine
                p, b, oigete_arv, valede_arv = \
                   self._calculate_response_ordered(tulemus, kv, lang, k_oige, f_locals, loendurid)
            else:
                p, b, oigete_arv, valede_arv, loendurid = \
                   self._calculate_response_multiple(sisuplokk, tulemus, kv, lang, k_oige, f_locals, loendurid)
            buf += b
            points = p
        else:
            buf += _("Ei ole vastatud") + '\n'

        if points is None:
            # hybriidhinnatav kysimus, mida ei saanud hinnata arvutiga
            if kv.arvutihinnatud:
                # varem on seda saanud arvutiga hinnata, ilmselt muudeti maatriksit
                kv.toorpunktid = kv.pallid = kv.oigete_arv = kv.valede_arv = None
            kv.arvutihinnatud = False
            buf += _("Hindamismaatriksist vastavat rida ei leitud") + '\n'
            return buf

        if tulemus.min_pallid is not None:
            if points < tulemus.min_pallid:
                buf += _("Miinimum on {p} punkti").format(p=fstr(tulemus.min_pallid)) + '\n'
                points = tulemus.min_pallid
        t_max_pallid = tulemus.get_max_pallid()
        if t_max_pallid is not None:
            if points > t_max_pallid:
                buf += _("Maksimum on {p} punkti").format(p=fstr(t_max_pallid)) + '\n'
                points = t_max_pallid

        # salvestame punktid kysimusevastuse kirjes
        # salvestame 
        kv.toorpunktid = points 
        kv.pallid = points * koefitsient
        if kysimus.pseudo or kysimus.sisuplokk.naide:
            oigete_arv = valede_arv = None
        kv.oigete_arv = oigete_arv
        kv.valede_arv = valede_arv
        kv.arvutihinnatud = not oige
        #log.debug('y%s %s: oiged=%s valed=%s' % (item.id, kysimus.kood, kv.oigete_arv, kv.valede_arv))

        # kui on olemas eraldi kvsisu kirje analyysi jaoks, siis märgime ka sellele, kas lugeda vastus õigeks
        if kv and sisuplokk and sisuplokk.tyyp in (const.INTER_GAP, const.INTER_PUNKT):
            aks = get_kvsisu(kv.kvsisud, const.SEQ_ANALYSIS)
            if aks:
                DIFF = .001
                if kv.pallid is None:
                    aks.oige = None
                elif t_max_pallid is not None and kv.pallid > t_max_pallid - DIFF:
                    aks.oige = const.C_OIGE
                elif kv.pallid > 0:
                    aks.oige = const.C_OSAOIGE
                else:
                    aks.oige = const.C_VALE

        if points:
            buf += _("Küsimus {s} annab {p} punkti").format(s=kood, p=fstr(points))
            if kysimus.ei_arvesta:
                buf += ' (%s)' % _("küsimust ei arvestata kogutulemuses")
            buf += '\n'
        else:
            buf += _("Küsimus {s} ei anna punkte").format(s=kood) + '\n'

        return buf
    
    def _blocks_total(self, responses, yhinne, ylesandevastus):
        "Loeme punktid kokku sisuplokkide kaupa, kuna sisuplokkide siseselt võidakse punkte ymardada"

        buf = '\n<b>' + _("Punktid sisuplokkide kaupa") + '</b>\n'
        kasitsi_hindamata = False
        # jagame punktid sisuplokkide kaupa

        class Blockresp(object):
            def __init__(self):
                self.punktid = 0
                self.arvutipunktid = 0
                self.kasitsipunktid = 0
                self.kysimusevastused = list()
        bresp = dict()

        for kood, kv in responses.items():
            kysimus = model.Kysimus.get(kv.kysimus_id)
            tulemus = kysimus and kysimus.tulemus
            if not tulemus:
                # ei ole tegelikult kysimus
                continue
                    
            if tulemus.arvutihinnatav or tulemus.hybriidhinnatav and kv.arvutihinnatud \
              or (not tulemus.max_pallid and not tulemus.max_pallid_arv):
                # arvutihinnatav kysimus
                khinne = None
            else:
                # käsitsihinnatav kysimus
                khinne = yhinne and yhinne.get_kysimusehinne(kv)
                    
            if khinne:
                # arvestame kehtiva hinde asemel konkreetse hindaja pandud hindeid
                points = khinne.toorpunktid
            else:
                # arvestame kehtivat hinnet (arvutihinnatud või mitte)
                try:
                    points = kv.toorpunktid
                except AttributeError:
                    points = kv.toorpunktid = None
            if points is None:
                kasitsi_hindamata = True
            elif not kysimus.ei_arvesta:
                # kui kysimuse eest on antud punkte, siis leiame sisuploki ja liidame sisuploki punktidele
                kysimus = model.Kysimus.get(kv.kysimus_id)
                sp_id = kysimus.sisuplokk_id
                br = bresp.get(sp_id)
                if not br:
                    br = bresp[sp_id] = Blockresp()
                br.punktid += points
                if tulemus.arvutihinnatav or kv.arvutihinnatud:
                    br.arvutipunktid += points
                else:
                    br.kasitsipunktid += points
                br.kysimusevastused.append(kv)

        total = arvuti = kasitsi = 0
        diff = 1e-12
        for sp_id, br in sorted(bresp.items()):
            sp = model.Sisuplokk.get(sp_id)

            e_buf = ''
            if sp.tyyp == const.INTER_GAP:
                if sp.kysimus.erand346:
                    # erand EH-346
                    valede_vastuste_arv = oigete_vastuste_arv = tyhjade_vastuste_arv = 0
                    tyhistatav = 0
                    for kv in br.kysimusevastused:
                        for kvs in get_kvsisud(kv.kvsisud):
                            if kvs.oige == const.C_OIGE:
                                oigete_vastuste_arv += 1
                            elif kvs.as_string() == '':
                                tyhjade_vastuste_arv += 1
                                tyhistatav += kvs.toorpunktid
                            else:
                                valede_vastuste_arv += 1
                                tyhistatav += kvs.toorpunktid
                            
                    e_buf = _("anti {n1} õiget vastust ja {n2} vale vastust, lisaks {n3} tühja vastust").format(
                        n1=oigete_vastuste_arv, n2=valede_vastuste_arv, n3=tyhjade_vastuste_arv)
                    if oigete_vastuste_arv == 1 and valede_vastuste_arv == 1:
                        e_buf = 'oli %sp; %s' % (fstr(br.punktid), e_buf)
                        e_buf += _(", kuid erandina valede ja tühjade vastuste eest vaikimisi punkte ei arvestata, mistõttu tühistame {p}p").format(p=fstr(tyhistatav)) 
                        br.punktid -= tyhistatav
                        br.arvutipunktid -= tyhistatav
                    e_buf = '(%s)' % e_buf

            buf += _("Sisuplokk {s}: {p1} punkti {p2}").format(s=sp.tahis or sp.seq, p1=fstr(br.punktid), p2=e_buf)

            # tulemuse arvutamine
            if sp.min_pallid is not None and br.punktid < sp.min_pallid:
                br.punktid = sp.min_pallid
                buf += _(", sisuploki min on {p} punkti").format(p=fstr(sp.min_pallid))

            if sp.max_pallid is not None and br.punktid > sp.max_pallid:
                br.punktid = sp.max_pallid
                buf += _(", sisuploki max on {p} punkti").format(p=fstr(sp.max_pallid))

            if sp.ymardamine:
                br.punktid = round(br.punktid + diff)
                buf += _(", ümardatakse {p} punktiks").format(p=fstr(br.punktid)) + '\n'
            else:
                buf += '\n'
                
            total += br.punktid

            # arvutihinnatav osa tulemusest
            points = br.arvutipunktid
            if points:
                if sp.max_pallid is not None and points > sp.max_pallid:
                    points = sp.max_pallid
                if sp.ymardamine:
                    points = round(points + diff)
                arvuti += points

            # käsitsihinnatav osa tulemusest
            points = br.kasitsipunktid
            if points:
                if sp.max_pallid is not None and points > sp.max_pallid:
                    points = sp.max_pallid                
                if sp.ymardamine:
                    points = round(points + diff)
                kasitsi += points

        if kasitsi_hindamata:
            # mõni kysimus on hindamata
            kasitsi = None
            total = None

        return total, arvuti, kasitsi, buf
    
    def _calculate_response_multiple(self, sisuplokk, tulemus, kv, lang, oige, f_locals, loendurid):
        """
        Arvutatakse küsimuse hindepallid (kui pole järjestamine).
        Vastused on paariseoste kaupa, hindamiseks moodustatakse kõikvõimalikud kolmikud.
        """
        matched_rows = dict()
        # kysimuse max pallid kõigi vastuste eest
        t_max_p = tulemus.get_max_pallid()
        # max pallid yhe yksikvastuse eest
        t_max_p_v = tulemus.max_pallid_vastus 
        # max vastuste arv
        t_max_vastus = tulemus.max_vastus
               
        def hm_matches(ks, lang, f_locals, prev_pos, pos_r, partvalue=None):
            "Võrdlus hindamismaatriksiga"
            # pos_r - vastuse järjekorranumber (kui küsimusele anti mitu vastust)
            # lisaks parameetritele on antud: tulemus, matched_rows, self
            hm_buf = ''
            ind_hm = 0
            korduv = False
            request = self.request
            hm_pos = None # leitud maatriksirea järjekorranumber

            hindamismaatriksid = tulemus.hindamismaatriksid
            if tulemus.baastyyp == const.BASETYPE_POSSTRING:
                # kasutame ainult lyngaga seotud osa hindamismaatriksist
                rseq = str(ks.koordinaat)
                hindamismaatriksid = [r for r in hindamismaatriksid if r.koordinaadid == rseq]
            for pos, m in enumerate(hindamismaatriksid):
                if m.maatriks != ks.maatriks:
                    continue
                is_match, rowpoints, rowbuf, rbuf = m.matches(ks, pos+1, lang=lang, f_locals=f_locals, partvalue=partvalue)
                if ind_hm == 0 and rbuf:
                    hm_buf += rbuf + '\n'
                ind_hm += 1
                hm_buf += rowbuf
                if is_match:
                    # kui nõutakse järjestust, siis kas on õige järjestus?
                    if tulemus.kardinaalsus == const.CARDINALITY_ORDERED_SQ1:
                        if prev_pos is not None and prev_pos > pos:
                            # eelmine element pidi olema tagapool
                            hm_buf += _("See vastus ei tohi olla eelmisest vastusest tagapool") + '\n'
                            hm_pos = pos
                            break
                    elif tulemus.kardinaalsus == const.CARDINALITY_ORDERED_POS:
                        # vaatame, kas on täpselt sama järjekorranumber
                        if pos_r != pos:
                            hm_buf += _("Õige vastus, aga vale asukoht") + (' (r:%s/c:%s)\n' % (pos_r, pos))
                            hm_pos = pos
                            break
                    # tabamus real
                    prev_match = matched_rows.get(m)
                    if prev_match and not m.korduv_tabamus:
                        # ei luba sama maatriksirida kasutada mitmele vastusele pallide andmiseks
                        hm_buf += _("Rea tabamist ignoreeritakse (korduv vastus)") + '\n'                                    
                        korduv = True
                        continue
                    else:
                        # tabamust arvestatakse (esialgu)
                        if not prev_match:
                            prev_match = matched_rows[m] = [(ks, rowpoints)]
                        else:
                            prev_match.append((ks, rowpoints))
                        if m.oige:
                            # hindamismaatriksis on vastus märgitud õigeks
                            _oige = const.C_OIGE
                        elif t_max_p is not None and t_max_p - .001 < rowpoints:
                            # kysimus andis max punktid
                            _oige = const.C_OIGE                            
                        elif t_max_p_v is not None and t_max_p_v - .001 < rowpoints:
                            # yksikvastus sai max punktid
                            _oige = const.C_OIGE
                        elif rowpoints > 0:
                            _oige = const.C_OSAOIGE
                        else:
                            _oige = const.C_VALE
                        #log.debug('OIGE HM_MATCHES %s=%s' % (ks.id, _oige))
                        return m, rowpoints, hm_buf, korduv, pos, _oige
            rowpoints = None
            if tulemus.baastyyp in (const.BASETYPE_INTEGER, const.BASETYPE_FLOAT) \
               and tulemus.vastus_pallid:
                try:
                    rowpoints = float(ks.sisu)
                except:
                    pass
            if t_max_p:
                oige = const.C_VALE
            else:
                oige = const.C_OIGE
            return None, rowpoints, hm_buf, korduv, hm_pos, oige

        def ks_vordus(ks, lang, f_locals, prev_pos, pos_r):
            "Vastuse avaldise võrdusmärkidega eraldatud osade võrdlemine hindamismaatriksiga"
            matched_row = ks_oige = None
            p = None
            ks_buf = _("Võrdusmärk eraldab vastused") + '\n'
            for partvalue in [r for r in (ks.sisu or '').split('=') if r]:
                ks_buf += '<b>%s</b>\n' % (_("Vastuse {s} hindamine").format(s='"%s"' % partvalue))
                part_m, part_p, hm_buf, part_korduv, prev_pos, hm_oige = hm_matches(ks, lang, f_locals, prev_pos, pos_r, partvalue)
                ks_buf += hm_buf
                if tulemus.koik_oiged and ((part_p or 0) <= 0):
                    # kõik peavad olema õiged, aga leiti yks vale
                    matched_row = part_m
                    p = part_p
                    ks_buf += _("Kõik võrdusmärkide vahelised osad peavad olema õiged") + '\n'
                    break
                if part_p is not None and (p is None or p < part_p):
                    # leiti seni parim punktide arv
                    # vastuse punktideks on parima võrdusmärkide vahelise osa punktid
                    matched_row = part_m
                    p = part_p
                    if ks_oige is None:
                        ks_oige = hm_oige
                    elif ks_oige != hm_oige:
                        ks_oige = const.C_OSAOIGE
                    continue
            return matched_row, p, ks_buf, prev_pos, ks_oige

        def ks_matches(ks, prev_pos, pos_r):
            # võrdleme vastust maatriksiridadega
            s_vastus = ks.as_string()
            ks_buf = '<b>%s</b>' % (_("Vastuse {s} hindamine").format(s='"%s"' % html.escape(s_vastus)))
            matched_row = None
            p = ks_oige = None
            korduv = False
            oige = ks.tyyp == const.RTYPE_CORRECT
            if oige:
                # hindaja on hinnanud õige/vale
                ks_buf += ' (%s)\n' % _("õige/vale")
                ks_oige = ks.oige
                if ks.oige == const.C_OIGE:
                    p = t_max_p
                else:
                    p = tulemus.min_pallid
            else:
                # võrdleme vastust hindamismaatriksiga
                # vaatame, kas on sisestatud nullipõhjusega (-9 või -8)
                ks_buf += ' (%s)\n' % (_("võrdlus hindamismaatriksiga"))
                ks_oige = ks.kood1 and ks.kood1.startswith('-') and int(ks.kood1[1:]) or \
                          ks.kood2 and ks.kood2.startswith('-') and int(ks.kood2[1:]) or None
                #ks_buf += ' ks_oige=%s ' % ks_oige
                if ks_oige:
                    # nullipõhjus
                    ks_buf += _("Sisestatud on nulli põhjus {s}").format(s=ks_oige) + '\n'
                    p = tulemus.min_pallid
                elif ks.on_vastuseta(tulemus):
                    ks_buf += _("Vastus puudub") + '\n'
                    ks_oige = const.C_VASTAMATA
                else:
                    # hindame vastust
                    if tulemus.vordus_eraldab and tulemus.baastyyp == const.BASETYPE_MATH:
                        # matemaatilise teksti sisestamine, kus võrdusmärk eraldab vastused
                        matched_row, p, hm_buf, prev_pos, ks1_oige = ks_vordus(ks, lang, f_locals, prev_pos, pos_r)
                        ks_buf += hm_buf
                    
                        if matched_row:
                            ks.hindamismaatriks_id = matched_row.id
                        else:
                            ks.hindamismaatriks_id = None
                    elif tulemus.min_sonade_arv and (ks.sonade_arv is not None) \
                        and (tulemus.min_sonade_arv > ks.sonade_arv):
                        # minimaalse sõnade arvu kontroll avatud vastusega küsimuses
                        ks_buf += _("Vastuses on liiga vähe sõnu") + '\n'
                        ks1_oige = const.C_VALE
                        p = tulemus.min_pallid or 0                        
                    else:
                        # tavalise kysimuse vastus
                        matched_row, p, hm_buf, korduv, prev_pos, ks1_oige = hm_matches(ks, lang, f_locals, prev_pos, pos_r)
                        ks_buf += hm_buf
                        if matched_row:
                            ks.hindamismaatriks_id = matched_row.id
                        else:
                            ks.hindamismaatriks_id = None

                    if ks_oige is None:
                        ks_oige = ks1_oige
                    elif ks_oige != ks1_oige:
                        ks_oige = const.C_OSAOIGE

            # pallid leitud
            if p is None:
                if korduv:
                    # ainus tabamus on sellisel maatriksireal,
                    # mille eest on mõnele eelnevale vastusele juba punkte antud
                    ks_buf += _("Korduva vastuse eest 0 punkti") + '\n'
                    p = 0
                elif not tulemus.arvutihinnatav and tulemus.hybriidhinnatav:
                    ks_buf += _("See vastus pole arvutiga hinnatav") + '\n'
                    # p jääb None
                elif ks_oige == const.C_VASTAMATA:
                    ks_buf += _("Vastamata vastus annab 0p") + '\n'
                    p = 0
                elif tulemus.vaikimisi_pallid:
                    # kui vastus ei taba yhtki maatriksirida, siis antakse vaikimisi punkte
                    ks_buf += _("Vaikimisi antakse {p} punkti").format(p=fstr(tulemus.vaikimisi_pallid)) + '\n'
                    p = tulemus.vaikimisi_pallid
                else:
                    # vastus ei taba yhtki maatriksirida ja vaikimisi punkte ei anta
                    ks_buf += _("Punkte ei anta") + '\n'
                    p = 0
            
            return [ks, matched_row, p, ks_buf, ks_oige, prev_pos]

        prev_pos = None # eelmise vastuse õige järjekorranumber
        rc = False
        points = 0
        buf = ''
        arvutihinnatud = True
        valede_arv = oigete_arv = 0
        # kohe peale salvestamist võivad olla vales järjekorras
        kvsisud = sorted(get_kvsisud(kv.kvsisud), key=lambda r: r.seq)
        vastuste_arv = len(kvsisud)
        oigete_vastuste_arv = 0

        # hindame kysimuse kõiki vastuseid
        kvsisud_p = list()
        for pos_r, ks in enumerate(kvsisud):
            ks, matched_row, p, ks_buf, ks_oige, prev_pos = ks_matches(ks, prev_pos, pos_r)
            kvsisud_p.append([ks, matched_row, p, ks_buf, ks_oige])

        # Vaatame yle kõik tabamuse saanud maatriksiread ja arvutame loendurite väärtused
        for m in list(matched_rows.keys()):
            li = matched_rows[m]
            cnt = len(li)
            if m.korduv_tabamus and m.tabamuste_arv:
                # leiame kõik selle maatriksi tabamuse saanud vastused
                for li2 in kvsisud_p:
                    if li2[1] == m:
                        if cnt == m.tabamuste_arv:
                            m_buf = _("Vastuses on nõutud arv rea tabamusi {n}").format(n=cnt) + '\n'
                        else:
                            m_buf = _("Vastuses on rea tabamusi {n1}, nõutud on {n2} - antakse 0p").format(n1=cnt, n2=m.tabamuste_arv) + '\n'
                            # nullime vastuse punktid
                            li2[2] = 0
                        # lisame selgituse
                        li2[3] += m_buf

            # jätame meelde maatriksi rea tähise kasutamise 
            reatahis = m.tahis
            if reatahis:
                loendurid[reatahis] += cnt

        # märgime punktid vastuste juurde
        for ks, matched_row, p, ks_buf, ks_oige in kvsisud_p:
            buf += ks_buf
            if p is not None:
                if p > 0:
                    oigete_vastuste_arv += 1
                if not oige:
                    # nullipõhjus või hindamismaatriksi järgi õige
                    ks.oige = ks_oige
                ks.toorpunktid = p
                if points is not None:
                    # kui on arvutihinnatav, siis points==None
                    points += p
                if ks.oige in (const.C_OIGE, const.C_OSAOIGE):
                    oigete_arv += 1
                elif ks.oige == const.C_VALE:
                    valede_arv += 1
            else:
                points = None
                arvutihinnatud = False
                if ks.hindamismaatriks_id:
                    # hybriidhinnatav, mida ei saa enam arvutiga hinnata,
                    # aga varem on arvutiga hinnatud
                    # tyhistame varasema tulemuse
                    ks.hindamismaatriks_id = None
                    ks.oige = None
                    ks.toorpunktid = None
            
        if tulemus.max_vastus is not None and vastuste_arv > tulemus.max_vastus:
            # tulemus ei sõltu vastuste õigsusest, kuna vastuseid anti liiga palju
            # (lasime enne vastused hinnata selleks, et kvsisu juurde märkida vastuse õigsus)
            points = tulemus.min_pallid or 0
            buf += _("Vastuste arv {n1} on suurem kui {n2}, mistõttu antakse miinimumpallid {p}").format(
                n1=vastuste_arv, n2=tulemus.max_vastus, p=fstr(points)) + '\n'
            valede_arv = vastuste_arv
            arvutihinnatud = True
        elif arvutihinnatud:
            if oigete_vastuste_arv and tulemus.min_oige_vastus and \
                   tulemus.min_oige_vastus > oigete_vastuste_arv:
                points = tulemus.min_pallid or 0
                buf += _("Anti {n1} õiget vastust, mis on vähem kui {n2}, mistõttu antakse miinimumpallid {p}").format(
                    n1=oigete_vastuste_arv, n2=tulemus.min_oige_vastus, p=fstr(points)) + '\n'
        return points, buf, oigete_arv, valede_arv, loendurid

    def _calculate_response_ordered(self, tulemus, kv, lang, oige, f_locals, loendurid):
        """
        Arvutatakse järjestamise ülesande hindepallid
        tulemus - tulemuse kirje, mille alusel hinnatakse
        kv - küsimuse vastuse objekt
        lang - keel
        oige - kas hinnata õige/vale põhjal
        """
        points = 0
        buf = ''
        oigete_arv = valede_arv = 0

        #ks = kv.give_kvsisu(0, const.RTYPE_ORDERED)
        ks = get_kvsisu(kv.kvsisud, 0)
        if not ks or ks.tyyp == const.RTYPE_CORRECT:
            # hindaja on juba hinnanud õige/vale
            if ks and ks.oige == const.C_OIGE:
                points = tulemus.get_max_pallid()
            else:
                points = tulemus.min_pallid
            return points, buf, oigete_arv, valede_arv

        results = {}
        best_mx = None
        for n_mx, hm_read in tulemus.get_maatriksid():
            buf += _("Hindamismaatriks {n}").format(n=n_mx) + "\n"
            # võrdleme vastust iga maatriksiga
            result = self._calculate_response_ordered_mx(tulemus, ks, hm_read, f_locals)
            results[n_mx] = result
            buf += result[1]
            mx_points = result[0]
            # selgitame välja maatriksi, mis andis kõige rohkem punkte
            if mx_points is not None:
                if best_mx is None or results[best_mx][0] < mx_points:
                    best_mx = n_mx

        if best_mx is not None:
            buf += _("Parim tulemus maatriksist {n}").format(n=best_mx) + "\n"
            result = results[best_mx]
            points = result[0]
            oigete_arv = result[2]
            valede_arv = result[3]
            ks.hindamisinfo = result[4]
            for reatahis, cnt in result[5].items():
                loendurid[reatahis] = (loendurid.get(reatahis) or 0) + cnt
        elif tulemus.arvutihinnatav:
            ks.hindamisinfo = len(ks.jarjestus)*'0'
        elif not tulemus.arvutihinnatav and tulemus.hybriidhinnatav:
            points = None
            buf += _("See vastus pole arvutiga hinnatav") + '\n'
            ks.hindamisinfo = None
            
        if points is not None:
            if valede_arv == 0 and oigete_arv != 0:
                ks.oige = const.C_OIGE
            elif oigete_arv == 0:
                ks.oige = const.C_VALE
            else:
                ks.oige = const.C_OSAOIGE
            ks.toorpunktid = points
        return points, buf, oigete_arv, valede_arv

    def _calculate_response_ordered_mx(self, tulemus, ks, hm_read, f_locals):
        rc = None
        points = 0
        buf = ''
        oigete_arv = valede_arv = 0
        prev_r = None # eelmise vastuse kood
        prev_pos = None # eelmise vastuse õige järjekorranumber
        failed = False
        oigsus = '' # jada elementide õigsus 
        loendurid = {}
        # võrdleme vastust hindamismaatriksiga
        for pos_r, r in enumerate(ks.jarjestus):
            # response on list, milles on järjestamise puhul küll üksainus objekt 
            prev_entry = None
            r_rc = False
            buf2 = ''
            if tulemus.kardinaalsus == const.CARDINALITY_ORDERED_POS:
                buf += _("Vastuses on {s1} järjekorras {s2}").format(s1=r, s2=pos_r)
            elif prev_r:
                buf += _("Vastuses on {s1} peale {s2}").format(s1=r, s2=prev_r)
            else:
                buf += _("Vastuses on {s} alguses").format(s=r)                         
            for pos, entry in enumerate(hm_read):
                rc1, p, buf1 = entry.matches_identifier(r, f_locals)
                buf2 += buf1
                if rc1:
                    # leidsime õige rea maatriksis
                    rc = False # kas anda punkte?
                    if tulemus.kardinaalsus == const.CARDINALITY_ORDERED_SEQ:
                        # vaatame, kas vastuses eelmine esines maatriksis varem
                        if prev_pos is not None and prev_pos < pos:
                            rc = True # anname punkte
                        if prev_pos is None and pos == 0:
                            # peab olema alguses ja ongi
                            rc = True
                    # elif tulemus.kardinaalsus == const.CARDINALITY_ORDERED_SQ1:
                    #     # vaatame, kas vastuses eelmine esines maatriksis varem
                    #     if prev_pos is not None and prev_pos < pos:
                    #         rc = True # anname punkte
                    #     if prev_pos is None:
                    #         # esimese vastuse loeme alati õigeks
                    #         rc = True
                    elif tulemus.kardinaalsus in (const.CARDINALITY_ORDERED_ADJ, const.CARDINALITY_ORDERED_COR):
                        # vaatame, kas vastuses eelmine oli maatriksis eelmine
                        if prev_entry == prev_r:
                            # vastus r on õiges kohas: järgneb õigele elemendile
                            rc = True
                    elif tulemus.kardinaalsus == const.CARDINALITY_ORDERED:
                        # vaatame, kas kõik on õiges järjekorras
                        # kui midagi on vales järjekorras, siis ei anta palle
                        if prev_entry == prev_r:
                            rc = True
                        else:
                            failed = True
                    elif tulemus.kardinaalsus == const.CARDINALITY_ORDERED_POS:
                        # vaatame, kas on täpselt sama järjekorranumber
                        rc = pos_r == pos
                    # elif tulemus.kardinaalsus == const.CARDINALITY_ORDERED_COR:
                    #     # õige kontroll on juba brauseris tehtud, anname punktid
                    #     rc = True

                    if rc:
                        # tuleb anda palle
                        if entry.pallid is not None:
                            p = entry.pallid
                        else:
                            p = 1
                        buf += ' ' + _("ja annab {p} palli").format(p=fstr(p))
                        points += p
                        r_rc = True

                        reatahis = entry.tahis
                        if reatahis:
                            loendurid[reatahis] = (loendurid.get(reatahis) or 0) + 1
                    else:
                        if tulemus.kardinaalsus == const.CARDINALITY_ORDERED_POS:
                            buf += _(", aga peab olema {s} ja ei anna palle").format(s=pos)        
                        else:
                            buf += _(", aga peab olema {s} ja ei anna palle").format(s=prev_entry and 'peale '+prev_entry or 'alguses')
                        if failed:
                            if points:
                                buf += '\n' + _("Selle küsimuse eest seni arvutatud {s} palli võetakse ära").format(s=fstr(points))
                            break
                    prev_pos = pos
                prev_entry = entry.kood1
                
            if tulemus.kardinaalsus != const.CARDINALITY_ORDERED_COR or r_rc:
                prev_r = r

            if r_rc:
                oigete_arv += 1
            else:
                valede_arv += 1
            oigsus += r_rc and '1' or '0'
            buf += '\n'
            #for line in buf2.splitlines():
            #    buf += ' * ' + line + '\n'
            if failed:
                rc = None
                break

        if rc is None:
            if not tulemus.arvutihinnatav and tulemus.hybriidhinnatav:
                points = None
            elif tulemus.vaikimisi_pallid is not None:
                buf += 'Vaikimisi antakse %s palli\n' % fstr(tulemus.vaikimisi_pallid)
                points = tulemus.vaikimisi_pallid
            else:
                points = tulemus.min_pallid
        return points, buf, oigete_arv, valede_arv, oigsus, loendurid

    def _calc_formula_locals(self, item, responses):
        "Väärtustame kasutaja vastused lokaalmuutujatena valemite väärtustamise jaoks"
        # item on ylesanne
        f_locals = {}
        for block in item.sisuplokid:
            for kysimus in block.kysimused:
                #log.debug('kysimus %s...' % kysimus.kood)
                tulemus = kysimus.tulemus
                kood = kysimus.kood
                if tulemus and kood:
                    baastyyp = tulemus.baastyyp
                    kardinaalsus = tulemus.kardinaalsus or const.CARDINALITY_SINGLE
                    #log.debug('  baastyyp=%s, kardinaalsus=%s, block.tyyp=%s' % (baastyyp, kardinaalsus,block.tyyp))
                    if block.tyyp != const.BLOCK_FORMULA:
                        # lahendaja poolt antud vastused, jätame f_locals sees valemi jaoks meele
                        if  baastyyp in (const.BASETYPE_INTEGER,
                                         const.BASETYPE_FLOAT,
                                         const.BASETYPE_STRING,
                                         const.BASETYPE_POSSTRING,
                                         const.BASETYPE_IDENTIFIER,
                                         const.BASETYPE_PAIR,
                                         const.BASETYPE_DIRECTEDPAIR,
                                         const.BASETYPE_POINT,
                                         const.BASETYPE_MATH):
                            # teisi tyype valemites ei saa kasutada
                            valuelist = []
                            value = None
                            kv = responses.get(kood)
                            if kv:
                                for kvs in get_kvsisud(kv.kvsisud):
                                    if baastyyp == const.BASETYPE_POINT:
                                        value = kvs.punkt
                                    elif baastyyp in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):
                                        value = (kvs.kood1, kvs.kood2)
                                    elif baastyyp == const.BASETYPE_POSSTRING:
                                        value = kvs.sisu
                                        if value and kvs.kood2:
                                            # vastus on hindamismaatriksi lyngas, mitte suvalises kohas
                                            # loome lynga jaoks oma muutuja KYSIMUS_LYNK
                                            f_locals[f'{kysimus.kood}_{kvs.kood2}'] = value
                                        # kysimuse muutuja vastus jääb tyhjaks
                                        continue
                                    else:
                                        value = kvs.kood1 or kvs.sisu
                                    if value:
                                        if baastyyp == const.BASETYPE_INTEGER:
                                            # float selleks juhuks, kui value on nt 1.0
                                            try:
                                                value = int(float(value.replace(',','.')))
                                            except ValueError:
                                                value = None
                                            except OverflowError:
                                                value = None
                                        elif baastyyp == const.BASETYPE_FLOAT:
                                            try:
                                                value = float(value.replace(',','.'))
                                            except ValueError:
                                                value = None
                                            except OverflowError:
                                                value = None
                                        elif baastyyp == const.BASETYPE_MATH:
                                            try:
                                                fvalue = model.fixlatex(value)
                                                log.debug('PROCESS:%s' % fvalue)
                                                value = model.process_sympy(fvalue)
                                            except Exception as e:
                                                log.error('process_sympy error: %s' % str(e))

                                        valuelist.append(value)
                            if kardinaalsus == const.CARDINALITY_SINGLE:
                                f_locals[kood] = value
                            else:
                                f_locals[kood] = valuelist

            #log.debug('yl %s locals: %s, responses:%s' % (item.id, f_locals, responses))
        return f_locals    

    def _calc_formula_response(self, kv, kysimus, f_locals):
        "Arvutatakse arvutatavad vastused"
        kood = kysimus.kood
        block = kysimus.sisuplokk
        assert block.tyyp == const.BLOCK_FORMULA, 'pole valemi plokk'
        errpos = 'Yl %s k %s: ' % (block.ylesanne_id, kood)
        k_locals = f_locals.copy()
        for ind, v in enumerate(kysimus.valikud):
            try:
                constant = eval(v.nimi, {}, {})
            except Exception as e:
                log.error('vigane konstant %d: %s' % (v.id, v.nimi))
            else:
                k_locals[v.kood] = constant

        value, err0, err, buf1 = model.eval_formula(block.sisu, k_locals)
        buf = 'Valem: %s\n' % (block.sisu)
        log.debug(buf)
        if err0:
            log.error(errpos + err0)
            buf += err0 + '\n'
        if err:
            log.error(errpos + err)
            buf += err + '\n'
        basetype = kysimus.tulemus.baastyyp
        if value is not None:
            if basetype == const.BASETYPE_STRING:
                value = str(value)
            elif basetype == const.BASETYPE_BOOLEAN:
                value = bool(value)
            elif basetype == const.BASETYPE_INTEGER:
                try:
                    value = int(value)
                except:
                    log.error(errpos + 'Valem arvu tüüpi, avaldis mitte')
                    try:
                        log.error('avaldis:%s' % value)
                    except:
                        pass
                    value = None
        #buf += ' (%s vastus "%s") \n' % (basetype, value)
        f_locals[kood] = value
        if value is not None:
            value = str(value)
            kv._current_seq = 0
            ks = kv.set_kvsisu(kv._current_seq, const.RTYPE_STRING, sisu=value)
        return buf

def get_kvsisud(kvsisud):
    return [ks for ks in kvsisud if ks.seq >= 0]

def get_kvsisu(kvsisud, seq):
    for ks in kvsisud:
        if ks.seq == seq:
            return ks
