"""Lünkteksti üksiklünga dialoogiaken
Põhimõte: lünkade sisu peab täiesti olema Sisuplokk.sisu teksti sees olemas,
siis saab kasutaja ise teksti sees kopeerida ja liigutada ja ümber nimetada
ja sellega ei teki segadusi.
Siinne kontroller on peamiselt lünga dialoogi kuvamiseks ja andmete valideerimiseks,
salvestamine peab käima kogu ckeditori akna kohta Sisuplokk.sisu salvestamisel.

1. sisuplokk.mako -> iinltext.mako kuvab ckeditori tekstitoimeti,
kus kasutaja vajutab lünga ikoonile.
2. ckeditor/plugins/gaps/plugin.js exec() küsib sisuplokk.mako käest
funktsiooniga get_dialog_self.url() dialoogi sisu kuvamise URLi
ja avab selle URLi dialoogina.
3. dialoogi sisu URL viitab Kysimuse kontrollerile meetodile new.
kui muudetakse olemasolevat lünka, siis see lünk HTML kujul antakse parameetriks.
4. kasutaja muudab dialoogiaknas andmeid ja vajutab "Salvesta".
5. andmed postitatakse Kysimuse kontrollerile, kus need valideeritakse.
Peale valideerimist täidetakse kysimuse ja tulemuse objektid, et
nende abil vorm kuvada. 
kuna andmed on juba serveris, siis ka salvestatakse kysimuse objekt, et
server teaks koodi genereerimisel varasemaid koode arvestada.
põhiline salvestamine jääb ikkagi sisuploki salvestamise juure.
(Kuid seetõttu võib tekkida olukord, kus küsimused on tabelis Kysimus uued,
aga lünktekst Sisuplokk.sisu on vana ja need ei ole kooskõlas omavahel.)
6. kui tekib vigu, siis kuvatakse dialoogivorm vigade näitamisega.
7. kui ei teki vigu, siis seatakse self.c.updated=True ja kuvatakse sama vorm,
mis kutsub välja plugina funktsiooni update(), mis teeb ckeditori aknas HTMLis muudatused
ning siis pannakse dialoogiaken kinni.

"""
import lxml.etree
import lxml.html
import re
import urllib.request, urllib.parse, urllib.error
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from .sisuplokk import which_form

log = logging.getLogger(__name__)

