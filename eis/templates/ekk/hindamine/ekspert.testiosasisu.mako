## Testiosa hindamine
<%inherit file="/avalik/khindamine/testiosasisu.mako"/>

<%def name="next_form()">
</%def>

<%def name="task_contents(sooritusylesanded, komplekt)">
<div>
% if len(c.testiosa.hindamiskogumid) == 0 or c.hindamiskogum:
      % for n_ty, syl in enumerate(sooritusylesanded):
      ${self.testiylesandesisu_inc((n_ty, syl, komplekt))}
      % endfor
      ${self.js_punktid()}
% endif
<script>
function approve_points(name, value)
{
## jäta pallid muutmata
$('input[name="'+name+'"]').val(value).change();
}
</script>
</div>
</%def>

<%def name="testiylesandesisu_inc(tys_params)">
<% c.tys_params = tys_params %>
<%include file="ekspert.testiylesandesisu.mako"/>
</%def>

<%def name="footer_buttons()">
<br/>

% if c.hindamine and c.hindamiskogum:
  % if c.olen_ekspert or c.olen_hindaja6:
${h.submit(_("Lõpeta hindamine"), id='lopeta')}
${h.submit(_("Peata hindamine"), id='peata')}
  % elif c.ekspert_labiviija:
${h.submit(_("Salvesta"))}
${h.submit(_("Märgi läbivaadatuks"), id='labi')}
  % endif
% endif

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

