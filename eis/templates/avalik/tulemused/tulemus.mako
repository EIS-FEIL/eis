<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Tulemus")}: ${c.item.test.nimi}
</%def>      
<%def name="require()">
<% c.includes['plotly'] = True %>
</%def>
<%def name="page_headers()">
  ${h.javascript_link("/static/eis/idcard/hwcrypto.min.js")}
  ${h.javascript_link("/static/eis/idcard/startsign.min.js")}
</%def>

<%def name="draw_tabs()">
<%namespace name="tab" file='/common/tab.mako'/>
<% test = c.item.test %>
% if test.diagnoosiv:
${tab.draw('tulemused', h.url('tulemus', id=c.item.id), _("Tagasiside"))}
% else:
${tab.draw('tulemused', h.url('tulemus', id=c.item.id), _("Tulemus"))}
% endif
% if c.item.staatus == const.S_STAATUS_TEHTUD and not test.salastatud and not c.item.vaie_ettepandud:
<%
  tk = c.item.testimiskord
  visibility = c.item.tulemus_nahtav(None, False, const.ISIK_SOORITAJA, test, tk)
%>
% if visibility.is_resp and not c.user.testpw_id:
<% sooritused = [r for r in c.item.sooritused if r.staatus==const.S_STAATUS_TEHTUD and r.testiosa.vastvorm_kood == const.VASTVORM_KE ] %>
% for tos in sooritused:
<% url_tos = h.url('tulemus_osa', test_id=test.id, testiosa_id=tos.testiosa_id, alatest_id='', id=tos.id) %>
% if len(sooritused) > 1:
${tab.draw('osa', url_tos, tos.testiosa.nimi)}
% else:
${tab.draw('osa', url_tos, _("Näita vastuseid"))}
% endif
% endfor
% endif
% endif
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tulemused' %>
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Tulemused"), h.url('tulemused'))}
${h.crumb(c.item.test.nimi, h.url('tulemus',id=c.item.id))}
</%def>
<%
  c.sooritaja_roll = const.ISIK_SOORITAJA
%>
<%include file="/avalik/tulemused/tulemus_sisu.mako"/>

% if c.test.testiliik_kood == const.TESTILIIK_SISSE:
<%
  testimiskord = c.item.testimiskord
  regkohad = testimiskord and testimiskord.reg_kohavalik and testimiskord.regkohad
%>
% if regkohad:
<div class="d-flex flex-wrap my-2">
  <div class="item mr-5">
    ${h.flb(_("Õppeasutused, millele avaldatakse testitulemused"))}
  </div>
  <div class="item mr-5">
    % for r in c.item.kandideerimiskohad:
    <div>
      ${r.koht.nimi}
      % if r.automaatne:
      (${_("praegune kool")})
      % endif
    </div>
    % endfor
  </div>
  % if c.item.kasutaja_id == c.user.id:
  <div class="item mr-5">
   ${h.btn_to_dlg(_('Muuda'), h.url('edit_tulemus', id=c.item.id, sub='vvk', partial=True), 
    title=_("Õppeasutused, millele avaldatakse testitulemused"), level=2)}
  </div>
  % endif
</div>
% endif
% endif

<%
  vaie = c.item.vaie
  if vaie and vaie.staatus > const.V_STAATUS_ESITAMATA:
      on_vaie = True
  else:
      on_vaie = False
%>

<div class="d-flex flex-wrap mt-2">
  <div class="flex-grow-1">
% if not c.user.testpw_id:
    ${h.btn_back(url=h.url('tulemused'))}
% endif
% if c.tagasiside_html:
<%
  pdf_url = h.url_current('download', format='pdf', id=c.item.id)
%>
${h.btn_to(_("Tagasiside (PDF)"), pdf_url)}
% endif
  </div>
  
% if c.item.testimiskord_id:
  <%
    if on_vaie:
       vaie_title = _("Vaie")
    elif c.saab_vaidlustada and c.user.get_kasutaja().vanus >= 18:
       vaie_title = _("Esita vaie")
    else:
       vaie_title = None
    if vaie_title:
       on_te = c.test.testiliik_kood == const.TESTILIIK_TASE
       dlgtitle = on_te and _("Vaie Haridus- ja Noorteametile") or _("Vaie Haridus- ja Teadusministeeriumile")
  %>
  % if vaie_title:
  <div>
    ${h.btn_to_dlg(vaie_title, h.url('edit_vaie', id=c.item.id), dlgtitle=dlgtitle,
    level=2, dialog_id='dvaie', size='lg')}
  </div>
  % endif
  
  % if c.item.kasutaja_id == c.user.id:
         <%
           sooritused = list(c.item.sooritused)
           on_mitu = len(sooritused) > 1 
           tutv_osad = list()
           for sooritus in sooritused:
              testiosa = sooritus.testiosa
              if sooritus.staatus == const.S_STAATUS_TEHTUD and testiosa.vastvorm_kood == const.VASTVORM_KP:
                  if c.saab_tutvuda or sooritus.skannfail:
                     tutv_osad.append((sooritus, testiosa))
         
         %>
         % if tutv_osad:
         <div>
         % for sooritus, testiosa in tutv_osad:
         <% buf = on_mitu and ' (%s)' % testiosa.nimi or '' %>
         % if c.saab_tutvuda:
         ${h.btn_to_dlg(_("Esita taotlus eksamitööga tutvumiseks") + buf, h.url('tulemus_edit_tellimine', id=sooritus.id),
         title=_("Esita taotlus eksamitööga tutvumiseks"), level=2)}
         % endif
         % if sooritus.skannfail:
         ${h.btn_to(_("Laadi alla") + buf, h.url('tulemus_skannfail', id=sooritus.id))}
         % endif
         % endfor
         </div>
         % endif
  % endif
         
% endif

</div>

% if c.item.testimiskord_id and not on_vaie and c.saab_vaidlustada:
% if c.user.get_kasutaja().vanus < 18:
% if c.test.testiliik_kood == const.TESTILIIK_TASE:
        <div class="py-3">
         Teie vanus on alla 18 aasta ning haldusmenetluse § 12 lõike 2 kohaselt
         ei või alaealine isik haldusmenetluses iseseisvalt menetlustoiminguid teha.
         Eksamitöö vaidlustamiseks saab avalduse esitada lapsevanem või eestkostja.
         Avalduse blanketi saamiseks palume lapsevanemal või eestkostjal pöörduda <a href="mailto:info@harno.ee">info@harno.ee</a>.
         </div>
% else:
        <div class="py-3">
         Teie vanus on alla 18 aasta ning haldusmenetluse § 12 lõike 2 kohaselt
         ei või alaealine isik haldusmenetluses iseseisvalt menetlustoiminguid teha.
         Eksamitöö vaidlustamiseks saab avalduse esitada lapsevanem või eestkostja.
         Avaldus tuleb esitada apellatsioonikomisjoni blanketil, kas digitaalselt allkirjastatuna
         aadressil <a href="mailto:apellatsioonid@hm.ee">apellatsioonid@hm.ee</a>
         või paberkandjal allkirjastatuna aadressil Munga 18, 50088 Tartu.
         Apellatsioonikomisjoni blanketi leiate Haridus- ja Teadusministeeriumi veebilehelt
         <a href="https://www.hm.ee/sites/default/files/vaide_blank.doc" rel="noopener">https://www.hm.ee/sites/default/files/vaide_blank.doc</a>.
         </div>
% endif
% endif
% endif
