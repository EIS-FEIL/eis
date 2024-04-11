"Ülesannete valideerimisskeemid"

import formencode
from eis.forms.validators import *

class OtsingForm(Schema):
    "Otsingu vorm"
    id = Int(if_missing=None)    
    idr = IDRange(if_missing=None)
    marksona = String(if_missing=None)
    koostaja = String(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    raskus_alates = Number(if_missing=None, min=-4, max=4)
    raskus_kuni = Number(if_missing=None, min=-4, max=4)
    lahendatavus_alates = Number(if_missing=None, min=0, max=100)
    lahendatavus_kuni = Number(if_missing=None, min=0, max=100)    
    vastvorm = String(if_missing=None)
    aine = String(if_missing=None)
    teema = String(if_missing=None)
    alateema = String(if_missing=None)
    opitulemus_id = Number(if_missing=None)
    aste = String(if_missing=None)
    mote = String(if_missing=None)
    ylkogu_id = Int(if_missing=None)
    oskus = String(if_missing=None)
    kysimus = String(if_missing=None)
    vahend = String(if_missing=None)

    staatus = formencode.ForEach(formencode.validators.Int())    
    ptest = Bool(if_missing=None)
    etest = Bool(if_missing=None)
    adaptiivne = Bool(if_missing=None)

    chained_validators = [Range('alates',
                                'kuni',
                                'Vahemiku lõpp ei saa olla enne algust'),
                          Range('raskus_alates',
                                'raskus_kuni',
                                'Vahemiku lõpp ei saa olla väiksem kui algus'),
                          ]

class HulgiYlesandeaineForm(Schema):
    aine_kood = String(not_empty=True)
    teemad2 = formencode.ForEach(String)    
    opitulemused = formencode.ForEach(Int)
    
class HulgiForm(Schema):
    ya = formencode.ForEach(HulgiYlesandeaineForm)
    kehtib_kuni = EstDateConverter(if_missing=None)
    
class YlesandeaineForm(Schema):
    id = Int
    aine_kood = String(not_empty=True)
    oskus_kood = String()
    teemad2 = formencode.ForEach(String)    
    opitulemused = formencode.ForEach(Int)
   
class YldandmedForm(Schema):
    "Üldandmete vorm"
    f_nimi = String(not_empty=True, max=256)
    f_keeletase_kood = String()
    f_aste_kood = String()
    v_aste_kood = formencode.ForEach(String)
    f_vastvorm_kood = String()
    f_ptest = Bool
    f_etest = Bool
    f_nutiseade = Bool
    f_adaptiivne = Bool
    f_on_tagasiside = Bool
    f_ymardamine = Bool
    f_pallemaara = Bool(if_missing=False)
    f_raskus_kood = Int
    f_konesyntees = Bool
    f_markus = String()
    f_marksonad = String(max=256)
    f_autor = String(max=128)
    f_lang = String()
    skeel = formencode.ForEach(String)
    #on_tahemargid = Bool
    pre_validators = [formencode.NestedVariables()]
    vahend_kood = formencode.ForEach(String)
    kasutliik_kood = formencode.ForEach(String)
    #vh = formencode.ForEach(VahendForm())
    ya = formencode.ForEach(YlesandeaineForm)
    #yt = formencode.ForEach(YlesandeteemaForm())

class PsisuplokkNewForm(Schema):
    "Uue sisuploki andmete vorm"
    #rowind = Int
    tyyp = String
    karv = Int
    max_pallid = Number
    varv = Int(if_missing=None)
    max_vastus = Int(if_missing=None)
    koodid = String(if_missing=None)
    oige_pallid = Number(if_missing=None)
    pintervall = Number(if_missing=None)

class PkysimusValikForm(Schema):
    kood = String
    #oige = Bool

class PkysimusForm(Schema):
    "Küsimuse andmete vorm"
    id = Int
    kood = PyIdentifier(not_empty=True) # õige rida, ajutiselt väljas
    max_pallid = Number(not_empty=True)
    max_vastus = Int(if_missing=None)
    oige_pallid = Number(if_missing=None)
    # oigekood
    pintervall = Number(if_missing=None)
    v = formencode.ForEach(PkysimusValikForm)
    oige = formencode.ForEach(String)
    
class PsisuplokkForm(Schema):
    "Üldandmete vorm"
    id = Int
    tyyp = String
    k = formencode.ForEach(PkysimusForm)
    
class PsisuplokidForm(Schema):
    sp = formencode.ForEach(PsisuplokkForm)

class PsisuForm(Schema):
    "Üldandmete vorm"
    f_nimi = String(not_empty=True, max=256)
    f_aine_kood = String(not_empty=True)

class SisuSPForm(Schema):
    "Sisu vorm"
    id = Number
    #on_tahemargid = Bool
    
class SisuForm(Schema):
    "Sisu vorm"
    f_nimi = String(not_empty=True)
    f_paanide_arv = Int(if_missing=None)
    f_paan1_laius = Int(min=15, max=85)
    f_lahendada_lopuni = Bool(if_missing=False)
    f_valimata_vastused = Bool(if_missing=False)    
    f_spellcheck = Bool(if_missing=False)
    f_segamini = Bool
    f_dlgop = Bool(if_missing=False)
    f_dlgop_aeg = Int(min=5, if_missing=None)
    f_dlgop_tekst = String(max=256, if_missing=None)
    f_dlgop_ei_edasi = Int(if_missing=None)
    f_fixkoord = Bool
    sp = formencode.ForEach(SisuSPForm())
    j_juhis = String(if_missing=None)
    #j_on_tahemargid = Bool
    
    chained_validators = [NotEmptyIffNotEmpty('f_dlgop', 'f_dlgop_aeg', 'f_dlgop_tekst', 'f_dlgop_ei_edasi')]
    
class SisuTranForm(Schema):
    "Sisu vorm"
    f_nimi = String(max=256, if_missing=None, not_empty=True)
    f_marksonad = String(max=256, if_missing=None)
    f_dlgop_tekst = String(max=256, if_missing=None) 
    
class EditorsettingForm(Schema):
    icon = formencode.ForEach(String, not_empty=True)
    #nupujuhis = String()

class MathsettingForm(Schema):
    icon = formencode.ForEach(String, not_empty=True)

class WmathsettingForm(Schema):
    removeLinks = Bool
    detectHand = Bool
    toolbar = String
    rows = Int
    tab = formencode.ForEach(String)
    icon = formencode.ForEach(String)

class MarkusForm(Schema):
    "Sisu vorm"
    teema = String(max=100, not_empty=True)
    sisu = String(not_empty=True)
    ylem_id = Number()

class YlesandefailimarkusForm(Schema):
    teema = String(max=100, not_empty=True)
    sisu = String(not_empty=True)
    ylem_id = Number()
    
class HotspotForm(Schema):
    kood = Identifier(not_empty=True)
    koordinaadid = String(not_empty=True)
    kujund = String(not_empty=True)
    nahtamatu = Bool(if_missing=False)
    max_vastus = Int(if_missing=None)
    
class AreaMapEntryForm(Schema):
    koordinaadid = String(not_empty=True)
    kujund = String(not_empty=True, max=10)
    pallid = Number()
    oige = Bool()
    tabamuste_arv = Int(if_missing=None, min=1)
    tahis = PyIdentifier(if_missing=None, max=25)
    selgitus = String(max=255)
    chained_validators = [RequireIfMissing('pallid',
                                           missing='oige'),
                          ]

class TrailMapEntryForm(Schema):
    #koordinaadid = String(not_empty=True, max=256)
    kood1 = String(not_empty=True, max=2000)
    pallid = Number()
    oige = Bool()
    chained_validators = [RequireIfMissing('pallid',
                                           missing='oige'),
                          ]

class GapImgForm(Schema):
    kood = Identifier()
    max_vastus = Int(if_missing=None)
    min_vastus = Int(if_missing=None)    
    laius = Int(if_missing=None)
    korgus = Int(if_missing=None)    
    eraldi = Bool(if_missing=False)
    seq = Int
    id = Int

class TranGapImgForm(Schema):
    laius = Int(if_missing=None)
    korgus = Int(if_missing=None)    
    id = Int()

class ImgForm(Schema):
    laius = Int(if_missing=None)
    korgus = Int(if_missing=None)    
    tiitel = String(if_missing=None, max=256)
    id = Int

class TranImgForm(Schema):
    laius = Int(if_missing=None)
    korgus = Int(if_missing=None)        
    tiitel = String(if_missing=None, max=256)
    id = Int

class ChoiceForm(Schema):
    kood = Identifier(not_empty=True)
    nimi = String()
    nimi_rtf = String(if_missing=None)
    varv = String(max=7, if_missing=None)
    removed = String(if_missing=None)
    min_vastus = Number(if_missing=None)
    max_vastus = Number(if_missing=None)
    fikseeritud = Bool(if_missing=None)
    eraldi = Bool(if_missing=None)
    kohustuslik_kys = String(if_missing=None, max=70)
    sp_peida = String(if_missing=None, max=70)
    sp_kuva = String(if_missing=None, max=70)
    selgitus = String(if_missing=None, max=255)
    chained_validators = [Range('min_vastus',
                                'max_vastus',
                                'Max ei saa olla väiksem kui min'),
                          AnyNotEmpty('nimi', 'nimi_rtf', 'varv', 'removed')
                          ]

class TranChoiceForm(Schema):
    nimi = String()
    nimi_rtf = String(if_missing=None)
    varv = String(max=7, if_missing=None)    
    chained_validators = [AnyNotEmpty('nimi', 'nimi_rtf', 'varv')
                          ]
    
class MapEntryForm(Schema):
    kood1 = String(if_missing='', max=2000)
    kood1_rtf = String(if_missing=None, max=2000)    
    kood2 = String(if_missing=None, max=256)    
    tingimus = String(if_missing=None, max=256)
    valem = Bool
    teisendatav = Bool
    vrd_tekst = Bool    
    pallid = Number()
    oige = Bool()
    tahis = PyIdentifier(if_missing=None, max=25)
    #korduv_tabamus = Bool()
    tabamuste_arv = Int(if_missing=None, min=1)
    chained_validators = [RequireIfMissing('pallid',
                                           missing='oige'),
                          ]

class TranMapEntryForm(Schema):
    kood1 = String(if_missing=None, max=2000)
    kood1_rtf = String(if_missing=None, max=2000)
    kood2 = String(if_missing=None, max=256)    

class MultipleMatrixForm(Schema):
    hm = formencode.ForEach(MapEntryForm()) # hindamismaatriks
    
class ResultDeclarationForm(Schema):
    kysimus_id = Int()
    kood = PyIdentifier(not_empty=True)
    yhisosa_kood = String(if_missing=None, max=10)
    min_pallid = Number()
    max_pallid = Number()
    vaikimisi_pallid = Number(if_missing=None)
    oige_pallid = Number(if_missing=None)    
    min_sonade_arv = Int(if_missing=None)
    pintervall = Number(if_missing=None)
    vastus_pallid = Bool(if_missing=None)    
    min_vastus = Number(if_missing=None, min=0)
    max_vastus = Number(if_missing=None, min=1)
    min_oige_vastus = Number(if_missing=None)
    tostutunne = Bool(if_missing=None)
    ladinavene = Bool(if_missing=None)
    tyhikud = Bool(if_missing=None)
    lubatud_tyhi = Bool(if_missing=None)    
    regavaldis = Bool(if_missing=None)
    regavaldis_osa = Bool(if_missing=None)
    ymard_komakohad = Number(if_missing=None, min=0, max=12)
    ymardet = Bool(if_missing=None)
    sallivusprotsent = Number(if_missing=None, min=0)
    valem = Bool(if_missing=None)
    vordus_eraldab = Bool(if_missing=None)
    koik_oiged = Bool(if_missing=None)
    arvutihinnatav = Bool(if_missing=None)
    hybriidhinnatav = Bool(if_missing=None)
    oigsus_kysimus_id = Int(if_missing=None)
    maatriksite_arv = Number(if_missing=1, min=1)
    naidisvastus = String(if_missing=None)
    naidis_naha = Bool(if_missing=False)
    naide = Bool(if_missing=False)
    pre_validators = [formencode.NestedVariables()]
    hs = formencode.ForEach(AreaMapEntryForm())
    hs_x = formencode.ForEach(AreaMapEntryForm())    
    ht = formencode.ForEach(TrailMapEntryForm())    
    hm1 = formencode.ForEach(MapEntryForm()) # hindamismaatriks
    hmx = formencode.ForEach(MultipleMatrixForm()) # järjestamise ja pildil järjestamise ja kolme hulgaga sobitamise korral
    kht_min_vastus = Int(if_missing=None)
    kht_max_vastus = Int(if_missing=None)    
    k_evast_edasi = Bool
    k_evast_kasuta = Bool
    k_muutmatu = Bool
    k_ei_arvesta = Bool
    chained_validators = [Range('min_pallid',
                                'max_pallid',
                                'Max ei saa olla väiksem kui min'),
                          Range('min_oige_vastus',
                                'max_vastus',
                                'Lahendajal pole võimalik palle saada'),
                          ]    

class TranResultDeclarationForm(Schema):
    kood = PyIdentifier(not_empty=True)
    pre_validators = [formencode.NestedVariables()]
    hm1 = formencode.ForEach(TranMapEntryForm())
    hm2 = formencode.ForEach(TranMapEntryForm())

class SliderForm(Schema):
    min_vaartus = Number(not_empty=True)
    max_vaartus = Number(not_empty=True)
    samm = Number()
    vertikaalne = Bool(if_missing=False)
    samm_nimi = Bool(if_missing=False)
    tagurpidi = Bool(if_missing=False)
    yhik = String(max=15, if_missing=None)
    asend_vasakul = Bool(if_missing=False)
    asend_paremal = Bool(if_missing=False)
    chained_validators = [Range('min_vaartus',
                                'max_vaartus',
                                'Max ei saa olla väiksem kui min'),
                          ]    
class AudioForm(Schema):
    peida_start = Bool
    peida_paus = Bool
    peida_stop = Bool
    naita_play = Bool
    max_vastus = Int(if_missing=None)
    
class TaustForm(Schema):
    player = Int(if_missing=None)
    laius = Int(if_missing=None)
    korgus = Int(if_missing=None)
    autostart = Bool(if_missing=False)
    loop = Bool(if_missing=False)
    nahtamatu = Bool(if_missing=False)
    max_kordus = Int(if_missing=None)
    segamini = Bool(if_missing=None)
    asend = Int(if_missing=0)
    masonry_layout = Bool(if_missing=None)
    fileurl = URL(if_missing=None, max=200)
    tiitel = String(if_missing=None, max=256)
    pausita = Bool(if_missing=False)
    isekorduv = Bool(if_missing=False)
    nocontrols = Bool(if_missing=False)
    kpc_kood = PyIdentifier(if_missing=None)
    
class TranTaustForm(Schema):
    tiitel = String(if_missing=None, max=256)
    laius = Int(if_missing=None) # ristsõnas
    korgus = Int(if_missing=None) # ristsõnas
    
class UploadForm(Schema):
    mimetype = String(max=256)

class TrailForm(Schema):
    algus = String(max=256)
    labimatu = String(max=256)    
    lopp = String(max=256)
    
class JoonistamineForm(Schema):
    on_seadistus = Bool()
    on_arvutihinnatav = Bool()
    # muud seaded on ilma prefiksita parameetrites, mille nimi on kujul draw_*
    
class LahterForm(Schema):
    min_vastus = Int(if_missing=None)
    max_vastus = Int(if_missing=1)
    rtf = Bool(if_missing=None)
    rtf_notshared = Bool(if_missing=None)    
    pikkus = Int(if_missing=None)
    max_pikkus = Int(if_missing=None)
    ridu = Int(if_missing=None)
    reakorgus = Number(if_missing=None)
    mask = String(if_missing=None, max=256)
    vihje = String(if_missing=None, max=256)
    algvaartus = Bool
    pos_x = Int(if_missing=None)
    pos_y = Int(if_missing=None)
    segamini = Bool(if_missing=False)
    sonadearv = Bool(if_missing=False)
    tekstianalyys = Bool(if_missing=False)
    n_asend = Int(if_missing=None)
    vastusesisestus = Int(if_missing=None)
    hindaja_markused = Bool(if_missing=None)
    vastus_taisekraan = Bool(if_missing=None)
    erand346 = Bool
    chained_validators = [Range('min_vastus',
                                'max_vastus',
                                'Maksimaalne arv ei saa olla väiksem kui minimaalne'),
                          ]

class TranLahterForm(Schema):
    pikkus = Int(if_missing=None)
    max_pikkus = Int(if_missing=None)
    ridu = Int(if_missing=None)
    mask = String(if_missing=None, max=256)
    vihje = String(if_missing=None, max=256)
    pos_x = Int(if_missing=None)
    pos_y = Int(if_missing=None)
    
class GeogebraForm(Schema):
    showtoolbar = Bool(if_missing=None)
    showmenubar = Bool(if_missing=None)    
    showalgebrainput = Bool(if_missing=None)
    allowstylebar = Bool(if_missing=None)

class KrattKysimusForm(Schema):
    speak = String
    text = String
    kordus = Int(if_missing=None)
    ooteaeg = Piiraeg(if_missing=None, with_sec=True)
    vastamisaeg = Piiraeg(if_missing=None, with_sec=True)
    
class KrattForm(Schema):
    krati_kuulamine_record = Bool
    krati_kuulamine_audio_piiraeg = Piiraeg(if_missing=None, with_sec=True) # heli salvestamisel
    kysimused = formencode.ForEach(KrattKysimusForm)
    outro = KrattKysimusForm
    audio_seadistamine = Bool
    
class GoogleChartsColInstForm(Schema):
    value = String(if_missing=None) # rolesonly veeru korral puudub
    roles = formencode.ForEach(String) # metadata rea korral
    
class GoogleChartsColForm(Schema):
    inst = formencode.ForEach(GoogleChartsColInstForm)

class GoogleChartsRowForm(Schema):
    col = formencode.ForEach(GoogleChartsColForm)

class GoogleChartsForm(Schema):
    active = formencode.ForEach(String)
    datasetcnt = Int(if_missing=None)
    header = GoogleChartsRowForm(if_missing=None)
    data = formencode.ForEach(GoogleChartsRowForm)

class MChoiceForm(Schema):
    colwidth = formencode.ForEach(String)

class CrosswordCharLahterForm(Schema):
    vihje = String(max=1)
    pos_x = Int(if_missing=None)
    pos_y = Int(if_missing=None)

class UncoverKysimusForm(Schema):
    seq = Int
    expr1 = String()
    expr1_rtf = String()
    expresp = String(not_empty=True)
    expr2 = String()
    expr2_rtf = String()
    chained_validators = [AnyNotEmpty('expr1', 'expr1_rtf', 'expr2', 'expr2_rtf')]

class TranUncoverKysimusForm(Schema):
    seq = Int
    expr1 = String()
    expr1_rtf = String()
    expr2 = String()
    expr2_rtf = String()
    
class SisuplokkForm(Schema):
    "Sisu vorm"

    f_tahis = String(max=15, if_missing=None)
    f_naide = Bool(if_missing=False)
    f_rtf = Bool(if_missing=False) # kasutusel lünkteksti juures
    f_nimi = String(max=2000, if_missing=None)
    f_tehn_tookask = String(max=512, if_missing=None)    
    staatus = Bool(if_missing=False) # kasutusel pildi juures
    f_ymardamine = Bool(if_missing=False) # kasutusel interakstiooni sisuplokis
    f_varvimata = Bool(if_missing=False)
    f_min_pallid = Number(if_missing=None) # kasutusel mitme kysimusega sisuplokis    
    f_max_pallid = Number(if_missing=None) # kasutusel mitme kysimusega sisuplokis    
    f_reanr = Bool(if_missing=False) # kasutusel alustekstis
    f_kopikeeld = Bool(if_missing=False) # kasutusel alustekstis
    f_kleepekeeld = Bool(if_missing=False) # kasutusel avatud tekstiga sisuplokkides
    f_kommenteeritav = Bool(if_missing=False) # kasutusel alustekstis
    f_nahtavuslogi = Bool # kasutusel alustekstis
    f_wirismath = Bool # alustekst
    f_laius = Int(if_missing=None) # ristsõnas
    f_korgus = Int(if_missing=None) # ristsõnas
    f_suurus = Int(if_missing=None) # ristsõnas    
    f_kujundus = Int(if_missing=None) # tekstiosa valikus
    f_pausita = Bool(if_missing=None) # kasutusel heli salvestamisel
    autostart = formencode.ForEach(String) # kasutusel heli salvestamisel
    f_piiraeg = Piiraeg(if_missing=None, with_sec=True) # heli salvestamisel
    f_hoiatusaeg = Int(if_missing=None) # heli salvestamisel
    f_select_promptita = Bool(if_missing=None) # kasutusel valikvastusega lünga sisuplokis
    pre_validators = [formencode.NestedVariables()]
    l = LahterForm(if_missing=None)
    l2 = LahterForm(if_missing=None)
    l3 = LahterForm(if_missing=None)        
    ggb = GeogebraForm(if_missing=None)
    ggc = GoogleChartsForm(if_missing=None)
    mch = MChoiceForm(if_missing=None)
    krk = KrattForm(if_missing=None)
    mo = TaustForm(if_missing=None)
    mot = formencode.ForEach(TaustForm)    
    moi = formencode.ForEach(ImgForm)
    hs = formencode.ForEach(HotspotForm())
    mod = formencode.ForEach(GapImgForm())
    unck = formencode.ForEach(UncoverKysimusForm())
    v = formencode.ForEach(ChoiceForm())
    v_rtf = Bool(if_missing=False)
    v1 = formencode.ForEach(ChoiceForm())
    v1_rtf = Bool(if_missing=False)
    v2 = formencode.ForEach(ChoiceForm())
    v2_rtf = Bool(if_missing=False)
    v3 = formencode.ForEach(ChoiceForm())
    v3_rtf = Bool(if_missing=False)
    am = formencode.ForEach(ResultDeclarationForm()) # ipos, ihottext2, colorarea
    am1 = ResultDeclarationForm(if_missing=None)
    am2 = ResultDeclarationForm(if_missing=None)
    auk = AudioForm(if_missing=None)
    ul = UploadForm(if_missing=None)
    sl = SliderForm(if_missing=None)
    tl = TrailForm(if_missing=None)
    jo = JoonistamineForm(if_missing=None)
    draw_width = Int(if_missing=None)
    draw_stroke = String(max=7, if_missing=None)
    draw_fill_none = Bool(if_missing=None)
    draw_fill = String(max=7, if_missing=None)
    draw_fill_opacity = String(if_missing=None)
    draw_fontsize = Int(if_missing=None)
    draw_textfill = String(max=7, if_missing=None)
    score_incorrect_resp = Bool(if_missing=None)
    move_cnt = Int(if_missing=None)
    chained_validators = [Range('f_min_pallid',
                                'f_max_pallid',
                                'Max ei saa olla väiksem kui min'),
                          ]    


class TranSisuplokkForm(Schema):
    "Sisuploki vorm toimetajale ja tõlkijale"
    f_laius = Int(if_missing=None) # ristsõnas
    f_korgus = Int(if_missing=None) # ristsõnas
    mo = TranTaustForm(if_missing=None)    
    pre_validators = [formencode.NestedVariables()]
    l = TranLahterForm(if_missing=None)
    l2 = TranLahterForm(if_missing=None)
    l3 = TranLahterForm(if_missing=None)  
    unck = formencode.ForEach(TranUncoverKysimusForm())
    moi = formencode.ForEach(TranImgForm)
    mod = formencode.ForEach(TranGapImgForm())          
    v = formencode.ForEach(TranChoiceForm())
    v1 = formencode.ForEach(TranChoiceForm())
    v2 = formencode.ForEach(TranChoiceForm())
    am = formencode.ForEach(TranResultDeclarationForm()) # ipos
    am1 = TranResultDeclarationForm(if_missing=None)
    am2 = TranResultDeclarationForm(if_missing=None)        
    ggb = GeogebraForm(if_missing=None)
    krk = KrattForm(if_missing=None)
    ggc = GoogleChartsForm(if_missing=None)
    move_cnt = Int(if_missing=None)
    
class LukusSisuplokkForm(Schema):
    """Sisuploki vorm ülesande koostajale, 
    kui ülesanne on lukustatud nii, et saab ainult hindamismaatriksit muuta.
    """
    pre_validators = [formencode.NestedVariables()]
    hs = formencode.ForEach(HotspotForm())
    am = formencode.ForEach(ResultDeclarationForm()) # ipos
    am1 = ResultDeclarationForm(if_missing=None)
    am2 = ResultDeclarationForm(if_missing=None)        

class LukusTranSisuplokkForm(Schema):
    """Sisuploki vorm toimetajale ja tõlkijale,
    kui ülesanne on lukustatud nii, et saab ainult hindamismaatriksit muuta.
    """
    pre_validators = [formencode.NestedVariables()]
    am = formencode.ForEach(TranResultDeclarationForm()) # ipos
    am1 = TranResultDeclarationForm(if_missing=None)
    am2 = TranResultDeclarationForm(if_missing=None)        

class FailForm(Schema):
    id = Int()

class JuhisedForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    a = formencode.ForEach(FailForm())
    s = formencode.ForEach(FailForm())
    o = formencode.ForEach(FailForm())

class ReeglidForm(Schema):
    pass

class YhisfailidForm(Schema):
    "Otsingu vorm"
    pass

class YhisfailForm(Schema):
    "Otsingu vorm"
    f_teema = String(max=256)
    f_yhisfail_kood = String()
    f_filename = String(max=256, if_missing=None)

class IsikForm(Schema):
    pass

class KoostamineIsikForm(Schema):
    kasutajagrupp_id = Int(not_empty=True)
    oigus = formencode.ForEach(String)
    kehtib_kuni = EstDateConverter

class KoostamineMailForm(Schema):
    subject = String(not_empty=True)
    body = String(not_empty=True)
    k_id = formencode.ForEach(Int)
    
class PunktikirjeldusForm(Schema):
    punktid = Number
    kirjeldus = String
    id = Int
    
class AspektForm(Schema):
    a_aspekt_kood = String(not_empty=True)
    a_max_pallid = Number(min=0, not_empty=True)
    a_kaal = Number(min=0, not_empty=True)
    a_pintervall = Number(min=0)
    a_hindamisjuhis = String()
    a_seq = Int()
    a_kuvada_statistikas = Bool
    a_pkirj_sooritajale = Bool
    pkirjeldus = formencode.ForEach(PunktikirjeldusForm())

class ImportFailForm(Schema):
    pass

class ImportForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    files = formencode.ForEach(ImportFailForm())

class NormTagasisideForm(Schema):
    id = Int
    tingimus_tehe = String(not_empty=True)
    tingimus_vaartus = Number()
    tagasiside = String
    op_tagasiside = String
    jatka = Bool
    chained_validators = [AllOrNothingEmpty('tingimus_vaartus','tagasiside')]
    
class NpTagasisideForm(Schema):
    normikood = String(not_empty=True)
    npts = formencode.ForEach(NormTagasisideForm())

class TagasisideForm(Schema):
    f_yl_tagasiside = String
    np = NpTagasisideForm
    kuva_tulemus = Bool
