<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['idcard'] = True
# laadime test.js, et dialoogiaknas saaks kuvada ylesande iframe
c.includes['test'] = True
%>
</%def>
<%def name="page_title()">
${_("Ettepanek vaidekomisjonile")} | ${c.sooritaja.nimi} 
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Eksperthindamine"), h.url('hindamine_eksperttood', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(c.sooritaja.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'ekspert' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="ekspert.tabs.mako"/>
</%def>

<% 
c.vaie = c.sooritaja.vaie 
moni_sooritus_tehtud = False
%>

${h.form_save(c.sooritus.id)}

% for n, tos in enumerate(c.sooritaja.sooritused):
<%
   ta = tos.toimumisaeg
   testiosa = tos.testiosa
   prefix = 'tos-%d' % n
   if tos.staatus == const.S_STAATUS_TEHTUD:
      moni_sooritus_tehtud = True
%>
<table class="table">
  <col width="150px"/>
  <col/>
  <tr>
    <td class="fh">${_("Testiosa")}</td>
    <td>${testiosa.nimi}</td>
  </tr>
  <tr>
    <td class="fh">
      ${_("Ekspertrühm")}

      % if c.olen_hindamisjuht:
      <p>
      ${h.btn_to_dlg(_("Vali eksperdid"),
      h.url('hindamine_ettepanek_new_ekspert', toimumisaeg_id=ta.id, sooritus_id=tos.id),
      title=_("Vali eksperdid"), width=400, size='md', level=2)}
      </p>
      % endif
    </td>
    <td>
      ${self.ekspertryhm(tos, ta, testiosa)}
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Soorituse tähis")}</td>
    <td>
      ${h.link_to(tos.tahised or '...', h.url('hindamine_ekspert_kogum',
      toimumisaeg_id=ta.id, id=tos.id))}
      <!--${tos.id}-->
      % if tos.staatus != const.S_STAATUS_TEHTUD:
      (${tos.staatus_nimi})
      % endif
    </td>
  </tr>
  <tr>
    <td colspan="2">
      ${self.sooritus(tos, ta, testiosa, prefix)}
    </td>
  </tr>
</table>
% endfor

<%
   if moni_sooritus_tehtud == False and c.vaie.pallid_parast is None:
      # ei ole millegi eest punkte anda
      c.vaie.pallid_parast = 0
      c.vaie.ettepanek_pohjendus = _("põhjendusel, et ")
%>
${h.rqexp()}
<div class="rounded border p-2">
  <div class="row">
    <% ch = h.colHelper('col-md-10 text-md-right','col-md-2') %>    
    <div class="col-lg-3">
      <div class="row">
        ${ch.flb(_("Hindepallid enne vaidlustamist"))}
        <div class="col-2">
          ${h.fstr(c.vaie.pallid_enne)}
        </div>
      </div>
      % if c.vaie.pallid_parast is not None:
      <div class="row">
        ${ch.flb(_("Muudetud hindepallid"))}
        <div class="col-2">
          ${h.fstr(c.vaie.pallid_parast)}
        </div>
      </div>
      % endif
    </div>
    % if c.vaie.pallid_parast is not None:
    <% ch = h.colHelper('col-md-2 text-md-right','col-md-10') %>
    <div class="col-lg-9">
      <div class="row">
        ${ch.flb(_("Ettepanek"), 'e_txt')}
        <div class="col-md-10" id="e_txt">
          ${c.vaie.gen_ettepanek_txt()}
        </div>
      </div>
      <div class="row">
        ${ch.flb(_("Põhjendus"), 'f_ettepanek_pohjendus', rq=True)}
        <div class="col-md-10">
          ${h.textarea('f_ettepanek_pohjendus', c.vaie.ettepanek_pohjendus, rows=4)}
        </div>
      </div>
    </div>
    % endif
  </div>

      % if c.vaie.staatus in (const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD) and c.is_edit:
      % if c.vaie.pallid_parast is not None:
      ${h.submit(_("Genereeri dokument"), id='kinnita')}
      % endif
      % endif
      
</div>

${h.end_form()}

