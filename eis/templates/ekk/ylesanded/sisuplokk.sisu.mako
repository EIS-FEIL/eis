<% 
c.ylesanne = c.item.ylesanne

if c.lang:
   if c.user.has_permission('ylesanded-tolkimine', const.BT_UPDATE,c.ylesanne):
      # tõlkimise ajal on ainult tõlkeväljad kirjutatavad
      c.can_tr = True
      if c.item.tyyp == const.BLOCK_HEADER and not c.user.has_permission('srcedit', const.BT_UPDATE):
         c.can_tr = False
      c.is_tr = c.is_edit
   c.is_edit = False
elif not c.lang and \
    not c.user.has_permission('ylesanded', const.BT_UPDATE,c.ylesanne) and \
    c.user.has_permission('ylesanded-toimetamine', const.BT_UPDATE,c.ylesanne):
   # toimetaja tohib ainult tekstivälju kirjutada
   c.can_tr = True
   c.is_tr = c.is_edit
   c.is_edit = False

c.can_tr_sisu = c.can_tr and not c.ylesanne.lukus
c.can_tr_hm = c.can_tr and c.ylesanne.lukus_hm_muudetav
c.is_tr = c.is_tr and c.can_tr_hm

if c.ylesanne.lukus:
   c.is_edit_hm = c.is_edit and c.can_update_hm
   c.is_edit = False
else:
   c.is_edit_hm = c.is_edit

%>
########## Vormi avamine
% if c.item.tyyp  or request.params.get('f_tyyp') in (const.BLOCK_MEDIA, const.INTER_POS, const.INTER_GR_GAP, const.INTER_HOTSPOT, const.INTER_GR_ORDER, const.INTER_GR_ASSOCIATE):

${h.form_save(c.item.id, multipart=True)}

% else:

${h.form_save(c.item.id)}

% endif
${h.hidden('f_tyyp', c.item.tyyp)}
${h.hidden('tyyp', c.item.tyyp)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)}
######### Vormi andmed

<div class="d-flex flex-wrap justify-content-between">
  <div>
    <h2>${c.item.tyyp_nimi}</h2>
    <span class="helpable" id="sptyyp_${c.item.tyyp}"></span>
  </div>
  % if c.item.id:
  <div class="flex-grow-1">
  <%include file="sisuplokk.lang.mako"/>
  </div>
  % endif

  % if c.item.id and c.item.tyyp in const.interaction_graphic and c.ylesanne.vahendid:
  ## pildi sisuplokkide koostamisel kuvame ka abivahendeid, et koostaja saaks kasutada joonlauda ja malli
  <div class="d-flex justify-content-end flex-grow-1">
      <%
        c.block = c.item
        c.item = c.ylesanne
      %>
      <%include file="/avalik/lahendamine/tools.mako"/>
      <% c.item = c.block %>
  </div>
  % endif
</div>

<div style="height:0">
<div id="sp_ckeditor_top" class="ckeditor-top-float"></div>
<script>
$(function(){
  init_ckeditor($('.editable-bold'), 'sp_ckeditor_top', '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16', true);
});
</script>
</div>

