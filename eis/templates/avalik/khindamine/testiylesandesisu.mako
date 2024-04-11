## Testiosa hindamine
${self.testiylesandesisu()}

<%def name="testiylesandesisu()">
<%
  ty = c.ty
  vy = c.vy
  vy_id = vy.id
  ylesandevastus = c.ylesandevastus
  ylesanne = c.vy.ylesanne
  ty_nimi = c.testiosa.kuva_yl_nimetus and ty.tran(c.lang).nimi or \
     (ty.liik_nimi + ' %s' % (ty_jrk or ''))
%>

<div class="div_ty" data-ty_tahis="${ty.tahis}">
  % if not c.ylesandevastus:
     ${h.alert_error(_("Pole sooritatud"), False)}
  % else:
   
   <div class="d-flex align-items-center">
     % if not c.testiosa.peida_yl_pealkiri:
     <h2 class="mb-1 h4">${ty_nimi}</h2>
     % endif
     <div class="form-group mr-3 d-flex justify-content-end align-items-center ml-auto">
             % if ty.liik == const.TY_LIIK_Y:
             <%
                ty_max_pallid = ty.max_pallid
                if ty_max_pallid is None and ylesanne:
                   ty_max_pallid = ylesanne.max_pallid
             %>
             <div class="mr-4 font-weight-bold">
             % if ylesandevastus and c.test.arvutihinde_naitamine:
             ${ylesandevastus.get_tulemus_eraldi()}
             % elif ylesandevastus and ylesandevastus.pallid is not None:
             ${_("Tulemus")}: ${ylesandevastus.get_tulemus()}
             % elif c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH and ty.naita_max_p:
             ${_("max {p}p").format(p=h.fstr(ty_max_pallid))}
             % endif
             </div>
             % endif
             
             % if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH and ylesandevastus:
             % if ylesandevastus.ajakulu != None:
             <div class="mr-4">
             ${_("Aeg")} ${ylesandevastus.ajakulu} ${_("sekundit")}
             </div>
             % endif
             % endif
     </div>
   </div>
     % if c.ty and c.app_ekk and c.ylesanne:
     <div style="font-size:small">
       ${_("Ülesande ID")}: ${c.ylesanne.id}
     </div>
     % endif

     % if ylesandevastus and ylesandevastus.pallid is not None:
       % for hinne in ylesandevastus.ylesandehinded:
         %  if hinne.markus:
   ${h.alert_notice('<i>' + _("Hindaja märkus.") + '</i> ' + hinne.markus)}
         % endif
       % endfor
     % endif

     ${self.task_contents(ty)}
   
     % if c.responded:
         <script>
           $(function(){
                 $('tr#ty${ty.id}.tr_ylesanne').addClass('saved');
                 $('tr#ty${ty.id}.tr_ylesanne').css({'background-color':'${c.unsaved_color}'}); // muudetud!
           });
         </script>
     % endif

   % endif     
 </div>
</%def>

<%def name="task_contents(ty)">
<%
  ## Lahendaja varem antud ja andmebaasis salvestatud vastuse kuvamine
  has_perm = not (c.read_only or c.preview) \
    or not c.ylesanne.salastatud and not (c.test.salastatud and c.test.testityyp == const.TESTITYYP_EKK) \
    or c.user.has_permission('ylesanded', const.BT_SHOW, obj=c.ylesanne) \
    or c.ylesanne.salastatud == const.SALASTATUD_SOORITATAV \
        and c.user.has_group(const.GRUPP_T_KORRALDAJA, c.test)
%>
  ${self.before_item()}

% if not has_perm:
   ${h.alert_error(_("Puudub ülesande vaatamise õigus"))}
% else:
<div class="testtys tools-null">
  <div class="testtys-before"></div>
  <%
    # ekk hindajavaates võib top akna URLis sooritus_id olla 0, seetõttu peab selle eraldi ette andma
    task_url = h.url_current('showtask', ty_id=ty.id, sooritus_id=c.sooritus.id)
    # siin iframe class ei või olla "ylesanne", muidu läheb
    # paremal ekraanipoolel oleva lahendamise iframega sassi
  %>
  <iframe class="hylesanne" src="${task_url}"
          onload="on_iframe_ylesanne_load(this)"
          width="100%" height="100px" scrolling="no" frameBorder="0"
          aria-label="${_("Ülesande sisu")}">
  </iframe>
  <div class="testtys-after"></div>
