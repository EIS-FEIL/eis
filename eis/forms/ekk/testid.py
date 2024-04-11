"Ülesannete valideerimisskeemid"

import formencode
from eis.forms.validators import *
import eiscore.const as const

class OtsingForm(Schema):
    "Otsingu vorm"
    id = Int(if_missing=None)
    idr = IDRange(if_missing=None)
    testiosa_id = Int(if_missing=None)

class HulgiForm(Schema):
    kehtib_kuni = EstDateConverter(if_missing=None)
    
class TestitaseForm(Schema):
    keeletase_kood = String()    
    pallid = Number(min=0, max=100)

class TestihinneForm(Schema):
    hinne = Int()    
    pallid = Number(min=0, max=100)

class TestikursusForm(Schema):
    tunnaine_kood = String(if_missing=None, max=10)    
    kursus_kood = String(if_missing=None)
    
class YldandmedForm(Schema):
    "Üldandmete vorm"
    f_nimi = String(not_empty=True, max=256)
    aste_kood = formencode.ForEach(String)
    f_aine_kood = String(not_empty=True, max=10)
    testikursus = formencode.ForEach(TestikursusForm())
    t = formencode.ForEach(TestitaseForm())
    h = formencode.ForEach(TestihinneForm())    
    f_testiliik_kood = String()
    f_rveksam_id = Int(if_missing=None)
    f_periood_kood = String()
    f_oige_naitamine = Bool(if_missing=False)
    f_arvutihinde_naitamine = Bool(if_missing=False)
    r_korduv_sooritamine = Bool(if_missing=False)
    r_korduv_sailitamine = Bool(if_missing=False)            
    f_tulemus_tugiisikule = Bool
    f_vastus_tugiisikule = Bool
    f_osalemise_peitmine = Bool
    f_opetajale_peidus = Bool
    f_lang = String(not_empty=True)
    skeel = formencode.ForEach(String)
    f_ui_lang = Bool
    f_markus = String()
    f_ymardamine = Bool()
    f_diagnoosiv = Bool()
    f_pallideta = Bool()
    f_protsendita = Bool()        
    f_autor = String(if_missing=None)
    ek_sisu = String(if_missing=None)    
    # täiendavad väljad SE, TE korral
    vahemikud = formencode.ForEach(Int)
    f_lavi_pr = Int(max=100, if_missing=None)

class StruktuurForm(Schema):
    order = String()
    
class TagasisideViisForm(Schema):
    #f_tulemus_vaade = Int
    #f_ajakulu_naitamine = Int
    f_tagasiside_mall = Int(if_missing=None)

class TagasisideDiagrammTcolForm(Schema):
    "Tabeli veeru kirjeldus"
    name = String(not_empty=True)
    expr = String(no_empty=True)
    displaytype = String

class TagasisideDiagrammForm(Schema):
    dname = String
    width = Int
    height = Int(if_missing=None)
    x_label = String(if_missing=None)
    npkoodid = formencode.ForEach(String)
    tykoodid = formencode.ForEach(String)
    y_label = String(if_missing=None)
    tasemed = formencode.ForEach(String)
    colornivs = formencode.ForEach(String)
    color = formencode.ForEach(String) # muud diagrammid
    ty_kood = String(if_missing=None)
    np_kood = String(if_missing=None)
    tcol = formencode.ForEach(TagasisideDiagrammTcolForm)
    tcol2 = formencode.ForEach(String)
    avg_row = formencode.ForEach(String)
    sex = String(if_missing=None)
    
class TagasisideVarForm(Schema):
    pass

class NormProtsentiilForm(Schema):
    id = Int
    protsent = Int
    protsentiil = Number

class NormSooritusryhmForm(Schema):
    id = Int
    ryhm = Int
    lavi = Number

