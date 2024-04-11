<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Sooritus")}: ${c.item.test.nimi}, ${c.item.kasutaja.isikukood} ${c.item.nimi}
</%def>      
<%namespace name="tab" file='/common/tab.mako'/>
<%def name="draw_tabs()">
<% test = c.item.test %>
% if test.diagnoosiv:
${tab.draw('toovaatamised', h.url('toovaatamine', id=c.item.id), _("Tagasiside"))}
% else:
${tab.draw('toovaatamised', h.url('toovaatamine', id=c.item.id), _("Tulemus"))}
% endif
% if (c.item.staatus == const.S_STAATUS_TEHTUD or c.is_debug and c.is_devel) and (c.app_ekk or not test.salastatud):
<%
  tk = c.item.testimiskord
  sooritused = []
  for r in c.item.sooritused:
      if r.staatus == const.S_STAATUS_TEHTUD or c.is_debug and c.is_devel:
          testiosa = r.testiosa
          vastvorm = testiosa.vastvorm_kood
          if vastvorm in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
              sooritused.append(r)
%>
% for tos in sooritused:
% if len(sooritused) > 1:
${tab.draw('osa', h.url('toovaatamine_osa', test_id=test.id, testiosa_id=tos.testiosa_id, alatest_id='', id=tos.id), tos.testiosa.nimi)}
% else:
${tab.draw('osa', h.url('toovaatamine_osa', test_id=test.id, testiosa_id=tos.testiosa_id, alatest_id='', id=tos.id), _("Näita vastuseid"))}
% endif
% endfor
% endif
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testitööde vaatamine"), h.url('toovaatamised'))}
${h.crumb('%s, %s' % (c.item.test.nimi, c.item.nimi), h.url('toovaatamine',id=c.item.id))}
</%def>

<h2>${c.item.nimi} (${c.item.kasutaja.isikukood})</h2>
<%
  c.sooritaja_roll = const.ISIK_KOOL
%>
<%include file="/avalik/tulemused/tulemus_sisu.mako"/>
<br/>
${h.btn_back(url=h.url('toovaatamised'))}

% if c.tagasiside_html:
<%
  sooritus_id = c.item.sooritused[0].id
  pdf_url = h.url_current('download', format='pdf', id=sooritus_id)
%>
${h.btn_to(_("Tagasiside (PDF)"), pdf_url)}
% endif
