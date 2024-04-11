<%inherit file="/avalik/lahendamine/esitlus.mako"/>

<%def name="gen_submit_url()">
<% c.submit_url = h.url_current('updatetask', ty_id=c.ty.id, vy_id=c.vy.id, ylesanne_id=c.ylesanne.id) %>
</%def>

<%def name="outside_contents()">
## erakorraline teade
## sisu lisatakse kohe genereerimisel või hiljem after_save_json() sees
## peale sisu tekkimist tõstab test.js selle lehe päisesse oma kohale
<% modified, sisu = c.user.get_emergency() %>
% if modified:
<div class="content-emergency" style="display:none" data-modified="${modified}">
  ${sisu}
</div>
% endif
## ülesande päis ja andmete hoiustamise koht
<div id="testtys1"
     % if c.ty.seq == 1:
     data-varianty1a1="A${c.ty.alatest_id or ''}"
     % endif
     % if not c.read_only and c.ty.ise_jargmisele:
     class="forcenext"
     % endif
     style="display:none">
${self.ty_heading(c.ty, c.ylesandevastus)}
${self.ty_valik(c.ty, c.ylesandevastus)}
${self.before_item()}
<div class="tools d-flex justify-content-end"></div>
</div>
## ülesande jalus
<div id="testtys2" style="display:none">
${self.after_item(c.vy, c.ylesandevastus)}
</div>
</%def>

<%def name="ty_heading(ty, ylesandevastus)">

<div class="d-flex align-items-center">
  % if not c.testiosa.peida_yl_pealkiri:
  <% ty_nimi = c.testiosa.kuva_yl_nimetus and ty.nimi %>
  <h5 class="mb-1">
  % if ty_nimi:
  ${ty_nimi}
  % elif c.alatest and not c.alatest.yl_segamini or not c.alatest and not c.testiosa.yl_segamini:
  ## kui pole segatud jrk
  ${ty.liik_nimi} ${ty.tahis}
  % else:
  ## kui on segatud jrk
  ${ty.liik_nimi}
  % endif
  </h5>
  % endif
     <div class="form-group mr-3 d-flex justify-content-end align-items-center ml-auto">
       <strong>
            <% yvb = ylesandevastus %>
             % if ty.liik == const.TY_LIIK_Y:
             <%
                ty_max_pallid = ty.max_pallid
                if ty_max_pallid is None and c.ylesanne:
                   ty_max_pallid = c.ylesanne.max_pallid
             %>
             % if ylesandevastus and c.showres and c.test.arvutihinde_naitamine:
             ${yvb.get_tulemus_eraldi()}
             % elif ylesandevastus and ylesandevastus.pallid is not None and c.showres:
             ${_("Tulemus")}: ${yvb.get_tulemus()}
             % elif c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH and ty.naita_max_p and ty_max_pallid != None:
             ${_("max {p}p").format(p=h.fstr(ty_max_pallid))}
             % endif
             % endif
             
             % if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH and ylesandevastus and c.read_only:
             % if ylesandevastus.ajakulu != None:
             <div>
               ${_("Aeg {s} sekundit").format(s=ylesandevastus.ajakulu)}
             </div>
             % endif
             % endif
           </strong>
     </div>
   ${self.time_limit_task(ty, ylesandevastus)}

</div>

     % if ylesandevastus and ylesandevastus.pallid is not None and c.showres:
       % for hinne in ylesandevastus.ylesandehinded:
         %  if hinne.markus:
   ${h.alert_notice('<i>' + _("Hindaja märkus.") + '</i> ' + hinne.markus)}
         % endif
       % endfor
     % endif
% if ty.on_valikylesanne:
  ${ty.sooritajajuhend}
% endif
</%def>

<%def name="ty_valik(ty, ylesandevastus)">
<%
   pealkirjad = (ty.pealkiri or '').split('\n')
   on_valikud = ty.on_valikylesanne and not ty.valik_auto
%>
% if on_valikud:
<%
  valitudylesanded = c.vyy or [vy for vy in ty.valitudylesanded]
