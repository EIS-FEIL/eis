## Suulise sooritamise hindamine
<%inherit file="/avalik/shindamine/suulinesisu.mako"/>

<%def name="search_form()">
<%
  c.sooritused = [c.sooritus]
  c.sooritajate_nimed = [(tos.id, tos.sooritaja.nimi) for tos in c.sooritused] # vt helivastus.mako
  c.sooritused_id = [c.sooritus.id]
%>

${h.form_search()}
<div class="question-status d-flex flex-wrap justify-content-between">
  <div class="item mr-5 mb-2">
    <% label = len(c.sooritused) == 1 and _("Sooritaja") or _("Sooritajad") %>
    ${h.flb(label, 'sooritused')}
    <div id="sooritused">
      % for tos in c.sooritused:
      ${self.sooritaja(tos, False)}
      % endfor
    </div>
  </div>
</div>
${h.end_form()}

<div>
  ## helivastused, mis on yles laaditud ilma ylesandeta
  ${self.helivastused(None)}
</div>
</%def>
  
<%def name="save_form()">
<%
  c.counter = 0 
  c.submit_url = c.f_submit_url(c.ty and c.ty.id)
%>
${h.form(url=c.submit_url, id="form_save_responses", multipart=True,
method='post', autocomplete='off')}

% if not c.komplekt:
    ${h.alert_notice(_("Ülesandekomplekt on määramata!"), False)}
    <br/>
% elif not c.hindamiskogum:
    ${h.alert_notice(_("Palun vali hindamiskogum!"), False)}
% elif not len(c.hindamiskogum.testiylesanded):
    ${h.alert_notice(_("Hindamiskogumis ei ole ülesandeid"), False)}
% else:
    ${self.punktitabel()}

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">

  </div>
  % if c.hindamine and c.is_edit:
  ${h.submit_dlg(op='lopeta')}
  % endif
</div>
% endif
${h.end_form()}
</%def>


<%def name="row_ylesanne(ty,vy)">
 <%
     nimi = _("Ülesanne") + ' %s %s' % (ty.seq, ty.tran(c.lang).nimi)
 %>
 % if not vy or not vy.ylesanne:
            ## komplekt valimata või ülesanne puudub komplektist
        <tr>
          <td class="field-header">
            ${nimi}
            <!--ty_id=${ty.id}-->
          </td>
        </tr>
 % else:
       <%
          ylesanne = vy.ylesanne
          yv = c.sooritus.get_ylesandevastus(ty.id)
          ## testiylesannete loendur
          c.counter += 1 
       %>
        <tr>
         <td class="field-header">
            <% url_yl = h.url('hindamine_hindajavaade_edit_lahendamine', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, indlg=True) %>
            ${h.link_to_dlg(nimi, url_yl, title=nimi, size='lg')}
           <!--ty_id=${ty.id} vy_id=${vy.id}-->
         </td>

          % if len(ylesanne.hindamisaspektid) == 0:
         <td class="field-header">${_("Toorpunktid, max {p}p").format(p=h.fstr(ylesanne.max_pallid))}
         </td>
          % else:
            % for ha in ylesanne.hindamisaspektid:
         <td class="field-header">
           ${ha.aspekt_nimi},
           <% va = yv and yv.get_vastusaspekt(ha.id) %>
           ${_("max {p}p").format(p=h.fstr(ha.max_pallid))}
         </td>
            % endfor
          % endif
         <td class="field-header">${_("Hindepallid, max {p}p").format(p=h.fstr(ty.max_pallid))}
         </td>

         <td class="field-header" rowspan="2">
           <!--ty_id=${ty.id} vy_id=${vy.id}-->
           <div class="pt-2">
             ${self.helivastused(ty.id)}
           </div>
         </td>

        </tr>

    % if yv and yv.pallid is not None:
        ${self.tr_ylesanne_kehtiv_tulemus(ty, vy, ylesanne, yv)}
    % endif

    % for n_tos, tos in enumerate(c.items):
        ${self.tr_ylesanne_sooritus(ty, vy, ylesanne, n_tos, tos)}
    % endfor
 % endif
</%def>


<%def name="tr_ylesanne_kehtiv_tulemus(ty,vy, ylesanne, yv)">
        <tr>
         <td class="field-header">
           ${_("Kehtiv tulemus")}
         </td>

          % if len(ylesanne.hindamisaspektid) == 0:
         <td class="field-header">
           % if yv and yv.toorpunktid:
           ${h.fstr(yv.toorpunktid)}p
           % endif
         </td>
          % else:
            % for ha in ylesanne.hindamisaspektid:
         <td class="field-header">
           <% va = yv and yv.get_vastusaspekt(ha.id) %>
           % if va and va.toorpunktid:
           ${h.fstr(va.toorpunktid)}p
           % endif
         </td>
            % endfor
          % endif
         <td class="field-header">
           % if yv and yv.pallid:
           ${h.fstr(yv.pallid)}p
           % endif
         </td>
        </tr>
</%def>

<%def name="tr_ylesanne_sooritus(ty, vy, ylesanne, n_tos, tos)">
## yhe ylesande yhe sooritaja kõik hindamised