${h.rqexp()}
<div class="form-wrapper mb-2">
  <div class="mb-1 row">

    ${h.flb(_("Sisuploki tähis"), 'f_tahis', 'col-md-3 col-xl-2 text-md-right', rq=True)}
    <div class="col-md-3 col-xl-2">
      ${h.text('f_tahis', c.item.tahis, placeholder=c.item.seq, size=13, maxlength=15)}
      % if c.is_edit:
      <script>
        $('#f_tahis').blur(function(){
        ## tähise muutmisel muuta teise astme (.nav-pills) saki pealkiri
        var value = $(this).val().replace(/[^a-z0-9]/gi, '') || $(this).attr('placeholder');
        if(value)
            $('ul.nav-pills a.nav-link.active').text(value);
        });
      </script>
      % endif
    </div>
  
  % if c.item.tyyp not in (const.BLOCK_HEADER, const.BLOCK_FORMULA, const.BLOCK_RANDOM):  
  <div class="form-group col-md-6 col-xl-8 align-contents-end row">
    % if c.item.is_interaction:
    <div class="col-md-12 col-xl-6">
      ${h.checkbox('f_naide', 1, checked=c.item.naide, label=_("Näide"))}
    </div>
    % endif
    % if c.item.tyyp == const.BLOCK_IMAGE:
    <div class="col-md-12 col-xl-6">      
      ${h.checkbox('staatus', 1, checked=c.item.staatus, label=_("Pilt kuvatakse"))}
    </div>
    % elif c.item.tyyp == const.BLOCK_MEDIA:
    <div class="col-md-12 col-xl-6">      
      ${h.checkbox('staatus', 1, checked=c.item.staatus, label=_("Mängija kuvatakse"))}
    </div>
    % elif c.item.tyyp == const.BLOCK_CUSTOM:
    <div class="col-md-12 col-xl-6">      
      ${h.checkbox('staatus', 1, checked=c.item.staatus, label=_("Link kuvatakse"))}
    </div>
    % endif
    <div class="col-md-12 col-xl-6">      
      ${h.checkbox('staatus2', 1, checked=c.item.staatus==2, label=_("Algselt nähtamatu"),
      onclick="if(this.checked)$('input#staatus_1').prop('checked', true);")}
    </div>
    % if c.item.is_interaction:
    <div class="col-md-12 col-xl-6">      
      ${h.checkbox('f_ymardamine', 1, checked=c.item.ymardamine, label=_("Punktid ümardatakse sisuploki piires"))}
    </div>
      % endif
    % if c.item.is_interaction:
    <div class="col-md-12 col-xl-6">      
      ${h.checkbox('f_varvimata', 1, checked=c.item.varvimata, label=_("Õigeid/valesid vastuseid ei värvita"))}
    </div>
    % endif
    % if c.item.tyyp in (const.INTER_TEXT, const.INTER_EXT_TEXT, const.INTER_INL_TEXT):
    <div class="col-md-12 col-xl-6">      
      ${h.checkbox('f_kleepekeeld', 1, checked=c.item.kleepekeeld, label=_("Takista kopeeritud teksti kleepimist väljale"))}
    </div>
    % endif
  </div>
  % endif

      
  % if c.item.tyyp not in (const.BLOCK_HEADER, const.BLOCK_FORMULA, const.BLOCK_RANDOM):

    ${h.flb(_("Küsimus või tööjuhend"),None, 'col-md-3 col-xl-2 text-md-right')}
    <div class="col-md-9 col-xl-10">
      <%
        ronly = not c.is_tr and not c.is_edit or bool(c.item.ylesanne and c.item.ylesanne.lukus)
        nimi = c.lang and c.item.tran(c.lang).nimi or c.item.nimi
      %>
      % if c.lang:
        ${h.literal(c.item.nimi)}
        <div class="linebreak"></div>
        ${h.lang_tag()}
      % endif
        % if ronly:
        ${h.readonly_rtf(nimi)}
        % else:
        ${h.textarea('f_nimi', nimi, ronly=ronly, rows=2, maxlength=2000, class_="editable-bold")}
        % endif
    </div>

    ${h.flb(_("Tehniline töökäsk"), 'f_tehn_tookask', 'col-md-3 col-xl-2 text-md-right')}
    <div class="col-md-9 col-xl-10">
      <%
        opt_tookask = c.opt.klread_kood('TOOKASK', c.item.tyyp, bit=c.ylesanne.aste_mask, lang=c.lang or c.ylesanne.lang)
        if not c.item.id and opt_tookask:
            # uue sisuploki loomisel pakume vaikimisi esimese töökäsu valikust
            c.item.tookask_kood = opt_tookask[0][0]
            c.item.tehn_tookask = opt_tookask[0][1]

        if c.item.tookask_kood:
            tookask = model.Klrida.get_str('TOOKASK', c.item.tookask_kood, c.item.tyyp, lang=c.ylesanne.lang) 
        else:
            tookask = c.item.tehn_tookask
            
        if c.lang:
            if c.item.tookask_kood:
               tran_tookask = model.Klrida.get_str('TOOKASK', c.item.tookask_kood, c.item.tyyp, lang=c.lang)
            else:
               tran_tookask = c.item.tran(c.lang).tehn_tookask
      %>
      % if c.lang:
        ${h.lang_orig(tookask)}<br/>
        ${h.lang_tag()}
        % if ronly or c.item.tookask_kood:
          ${h.text('f_tehn_tookask', tran_tookask, maxlength=512, ronly=True)}
          ${h.hidden('f_tehn_tookask', tran_tookask)}
        % else:
          ${h.text('f_tehn_tookask', tran_tookask, maxlength=512, ronly=False)}
        % endif
      % else:
        ${h.text('f_tehn_tookask', tookask, maxlength=512, ronly=ronly)}
      % endif

      % if c.is_edit and opt_tookask:
      ${h.select('f_tookask_kood', c.item.tookask_kood, opt_tookask, empty=True)}
      % endif
      <script>
        $('#f_tookask_kood').change(function(){
          var o = $('#f_tookask_kood option:selected');
          $('#f_tehn_tookask').val(o.val() ? o.text() : '');
        });
        $('#f_tehn_tookask').change(function(){
          $('#f_tookask_kood').val('');
        });
      </script>
    </div>


  % if c.item.tyyp in (const.INTER_INL_TEXT, const.INTER_INL_CHOICE, const.INTER_EXT_TEXT, const.INTER_GAP, const.INTER_HOTTEXT, const.INTER_CROSSWORD, const.INTER_POS, const.INTER_TXPOS):  

    ${h.flb(_("Sisuploki miinimumpunktid"), 'f_min_pallid', 'col-md-3 col-xl-2 text-md-right')}
    <div class="col-md-3 col-xl-2">
      ${h.float5('f_min_pallid', c.item.min_pallid)}
    </div>

    ${h.flb(_("Sisuploki maksimumpunktid"), 'f_max_pallid', 'col-md-3 text-md-right')}
    <div class="col-md-3 col-xl-3">
      ${h.float5('f_max_pallid', c.item.max_pallid)}
    </div>
  % endif
  % endif