${h.form_save(c.sooritus.id, multipart=True)}
${h.hidden('sub','ddoc')}
<div class="p-2">
  <div class="row">
    <div class="col-md-3 text-md-right fh">
      ${_("Ettepanek printimiseks")}
    </div>
    <div class="col-md-9">
      ${h.btn_to(_("Laadi alla"), h.url('hindamine_ettepanek_format',
      toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id, format='pdf', trykk=True))}
    </div>
  </div>
% if c.vaie.ettepanek_dok:
  <div class="row">
    <div class="col-md-3 text-md-right fh">
      ${_("Ettepaneku dokument")}
    </div>
    <div class="col-md-9">
      ${h.btn_to(_("Laadi alla"), h.url('hindamine_ettepanek_format',
      toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id, format=c.vaie.ettepanek_ext))}

      % if c.vaie.staatus in (const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD):
              % if c.vaie.ettepanek_ext != const.DDOC:
            ${h.button(_("Allkirjasta smart-ID abil"), onclick='smartidSign()')}
            ${h.button(_("Allkirjasta mobiil-ID abil"), onclick='mobileSign()')}
            ${h.button(_("Allkirjasta ID-kaardiga"), onclick='getCertBdoc()')}
              % endif

      ${h.file('ettepanek_dok', value=_("Fail"))}
      ${h.submit(_("Laadi"))}

      ${h.submit(_("Edasta vaidekomisjonile"), id='edasta')}
      % endif
      <div id="ddoc_status"></div>
    </div>
  </div>
% endif
</div>
${h.end_form()}

% if c.vaie.ettepanek_dok:
## Digiallkirjastamise väljad ja vormid
<div id="pluginLocation"></div>
<div id="error" style="color:red;"></div>

${h.form_save(c.sooritus.id, form_name='form_prepare')}
${h.hidden('sub', 'prepare_signature')}
${h.hidden('cert_hex', '')}
${h.hidden('cert_id', '')}
${h.hidden('phoneno', c.user.telefon)}
${h.hidden('dformat', '')}
${h.end_form()}

${h.form_save(c.sooritus.id, form_name='form_finalize')}
${h.hidden('sub', 'finalize_signature')}
${h.hidden('signature', '')}
${h.hidden('signature_id', '')}
${h.hidden('container_id', '')}
${h.hidden('dformat', '')}
${h.end_form()}

% endif

<%def name="ekspertryhm(tos, ta, testiosa)">
      <%
         # ekspertrühma liikmed, kes on vähemalt mõne selle soorituse
         # hindamiskogumi läbivaatajaks märgitud
         eksperthindajad = model.Labiviija.query.\
             filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT).\
             filter(model.Labiviija.toimumisaeg_id==ta.id).\
             filter(model.sa.exists().where(model.sa.and_(model.Labiviija.id==model.Labivaatus.ekspert_labiviija_id,
                                              model.Labivaatus.hindamine_id==model.Hindamine.id,
                                              model.Hindamine.hindamisolek_id==model.Hindamisolek.id,
                                              model.Hindamisolek.sooritus_id==tos.id))).\
             all()

         hkogumid = [hk for hk in testiosa.hindamiskogumid if hk.staatus]
      %>
      % if not len(eksperthindajad):
      ${h.alert_error(_("Ekspertrühm on moodustamata"))}
      % else:
      <table cellpadding="5"  class="table table-borderless table-striped">
        <tr>
          <td rowspan="2" class="fh">${_("Ekspert")}</td>
          <td class="fh" colspan="${len(hkogumid)}">${_("Hindamiskogumite läbivaatus")}</td>
        </tr>
        <tr>
          % for hk in hkogumid:
          <td class="fh">
            ${h.link_to(hk.tahis, h.url('hindamine_ekspert_hindamised',
            toimumisaeg_id=ta.id, sooritus_id=tos.id, hindamiskogum_id=hk.id))}
          </td>
          % endfor
        </tr>
        % for rcd in eksperthindajad:
        <tr>
          <td>
            ${rcd.kasutaja.nimi}
          </td>
          % for hk in hkogumid:
            <%
               holek = tos.give_hindamisolek(hk)
               hindamine = holek.give_hindamine(const.HINDAJA5)
               labivaatus = hindamine.get_labivaatus(rcd.id)
            %>
            <td>
            % if labivaatus and labivaatus.staatus:
            ${_("Jah")}
            % elif labivaatus:
            ${_("Pooleli")}
            % else:
            ${_("Ei")}
            % endif
            </td>
          % endfor
        </tr>
        % endfor