% for n_hindamine, hindamine in enumerate(c.hindamised):
        <% 
           yhinne = hindamine and hindamine.get_vy_ylesandehinne(vy.id) or None
           prefix = 'ty-%s.he%s' % (c.counter, n_hindamine)           
        %>
        <tr>
          <td>
            ${hindamine.liik_nimi}
            % if hindamine.hindaja_kasutaja:
            ${hindamine.hindaja_kasutaja.nimi}
            % endif
          </td>

          % if len(ylesanne.hindamisaspektid) == 0:
          <td nowrap>
            ${h.fstr(yhinne and yhinne.toorpunktid)}
            % if yhinne and yhinne.markus:
            <br/>${yhinne.markus}
            % endif
          </td>
          % else:
            % for n_ha, ha in enumerate(ylesanne.hindamisaspektid):
          <td>
            <% 
               aspektihinne = yhinne and yhinne.get_aspektihinne(ha.id) or None
               a_prefix = '%s.a%s' % (prefix, n_ha)
            %>
            ${h.fstr(aspektihinne and aspektihinne.toorpunktid)}
            % if aspektihinne and aspektihinne.markus:
            <br/>${aspektihinne.markus}
            % endif
          </td>
            % endfor
          % endif

          <td nowrap>
            % if yhinne:
            ${h.fstr(yhinne.pallid)}
              % if hindamine.liik >= const.HINDAJA4 and c.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
              * 2
              % endif
            % endif
          </td>
        </tr>
% endfor


% if c.hindamine and (c.olen_ekspert or c.ettepanek or c.olen_hindaja6):
     ## minu eksperthindamine IV hindamisena
     ## või vaide korral hindamise ettepaneku sisestamine
     <%
        kasutaja = c.user.get_kasutaja()
        yhinne = c.hindamine and c.hindamine.get_vy_ylesandehinne(vy.id) or None
        prefix = 'ty-%s' % (c.counter)

     %>
        <tr>
          <td>
            ${kasutaja.nimi}
            ${c.hindamine.liik_nimi}

            ${h.hidden('%s.ty_id' % prefix, ty.id)}
            ${h.hidden('%s.vy_id' % prefix, vy.id)}
          % if len(ylesanne.hindamisaspektid) > 0:
            ## veateadete koht
            ${h.hidden('%s.toorpunktid' % prefix, '')}
          % endif
          </td>

          % if len(ylesanne.hindamisaspektid) == 0:
          <td nowrap>
            ${h.float5('%s.toorpunktid' % prefix, yhinne and yhinne.s_toorpunktid, maxvalue=ylesanne.max_pallid)}
            ${h.button('', mdicls=yhinne and yhinne.markus and 'mdi-comment-text' or 'mdi-comment-text-outline', class_='notes_btn mdibtn', name=prefix, level=2)} 
            ${h.hidden('%s.markus' % prefix, yhinne and yhinne.markus)}
          </td>
          % else:
            % for n_ha, ha in enumerate(ylesanne.hindamisaspektid):
          <td>
            <% 
               aspektihinne = yhinne and yhinne.get_aspektihinne(ha.id) or None
               ha_prefix = '%s.ha-%d' % (prefix, n_ha)
            %>
            ${h.float5('%s.toorpunktid' % ha_prefix, aspektihinne and aspektihinne.s_toorpunktid, maxvalue=ha.max_pallid)}
            ${h.button('', mdicls=aspektihinne and aspektihinne.markus and 'mdi-comment-text' or 'mdi-comment-text-outline', class_='notes_btn mdibtn', name=ha_prefix, level=2)}
            ${h.hidden('%s.markus' % ha_prefix, aspektihinne and aspektihinne.markus)}
            ${h.hidden('%s.a_kood' % ha_prefix, ha.aspekt_kood)}
          </td>
            % endfor
          % endif
          <td>
            % if yhinne:
            ${h.fstr(yhinne.pallid)}
              % if c.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
              * 2
              % endif
            % endif
          </td>
        </tr>

% endif
% if c.hindamine and c.toimumisaeg.tulemus_kinnitatud and c.ettepanek:

     ## vaide korral hindamiste läbivaatus,
     ## ekspertrühma liige saab teha märkuseid, kuid mitte anda hindepalle
     <%
        yhinne = c.hindamine and c.hindamine.get_vy_ylesandehinne(vy.id) or None
        minumarkus = None
        prefix = 'ty-%s' % (c.counter)
     %>
     % if yhinne:
     ## teiste ekspertrühma liikmete märkused
       % for rcd in yhinne.ylesandehindemarkused:
         % if rcd.ekspert_labiviija.kasutaja_id == c.user.id and not c.ettepanek:
           <% minumarkus = rcd %>
         % else:
     <tr>
       <td>${_("Ekspert")} 
         % if rcd.ekspert_labiviija.kasutaja:
         ${rcd.ekspert_labiviija.kasutaja.nimi}
         % endif
         <!--yhinne_id=${yhinne.id} yhm_id=${rcd.id}-->
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
       <td>${_("Ekspert")} ${c.user.fullname}</td>
       <td colspan="5">
         ${h.textarea('%s.markus' % prefix, minumarkus and minumarkus.markus, rows=2)}
         ${h.hidden('%s.ty_id' % prefix, ty.id)}
         ${h.hidden('%s.vy_id' % prefix, vy.id)}
       </td>
     </tr>
     % endif
% endif
</%def>