</div>
% endif
  ${self.after_item(c.vy, c.ylesandevastus)}
</%def>

<%def name="before_item()">
<%
   if not c.vy.ylesanne.arvutihinnatav:
     ## ylesannete loendur
     c.counter = 0
     ## kysimuste loendur ylesandes
     c.q_counter = 0
   ## hindamise väljade prefiks
   c.val_prefix = 'ty-0' 

   c.on_aspektid = c.vy.on_aspektid
   ## kas kuvada kysimuste hindamise väljad
   c.on_hindamine = True
   ## kas kuvada ülesande sees küsimuste koodid
   c.show_q_code = True

   ## hindaja antud hinne ylesandele
   c.yhinne = None
   if c.hindamine:
      if c.ylesandevastus:
         c.yhinne = c.hindamine.get_ylesandehinne(c.ylesandevastus)
      else:
         c.yhinne = c.hindamine.get_vy_ylesandehinne(c.vy.id)
   c.load_iframe = True
%>
</%def>

<%def name="after_item(vy, vastus)">
% if not c.on_kriteeriumid:
% if not vy.ylesanne.arvutihinnatav:
${self.div_hindamine_manual(vy, vastus)}
% endif
% if not c.hindamiskogum and c.yhinne:
## avaliku vaate hindamisel võimalus ylesanne probleemseks märkida
${self.yl_probleem()}
% endif
% endif
</%def>

<%def name="div_hindamine_manual(vy, vastus)">
 <%
   ty = vy.testiylesanne
   ylesanne = vy.ylesanne
   ty_divid = 'ty_%d_0' % (ty.id)
 %>
   ${h.hidden('%s.ty_id' % c.val_prefix, ty.id)}
   ${h.hidden('%s.vy_id' % c.val_prefix, vy.id)}
   ${h.hidden('%s.yv_id' % c.val_prefix, c.ylesandevastus and c.ylesandevastus.id or '')}
 
   % if c.on_aspektid:
     ## hindamisaspektidega ylesanne
     ${self.tbl_hindamine_aspektid(ty, vy, ylesanne, c.val_prefix, vastus)}
   % endif
   ## nyyd sisestatakse veel ainult terve ylesande kohta käiv märkus
   ${self.tbl_hindamine_ylesanne_total(ty, vy, ylesanne, c.val_prefix,vastus)}

     ## kui ylesande punktide sisestamist ei toimu, siis teeme hidden välja,
     ## mille juures vigu näidata (kui ylesande max punktide arv yletatakse)
   ${h.hidden('%s.toorpunktid' % c.val_prefix, c.yhinne and c.yhinne.toorpunktid_kasitsi)}
</%def>

<%def name="tbl_hindamine_ylesanne_total(ty, vy, ylesanne, prefix, ylesandevastus)">
## Aspektideta ylesande pallide tabel
<% 
   if ylesanne.arvutihinnatav:
      hinne = ylesandevastus
   else:
      hinne = c.yhinne 