class NormTagasisideForm(Schema):
    id = Int
    ahel_testiylesanne_id = Int(if_missing=None)
    tingimus_tehe = String(not_empty=True)
    tingimus_vaartus = Number
    tingimus_valik = String(if_missing=None)
    tagasiside = String
    op_tagasiside = String
    uus_testiylesanne_id = Int(if_missing=None)    
    nsgrupp_id = Int(if_missing=None)
    chained_validators = [AnyNotEmpty('tagasiside', 'uus_testiylesanne_id'),
                          AnyNotEmpty('tingimus_vaartus', 'tingimus_valik'),]

class TranNormTagasisideForm(Schema):
    id = Int
    tagasiside = String
    op_tagasiside = String
       
class TagasisideTunnusFormNP(Schema):
    normityyp = Int(not_empty=True)
    alatestigrupp_id = Int(if_missing=None)    
    nimi = String(max=330, if_missing=None)
    kood = Identifier(max=50, if_missing=None)

    # psyh
    alatest_id = Int(if_missing=None)
    alatestigrupp_id = Int(if_missing=None)
    
    # õpip
    on_opilane = Bool
    on_grupp = Bool
    lang = String(if_missing=None)
    kysimus_kood = String(max=2000)
    min_vaartus = Number(if_missing=None)
    max_vaartus = Number(if_missing=None)
    
    # diag
    ylesandegrupp_id = Int(if_missing=None)
    testiylesanne_id = Int(if_missing=None)

    # tingimused
    # psyh
    protsentiilid = formencode.ForEach(NormProtsentiilForm())
    on_oigedvaled = Bool(if_missing=False)
    pooratud = Bool(if_missing=False)

    # õpip
    sryhmad = formencode.ForEach(NormSooritusryhmForm())    
    min_max = String(max=20, if_missing=None)
    pooratud_varv = Bool(if_missing=False)
    varv2_mk = Bool(if_missing=False)
    
    # diag
    npts = formencode.ForEach(NormTagasisideForm())

class TagasisideTunnusForm(Schema):
    np = TagasisideTunnusFormNP

class TranTagasisideTunnusFormNP(Schema):
    filter_extra_fields = True
    nimi = String(max=330, if_missing=None)
    npts = formencode.ForEach(TranNormTagasisideForm())

class TranTagasisideTunnusForm(Schema):
    np = TranTagasisideTunnusFormNP

class TagasisideAtgruppForm(Schema):
    nimi = String(max=256)
    id = Int
     
class TagasisideAtgrupidForm(Schema):
    atg = formencode.ForEach(TagasisideAtgruppForm)    

class TagasisideNsgruppForm(Schema):
    nimi = String(max=1024)
    id = Int

class TagasisideNsgrupidForm(Schema):
    nsg = formencode.ForEach(TagasisideNsgruppForm)

class TagasisideYlgruppForm(Schema):
    nimi = String(max=1024)
    id = Int

class TagasisideYlgrupidForm(Schema):
    ylg = formencode.ForEach(TagasisideYlgruppForm)
    
class NormForm(Schema):
    id = Int
    grupp_prefix = String

class TagasisideTunnusedForm(Schema):
    normid = formencode.ForEach(NormForm())
       
class TestiosaForm(Schema):
    t_nimi = String(not_empty=True, max=256)
    seq = Int(if_missing=None)
    f_tahis = String(max=10, not_empty=True)
    f_nimi = String(not_empty=True, max=256)
    f_skoorivalem = String(if_missing=None, max=256)
    f_vastvorm_kood = String(max=10)
    piiraeg = Piiraeg()
    f_piiraeg_sek = Bool
    hoiatusaeg = Int
    f_aeg_peatub = Bool
    f_alustajajuhend = String()
    f_sooritajajuhend = String()    
    f_tulemus_tunnistusele = Bool()   
    f_rvosaoskus_id = Int(if_missing=None)
    f_naita_max_p = Bool
    f_lotv = Bool
    f_yhesuunaline = Bool
    f_yl_segamini = Bool
    f_yl_lahk_hoiatus = Bool
    f_yl_pooleli_hoiatus = Bool    
    f_yl_lahendada_lopuni = Bool
    f_ala_lahk_hoiatus = Bool
    f_kuva_yl_nimetus = Bool
    f_peida_yl_pealkiri = Bool
    peida_yl_list = Bool
    f_peida_pais = Bool    
    f_yl_jrk_alatestiti = Bool
    f_katkestatav = Bool
    f_lopetatav = Bool
    
