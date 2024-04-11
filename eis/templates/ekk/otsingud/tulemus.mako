<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Sooritus")}: ${c.item.test.nimi}, ${c.item.kasutaja.isikukood} ${c.item.nimi}
</%def>      
<%namespace name="tab" file='/common/tab.mako'/>
<%def name="require()">
<% c.includes['plotly'] = True %>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<%def name="draw_tabs()">
<% test = c.item.test %>
% if test.diagnoosiv:
${tab.draw('testisooritused', h.url('otsing_testisooritus', id=c.item.id), _("Tagasiside"))}
% else:
${tab.draw('testisooritused', h.url('otsing_testisooritus', id=c.item.id), _("Tulemus"))}
% endif
% if (c.item.staatus == const.S_STAATUS_TEHTUD or c.is_debug and c.is_devel) and (c.app_ekk or not test.salastatud):
<%
  tk = c.item.testimiskord
  sooritused = []
  for r in c.item.sooritused:
      if (r.staatus == const.S_STAATUS_TEHTUD or c.is_debug and c.is_devel) and not r.klastrist_toomata:
          testiosa = r.testiosa
          vastvorm = testiosa.vastvorm_kood
          if vastvorm in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
              sooritused.append(r)
%>
% for tos in sooritused:
% if len(sooritused) > 1:
${tab.draw('osa', h.url('tulemus_osa', test_id=test.id, testiosa_id=tos.testiosa_id, alatest_id='', id=tos.id), tos.testiosa.nimi)}
% else:
${tab.draw('osa', h.url('tulemus_osa', test_id=test.id, testiosa_id=tos.testiosa_id, alatest_id='', id=tos.id), _("Näita vastuseid"))}
% endif
% if c.app_ekk and c.is_devel and test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
${tab.draw('osa', h.url('muud_pstulemus', id=tos.id), u'PS profiilileht')}
% endif
% endfor
% endif
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('otsing_testisooritused'))}
${h.crumb('%s, %s' % (c.test.nimi, c.item.nimi), h.url('otsing_testisooritus',id=c.item.id))}
</%def>

<h2>${c.item.nimi} (${c.item.kasutaja.isikukood})</h2>
<%include file="/avalik/tulemused/tulemus_sisu.mako"/>

<%
  c.testikoht1_id = None
  for tos in c.sooritaja.sooritused:
     if tos.testikoht_id:
         c.testikoht1_id = tos.testikoht_id
         break
%>
${self.toovaatajad()}

<%def name="toovaatajad()">
% if c.toovaatajad:
<h3>${_("Testitöö vaatajad")}</h3>
<table  class="table table-borderless table-striped" width="100%">
  <thead>
    ${h.th(_("Nimi"))}
    ${h.th(_("Kehtib kuni"))}
    <th></th>
  </thead>
  <tbody>
    % for tv_id, nimi, kuni in c.toovaatajad:
    <tr>
      <td>${nimi}</td>
      <td>${h.str_from_date(kuni)}</td>
      <td>
        % if c.user.has_permission('korraldamine', const.BT_UPDATE, testikoht_id=c.testikoht1_id):
        ${h.btn_to_dlg(_("Muuda"),
        h.url('otsing_testisooritus_edit_toovaataja', id=tv_id, sooritaja_id=c.sooritaja.id),
        mdicls='mdi-file-edit', level=2,
        title=_("Testitöö vaataja"))}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
</%def>


${h.btn_back(url=h.url('otsing_testisooritused'))}

% if c.tagasiside_html:
<%
  sooritus_id = c.item.sooritused[0].id
  pdf_url = h.url_current('download', format='pdf', id=sooritus_id)
%>
${h.btn_to(_("Tagasiside (PDF)"), pdf_url, level=2)}
% endif


% if c.sooritaja.testimiskord_id and c.user.has_permission('korraldamine', const.BT_UPDATE, testikoht_id=c.testikoht1_id):
${h.btn_to_dlg(_("Lisa testitöö vaataja"),
h.url('otsing_testisooritus_toovaatajad', sooritaja_id=c.sooritaja.id),
title=_("Testitöö vaataja"), level=2)}
% endif