</div>
  ${c.item.ctrl.edit()}
</div> 
<div class="clearfix"> </div>
<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('ylesanded_sisu', id=c.item.ylesanne_id, lang=c.lang), level=2)}

    % if c.item.id and len([r for r in c.item.sisuobjektid if r.filename]):
    ${h.btn_to(_("Laadi failid alla"), h.url_current('download', format='zip', id=c.item.id, lang=c.lang), method='get', level=2)}
    % endif

    % if c.is_edit or c.is_edit_hm or c.is_tr:

    <% valik_tyybid = (const.INTER_MATCH2, const.INTER_MATCH3, const.INTER_CHOICE, const.INTER_ASSOCIATE, const.INTER_ORDER, const.INTER_HOTTEXT, const.INTER_INL_CHOICE, const.INTER_GAP, const.INTER_TXPOS, const.INTER_TXPOS2, const.INTER_TXGAP, const.INTER_TXASS, const.INTER_COLORAREA, const.INTER_MCHOICE) %>
    % if c.item.id and (c.is_edit or c.is_edit_hm) and not c.is_tr and c.block.tyyp in valik_tyybid:
    ${h.submit(_("Genereeri selgitused"), id="gendesc", level=2)}
    % endif

    % endif

    % if c.block.tyyp == const.INTER_PUNKT and c.item.id:
    ${h.btn_to_dlg(_("Nupuriba"),
    h.url('ylesanne_edit_sisuplokk', ylesanne_id=c.item.ylesanne_id, id=c.item.id, sub='icons', partial=True), title=_("Nupuriba"), level=2)}
    % endif
  </div>
  <div>
  % if c.is_edit or c.is_edit_hm or c.is_tr:    
    % if c.item.id:
    ${h.btn_to(_("Vaata"), h.url('ylesanne_sisuplokk', id=c.item.id,
ylesanne_id=c.item.ylesanne_id, lang=c.lang), level=2)}
    % endif
    <%
    is_save = True
    if c.ylesanne.lukus:
       # lukus ylesandes saab salvestada ainult hindamismaatriksit,
       # kuid lynkylesande hindamismaatriks salvestatakse kysimuse kaupa
       is_save = c.item.tyyp not in (const.INTER_INL_CHOICE,) and not c.app_eis
       # avalikus vaates ei saa lukus ylesannet muuta
    %>
    % if is_save:
    ${h.submit()}
    % endif
  % elif c.can_update_hm or c.can_tr:
    ${h.btn_to(_("Muuda"), h.url('ylesanne_edit_sisuplokk', id=c.item.id,
    ylesanne_id=c.item.ylesanne_id, lang=c.lang, is_tr=c.can_tr))}
  % endif
  </div>
</div>
${h.end_form()}