<% c.debug_hk = False %>
% if c.debug_hk:
## pallid hindamiskogumite kaupa
        <tr>
         <td class="fh">${_("Kehtiv tulemus")}</td>
         <% kokku = 0 %>
   % for hk in hkogumid:
         <% 
            holek = tos.give_hindamisolek(hk) 
            kokku += holek.pallid or 0
         %>
         <td class="fh">${h.fstr(holek.pallid)}</td>
   % endfor
         <td class="fh">${h.fstr(kokku)}</td>
        </tr>
        <tr>
          <td class="fh">${_("Vaidehindamine")}</td>
          <% kokku = 0 %>
   % for hk in hkogumid:
         <% 
            holek = tos.give_hindamisolek(hk) 
            hindamine = holek.get_hindamine(const.HINDAJA5)
            kokku += hindamine and hindamine.pallid or 0
         %>
         <td class="fh">${h.fstr(hindamine and hindamine.pallid)}</td>
   % endfor
         <td class="fh">${h.fstr(kokku)}</td>
        </tr>
% endif

      </table>
      % endif
</%def>

<%def name="sooritus(tos, ta, testiosa, baseprefix)">
   <% 
     di_hkogumid = {} 
     hkogumid = [hk for hk in testiosa.hindamiskogumid if hk.staatus]
     for n, hk in enumerate(hkogumid):
        di_hkogumid[hk.id] = {'prefix': '%s.hk-%d' % (baseprefix, n),
                              'holek': tos.give_hindamisolek(hk),
                             }
   %>

      <table cellpadding="5"  class="table table-borderless table-striped" width="100%">
        <thead>
          <tr>
            % if testiosa.on_alatestid:
            ${h.th(_("Alatest"))}
            ${h.th(_("Testiplokk"))}
            % endif
            ${h.th(_("Ülesanne"), colspan=2, width="25%")}
            ${h.th(_("Max pallid"))}
            ${h.th(_("Vaidlustatud hindepallid"))}
            ${h.th(_("Muudetud hindepallid"))}            
            ${h.th(_("Max toorpunktid"))}
            ${h.th(_("Kaal"))}
            ${h.th(_("Vaidlustatud toorpunktid"))}
            ${h.th(_("Muudetud toorpunktid"))}
            ${h.th(_("Ekspertide märkused"))}
% if c.debug_hk:
            ${h.th(_("Hindamiskogum"))}
% endif
          </tr>
        </thead>
        <tbody>
          <%
             if testiosa.on_alatestid and c.sooritaja.kursus_kood:
                testiylesanded = [ty for ty in testiosa.testiylesanded if ty.alatest.kursus_kood==c.sooritaja.kursus_kood]
             else:
                testiylesanded = [ty for ty in testiosa.testiylesanded]
          %>
  % for ind_ty, ty in enumerate(testiylesanded):
  <%
     di = di_hkogumid[ty.hindamiskogum.id]
     holek = di['holek']
     prefix = '%s.ty-%d' % (di['prefix'], ind_ty)
  %>
  ${self.tr_ylesanne(tos, ty, holek, prefix)}
  % endfor
        </tbody>
        <tfoot>
          <tr>
            % if testiosa.on_alatestid:
            <td colspan="4" class="fh">${_("TESTIOSA KOKKU")}</td>
            % else:
            <td colspan="2" class="fh">${_("TESTIOSA KOKKU")}</td>
            % endif
            <td class="fh">${h.fstr(testiosa.max_pallid)}</td>
            <td class="fh">
              % if tos.staatus == const.S_STAATUS_TEHTUD:
              ${h.fstr(tos.pallid_enne_vaiet)}
              % else:
              ${tos.staatus_nimi}
              % endif
            </td>
            <td>
            % if tos.staatus == const.S_STAATUS_TEHTUD:
              ## arvutatakse muudetud hindepallid kokku
              ${h.fstr(tos.pallid_peale_vaiet)}
            % if tos.ylesanneteta_tulemus and c.olen_hindamisjuht:
                <br/>
                ${h.link_to_dlg(_("Muuda"),
                h.url('hindamine_ettepanek_edit_hindamine',
                toimumisaeg_id=c.toimumisaeg.id, sooritus_id=tos.id, id=0, sub='kokku'),
                title=_("TESTIOSA KOKKU"), width=900, size='lg')}
              % endif
            % else:
              ${tos.staatus_nimi}
            % endif
            </td>
            <td class="fh" colspan="5"></td>
            % if c.debug_hk:
            <td></td>
            % endif
          </tr>
        </tfoot>
      </table>
