<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Suulise vastamise intervjuu")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Intervjuu läbiviimine"), h.url('svastamised'))} 
${h.crumb(c.test.nimi + ', ' + c.testiruum.testikoht.koht.nimi + ' ' + (c.testiruum.tahis or ''),
h.url('svastamine_vastajad', testiruum_id=c.testiruum.id))} 
${h.crumb(_("Intervjuu"))}
</%def>

<%def name="require()">
<%
  c.includes['audiorecorder'] = True 
  c.includes['subtabs'] = True
  c.includes['test'] = c.includes['spectrum'] = True 
  c.includes['math'] = True
%>
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%namespace name="audiorecorder" file='/sisuplokk/audiorecorder.mako'/>
% if c.sooritused:
<h1>${_("Intervjuu")}</h1>
% else:
<h1>${_("Heli salvestamise kontroll")}</h1>
% endif
<%
  c.testikoht = c.testiruum.testikoht
  c.toimumisaeg = c.testikoht.toimumisaeg
  c.sooritused_id = [tos.id for tos in c.sooritused]
  c.s_sooritused_id = ','.join(map(str, c.sooritused_id))
  c.sooritajate_nimed = [(tos.id, tos.sooritaja.nimi) for tos in c.sooritused]
%>

% if c.sooritused:
${self.search_form()}
% endif

${h.form_save(None)}
% if not c.sooritused:
<div style="min-height:200px">
  ${self.audiofiles(0,0,0)}
</div>
% elif not c.komplekt:
${h.alert_notice(_("Palun vali ülesandekomplekt!"), False)}
% else:
${self.punktitabel()}
% endif

<div class="d-flex flex-wrap mt-3">
  <div class="flex-grow-1">
    ${h.btn_back(url=h.url('svastamine_vastajad', testiruum_id=c.testiruum.id))}
  </div>
  % if c.komplekt and c.sooritused:
  ${h.submit(_("Katkesta intervjuu"), name='katkesta')}
  ${h.submit(_("Lõpeta intervjuu"), name='lopeta')}
  % endif
</div>
${h.end_form()}


<%def name="search_form()">
${h.form_search()}

<div class="question-status d-flex flex-wrap justify-content-between">
  <div class="item mr-5 mb-2">
    ${h.flb(_("Test"),'test_nimi')}
    <div id="test_nimi">
      ${c.test.nimi}
      ${c.testiosa.tahis}
    </div>
  </div>
  <div class="item mr-5 mb-2">
    ${h.flb(_("Soorituskoht"), 'koht_nimi')}
    <div id="koht_nimi">
      ${c.testikoht.koht.nimi}
      ${c.testiruum.tahis}
    </div>
  </div>
  <div class="item mr-5 mb-2">
    <% label = len(c.sooritused) == 1 and _("Sooritaja") or _("Sooritajad") %>
    ${h.flb(label, 'sooritajad')}
    <div id="sooritajad">
      % for tos in c.sooritused:
      ${self.sooritaja(tos)}
      % endfor
    </div>
  </div>

  % if len(c.alatestid_opt) > 0:
  <div class="item mr-5 mb-2">
    ${h.flb(_("Alatest"), 'alatest_id')}
    <div>
      % if len(c.alatestid_opt)> 1:
      ${h.select('alatest_id', c.alatest_id,
      c.alatestid_opt, onchange='this.form.submit()')}
      % else:
      ${c.alatestid_opt[0][1]}
      ${h.hidden('alatest_id', c.alatestid_opt[0][0])}
      % endif
    </div>
  </div>
  % endif
  <div class="item mr-5 mb-2">
    ${h.flb(_("Ülesandekomplekt"),'komplekt_id')}
    <div>
      % if len(c.opt_komplektid) == 1:
      ${c.opt_komplektid[0][1]}
      ${h.hidden('komplekt_id', c.komplekt_id)}
      % else:
      ${h.select('komplekt_id', c.komplekt_id, c.opt_komplektid, wide=False, empty=len(c.opt_komplektid)>1, 
      onchange='this.form.submit()')}
      % endif
    </div>
  </div>
</div>
${h.end_form()}

<div>
  ## helivastused, mis on yles laaditud ilma ylesandeta
  ${self.helivastused(None)}
</div>

</%def>

<%def name="sooritaja(tos)">
      <%
        # ülesannete keeleks võtame ühe sooritaja keele
        c.lang = tos.sooritaja.lang
      %>
      <div class="d-flex flex-wrap">
        <div>
          ${tos.tahised} ${tos.sooritaja.nimi}
          ${h.hidden('sooritus_id', tos.id)}
        </div>

        <% erivajadused = tos.get_str_erivajadused() %>
        % if erivajadused:
        <div>
          <a onclick="$('#erivajadused_${tos.id}').toggle()" class="px-3">
            ${_("Eritingimused")}
          </a>
          <span id="erivajadused_${tos.id}" style="display:none">
            ${erivajadused}
          </span>
        </div>
        % endif
      </div>
