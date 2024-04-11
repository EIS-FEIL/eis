<%inherit file="/avalik/khindamine/hindamine.ylesanne.mako"/>


<script>
function approve_points(name, value)
{
## jäta pallid muutmata
$('input[name="'+name+'"]').val(value).change();
}
</script>

<%def name="testiylesandesisu()">
<% c.tys_params = (0, c.syl, c.komplekt) %>
<%include file="ekspert.testiylesandesisu.mako"/>
% if c.yv:
${self.audio_play_all()}
% endif
</%def>

<%def name="probleem()">

</%def>

<%def name="tbl_hindamine_kriteeriumid()">
## Hindamiskriteeriumitega hindamiskogumi pallide tabel
<%
  kriteeriumid = list(c.hindamiskogum.hindamiskriteeriumid)
  a_max_pallid = sum([kr.max_pallid for kr in kriteeriumid])
%>
  <table width="100%"  class="table vertmar table-align-top">
     <caption>${_("Hindamiskogumi hindamine hindamiskriteeriumite kaupa")}</caption>
     <tr>
       <th>${_("Aspekt")}</th>
       <th>${_("Liik")}</th>
       <th>${_("Hindaja")}</th>
       <th>${_("Toorpunktid")}</th>
       <th nowrap>${_("Max toorpunktid")}</th>
       <th>${_("Kaal")}</th>
       <th nowrap>${_("Null punkti põhjus")}</th>
       <th width="50%">${_("Märkus")}</th>
     </tr>
 % for n_ha, ha in enumerate(kriteeriumid):
   <% 
    a_prefix = 'kr-%d' % (n_ha)
    krvastus = c.sooritus.get_kriteeriumivastus(ha.id)
    row_cnt = len(c.hindamised) + (krvastus and krvastus.toorpunktid is not None and 1 or 0)
    if c.hindamine and (c.olen_ekspert or c.ettepanek or c.olen_hindaja6):
      # aspektihindajate loetelule lisame iseend
      row_cnt += 1
    aspekt_printed = False
   %> 

     ## varasemad hindamised
     % for hindamine in c.hindamised:
       <% 
          kasutaja = hindamine.hindaja_kasutaja 
          krhinne = hindamine.get_kriteeriumihinne(ha.id)
       %>
     <tr>
       % if not aspekt_printed:
       <td rowspan="${row_cnt}">${ha.aspekt_nimi}
         <!-- kr ${ha.id} krv ${krvastus and krvastus.id} hindamine ${hindamine.id} krh ${krhinne and krhinne.id} -->
       </td>
         <% aspekt_printed = True %>
       % endif
       <td>${hindamine.liik_nimi}</td>
       <td>
         % if kasutaja:
         ${kasutaja.nimi} 
         % endif
         ${h.str_from_datetime(krhinne and krhinne.modified)}
         % if hindamine.staatus != const.H_STAATUS_HINNATUD:
         (${hindamine.staatus_nimi.lower()})
         % endif
       </td>
       <td>${h.fstr(krhinne and krhinne.toorpunktid)}</td>
       <td class="fh">${h.fstr(ha.max_pallid)}</td>
       <td class="fh">${h.fstr(ha.kaal)}</td>
       <td>${krhinne and krhinne.nullipohj_nimi}</td>
       <td>${krhinne and krhinne.markus or ''}</td>
     </tr>
     % endfor

     ## kehtiv tulemus
     % if krvastus and krvastus.toorpunktid is not None:
     <tr>
       % if not aspekt_printed:
       <td rowspan="${row_cnt}">${ha.aspekt_nimi}</td>
         <% aspekt_printed = True %>
       % endif
       <td colspan="2"><b>${_("Kehtiv tulemus")}</b></td>
       <td>
         ${h.fstr(krvastus.toorpunktid)}
         % if c.hindamine and (c.olen_ekspert or c.olen_hindaja6):
         ${h.button(_("Jäta samaks"), onclick="approve_points('%s.toorpunktid', '%s')" % (a_prefix, h.fstr(krvastus.toorpunktid)), level=2)}
         % endif
       </td>
       <td class="fh">
         % if c.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
         ${h.fstr(ha.max_pallid*2)}
         % else:
         ${h.fstr(ha.max_pallid)}
         % endif
       </td>
       <td class="fh">${h.fstr(ha.kaal)}</td>
       <td colspan="2">
       </td>
     </tr>
     % endif

  % if c.hindamine and (c.olen_ekspert or c.ettepanek or c.olen_hindaja6):
     ## minu IV eksperthindamise sisestamine
     ## või vaide korral hindamise ettepaneku sisestamine
     <%
        kasutaja = c.user.get_kasutaja()
        krhinne = c.hindamine.get_kriteeriumihinne(ha.id) or None
     %>
     <tr>
       % if not aspekt_printed:
       <td rowspan="${row_cnt}">${ha.aspekt_nimi}</td>
         <% aspekt_printed = True %>
       % endif
       <td>${c.hindamine.liik_nimi}</td>
       <td>
         ${kasutaja.nimi}          
         ${h.str_from_datetime(krhinne and krhinne.modified)}
       </td>
       <td>
         ${h.float5('%s.toorpunktid' % a_prefix, krhinne and krhinne.s_toorpunktid,
         maxvalue=ha.max_pallid)}
         ${h.hidden('%s.a_kood' % a_prefix, ha.aspekt_kood)}
       </td>
       <td class="fh">${h.fstr(ha.max_pallid)}</td>
       <td class="fh">${h.fstr(ha.kaal)}</td>       
       <td>
         <%
           bit = c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) and const.NULLIP_BIT_P or const.NULLIP_BIT_E
           defval = krhinne and krhinne.nullipohj_kood
           opt_nullipohj = c.opt.klread_kood('NULLIPOHJ', empty=True, vaikimisi=defval, bit=bit)
         %>
         
         ${h.select('%s.nullipohj_kood' % a_prefix, 
         krhinne and krhinne.nullipohj_kood, opt_nullipohj, wide=False,
         disabled=not krhinne or not krhinne.toorpunktid==0)}
       </td>
       <td>
         ${h.textarea('%s.markus' % a_prefix, krhinne and krhinne.markus, rows=2)}
       </td>
     </tr>
  % endif

 % endfor
  </table>