class TestiosaTForm(Schema):
    t_nimi = String(if_missing=None, max=256)
    f_nimi = String(not_empty=True, max=256)

class AlatestForm(Schema):
    piiraeg = Piiraeg(with_sec=True, if_missing=None) # puudub tõlkimisel
    f_piiraeg_sek = Bool
    hoiatusaeg = Int(if_missing=None) # puudub tõlkimisel
    f_nimi = String(not_empty=True, max=256)
    f_numbrita = Bool
    f_sooritajajuhend = String(max=1024)
    f_alatest_kood = String(if_missing=None)
    f_kursus_kood = String(if_missing=None)
    max_pallid = Number(if_missing=None)
    f_skoorivalem = String(if_missing=None, max=256)
    f_rvosaoskus_id = Int(if_missing=None)
    f_on_yhekordne = Bool(if_missing=False)
    f_yl_segamini = Bool(if_missing=False)
    f_yhesuunaline = Bool(if_missing=False)    
    f_peida_pais = Bool(if_missing=False)
    f_alatestigrupp_id = Int(if_missing=None)

class AlatestTForm(Schema):
    f_nimi = String(not_empty=True, max=256)
    f_sooritajajuhend = String(max=1024)
    
class TestiplokkForm(Schema):
    f_alatest_id = Int()
    f_nimi = String(not_empty=True, max=256)

class TestiylesanneDiag2Form(Schema):
    f_on_jatk = Bool(if_missing=False)
    f_max_pallid = Number(not_empty=False)
    mitu = Int(if_missing=None)
    
class TestiylesanneForm(Schema):
    f_alatest_id = Int(if_missing=None)
    f_testiplokk_id = Int(if_missing=None)
    f_yhisosa_kood = String(max=10, if_missing=None)
    f_nimi = String(not_empty=False, max=256)
    f_max_pallid = Number(not_empty=False)
    f_naita_max_p = Bool
    f_on_markus_sooritajale = Bool
    on_valikylesanne = Bool()
    f_sooritajajuhend = String(max=1024, if_missing=None)
    pealkiri = formencode.ForEach(String)
    f_hindamine_kood = String(if_missing=None)
    f_arvutihinnatav = Bool(if_missing=False)
    f_valikute_arv = Int(if_missing=1)
    f_valik_auto = Bool(if_missing=False)
    piiraeg = Piiraeg(with_sec=True, if_missing=None) 
    f_piiraeg_sek = Bool
    min_aeg = Piiraeg(with_sec=True, if_missing=None) 
    hoiatusaeg = Int(if_missing=None) 
    f_alateema_kood = String(if_missing=None)
    f_teema_kood = String()
    f_mote_kood = String()
    f_aste_kood = String()
    f_tyyp = String()
    f_kasutusmaar = Number()
    f_liik = String
    f_kuvada_statistikas = Bool(if_missing=False)
    f_ise_jargmisele = Bool(if_missing=False)
    mitu = Int(if_missing=None)
    
class TestiylesanneTForm(Schema):
    f_alatest_id = Int(if_missing=None)
    f_testiplokk_id = Int(if_missing=None)
    f_nimi = String(not_empty=True, max=256)
    f_sooritajajuhend = String(max=1024, if_missing=None)
    pealkiri = formencode.ForEach(String)

class YlesandegruppModifyForm(Schema):
    nimi = String(max=1024)