class KysimusController(BaseController):
    """Ülesande sisu"""
    _permission = 'ylesanded'

    def new(self):
        """Olemasolevate lünkade muutmine ja uute loomine.
        """
        if self.params_lang():
            self.error(_("Uue lünga lisamiseks vali esmalt keelevalikus ülesande põhikeel"))
        return self.edit()

    def edit(self):
        self._edit_d()
        # dialoogi kuvamine
        template = 'ekk/ylesanded/kysimus.mako'
        return self.render_to_response(template)

    def _edit_d(self):
        # kuvatava välja andmed võetakse parameetriks antud data htmli seest, mitte andmebaasist
        # kui kood pole parameetris, siis otsitakse seda data seest
        c = self.c
        id = self.request.matchdict.get('id')
        kood = id

        data = self.request.params.get('data') # olemasolev väli HTMLina
        #tyyp = self.request.params.get('tyyp') # const.INTER_TEXT või const.INTER_CHOICE
        #c.rtf = self.request.params.get('rtf') == '1' # kas valikud on kireva tekstiga
        model.Session.autoflush = False

        ctrl = BlockController.get(c.item, c.ylesanne, self) # teeb c.item.ctrl, mida kysimus.mako kasutab
        ctrl.lang = c.lang = self.params_lang()
        is_tr = self.request.params.get('is_tr') or ctrl.lang

        if c.item.tyyp == const.INTER_CROSSWORD:
            c.pos_x = int(self.request.params.get('l.pos_x'))
            c.pos_y = int(self.request.params.get('l.pos_y'))
            c.kysimus = self._get_kysimus_cw(kood, is_tr)                       
            if c.kysimus:
                c.tulemus = c.kysimus.tulemus or \
                                 c.new_item(kood=c.kysimus.kood,
                                                 kardinaalsus=const.CARDINALITY_SINGLE,
                                                 baastyyp=const.BASETYPE_STRING,
                                                 arvutihinnatav=True)
            
        elif data:
            # olemasoleva lynga muutmine
            # IE annab data vigasena
            #if self.h.is_msie():
            # vaja asendada pattern/title atribuutides esinevad <>
            data = _repair_xml(data)
            #log.debug(data)
            data = data.replace('<br>','<br/>')
            # olemasolevast väljast võetakse dialoogi algväärtused
            # XML does not have any named entities besides &lt;, &gt;, &quot;, &apos; and &amp;
            field = lxml.html.fromstring(data)
            if c.item.tyyp == const.INTER_INL_CHOICE and field.tag == 'select':
                # valikulünk
                is_rtf = bool(field.get('rtf'))
                valikud = []
                if not kood:
                    kood = field.get('id') or field.get('name') 
                if kood:
                    c.kysimus = self._get_kysimus(kood, is_tr)
                for m, opt in enumerate(field.iterdescendants('option')):
                    o_kood = opt.get('value')
                    o_nimi = opt.text
                    if o_kood:
                        if is_rtf:
                            # kasutaja on sisestanud HTMLi, see tuleb dekodeerida
                            o_nimi = urllib.parse.unquote(o_nimi)
                        v = c.kysimus.get_valik(o_kood)
                        o_desc = v and v.selgitus or opt.get('desc')

                        valikud.append(model.Sisuvalik(id=m, kood=o_kood, nimi=o_nimi, selgitus=o_desc))
                    elif not kood:
                        # kood esimesel real
                        kood = o_nimi
                        c.kysimus = self._get_kysimus(kood, is_tr)
                            
                if not c.lang:
                    c.kysimus.rtf = is_rtf
                    c.valikud = valikud
                else:
                    # tõlkimise korral ei saa kasutaja valikuid lisada
                    # systeem tagab, et valikute arv vastab põhikeele valikutele
                    orig_kysimused = c.item.get_sisukysimused(kood)
                    if len(orig_kysimused):
                        orig_valikud = orig_kysimused[0].valikud
                    else:
                        orig_valikud = []

                    for n, sv in enumerate(orig_valikud):
                        if len(valikud) > n:
                            sv.tran_nimi = valikud[n].nimi
                    c.valikud = orig_valikud

                c.tulemus = ctrl.parse_kysimus_choice(c.kysimus, field)
                    
            elif c.item.tyyp == const.INTER_GAP and field.tag == 'input':
                # pangaga lünk
                if not kood:
                    kood = field.get('value') or field.get('id') or field.get('name') 
                c.kysimus = self._get_kysimus(kood, is_tr, field)
                c.tulemus = ctrl.parse_kysimus(c.kysimus, field)

            elif c.item.tyyp == const.INTER_PUNKT and field.tag == 'input':
                # kirjavahemärgi lisamine
                c.kysimus = self._get_kysimus(kood, is_tr, field)
                c.tulemus = c.kysimus.tulemus

            elif c.item.tyyp == const.INTER_INL_TEXT and field.tag == 'input':
                # avatud lünk
                if not kood:
                    kood = field.get('value') or field.get('id') or field.get('name') 
                c.kysimus = self._get_kysimus(kood, is_tr)
                c.tulemus = ctrl.parse_kysimus_text(c.kysimus, field)                

            elif c.item.tyyp == const.INTER_INL_TEXT and field.tag == 'textarea':
                # avatud lünk, kirev tekst
                if not kood:
                    kood = field.text or field.get('id') or field.get('name') 
                c.kysimus = self._get_kysimus(kood, is_tr)
                c.tulemus = ctrl.parse_kysimus_text(c.kysimus, field)                

            elif c.item.tyyp == const.INTER_HOTTEXT and field.tag == 'span':
                # tekstiosa valik
                if not kood:
                    kood = field.get('group')
                c.kysimus = self._get_kysimus(kood, is_tr)
                c.valik = ctrl.parse_kysimus_valik(c.kysimus, field)

            elif c.item.tyyp == const.INTER_COLORTEXT and field.tag == 'span':
                # tekstiosa värvimine
                if not kood:
                    kood = field.get('group')
                c.kysimus = self._get_kysimus(kood, is_tr)
                c.valik = ctrl.parse_kysimus_valik(c.kysimus, field)
            else:
                log.debug('OOTAMATU element: %s' % field.tag)
        else:
            defaults = dict()
            if c.item.tyyp == const.INTER_GAP:
                defaults['max_vastus'] = 1
                if c.item.give_kysimus(0).gap_lynkadeta:
                    defaults['min_vastus'] = 0
                else:
                    defaults['min_vastus'] = 1
            # uue välja lisamine
            c.kysimus = self._get_kysimus(kood, is_tr, **defaults)            
            #c.kysimus = model.Kysimus(sisuplokk=c.item, kood=kood)

            if self.request.params.get('basetype') == const.BASETYPE_MATH:
                baastyyp = const.BASETYPE_MATH
            elif c.item.tyyp in (const.INTER_INL_CHOICE, const.INTER_GAP):
                baastyyp = const.BASETYPE_IDENTIFIER
            else:
                baastyyp = const.BASETYPE_STRING

            if c.item.tyyp != const.INTER_INL_TEXT:
                arvutihinnatav = True
            else:
                arvutihinnatav = False

            c.tulemus = c.kysimus.tulemus or \
                             c.new_item(kood=kood,
                                             kardinaalsus=const.CARDINALITY_SINGLE,
                                             baastyyp=baastyyp,
                                             arvutihinnatav=arvutihinnatav)
            c.valikud = []

        return self.response_dict

    def _copy_kysimus(self, field, kood):
        "Kui HTML elemendil field on atribuut copy, siis luuakse uus kysimus vastava kysimuse koopiana"
        o_kood = field.get('copy')
        if o_kood:
            o_kysimus = self.c.item.get_kysimus(kood=o_kood)
            if o_kysimus:
                kysimus = o_kysimus.copy()
                kysimus.sisuplokk = self.c.item
                kysimus.kood = kood
                tulemus = kysimus.tulemus
                if tulemus:
                    tulemus.kood = kood
                return kysimus

    def _get_kysimus(self, kood, is_tr, field=None, **defaults):
        kysimus = None
        if kood:
            kysimus = self.c.item.get_kysimus(kood)
        if not kysimus:
            if not is_tr and field is not None:
                # kontrollime copy atribuudi olemasolu ja võimalusel kopeerime olemasoleva kysimuse
                kysimus = self._copy_kysimus(field, kood)
            if not kysimus:
                kysimus = model.Kysimus(sisuplokk=self.c.item, kood=kood, **defaults)
            if is_tr:
                self.error(_("Küsimust {s} ei ole olemas").format(s=kood))
        return kysimus

    def _get_kysimus_cw(self, kood, is_tr):
        # posdata on kujul X_Y
        kysimus = None
        if kood:
            kysimus = self.c.item.get_kysimus(kood)        
        if not kysimus:
            if is_tr:
                self.error(_("Küsimust {s} ei ole olemas").format(s=kood))
            else:
                # on kysimus, sõna
                #kood = self.c.ylesanne.gen_kysimus_kood('X_%d_%d' % (pos_x, pos_y))
                kood = self.c.ylesanne.gen_kysimus_kood()
                kysimus = self.c.new_item(sisuplokk=self.c.item, kood=kood)
        return kysimus

    def show(self):
        return self.edit()

    def create(self):
        return self.update()
    
    def update(self):
        # andmed võetakse postitatud vormist, valideeritakse ja paigutatakse
        # ajutistesse objektidesse, mida ei salvestata, vaid kuvatakse ainult vormil
        c = self.c
        self._form_update()

        if c.item.tyyp == const.INTER_CROSSWORD:
            # postitati iframe sisse, vaja on <html> ja <body> elemente
            c.in_iframe = True
        template = 'ekk/ylesanded/kysimus.mako'
        if not self.form:
            # anti juba teade, et ei tohi enam muuta
            return self.render_to_response(template)
        
        if self.form.errors:
            return Response(self.form.render(template, extra_info=self._edit_d()))

        # salvestatakse selleks, et süsteem teaks uusi koode genereerides juba loodud koode
        model.Session.commit()
        if c.item.tyyp == const.INTER_CROSSWORD:
            # genereerime peavormi uuesti
            c.updated_url = self.url('ylesanne_edit_sisuplokk', id=c.item.id, ylesanne_id=c.ylesanne.id, lang=c.lang)
        elif c.item.tyyp == const.INTER_MCHOICE:
            # muudame peavormil selle kysimuse hindamismaatriksit
            selector = "input.oigekood-k%s" % c.kysimus.id
            buf = "$('%s').prop('checked', false);" % selector
            li = ['[value="%s"]' % hm.kood1 for hm in c.tulemus.hindamismaatriksid if hm.pallid > 0]
            if li:
                buf += "$('%s').filter('%s').prop('checked', true);" % (selector, ','.join(li))
            buf += 'close_dialog();'
            buf = '<html><script>%s</script></html>' % buf
            return Response(buf)
        c.updated = True
        return self.render_to_response(template)            
        
    def _form_update(self):
        c = self.c
        # id on vormi avamisel kehtinud kood
        old_kood = id = self.request.matchdict.get('id')

        is_tr = self.request.params.get('is_tr')
        form = which_form(self, c.ylesanne, is_tr, c.can_update_hm)
        if not form:
            self.error(_("Ülesannet ei tohi enam muuta!"))
            return
        self.form = Form(self.request, schema=form)
        rc = self.form.validate()

        if rc:
            try:
                # kysimuse uus kood
                kood = self.form.data['am1'].get('kood')
                if not is_tr and old_kood and c.item.tyyp == const.INTER_CROSSWORD:
                    # need sisuplokityybid, kus kasutaja poolt koodi muutmisel
                    # muudetakse senise kysimuse kood, mitte ei looda uut kysimust
                    c.kysimus = c.item.get_kysimus(old_kood)
                    # kui sama teha lynkylesannetes, siis tuleks ka tõlgete sisus koodid muuta
                    
                if kood and not c.kysimus:
                    c.kysimus = c.item.get_kysimus(kood)              
                
                if (is_tr or c.ylesanne.lukus) and not c.kysimus:
                    errors = {'am1.kood': _("Küsimust {s} ei ole olemas").format(s=kood)}
                    raise ValidationError(self, errors)

                if not c.kysimus:
                    c.kysimus = model.Kysimus(sisuplokk=c.item, kood=kood)

                ctrl = BlockController.get(c.item, c.ylesanne, self)
                c.lang = ctrl.lang = self.params_lang()
                if is_tr:
                    ctrl.tran_update_kysimus(c.kysimus)
                else:
                    ctrl.update_kysimus(c.kysimus)
                    if not c.ylesanne.lukus:
                        c.kysimus.rtf = bool(self.request.params.get('v_rtf')) or bool(self.request.params.get('l.rtf'))
                    
                if c.item.tyyp == const.INTER_INL_CHOICE:
                    if c.ylesanne.lukus:
                        orig_kysimused = c.item.get_sisukysimused(kood)
                        if len(orig_kysimused):
                            orig_valikud = orig_kysimused[0].valikud
                        else:
                            orig_valikud = []
                        c.valikud = orig_valikud
                    else:
                        c.valikud = ctrl.update_sisuvalikud(c.kysimus)

                if not c.kysimus.pseudo:
                    c.tulemus = c.kysimus.give_tulemus()
            except ValidationError as e:
                self.form.errors = e.errors

    def delete(self):
        "Ristsõna küsimuse kustutamine"
        c = self.c
        assert c.item.tyyp == const.INTER_CROSSWORD, 'Vale tüüp'
        id = self.request.matchdict.get('id')
        kysimus = model.Kysimus.get(id)
        if kysimus and kysimus.sisuplokk_id == c.item.id:
            self._delete_except(kysimus)
        return HTTPFound(location=self.url('ylesanne_edit_sisuplokk', id=c.item.id, ylesanne_id=c.ylesanne.id, lang=c.lang))

    def _delete_except(self, item):
        try:
            mo = item.sisuobjekt
            if mo:
                mo.delete()
            item.delete()
            model.Session.commit()
        except sa.exc.IntegrityError as e:
            msg = _("Ei saa enam kustutada, sest on seotud andmeid")
            try:
                log.info('%s [%s] %s' % (msg, self.request.url, str(e)))
            except:
                pass
            self.error(msg)
            model.Session.rollback()

    def __before__(self):
        """Väärtustame self.c.item ylesandega ning self.c.lang keelega,
        seejuures kontrollime, et self.c.lang oleks selle ülesande tõlkekeel.
        """
        c = self.c
        id = self.request.matchdict.get('ylesanne_id')
        c.ylesanne = model.Ylesanne.get(id)
        c.can_update = c.user.has_permission('ylesanded', const.BT_UPDATE, c.ylesanne)
        c.can_update_sisu = c.can_update and not c.ylesanne.lukus
        c.can_update_hm = c.can_update and c.ylesanne.lukus_hm_muudetav

        c.lang = self.params_lang()
        if c.lang and c.lang not in c.ylesanne.keeled or \
                c.lang == c.ylesanne.lang:
            c.lang = None
        c.item = model.Sisuplokk.get(self.request.matchdict.get('sisuplokk_id'))

        super(KysimusController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.ylesanne}