<script>
## kas on tõlkimine (info, mida ckeditori pluginas kasutada)
var ckeditor_is_tr = ${c.is_tr and 'true' or 'false'};
function get_dialog_url(kood, data, command, pos_x, pos_y, container)
{
## kood - lünga (küsimuse) kood
## data - olemasolev väli HTMLina
## command - gaptext või gapchoice või gapmatch
## genereeritakse URL, millega saab dialoogaknas näidata alamsisuplokki
var tyyp='${const.INTER_TEXT}';
if(command == 'gapchoice')
   tyyp = '${const.INTER_CHOICE}';
else if(command == 'gapmatch')
   tyyp = '${const.INTER_GAP}';
else if(command == 'crossword')
   tyyp = '${const.INTER_CROSSWORD}';
% if c.is_edit_hm or c.is_tr:
  var url="";
  if((command == 'crossword') && data)
    url="${h.url('ylesanne_sisuplokk_new_cwchar',ylesanne_id=c.item.ylesanne_id,sisuplokk_id=c.item.id,lang=c.lang,data='__DATA__')}";
  else if(kood)
    url="${h.url('ylesanne_sisuplokk_edit_kysimus',id='__KOOD__',ylesanne_id=c.item.ylesanne_id,sisuplokk_id=c.item.id,lang=c.lang,tyyp='__TYYP__',data='__DATA__',is_tr=c.is_tr)}";
  else
    url="${h.url('ylesanne_sisuplokk_new_kysimus',ylesanne_id=c.item.ylesanne_id,sisuplokk_id=c.item.id,lang=c.lang,tyyp='__TYYP__',data='__DATA__')}";

% else:
  var url="${h.url('ylesanne_sisuplokk_kysimus',id='__KOOD__', ylesanne_id=c.item.ylesanne_id,sisuplokk_id=c.item.id,lang=c.lang,tyyp='__TYYP__',data='__DATA__')}";
% endif
% if c.block.tyyp == const.INTER_PUNKT:
  url="${h.url('ylesanne_sisuplokk_edit_kysimus',id='__KOOD__',ylesanne_id=c.item.ylesanne_id,sisuplokk_id=c.item.id,lang=c.lang,tyyp='__TYYP__',data='__DATA__', is_tr=c.is_tr)}";
  url += '&kood2='+kood;
  ## container on editori element, mille järgi leiame kysimuse ID
  kood = $(container).closest('tr').find('span.kysimus-kood').attr('data-kood');
  if(!kood)
     return;
% endif

data = (data ? encodeURIComponent(data) : '');
  url = url.replace('__TYYP__',tyyp).replace('__DATA__',data).replace('__KOOD__',kood);
  if(command == 'crossword')
  {
     url = url + '&l.pos_x=' + pos_x + '&l.pos_y=' + pos_y;
  }
  else if(command == 'gapmath')
  {
     url = url + '&basetype=math';
  }
  return url;
}
function is_kood_inuse(kood)
{
<%
   koodid = [t.kood for t in c.ylesanne.tulemused]
   for p in c.ylesanne.sisuplokid:
     koodid = koodid + [k.kood for k in p.kysimused]
%>
var koodid = [${','.join(map(lambda k: "'%s'" % k, koodid))}];
return(koodid.indexOf(kood) != -1);
}

% if c.is_edit or c.is_tr:
## ckeditoris pildi ja audio viitamiseks võimalikud loetelud
<%
  q = (model.SessionR.query(model.Meediaobjekt.filename)
       .join(model.Meediaobjekt.sisuplokk)
       .filter(model.Sisuplokk.ylesanne_id==c.ylesanne.id)
       .filter(model.Sisuplokk.tyyp==const.BLOCK_MEDIA)
       .filter(model.Meediaobjekt.fileversion!=None)
       .filter(model.Meediaobjekt.mimetype.like('audio/%'))
       .order_by(model.Meediaobjekt.filename))
  li_audio = [[fn, 'images/%s' % fn] for fn, in q.all()]
  q = (model.SessionR.query(model.Piltobjekt.filename)
       .join(model.Piltobjekt.sisuplokk)
       .filter(model.Sisuplokk.ylesanne_id==c.ylesanne.id)
       .filter(model.Sisuplokk.tyyp==const.BLOCK_IMAGE)
       .filter(model.Piltobjekt.fileversion!=None)
       .order_by(model.Piltobjekt.filename))
  li_img = [[fn, 'images/%s' % fn] for fn, in q.all()]  
%>
var task_audio_list = ${model.json.dumps(li_audio)};
var task_img_list = ${model.json.dumps(li_img)};
% endif
</script>