</%def>

<%def name="punktitabel()">
% for sooritus_id in c.sooritused_id:
${h.hidden('sooritus_id', sooritus_id)}
% endfor
${h.hidden('komplekt_id', c.komplekt.id)}

<% c.counter = -1 %>
<div>
  % for ty in c.testiylesanded:
     ${self.row_testiylesanne(ty)}
  % endfor
</div>

</%def>

<%def name="row_testiylesanne(ty)">
             % if not ty.on_valikylesanne:
                <% vy = ty.get_valitudylesanne(c.komplekt) %>
                  ${self.row_ylesanne(ty,vy)}
             % else:
                % for seq in range(1, ty.valikute_arv+1):
                  <% vy = ty.get_valitudylesanne(c.komplekt, seq=seq) %>
                  ${self.row_ylesanne(ty,vy)}
                % endfor
             % endif
</%def>

<%def name="row_ylesanne(ty,vy)">
 <%
     nimi = _("Ülesanne") + ' %s %s' % (ty.seq, ty.tran(c.lang).nimi)
 %>
 <div class="p-2 mb-1" style="border-bottom: 1px solid #f5f7f8;">
 % if not vy or not vy.ylesanne:
     ## komplekt valimata või ülesanne puudub komplektist
   <b>${nimi}</b>
   <!--ty_id=${ty.id}-->
 % else:
       <%
          ylesanne = vy.ylesanne
          ## testiylesannete loendur
          c.counter += 1 
          url_yl = h.url('khindamine_edit_lahendamine', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, indlg=True, inint=True)
       %>
       <div>
         <b>
           ${h.link_to_dlg(nimi, url_yl, title=nimi, size='lg')}
         </b>
       </div>
       ${self.audiofiles(ty.id, vy.id, vy.ylesanne_id)}
 % endif
 </div>
</%def>

<%def name="audiofiles(ty_id, vy_id, ylesanne_id)">
       <div class="audioparent m-1" data-y_id="${ylesanne_id}" data-ty_id="${ty_id}">
         ${audiorecorder.recorder('audio', 'audio_%s' % vy_id, 'mb-2')}
       </div>
       <div id="files_${ty_id}">
         ${self.helivastused(ty_id)}
       </div>
</%def>

<%def name="helivastused(ty_id)">
  % for hvf_id, in model.Helivastus.get_hvf_by_sooritus(c.sooritused_id, ty_id):
   <% c.helivastusfail = model.Helivastusfail.get(hvf_id) %>
   % if c.helivastusfail:
   <%include file="helivastus.mako"/>
   % endif
  % endfor
</%def>

<script>
var wnd_yl = null;
function popup_yl(url)
{
    wnd_yl = window.open(url, "wnd_yl", "toolbar=0,location=0,status=0,menubar=0,scrollbars=1");
}
## faili jrk nr
var last_recIndex = null; 

## funktsiooni kasutab web-audio-recorder-app/js/app.js
function response_changed(resultfield){
  dirty = true;
}
## heli salvestamine serveris
function custom_audio_fd(fd, asblock, recorder) {
 ## fd on FormData, millega kogutakse audiofaili salvestamisegax kaasa minevad andmed 
  fd.append('sub', 'file');
  var p = asblock.closest('.audioparent'), y_id = p.attr('data-y_id'), ty_id = p.attr('data-ty_id');
  fd.append('y_id', y_id);
  fd.append('ty_id', ty_id);
  fd.append('sooritused_id', "${c.s_sooritused_id}");
  var rec = recorder.rec,
      recIndex = recorder.recIndex;
  if(recorder.hvf_id && (recIndex == last_recIndex))
  {
     fd.append('hvf_id', recorder.hvf_id);
  }
  return {'fd': fd, 'action': "${h.url_current("create")}"};
}
function custom_audio_success(data, asblock, recorder) {
  var p = asblock.closest('.audioparent'), ty_id = p.attr('data-ty_id'), files = $('div#files_' + ty_id);
  var rec = recorder.rec,
      recIndex = recorder.recIndex;
  var hvf_div = $(data);
  var hvf_id = hvf_div.prop('id');
  ## kui diktofonis pole vahepeal uut faili alustatud,
  ## siis märgime andmebaasis salvestatud kirje ID diktofoni juurde
  if(recorder.recIndex == recIndex)
      recorder.hvf_id = hvf_id;
  ## kui faili on varem pausi ajal juba salvestatud,
  ## siis muudame olemasolevat, muidu lisame uue rea
  var old_div = files.find('.hvf[id="' + hvf_id + '"]');
  if(old_div.length)
      old_div.replaceWith(hvf_div);
  else
      files.append(hvf_div);
}
$('form#form_save').submit(function(){
## kui heli on serverisse salvestamata, siis salvestatakse
   if($('.asblock-audio.dirty').length)
   {
      alert_dialog("${_("Helifaili pole veel serverisse saadetud!")}");
      event.preventDefault();
      return false;
   }
});
</script>
