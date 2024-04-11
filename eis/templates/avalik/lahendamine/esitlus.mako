<!DOCTYPE html>
<html lang="${request.locale_name}" translate="no">
<head>
  % if c.google_gtm:
  <%include file="/common/google_gtm.head.mako"/>
  % endif
  <meta charset="UTF-8" />
  <meta http-equiv="Pragma" content="no-cache"/>
  <meta http-equiv="Expires" content="-1"/>
  <base href="${h.url_current('showtask')}/${c.ylesanne.id}/">
  <%
    c.on_esitlus = True
    c.include_responsivevoice = c.ylesanne.konesyntees and c.lang == 'ru'
    c.disain_ver = c.ylesanne.disain_ver
  %>
  <%include file="/common/include.mako"/>
  % if c.block_correct:
  <title>${_("Õige vastus")}</title>
  % endif
  ${c.head}
  <% on_rtf_shared = c.includes.get('ckeditor') and c.ylesanne.get_on_rtf_shared() %>
  % if on_rtf_shared and c.is_edit and not c.read_only:
  ## lahendamise korral kuvame algselt nupurea dialoogiaknas
  ## ootame ära, kui CKEDITOR on valmis, sest siis on nupurea suurus teada
  <script>
    CKEDITOR.on("instanceReady", function(event){
       init_ckeditor_top();
    });
  </script>
  % endif
  % if c.ylesanne.konesyntees:
  <script>
    $(document).ready(add_speech_icons);
  </script>
  % endif
  % if c.is_edit and not c.read_only:
  <script>
  ## tyhistame ajaloo, et ei saaks back-nupuga ära minna
  if(window.parent.document.getElementsByClassName('in-write').length)
    if(history.pushState){history.pushState(null, null, document.URL);
       window.addEventListener('popstate', function () { history.pushState(null, null, document.URL); });  }
  </script>
  % endif
  <%
    bodykw = ''
    if c.ty:
       bodykw = f' data-tyid="{c.ty.id}"'
    if c.ylesanne.lahendada_lopuni:
       bodykw += ' data-lopuni="true"'
    if c.read_only and c.refresh_showtask_url:
       bodykw += ' data-refresh-url="' + c.refresh_showtask_url + '"'
  %>
</head>
% if c.block_correct:
<body class="correct-response">
% else:
<body style="background:#fff" ${bodykw}>
% endif
% if c.google_gtm:
<%include file="/common/google_gtm.body.mako"/>  
% endif
<div class="tools d-flex justify-content-end"></div>
</div>

<%def name="outside_contents()">
<div id="testtys1" style="display:none">
</div>
<div id="testtys2" style="display:none">
</div>
</%def>
${self.outside_contents()}

<%def name="countdown_reset()">
</%def>

% if on_rtf_shared:
<%include file="esitlus_ckeditor_help.mako"/>

% if c.is_edit and not c.read_only:
<div style="float:right;" id="y_ckeditor_top_dock">
% if c.ES96 or True:
    <div id="y_ckeditor_ttop" style="float:left;padding:4px;z-index:10;display:none;">
% else:
    <div id="y_ckeditor_ttop" style="float:left;padding:4px;z-index:10;">
% endif
      <div id="y_ckeditor_top" style="float:left">
      </div>
% if c.ckeditor_help:
      <div style="float:left;margin:10px;">
        <a class="help" onclick="open_dialog({'contents_elem': $('div.nupuriba-help'), 'title:'Nupurea juhend'})">
          <img src="/static/images/abi7.gif" width="16px" alt="${_("Abiinfo")}" border="0"/>
        </a>
      </div>
% endif
      <div style="float:right;padding:2px 2px 5px 13px">
% if c.ES96 or True:
        <div class="xclose" onclick="$('#y_ckeditor_ttop').hide()">&times</div>        
% else:
        <div class="ckeditor-undock">
        ${h.checkbox('y_dock', 1, checked=True, title=_("Nupurea lukustamine"), onclick="ckeditor_top_undock()")}
        </div>
        <div class="xclose ckeditor-dock" onclick="ckeditor_top_dock()">&times</div>
% endif
      </div>
    </div>
</div>
% endif