</%def>

<%def name="footer_buttons()">
<div class="m-2 d-flex flex-wrap justify-content-end">
<%
  disabled = not c.hindaja
  prev_ty_id = next_ty_id = prev_url = next_url = None
  found = False
  if c.ty:
     for ty_id in c.testiylesanded_id:
       if found:
          next_ty_id = ty_id
          break
       elif ty_id == c.ty.id:
          found = True
       else:
          prev_ty_id = ty_id
%>
  % if prev_ty_id:
  <div>
    ${h.button(_("Eelmine ülesanne"), id=f'prev_{prev_ty_id}', class_='prevty', mdicls='mdi-arrow-left-circle')}
  </div>
  % endif

  % if not (c.on_kriteeriumid and c.ty) and c.testiylesanded_id and c.hindamine:
    % if c.olen_ekspert or c.olen_hindaja6:
  <div>
    ${h.button(_("Lõpeta hindamine"), id='lopeta', class_='hbsave')}
  </div>
  <div>
    ${h.button(_("Salvesta"), id='peata', class_='hbsave')}
  </div>
  % elif c.ekspert_labiviija:
##  <div>
##    ${h.button(_("Salvesta"), id='peata', class_='hbsave')}
##  </div>
  <div>
    ${h.button(_("Märgi läbivaadatuks"), id='labi', class_='hbsave')}    
  </div>
    % endif
  % endif
  % if next_ty_id:
  <div>
    ${h.button(_("Järgmine ülesanne"), id=f'next_{next_ty_id}', class_='nextty', mdicls2='mdi-arrow-right-circle')}
  </div>
  % endif
</div>


<script>
  % if not c.on_kriteeriumid and c.hindamine:
  ## ei ole kriteeriumitega hindamiskogum ja toimub hindamine
  $('button.nextty,button.prevty,button.hbsave,button.nexth').click(function(){
    if(is_dblclick($(this)))
      return;
    var container = $('#hindamine_hk_div');
    var form = $('form#form_save_h');
    var iframe = $('iframe.hylesanne');
    copy_valuation_from_iframe(iframe, form);  
    var data = form.serialize() + '&op=' + this.id;
    dialog_load(form.attr('action'), data, 'post', container);
  });
  % elif not c.ty and c.hindamine:
  ## kriteeriumite salvestamine
  $('button.hbsave,button.nexth').click(function(){
    if(is_dblclick($(this)))
      return;
    var container = $('#hindamine_hk_div');
    var form = $('form#form_save_h');
    var data = form.serialize() + '&op=' + this.id;
    dialog_load(form.attr('action'), data, 'post', container);
  });
  % else:
  ## ylesande vahetamine
  $('button.nextty,button.prevty').click(function(){
    if(is_dblclick($(this)))
      return;
    var container = $('#hindamine_hk_div');
    var form = $('form#form_ty');
    var data = form.serialize() + '&op=' + this.id;
    dialog_load(form.attr('action'), data, 'get', container);
  });
  % endif
 
  % if c.ty:
  $('#h_navacc0 a.nav-link,#h_navacc1 a.nav-link').click(function(){
     ## kasutaja klikkis sakil
     var container = $('#hindamine_hk_div');
   % if c.on_kriteeriumid or not c.hindamine:
     ### siin ei salvestata (salvestatakse mujal kriteeriume või on ekspertvaatamine)
     var form = $('form#form_ty');
     var data = form.serialize() + '&op=' + this.id;
     dialog_load(form.attr('action'), data, 'get', container);
   % else:
     ## hindamise salvestamine
      var form = $('form#form_save_h');
      var iframe = $('iframe.hylesanne');
      copy_valuation_from_iframe(iframe, form);  
      var data = form.serialize() + '&op=' + this.id;
      dialog_load(form.attr('action'), data, 'post', container);
   % endif
      return false;
  });
  % endif
  % if not c.pole_hinnata:
  ${self.js_update_r_tabs()}
  % endif
</script>
</%def>