%>
<table width="100%" class="table vertmar table-align-top">
  <thead>
  <tr>
    % if ylesandevastus.pallid_arvuti is not None:
    <th></th>
    % endif
    <th>${_("Toorpunktid kokku")}</th>
    <th>${_("Koefitsient")}</th>
    <th>${_("Hindepallid")}</th>
    % if ty.on_markus_sooritajale:
    <th>${_("Hindaja märkus sooritajale")}</th>
    % endif
  </tr>
  </thead>
  <tbody>
  <tr>
    % if ylesandevastus.pallid_arvuti is not None:
    <td width="100px">${_("Hindaja")}</td>
    % endif
    <td width="160px" class="val-total-tp">
      % if hinne and hinne.toorpunktid is not None:
      ${h.fstr(hinne.toorpunktid_kasitsi)}
      % endif
    </td>
    <td width="100px" class="val-koef">${h.fstr(vy.koefitsient)}</td>
    <td width="100px" class="val-total-p">
      % if hinne and hinne.pallid is not None:
      ${h.fstr(hinne.pallid_kasitsi)}
      % endif
    </td>
    % if ty.on_markus_sooritajale:
    <td>
      ${h.textarea('%s.markus' % prefix, c.yhinne and c.yhinne.markus, rows=3)}
    </td>
    % endif
  </tr>
  % if ylesandevastus.pallid_arvuti is not None:
  <tr>
    <td>${_("Arvutihinnatud")}</td>
    <td>${h.fstr(ylesandevastus.toorpunktid_arvuti)}</td>
    <td>${h.fstr(vy.koefitsient)}</td>
    <td>${h.fstr(ylesandevastus.pallid_arvuti)}</td>
    % if ty.on_markus_sooritajale:
    <td></td>
    % endif
  </tr>
  % endif
  </tbody>
</table>
</%def>


<%def name="tbl_hindamine_aspektid(ty, vy, ylesanne, prefix, ylesandevastus)">
## Aspektidega ylesande pallide tabel
   <% yhinne = c.yhinne %>
   <table width="100%"  class="table vertmar table-align-top">
     <caption>${_("Ülesande vastuse hindamine hindamisaspektide kaupa")}</caption>
     <thead>
     <tr>
       <th>${_("Aspekt")}</th>
       <th>${_("Toorpunktid")}</th>
       <th nowrap>${_("Max")}</th>
       <th>${_("Kaal")}</th>
       % if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) or c.test.aine_kood in c.opt.nullipained:
      <th nowrap>${_("Null punkti põhjus")}</th>
       % endif      
       % if ty.on_markus_sooritajale:
       <th width="50%">${_("Märkus sooritajale")}</th>
       % endif
     </tr>
     </thead>
     <%
       hindamisaspektid = list(ylesanne.hindamisaspektid)
       a_max_pallid = sum([ha.max_pallid for ha in hindamisaspektid])
       hide_kirj = len(hindamisaspektid) > 1
     %>
     % for n_ha, ha in enumerate(hindamisaspektid):
         <% 
           aspektihinne = yhinne and yhinne.get_aspektihinne(ha.id) or None
           a_prefix = '%s.ha-%d' % (prefix, n_ha)
           apunktid = aspektihinne and aspektihinne.toorpunktid or None
           ahinnatud0 = ylesandevastus and ylesandevastus.mittekasitsi
           punktikirjeldused = list(ha.punktikirjeldused)
         %>
     <tbody class="accordion">
     <tr class="tr-asp accordion-card" id="tr_asp_${ha.id}">
       <td>
         % if punktikirjeldused and hide_kirj:
         <div class="accordion-title">
           <button
             class="btn btn-link collapsed"
             type="button"
             data-toggle="collapse"
             data-target=".tr-pkirj-${ha.id}"
             aria-expanded="true"
             aria-controls=".tr-pkirj-${ha.id}">
             <span class="btn-label"><i class="mdi mdi-chevron-down"></i>
               ${ha.aspekt_nimi}
             </span>
           </button>
         </div>
         % else:
         ${ha.aspekt_nimi}
         % endif
       </td>
       <td>
         % if ahinnatud0:
         ${h.hidden('%s.toorpunktid' % a_prefix, '0')}
         0
         % else:
         ${h.float5('%s.toorpunktid' % a_prefix, aspektihinne and  aspektihinne.s_toorpunktid, 
         maxvalue=ha.max_pallid, data_pintervall=ha.pintervall, class_='val-tp asp-punktid')}
         % endif
         ${h.hidden('%s.a_kood' % a_prefix, ha.aspekt_kood)}
       </td>
       <td>${h.fstr(ha.max_pallid)}</td>
       <td class="val-kaal">${h.fstr(ha.kaal)}</td>
       % if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) or c.test.aine_kood in c.opt.nullipained:
       <td>
         % if ylesandevastus and ylesandevastus.mittekasitsi:
         ${h.hidden('%s.nullipohj_kood' % a_prefix, const.NULLIPOHJ_VASTAMATA)}
         ${_("Vastamata")} 
         % else:
         <%
           bit = c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) and const.NULLIP_BIT_P or const.NULLIP_BIT_E
           defval = aspektihinne and aspektihinne.nullipohj_kood
           opt_nullipohj = c.opt.klread_kood('NULLIPOHJ', empty=True, vaikimisi=defval, bit=bit)
         %>
         ${h.select('%s.nullipohj_kood' % a_prefix, 
         aspektihinne and aspektihinne.nullipohj_kood, 
         opt_nullipohj,
         wide=True,
         disabled=not aspektihinne or not aspektihinne.toorpunktid==0)}
         % endif
       </td>
       % endif
       % if ty.on_markus_sooritajale:
       <td>
         ${h.textarea('%s.markus' % a_prefix, aspektihinne and aspektihinne.markus, rows=2, class_='asp-markus')}
       </td>
       % endif
     </tr>
     <%
       if ha.pkirj_sooritajale:
          cbcls = 'asp-pkirj asp-pkirj-j'
       else:
          cbcls = 'asp-pkirj'
     %>    
     % for pk in punktikirjeldused:
     <tr class="tr-pkirj tr-pkirj-${ha.id} ${hide_kirj and 'collapse' or ''}" aria-labelledby="tr_asp_${ha.id}">
       <td class="pl-6">
         <% label = h.fstr(pk.punktid) + 'p' %>
         ${h.radio('%s.pkp' % a_prefix, h.fstr(pk.punktid), class_=cbcls,
         checked=pk.punktid == apunktid, disabled=ahinnatud0, label=label)}
       </td>
       <td colspan="4">
         % if pk.kirjeldus:
         <div class="pkirj-txt">${pk.kirjeldus.replace('\n', '<br/>')}</div>
         % endif
       </td>
     </tr>
     % endfor
     </tbody>
     % endfor
   </table>
