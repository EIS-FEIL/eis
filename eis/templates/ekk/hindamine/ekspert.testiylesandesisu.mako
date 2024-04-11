## Testiosa hindamine
<%inherit file="/avalik/khindamine/testiylesandesisu.mako"/>

<%def name="after_item(vy, vastus)">
% if not c.on_kriteeriumid:
   ${h.hidden('%s.ty_id' % c.val_prefix, c.ty.id)}
   ${h.hidden('%s.vy_id' % c.val_prefix, c.vy.id)}
% if not c.ty.arvutihinnatav:
${self.ty_valuation(c.ty, c.ylesandevastus)}
${self.div_hindamine_manual(vy, vastus)}
% else:
${self.tbl_hindamine_ylesanne_total(c.ty, vy, vy.ylesanne, vastus)}
% endif
% endif

</%def>

<%def name="ty_valuation(ty, ylesandevastus)">
      <%
        # lahendaja vastus hindamise tabelis kuvamiseks
        c.responses = ylesandevastus.get_responses()
        # kui kasutaja on hindaja, siis leitakse õiged vastused
        c.correct_responses = c.ylesanne.correct_responses(ylesandevastus,
                                                       lang=c.lang,
                                                       naide_only=False,
                                                       hindaja=True,
                                                       naidistega=False)
      %>
        ## hindamiste tabel hindajale ning osade sisuplokkide korral ka õiged vastused või näidisvastused
        % for c.block in c.ylesanne.sisuplokid:      
          % if c.block.staatus != const.B_STAATUS_KEHTETU and not c.block.naide and c.block.is_interaction:
            ## plokk on nähtav, pole näidis ja on vastatav
            <%include file="/sisuplokk/valuation.mako"/>
          % endif
        % endfor
</%def>

<%def name="div_hindamine_manual(vy, vastus)">
   <%
   ty = vy.testiylesanne
   ylesanne = vy.ylesanne
   %>
   
   % if c.on_aspektid:
     ## hindamisaspektidega ylesanne
     ${self.tbl_hindamine_aspektid(ty, vy, ylesanne, c.val_prefix, vastus)}
   % endif

   ## nyyd sisestatakse veel ainult terve ylesande kohta käiv märkus
   ${self.tbl_hindamine_ylesanne_markus(ty, vy, ylesanne, c.val_prefix, vastus)}
</%def>

<%def name="tbl_hindamine_ylesanne_total(ty, vy, ylesanne, ylesandevastus)">
% if ylesandevastus and ylesandevastus.toorpunktid is not None:
   <table class="table vertmar table-align-top">
     <thead>
     <tr>
       <th></th>
       <th>${_("Toorpunktid")}</th>
       <th>${_("Max toorpunktid")}</th>
       <th>${_("Hindepallid")}</th>
       <th nowrap>${_("Max pallid")}</th>
     </tr>
     </thead>
     <tbody>
     <tr>
       <td><b>${_("Ülesande hindamine")}</b></td>
       <td>${h.fstr(ylesandevastus.toorpunktid)}
       </td>
       <td class="fh">
         % if ty.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
         ${h.fstr(ylesanne.max_pallid*2)}
         % else:
         ${h.fstr(ylesanne.max_pallid)}
         % endif
       </td>
       <td>${h.fstr(ylesandevastus.pallid)}</td>
       <td class="fh">${h.fstr(ty.max_pallid)}</td>
     </tr>
     </tbody>
   </table>
% endif
</%def>

<%def name="tbl_hindamine_ylesanne_markus(ty, vy, ylesanne, prefix, ylesandevastus)">
## ylesande märkused
   <table width="100%"  class="table vertmar">
     <caption>${_("Ülesande tulemus")}</caption>
     <thead>
     <tr>
       <th>${_("Liik")}</th>
       <th>${_("Hindaja")}</th>
       <th>${_("Toorpunktid")}</th>
       <th>${_("Max toorpunktid")}</th>
       <th>${_("Hindepallid")}</th>
       <th nowrap>${_("Max pallid")}</th>
       <th width="30%">${_("Märkus")}</th>
     </tr>
     </thead>
     <tbody>
     % for hindamine in c.hindamised:
     <% 
        kasutaja = hindamine.hindaja_kasutaja 
        yhinne = hindamine.get_vy_ylesandehinne(vy.id) or None
     %>
     % if hindamine.loplik:
     <tr class="selected">
     % else:
     <tr>
     % endif
       <td>${hindamine.liik_nimi}
         % if hindamine.tyhistatud:
         (${_("tühistatud")})
         % endif
       </td>
       <td>
         % if kasutaja:
         ##${kasutaja.isikukood} 
         ${kasutaja.nimi} 
         % endif
         ${h.str_from_datetime(yhinne and yhinne.modified)}
         % if hindamine.staatus != const.H_STAATUS_HINNATUD:
         (${hindamine.staatus_nimi.lower()})
         % endif
         <!--hindamine ${hindamine.id}-->
       </td>
       <td>            
         % if yhinne and yhinne.toorpunktid is not None:
         ${h.fstr(yhinne.toorpunktid)}