def _repair_xml(data):
    """IE poolt antud vigane XML tehakse korda, nii et seda saaks XML parseriga parsida
    """
    # <SELECT min_pallid="0" max_pallid="10" vaikimisi_pallid="0" hm0="B/10/0">
    # <OPTION selected value=A>essa nossa</OPTION><OPTION value=B>tessa</OPTION>
    # </SELECT>
    # tuleb lisada jutumärgid ja panna elementide nimed väiketähtedesse
    buf = '' # siia tuleb korras XML
    ignore_attr = in_tag = in_tag_first_word = in_attr = in_key = in_value = False
    sep = None
    for n in range(len(data)):
        # vigane XML vaadatakse tähthaaval üle
        c = data[n]
            
        if not in_tag:
            if c == '<':
                in_tag = in_tag_first_word = True
            buf += c
        elif in_tag:
            if c == '>' and not in_value:
                key = None
                in_tag = in_tag_first_word = in_attr = ignore_attr = in_value = in_key = False
                buf += c
            elif in_tag_first_word:
                # esimene sõna suurtähtedesse
                if c == ' ':
                    in_tag_first_word = in_attr = ignore_attr = False
                    buf += c
                else:
                    buf += c.lower()

            elif not in_attr:
                if c == ' ':
                    buf += c
                elif c == '_':
                    # atribuudi nimi algab alakriipsuga, ignoreerime seda atribuuti
                    in_attr = in_key = ignore_attr = True
                    key = c
                else:
                    in_attr = in_key = True
                    key = c
            elif in_attr:
                if in_key:
                    if c == ' ':
                        # ilma väärtuseta atribuut, viskame välja
                        in_attr = in_key = ignore_attr = False
                        c = None
                    elif c == '=':
                        # key sai läbi
                        in_key = False
                        if not ignore_attr:
                            buf += key + c
                        in_value = True
                        value = ''
                        sep = None
                    else:
                        # key jätkub
                        key += c
                elif in_value:
                    if sep is None:
                        if c in ('"',"'"):
                            # algab uus väärtus ilusti jutumärkide sees
                            sep = c
                            value = c
                        elif c == ' ' or c == '>':
                            # jutumärkideta väärtus sai läbi
                            if not ignore_attr:
                                buf += '"'+value.replace('"','\"')+'"'+c
                            in_value = in_attr = ignore_attr = False
                            if c == '>':
                                in_tag = in_tag_first_word = in_key = False
                        elif c == '<':
                            value += '&lt;'
                        else:
                            # jutumärkideta väärtus jätkub
                            value += c
                    else:
                        # jutumärkide sees olev atribuut
                        if c == '<':
                            value += '&lt;'
                        else:
                            value += c
                        if c == sep:
                            # väärtus sai läbi
                            if not ignore_attr:
                                buf += value
                                value = None
                            in_attr = in_value = ignore_attr = False

    return buf

def _inner_xml(element):
    buf = lxml.etree.tostring(element, encoding=str, xml_declaration=False, method='xml')
    # eemaldame wrapper-elemendi
    buf = buf[buf.find('>')+1:buf.rfind('<')]
    return buf.strip()

if __name__ == '__main__':
    s = '<INPUT contentEditable=false value=K1 size=20 type=text _cke_expando="64" baastyyp="string" min_pallid max_pallid vaikimisi_pallid pattern hm0="z<45/6/0"></input>'
    s = '<SELECT id=b min_pallid="0" max_pallid="" vaikimisi_pallid="0" hm0="A//1"><OPTION selected>b</OPTION><OPTION value=A>mehed</OPTION><OPTION value=B>päkapikud</OPTION><OPTION value=C>kotionu</OPTION><OPTION value=D>koll</OPTION></SELECT>'
    print(_repair_xml(s))