%>
  <div class="rounded border px-4 py-1">
  % for seq, vy in enumerate(valitudylesanded):
          <div class="my-2">
            <%
              pealkiri = len(pealkirjad) > seq and pealkirjad[seq]
              label = pealkiri or _("VALIKÜLESANNE {n}").format(n=seq+1)
            %>
             ${h.radio('valik', vy.id, checked=vy.id == c.vy.id,
                       ronly=c.read_only, class_="vyvalik",
                       label=label, onclick="change_vyvalik()")}
          </div>
  % endfor
  </div>
% endif
</%def>

<%def name="time_limit_task(ty, ylesandevastus)">                
% if not c.read_only and (ty.piiraeg or ty.min_aeg):
     <div class="form-group mr-3 d-flex justify-content-end align-items-center ml-auto">
<%
  l_min = ty.min_aeg
  l_max = ty.piiraeg
  l_kulutatud = ylesandevastus and ylesandevastus.ajakulu or 0
  l_hoiatus = ty.hoiatusaeg
  showsec = ty.piiraeg_sek and 'true' or ''
%>
  % if l_max:
  <% l_jaanud_max = max(0, l_max - l_kulutatud) %>
       <label class="mr-3 mb-0">${_("Ülesande max aeg")}:
         ${h.str2_from_timedelta(l_max)}
       </label>
       <div class="circle-wrap countdown-ty" limit="${l_max}" leftmax="${l_jaanud_max}" warntime="${l_hoiatus}" showsec="${showsec}">
         <span class="countdown-warn-msg" style="display:none">
           ${_("Ülesande lahendamiseks on jäänud veel alla {0} minuti")}
         </span>
       </div>
  % endif
  % if l_min:
     ## on olemas min piiraeg
     <% l_jaanud_min = max(0, l_min and (l_min - l_kulutatud) or 0) %>
     % if l_jaanud_min:
         <span class="min_aeg-ty" style="display:none" leftmin="${l_jaanud_min}"></span>
     % endif
  % endif
     </div>
% endif
</%def>

<%def name="ty_skann(ty, ylesandevastus)">
% if c.prepare_correct and c.ylesandevastus and c.ylesandevastus.skann:
<div class="my-1">
      ${h.image(h.url('tulemus_yvskann', sooritus_id=c.sooritus_id,
      id=c.ylesandevastus_id), width=c.ylesandevastus.laius_orig and c.ylesandevastus.laius_orig/4)}
</div>
% endif
</%def>

<%def name="before_item()">
## vajadusel kirjutatakse üle
</%def>

<%def name="after_item(vy, ylesandevastus)">
## hindamise korral kirjutatakse üle
</%def>

<%def name="countdown_reset()">
## taimerite muutmine, kui testi sooritamise ajal on serveris piiraega muudetud
## TODO
% if 0 and c.sooritus_piiraeg_muutus:
<script>
<%
  l_max, l_ajakulu, l_left_max = c.sooritus.get_piiraeg(c.testiosa)
  showsec = c.testiosa.piiraeg_sek and 'true' or 'false'
%>
% if l_max:
var el = parent.$('#countdown_testiosa');
el.find('.countdown-max').text("${h.str2_from_timedelta(l_max)}");
parent.CountDownA_reset(el.attr('id'), {limit: ${l_max}, leftmax: ${l_left_max}, show_seconds: ${showsec}});
% endif
% if c.alatest:
<%
  atos = c.alatestisooritus or c.sooritus.give_alatestisooritus(c.alatest.id)
  alatest = atos.alatest
  showsec = alatest.piiraeg_sek and 'true' or 'false'
  l_max, l_ajakulu, l_left_max = atos.get_piiraeg(alatest)
%>
% if l_max:
var el = parent.$('#countdown_alatest');
el.find('.countdown-max').text("${h.str2_from_timedelta(l_max)}");
parent.CountDownA_reset(el.attr('id'), {limit: ${l_max}, leftmax: ${l_left_max}, show_seconds: ${showsec}});
% endif
% endif
var fld = '<input type="hidden" name="cdupd" value="${c.sooritus.piiraeg_muutus}"/>';
$(fld).appendTo($('form#form_save_y_responses'));
</script>
% endif
</%def>

${self.countdown_reset()}