##         % if ylesandevastus.toorpunktid_arvuti:
##         (+ ${h.fstr(ylesandevastus.toorpunktid_arvuti)})
##         % endif
         % endif
       </td>
       <td class="fh">${h.fstr(ylesanne.max_pallid)}</td>
       <td>
         % if yhinne and yhinne.pallid is not None:
         ${h.fstr(yhinne.pallid)}
           % if hindamine.liik >= const.HINDAJA4 and ty.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
           * 2
         % endif
##         % if ylesandevastus.pallid_arvuti:
##         (+ ${h.fstr(ylesandevastus.pallid_arvuti)})
##         % endif
         % endif
       </td>
       <td class="fh">
         % if ty.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
         ${h.fstr(ty.max_pallid/2.)}
         % else:
         ${h.fstr(ty.max_pallid)}
         % endif
       </td>
       <td>
         ${yhinne and yhinne.markus}
       </td>
     </tr>
     % endfor

     ## kehtiv tulemus
     % if ylesandevastus and ylesandevastus.toorpunktid is not None:
     <tr>
       <td colspan="2"><b>${_("Kehtiv tulemus")}</b></td>
       <td>${h.fstr(ylesandevastus.toorpunktid)}
       </td>
       <td class="fh">
         % if ty.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
         ${h.fstr(ylesanne.max_pallid*2)}
         % else:
         ${h.fstr(ylesanne.max_pallid)}
         % endif
       </td>
       <td>${h.fstr(ylesandevastus.pallid)}</td>
       <td class="fh">${h.fstr(ty.max_pallid)}</td>
       <td colspan="1">
       </td>
     </tr>
     % endif

  % if c.hindamine and (c.olen_ekspert or c.ettepanek or c.olen_hindaja6):
     ## minu eksperthindamine IV hindamisena 
     ## või vaide korral hindamise ettepanek
     <%
        kasutaja = c.user.get_kasutaja()
        yhinne = c.hindamine and c.hindamine.get_vy_ylesandehinne(vy.id) or None
     %>
     <tr>
       <td>${c.hindamine.liik_nimi} </td>
       <td>
         ##${kasutaja.isikukood} 
         ${kasutaja.nimi} 
         ${h.str_from_datetime(yhinne and yhinne.modified)}
       </td>
       <td>            
         <span class="val-total-tp">
         % if yhinne and yhinne.toorpunktid is not None:
           ${h.fstr(yhinne.toorpunktid)}
         % endif
         </span>
##         % if ylesandevastus.toorpunktid_arvuti:
##         (+ ${h.fstr(ylesandevastus.toorpunktid_arvuti)})
##         % endif
       </td>
       <td class="fh">${h.fstr(ylesanne.max_pallid)}</td>
       <td>
         % if yhinne and yhinne.pallid is not None:
         <span class="val-total-p">${h.fstr(yhinne.pallid)}</span> 
           % if ty.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
           * 2
           % endif
         % endif
##         % if ylesandevastus.toorpunktid_arvuti:
##         (+ ${h.fstr(ylesandevastus.pallid_arvuti)})
##         % endif
         <span class="val-koef" style="display:none">${vy.koefitsient}</span>
       </td>
       <td>
         % if ty.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
         ${h.fstr(ty.max_pallid/2.)}
         % else:
         ${h.fstr(ty.max_pallid)}
         % endif
       </td>
       <td>
         ${h.textarea('%s.markus' % prefix, yhinne and yhinne.markus, rows=2)}
       </td>
     </tr>
  % endif

  % if c.hindamine and c.toimumisaeg.testimiskord.tulemus_kinnitatud and c.ettepanek:
     ## vaide korral hindamiste läbivaatus,
     ## ekspertrühma liige saab teha märkuseid, kuid mitte anda hindepalle
     <%
        yhinne = c.hindamine and c.hindamine.get_vy_ylesandehinne(vy.id) or None
        minumarkus = None
     %>
     % if yhinne:
     ## teiste ekspertrühma liikmete märkused
       % for rcd in yhinne.ylesandehindemarkused:
         % if rcd.ekspert_labiviija.kasutaja_id == c.user.id and not c.ettepanek:
           <% minumarkus = rcd %>
         % else:
     <tr>
       <td>${_("Läbivaatus")}</td>
       <td>
         ${rcd.ekspert_labiviija.kasutaja.nimi}
       </td>
       <td colspan="5">
         ${rcd.markus}
       </td>
     </tr>
         % endif
       % endfor
     % endif

     % if not c.ettepanek:
     ## minu märkused
     <tr>
       <td>${_("Läbivaatus")}</td>
       <td>${c.user.fullname}</td>
       <td colspan="5">
         ${h.textarea('%s.markus' % prefix, minumarkus and minumarkus.markus, rows=2)}
       </td>
     </tr>
     % endif

  % endif
     </tbody>
   </table>