class YlesandegrupidModifyForm(Schema):
    ylg = formencode.ForEach(YlesandegruppModifyForm)

class YlesandegruppForm(Schema):
    yg_nimi = String(max=1024, if_missing=None)
    
class YlesandedForm(Schema):
    pass

class KomplektOtsiylesandedForm(Schema):
    pass

class StruktuurOtsiylesandedForm(Schema):
    pass

class KomplektForm(Schema):
    f_tahis = String(max=10)
    alatest_id = formencode.ForEach(Int)
    komplektivalik_id = formencode.ForEach(Int)
    skeel = formencode.ForEach(String, not_empty=True)

class KomplektivalikForm(Schema):
    alatest_id = formencode.ForEach(Int)
    
class ErialatestForm(Schema):
    lisaaeg = Piiraeg(with_sec=False)
    dif_hindamine = Bool(if_missing=None)
    alatest_id = Int()

class ErialatestidForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    ek = formencode.ForEach(ErialatestForm())

class TestifailimarkusForm(Schema):
    teema = String(max=100, not_empty=True)
    sisu = String(not_empty=True)
    ylem_id = Number()

class SisestuskogumiylesanneForm(Schema):
    id = Int()
    sisestusviis = String()
    hyppamisviis = Int(if_missing=0)
    
class SisestuskogumForm(Schema):
    f_nimi = String(not_empty=True, max=100)
    f_on_skannimine = Bool(if_missing=False)
    f_naita_pallid = Bool(if_missing=False)
    f_tasu = Number(if_missing=None)
    pre_validators = [formencode.NestedVariables()]
    ty = formencode.ForEach(SisestuskogumiylesanneForm())
    
class HindamiskogumForm(Schema):
    sisestuskogum_id = Int(if_missing=None)
    testiosa_id = Int()
    f_tahis = String(max=10)
    f_nimi = String(not_empty=True)
    f_on_digiteerimine = Bool(if_missing=False)
    f_hindamine_kood = String()
    f_kahekordne_hindamine = Bool(if_missing=False)
    f_kahekordne_hindamine_valim = Bool(if_missing=False)
    f_paarishindamine = Bool(if_missing=False)
    f_kontrollijaga_hindamine = Bool(if_missing=False)    
    f_on_hindamisprotokoll = Bool(if_missing=False)
    f_erinevad_komplektid = Bool(if_missing=False)
    f_hindajate_erinevus = Number(if_missing=None)
    f_hindamine3_loplik = Bool(if_missing=False)        
    f_arvutus_kood = String(if_missing='k')
    f_tasu = Number()
    f_intervjuu_tasu = Number(if_missing=None)
    f_intervjuu_lisatasu = Number(if_missing=None)    
    f_oma_kool_tasuta = Bool(if_missing=False)
    f_komplektivalik_id = Int(not_empty=True)
    f_on_markus_sooritajale = Bool
    
class KritkirjeldusForm(Schema):
    kirjeldus = String
    
class HindamiskriteeriumForm(Schema):
    a_aspekt_kood = String(not_empty=True)
    a_max_pallid = Number(min=0, not_empty=True)
    a_kaal = Number(min=0, not_empty=True)
    a_hindamisjuhis = String()
    a_seq = Int()
    a_kuvada_statistikas = Bool
    a_pkirj_sooritajale = Bool
    pkirjeldus = formencode.ForEach(KritkirjeldusForm())