</%def>

<%def name="tr_ylesanne(tos, ty, holek, prefix)">
     <%
        ylesandevastus = tos.get_ylesandevastus(ty.id)
        vy = ylesandevastus and ylesandevastus.valitudylesanne
        ylesanne = vy and vy.ylesanne
        rowspan = 1 + (ylesanne and len(ylesanne.hindamisaspektid) or 0)
        colspan = rowspan == 1 and 2 or 1
        hindamine = holek.give_hindamine(const.HINDAJA5)
        yhinne = hindamine and ylesandevastus and hindamine.get_vy_ylesandehinne(ylesandevastus.valitudylesanne_id) or None
        arvutus = ty.hindamiskogum.arvutus_kood
        # kas on muudetud või mitte
        if yhinne:
           toorpunktid = yhinne.toorpunktid or 0
           pallid = yhinne.pallid or 0
        else:
           toorpunktid = pallid = None
        if pallid != None:
           if arvutus == const.ARVUTUS_SUMMA:
              pallid *= 2
           if ylesandevastus:
              if arvutus == const.ARVUTUS_SUMMA:
                 if ylesandevastus.toorpunktid_enne_vaiet == toorpunktid*2:
                   ## kui ei ole muudetud, siis ei kuvata
                   toorpunktid = None
              else:
                 if ylesandevastus.toorpunktid_enne_vaiet == toorpunktid:
                   ## kui ei ole muudetud, siis ei kuvata
                   toorpunktid = None         
        ty_title = ty.nimi or ty.tahis
     %>
         <tr>
           % if ty.alatest_id:
           <td class="fh" rowspan="${rowspan}">${ty.alatest.nimi}</td>
           <td class="fh" rowspan="${rowspan}">
             % if ty.testiplokk_id:
             ${ty.testiplokk.nimi}
             % endif
           </td>
           % endif
           <td rowspan="${rowspan}" colspan="${colspan}">
             <span class="pr-2">${ty_title}</span>
             % if tos.staatus == const.S_STAATUS_TEHTUD:
             ${h.link_to_dlg(_("Punktid"),
             h.url('hindamine_ettepanek_edit_hindamine', toimumisaeg_id=c.toimumisaeg.id, sooritus_id=tos.id, id=ty.id),
             title=ty_title, width=900, size='lg')}
             <!--
                 hindamine_id=${hindamine and hindamine.id}
                 ty_id=${ty.id}
                 vy_id=${vy and vy.id}
                 yhinne_id=${yhinne and yhinne.id}
                 yv_id=${ylesandevastus and ylesandevastus.id}
               -->

             <% hkogum = ty.hindamiskogum %>
             % if ty.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) and hkogum.on_hindamisprotokoll == False and ty.sisestusviis in (const.SISESTUSVIIS_VASTUS, const.SISESTUSVIIS_OIGE) and not tos.ylesanneteta_tulemus:
               &nbsp;
             ${h.link_to_dlg(_("Vastused"),
             h.url('hindamine_ettepanek_edit_vastus', toimumisaeg_id=c.toimumisaeg.id, sooritus_id=tos.id, id=ty.id),
             title=_("Vastuste sisestamine"), width=900, size='lg')}
             % endif

             % endif
           </td>
           % if colspan == 1:
           ## aspektidega ylesanne
           <td class="fh">${_("KOKKU")}</td>
           % endif

           ## hindepallid
           <td class="fh">${h.fstr(ty.max_pallid)}</td>
           <td class="fh">
             ## vaidlustatud pallid
             % if ylesandevastus:
             ${h.fstr(ylesandevastus.pallid_enne_vaiet)}

             % if c.is_debug:
             <span class="font-weight-normal">
               (${h.fstr(ylesandevastus.pallid_kasitsi or 0)} + ${h.fstr(ylesandevastus.pallid_arvuti or 0)})
             </span>
             % endif
             % endif
           </td>
           <td>
             ## muudetud pallid
             % if pallid != None:
             ${h.fstr(pallid)}
             % endif
           </td>
           <td class="fh">
             % if ylesanne:
             ${h.fstr(ylesanne and ylesanne.max_pallid)}
             % if arvutus == const.ARVUTUS_SUMMA:
             * 2
             % endif
             % endif
           </td>
           <td class="fh"></td>
           <td class="fh">
             ## vaidlustatud toorpunktid
             % if ylesandevastus and ylesandevastus.toorpunktid_enne_vaiet is not None:
               % if arvutus == const.ARVUTUS_SUMMA:
             ${h.fstr(ylesandevastus.toorpunktid_enne_vaiet/2.)} * 2
               % else:
             ${h.fstr(ylesandevastus.toorpunktid_enne_vaiet)}
               % endif
             % endif
           </td>
           <td>
             ## muudetud toorpunktid
           % if tos.staatus == const.S_STAATUS_TEHTUD:
             ${h.fstr(toorpunktid)}
            % endif
           </td>

           <td>
             % if yhinne:
             % for m in yhinne.ylesandehindemarkused:
             <i>${m.ekspert_labiviija.kasutaja.nimi}:</i>
             ${m.markus}<br/>
             % endfor
             % endif
           </td>
           % if c.debug_hk:
           <td>${ty.hindamiskogum.tahis}</td>
           % endif
         </tr>
         % if ylesanne:
         % for n_ha, ha in enumerate(ylesanne.hindamisaspektid):
         <%
            ha_prefix = '%s.ha-%d' % (prefix, n_ha)
         %>
         ${self.tr_aspekt(ylesandevastus, yhinne, ha, ha_prefix, arvutus)}
         % endfor
         % endif