</%def>

<%def name="tbl_hindamine_aspektid(ty, vy, ylesanne, prefix, ylesandevastus)">
## Aspektidega ylesande pallide tabel
  <table width="100%"  class="table vertmar table-align-top">
     <caption>${_("Hindamine")}</caption>
     <thead>
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
     </thead>
     <tbody>
 % for n_ha, ha in enumerate(ylesanne.hindamisaspektid):
   <% 
    a_prefix = '%s.ha-%d' % (prefix, n_ha)
    vastusaspekt = ylesandevastus and ylesandevastus.get_vastusaspekt(ha.id)
    row_cnt = len(c.hindamised) + (vastusaspekt and vastusaspekt.toorpunktid is not None and 1 or 0)
    if c.hindamine and (c.olen_ekspert or c.ettepanek or c.olen_hindaja6):
      # aspektihindajate loetelule lisame iseend
      row_cnt += 1
    aspekt_printed = False
   %> 

     ## varasemad hindamised
     % for hindamine in c.hindamised:
       <% 
          kasutaja = hindamine.hindaja_kasutaja 
          yhinne = hindamine.get_vy_ylesandehinne(vy.id) or None
          aspektihinne = yhinne and yhinne.get_aspektihinne(ha.id) or None
       %>
     <tr>
       % if not aspekt_printed:
       <td rowspan="${row_cnt}">${ha.aspekt_nimi}
         <!-- ha ${ha.id} yv ${ylesandevastus and ylesandevastus.id} va ${vastusaspekt and vastusaspekt.id} hindamine ${hindamine.id} yh ${yhinne and yhinne.id} ah ${aspektihinne and aspektihinne.id} -->
       </td>
         <% aspekt_printed = True %>
       % endif
       <td>${hindamine.liik_nimi}</td>
       <td>
         % if kasutaja:
         ${kasutaja.nimi} 
         % endif
         ${h.str_from_datetime(yhinne and yhinne.modified)}
         % if hindamine.staatus != const.H_STAATUS_HINNATUD:
         (${hindamine.staatus_nimi.lower()})
         % endif
       </td>
       <td>${h.fstr(aspektihinne and aspektihinne.toorpunktid)}</td>
       <td class="fh">${h.fstr(ha.max_pallid)}</td>
       <td class="fh">${h.fstr(ha.kaal)}</td>
       <td>${aspektihinne and aspektihinne.nullipohj_nimi}</td>
       <td>${aspektihinne and aspektihinne.markus or ''}</td>
     </tr>
     % endfor

     ## kehtiv tulemus
     % if vastusaspekt and vastusaspekt.toorpunktid is not None:
     <tr>
       % if not aspekt_printed:
       <td rowspan="${row_cnt}">${ha.aspekt_nimi}</td>
         <% aspekt_printed = True %>
       % endif
       <td colspan="2"><b>${_("Kehtiv tulemus")}</b></td>
       <td>
         ${h.fstr(vastusaspekt.toorpunktid)}
         % if c.hindamine and (c.olen_ekspert or c.olen_hindaja6):
         ${h.button(_("Jäta samaks"), onclick="approve_points('%s.toorpunktid', '%s')" % (a_prefix, h.fstr(vastusaspekt.toorpunktid)), level=2)}
         % endif
       </td>
       <td class="fh">
         % if ty.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
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
        yhinne = c.hindamine.get_vy_ylesandehinne(vy.id) or None
        aspektihinne = yhinne and yhinne.get_aspektihinne(ha.id) or None
     %>
     <tr>
       % if not aspekt_printed:
       <td rowspan="${row_cnt}">${ha.aspekt_nimi}</td>
         <% aspekt_printed = True %>
       % endif
       <td>${c.hindamine.liik_nimi}</td>
       <td>
         ##${kasutaja.isikukood} 
         ${kasutaja.nimi}          
         ${h.str_from_datetime(aspektihinne and aspektihinne.modified)}
       </td>
       <td>
         % if ylesandevastus and ylesandevastus.mittekasitsi:
         ${h.hidden('%s.toorpunktid' % a_prefix, '0')}
         0
         % else:
         ${h.float5('%s.toorpunktid' % a_prefix, aspektihinne and aspektihinne.s_toorpunktid, class_="val-tp",
         maxvalue=ha.max_pallid)}
         % endif
         ${h.hidden('%s.a_kood' % a_prefix, ha.aspekt_kood)}
       </td>
       <td class="fh">${h.fstr(ha.max_pallid)}</td>
       <td class="fh">${h.fstr(ha.kaal)}</td>       
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
         opt_nullipohj, wide=False,
         disabled=not aspektihinne or not aspektihinne.toorpunktid==0)}
         % endif
       </td>
       <td>
         ${h.textarea('%s.markus' % a_prefix, aspektihinne and aspektihinne.markus, rows=2)}
       </td>
     </tr>
  % endif

 % endfor
     </tbody>
  </table>
</%def>