class TestimiskordForm(Schema):
    f_on_mall = Bool
    f_nimi = String(max=256, if_missing=None)
    f_tahis = Alphanum(max=20, not_empty=True)
    f_testsessioon_id = Int()
    f_aasta = Int
    f_vaide_algus = EstDateConverter()
    f_vaide_tahtaeg = EstDateConverter()    
    f_on_avalik_vaie = Bool
    f_korduv_reg_keelatud = Bool
    f_reg_kohavalik = Bool(if_missing=False)
    f_reg_voorad = Bool(if_missing=False)
    f_korraldamata_teated = Bool(if_missing=False)
    
    lang = formencode.ForEach(String, not_empty=True)
    f_cae_eeltest = Bool(if_missing=None)
    f_reg_piirang = String(if_missing=None)
    f_reg_sooritaja = Bool(if_missing=False)
    f_reg_xtee = Bool(if_missing=False)
    f_reg_kool_ehis = Bool(if_missing=False)
    f_reg_kool_eis = Bool(if_missing=False)
    f_reg_kool_valitud = Bool(if_missing=False)
    f_reg_ekk = Bool(if_missing=False)
    f_reg_sooritaja_alates = EstDateConverter()
    f_reg_sooritaja_kuni = EstDateConverter()
    f_reg_xtee_alates = EstDateConverter(if_missing=None)
    f_reg_xtee_kuni = EstDateConverter(if_missing=None)
    f_reg_kool_alates = EstDateConverter()
    f_reg_kool_kuni = EstDateConverter()
    peidus_kuni = EstDateConverter()
    peidus_kell = EstTimeConverter()

    f_erivajadus_alates = EstDateConverter()
    f_erivajadus_kuni = EstDateConverter()
    
    f_kool_testikohaks = Bool(if_missing=False)
    f_sisestus_isikukoodiga = Bool(if_missing=False)

    f_osalemistasu = Number()
    f_kordusosalemistasu = Number()
    f_prot_vorm = Number(if_missing=0) # const.PROT_VORM_VAIKIMISI
    f_on_helifailid = Bool
    f_on_turvakotid = Bool
    f_osalemise_naitamine = Bool(if_missing=False)
    f_tulemus_koolile = Bool()
    f_tulemus_admin = Bool()    
    f_analyys_eraldi = Bool()
    f_stat_valim = Bool
    arvutada_kohe = Bool
    f_markus = String(max=1024)
    
    chained_validators = [Range('f_reg_sooritaja_alates',
                                'f_reg_sooritaja_kuni',
                                'Vahemiku algus ei saa olla peale lõppu'),
                          Range('f_reg_xtee_alates',
                                'f_reg_xtee_kuni',
                                'Vahemiku algus ei saa olla peale lõppu'),
                          Range('f_reg_kool_alates',
                                'f_reg_kool_kuni',
                                'Vahemiku algus ei saa olla peale lõppu'),
                          Range('f_vaide_algus',
                                'f_vaide_tahtaeg',
                                'Vaidlustamise algus ei saa olla peale lõppu'),                          
                          Range('f_erivajadus_alates',
                                'f_erivajadus_kuni',
                                'Vahemiku algus ei saa olla peale lõppu'),
                          NotEmptyIffNotEmpty('f_reg_sooritaja',
                                              'f_reg_sooritaja_alates',
                                              'f_reg_sooritaja_kuni'),
                          NotEmptyIffNotEmpty('f_reg_xtee',
                                              'f_reg_xtee_alates',
                                              'f_reg_xtee_kuni'),
                          ]    

class ValjastusymbrikuliikForm(Schema):
    nimi = String(not_empty=True, max=256)
    id = Int()
    maht = Int(min=1)
    lisatoode_koef = Number(min=1)
    lisatoode_arv = Int(min=0)
    ymarduskordaja = Int(min=1)
    sisukohta = Int
    keeleylene = Bool

class TagastusymbrikuliikForm(Schema):
    nimi = String(not_empty=True, max=100)
    id = Int()
    maht = Int()
    sisukohta = Int()
    hindamiskogum_id = formencode.ForEach(Int)
    
class ToimumispaevForm(Schema):
    kuupaev = EstDateConverter(not_empty=True)
    valim = Bool
    kell = EstTimeConverter()
    a_lopp = EstTimeConverter(if_missing=None)
    d_lopp = EstDateConverter(if_missing=None)
    t_lopp = EstTimeConverter(if_missing=None)    
    id = Int()