</%def>

<%def name="yl_probleem()">
<div class="p-2">
  ${h.checkbox1('ty-0.on_probleem', 1, checked=c.yhinne.on_probleem, label=_("Probleem"), class_="y-on-probleem")}
  <span class="y-onprob">
  ${h.text('ty-0.probleem_varv', c.yhinne.probleem_varv or '#fee',
  style="display:none", class_='y-prob-spectrum')}
  </span>
  <div style="display:none" class="y-onprob">
    ${h.textarea('ty-0.probleem_sisu', c.yhinne.probleem_sisu)}
  </div>
   <script>
     var setprobl = function(){
        var checked = $('.y-on-probleem').prop('checked');
        $('.y-onprob').toggle(checked);
        var c = $('.y-prob-spectrum').val();
        c = (!checked ? 'initial' : c);
        $('#hindamine_hk_div .tab-pane').css('background-color', c);
     }
     $('input.y-on-probleem').click(setprobl);
     setprobl();
      
     $("input.y-prob-spectrum").spectrum({
      preferredFormat: "hex",
      showPalette: true,
      showPaletteOnly: true,
      ##showInput: true,
      hideAfterPaletteSelect: true,
      allowEmpty: true,
      palette: [
        ["#fee","#f6e3c7","#fafacf","#ccf2cc","#d3fcfc","#dee5fa","#fae9fa","#fce1e1"],
        ["#f4cccc","#fce5cd","#fff2cc","#d9ead3","#d0e0e3","#cfe2f3","#d9d2e9","#ead1dc"],
        ["#ea9999","#f9cb9c","#ffe599","#b6d7a8","#a2c4c9","#9fc5e8","#b4a7d6","#d5a6bd"],
        ["#e06666","#f6b26b","#ffd966","#93c47d","#76a5af","#6fa8dc","#8e7cc3","#c27ba0"],
    ]
      }).change(setprobl);
   </script>
</div>
</%def>