% if c.ckeditor_help:
<div class="nupuriba-help" style="display:none;">
  ${c.ckeditor_help}
</div>
% endif

% endif

<%
  classes = 'ylesanne esitlus-body'
  if c.ylesanne.paanide_arv == 2:
     classes += ' width-1800'
  if c.is_test:
     classes += ' eis-test'
%>
<div class="${classes}">
% if c.read_only and c.btn_correct:
<div class="text-right m-1">
  <% href = h.url_current('correct', task_id=c.ylesanne.id, yv_id=c.ylesandevastus and c.ylesandevastus.id or None, lang=c.lang, kl_id=c.klaster_id) %>
${h.button(_("Näita õiget vastust"), id="show_correct", level=2, href=href)}
<script>
  $('button#show_correct').click(function(){
top.window.open_dlg({dialog_id:'correct', title:'${_("Õige vastus")}', iframe_url:$(this).attr('href'), force:true, autosize:true});
   });
</script>
</div>
% endif
<span tabindex="1"></span>
<%
  lahendusjuhis = c.ylesanne.lahendusjuhis
  juhis = lahendusjuhis and lahendusjuhis.tran(c.lang).juhis
%>
% if juhis:
<div class="juhis-box">${h.literal(juhis)}</div>
% endif 

<%def name="gen_submit_url()">
<% c.submit_url = '' %>
</%def>

% if not c.read_only:
<%  
  # kas ylesandelt lahkumine peab toimuma jsonis (et saaks tagasisidet kuvada)
  form_kw = {}
  if c.ylesanne.yl_tagasiside or c.ylesanne.normipunktid:
     form_kw['data-nextjson'] = 'true'
  self.gen_submit_url()
%>
${h.form(url=c.submit_url, id="form_save_y_responses", multipart=True, method='post', autocomplete='off', **form_kw)}
${h.hidden('lang', c.lang)}
## jooksva ylesande ID krati jaoks (URLi sees on ka)
${h.hidden('ylesanne_id', c.ylesanne.id)}
${h.hidden('datatype', '')}
% if c.ty:
${h.hidden('ty_tahis', c.ty.tahis)}
% endif
${h.hidden('yv_id', c.ylesandevastus and c.ylesandevastus.id or '')}
## ptyid - d-testis praeguse põhiylesande ID, mille juures on lahendamise jrk
% if c.ptyid:
${h.hidden('ptyid', c.ptyid)}
% endif
## sop - miks salvestatakse
${h.hidden('sop', '')}
## järgmine ylesanne
${h.hidden('n_ty_id', '')}
## klikiloenduri ajaarvestus (vt vbtimer)
${h.hidden('vbloadtm','')}
${h.hidden('vbsavetm','')}
## kas kõik kohustuslikud kysimused said vastatud
${h.hidden('finished', c.ylesandevastus and c.ylesandevastus.lopetatud and '1' or '0')}
## edasi kantud eelnevate ylesannete vastused
% for key in c.eelnevad or {}:
${h.hidden('eelnevad.%s' % key, c.eelnevad[key])}
% endfor
% endif
${c.body}

% if c.on_hindamine and c.ylesanne.fixkoord:
<div class="y-hinded"></div>
<script>
  $('.y-hinded').append($('a.hinded'));
</script>
% endif

% if not c.read_only:
${self.countdown_reset()}
${h.end_form()}
## osaliselt vastuste saatmise vorm (vt test.js)
${h.form(url=c.submit_url, id="form_autosave", multipart=True, method='post', style="display:none")}
${h.end_form()}
% endif

## õpipädevuse dialoog "Kas soovid edasi mõtelda", kui vastamist ei alustata piisavalt kiiresti 
% if not c.read_only and c.ylesanne.dlgop_aeg and c.ylesanne.dlgop_tekst and c.ylesanne.dlgop_ei_edasi:
<div class="dlgop-contents" data-ei_edasi="${c.ylesanne.dlgop_ei_edasi}" data-sec="${c.ylesanne.dlgop_aeg}" style="display:none">
  ${c.ylesanne.tran(c.lang).dlgop_tekst}
</div>
% endif

</div>
<div style="display:none;" class="y-tools">
  <%include file="/avalik/lahendamine/tools.mako"/>
</div>
</body>
</html>