class ToimumisaegForm(Schema):
    
    tpv = formencode.ForEach(ToimumispaevForm())
    f_ruum_voib_korduda = Bool
    f_aja_jargi_alustatav = Bool
    f_algusaja_kontroll = Bool
    f_kell_valik = Bool
    f_vaatleja_maaraja = Bool()
    f_vaatleja_koolituskp = EstDateConverter()
    komplekt_id = formencode.ForEach(Int(), convert_to_list=True, not_empty=True)
    f_komplekt_valitav = Bool()
    f_komplekt_valitav_y1 = Bool()
    f_keel_admin = Bool
    
    # hindamise väljad
    f_hindaja1_maaraja = Int(if_missing=None)
    f_hindaja2_maaraja = Int(if_missing=None)
    f_hindaja1_maaraja_valim = Int(if_missing=None)
    f_hindaja2_maaraja_valim = Int(if_missing=None)    
    f_hindaja_koolituskp = EstDateConverter(if_missing=None)
    f_intervjueerija_maaraja = Int(if_missing=None)
    f_intervjueerija_koolituskp = EstDateConverter(if_missing=None)

    f_admin_teade = Bool(if_missing=None)
    f_esimees_maaraja = Bool(if_missing=False)
    f_komisjoniliige_maaraja = Bool(if_missing=False)
    f_komisjon_maaramise_tahtaeg = EstDateConverter()
    
    # SE,TE korral
    f_esimees_koolituskp = EstDateConverter(if_missing=None)
    f_komisjoniliige_koolituskp = EstDateConverter(if_missing=None)

    f_reg_labiviijaks = Bool()
    f_hindaja_kaskkirikpv = EstDateConverter(if_missing=None)
    f_intervjueerija_kaskkirikpv = EstDateConverter(if_missing=None)        
    f_ruumide_jaotus = Bool()
    f_labiviijate_jaotus = Bool()
    f_hinnete_sisestus = Bool()
    f_kahekordne_sisestamine = Bool()
    f_oma_prk_hindamine = Bool()
    f_oma_kooli_hindamine = Bool()
    f_sama_kooli_hinnatavaid = Int()
    f_hindamise_luba = Bool
    hindamise_algus_kp = EstDateConverter(if_missing=None)
    hindamise_algus_kell = EstTimeConverter(if_missing=None)
    f_hindamise_tahtaeg = EstDateConverter(if_missing=None)
    f_protok_ryhma_suurus = Int()
    f_on_arvuti_reg = Bool(if_missing=False)
    f_on_reg_test = Bool(if_missing=False)
    f_samaaegseid_vastajaid = Int(if_missing=None)
    f_valjastuskoti_maht = Int()
    f_tagastuskoti_maht = Int()
    f_jatk_voimalik = Bool()
    prot_admin1 = Int(if_missing=0)
    prot_admin2 = Int(if_missing=0)
    f_prot_eikinnitata = Bool
    f_eelvaade_admin = Bool()
    f_nimi_jrk = Bool
    f_verif = String(if_missing=None)
    f_verif_seb = Bool
    f_vaatleja_tasu = Number()
    f_vaatleja_lisatasu = Number()
    f_komisjoniliige_tasu = Number()
    f_esimees_tasu = Number()
    f_admin_tasu = Number()    

    pre_validators = [formencode.NestedVariables()]
    vb = formencode.ForEach(ValjastusymbrikuliikForm())
    tb = formencode.ForEach(TagastusymbrikuliikForm())
    chained_validators = [Range('hindamise_algus_kp',
                                'f_hindamise_tahtaeg',
                                'Vahemiku algus ei saa olla peale lõppu'),
                          ]    
    