</%def>

<%def name="tr_aspekt(ylesandevastus, yhinne, ha, ha_prefix, arvutus)">
         <%
            vastusaspekt = ylesandevastus and ylesandevastus.get_vastusaspekt(ha.id)
            aspektihinne = yhinne and yhinne.get_aspektihinne(ha.id) or None

            if aspektihinne and aspektihinne.toorpunktid != None:
               toorpunktid = aspektihinne.s_toorpunktid
               if vastusaspekt:
                  if arvutus == const.ARVUTUS_SUMMA:
                     if vastusaspekt.toorpunktid_enne_vaiet == aspektihinne.toorpunktid*2:
                        ## kui ei ole muudetud, siis ei kuvata
                        toorpunktid = None
                  else:
                     if vastusaspekt.toorpunktid_enne_vaiet == aspektihinne.toorpunktid:
                        ## kui ei ole muudetud, siis ei kuvata
                        toorpunktid = None
            else:
               toorpunktid = None
         %>
         <tr>
           <td>${ha.aspekt_nimi}</td>
           ## hindepallid
           <td class="fh">
             % if ylesandevastus:
             ${h.fstr(ha.max_pallid*ylesandevastus.valitudylesanne.koefitsient)}
             % endif
           </td>
           <td class="fh">
             % if vastuaspekt:
             ${h.fstr(vastusaspekt.pallid_enne_vaiet)}
             % endif
           </td>
           <td>
             % if toorpunktid:
             ${h.fstr(aspektihinne.pallid)}
             % endif
           </td>
           ## toorpunktid
           <td class="fh">${h.fstr(ha.max_pallid)}
             % if arvutus == const.ARVUTUS_SUMMA:
             * 2
             % endif
           </td>
           <td class="fh">${h.fstr(ha.kaal)}</td>
           <td class="fh">
             % if vastusaspekt:
               % if arvutus == const.ARVUTUS_SUMMA:
             ${h.fstr(vastusaspekt.toorpunktid_enne_vaiet/2.)} * 2
               % else:
             ${h.fstr(vastusaspekt.toorpunktid_enne_vaiet)}
               % endif
             % endif
           </td>
           <td>
             ${h.fstr(toorpunktid)}
           </td>
% if c.debug_hk:
           <td colspan="2">
% else:
           <td>
% endif
           </td>
         </tr>
</%def>