class KutseToimumisaegForm(Schema):
    testiosa_id = Int
    tpv = formencode.ForEach(ToimumispaevForm())
    ruum_voib_korduda = Bool
    komplekt_id = formencode.ForEach(Int(), convert_to_list=True, not_empty=True)
    komplekt_valitav = Bool()
    komplekt_valitav_y1 = Bool()
    
    on_arvuti_reg = Bool(if_missing=False)
    aja_jargi_alustatav = Bool

    pre_validators = [formencode.NestedVariables()]

class KutseTestimiskordForm(Schema):
    f_tahis = Alphanum(max=20)
    f_testsessioon_id = Int()
    lang = formencode.ForEach(String, not_empty=True)
    ta = formencode.ForEach(KutseToimumisaegForm)

class IsikForm(Schema):
    isikukood = Isikukood()
    eesnimi = String()
    perenimi = String()

class KoostamineMailForm(Schema):
    subject = String(not_empty=True)
    body = String(not_empty=True)
    k_id = formencode.ForEach(Int)
                              
class KoostamineIsikudForm(Schema):
    isikukood = String(if_missing=None)
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)
    ametnik = Int(if_missing=1)

class KoostamineIsikForm(Schema):
    kasutajagrupp_id = Int(not_empty=True)
    oigus = formencode.ForEach(String)
    kehtib_kuni = EstDateConverter

class KoostamineIsikFailForm(Schema):
    kehtib_kuni = EstDateConverter
    
class KoostamineOlekForm(Schema):
    staatus = Int
    avaldamistase = Int
    t_avalik_alates = EstDateConverter()
    t_avalik_kuni = EstDateConverter()
    markus = String
    chained_validators = [Range('t_avalik_alates',
                                't_avalik_kuni',
                                'Vahemiku algus ei saa olla peale lõppu'),
                          ]    
    
class EeltestMailForm(Schema):
    subject = String(not_empty=True)
    body = String(not_empty=True)

class EeltestForm(Schema):
    t_avaldamistase = Int()
    t_avalik_alates = EstDateConverter()
    t_avalik_kuni = EstDateConverter()
    e_markus_korraldajatele = String(max=512)
    e_tagasiside_sooritajale = Bool
    e_tagasiside_koolile = Bool
    komplekt_id = formencode.ForEach(Int)
    chained_validators = [Range('t_avalik_alates',
                                't_avalik_kuni',
                                'Vahemiku algus ei saa olla peale lõppu'),
                          ]    

class TagasisidevormVabaForm(Schema):
    liik = Int(if_missing=None)
    f_sisu = String()
    staatus = Int(if_missing=0)
    f_nimi = String(max=100)
    f_lang = String(if_missing=None)
    f_kursus = String(if_missing=None)
    f_nahtav_opetajale = Bool
    sup_id = Int
    seq = Int
    
class DiagnoosForm(Schema):
    tingimus_kood = String(not_empty=True)
    tingimus_tehe = String
    tingimus_vaartus = Int
    tingimus_valik = String(if_missing=None)
    uus_ylesanne_id = Int
    uus_valitudylesanne_id = Int(if_missing=None)
    tagasiside = String
    id = Int
    chained_validators = [AnyNotEmpty('tingimus_vaartus', 'tingimus_valik'),
                          AnyNotEmpty('uus_ylesanne_id', 'tagasiside'),
                          ]    
    
class DiagnoosidForm(Schema):
    dia = formencode.ForEach(DiagnoosForm())

class TagasisidevormDiagForm(Schema):
    f_ts_loetelu = Bool
    f_ylgrupp_kuva = Int(if_missing=const.KUVA_EI)
    f_ylgrupp_nimega = Bool
    f_nsgrupp_kuva = Int(if_missing=const.KUVA_EI)
    f_nsgrupp_nimega = Bool
    f_kompaktvaade = Bool
    f_ts_sugu = Bool
    
class TranTagasisidevormDiagForm(Schema):
    pass
    
