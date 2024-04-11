<%inherit file="/common/formpage.mako"/>

<%def name="page_title()">
${_("Testi toimumise protokolli koostamine")} | ${c.testikoht.tahised}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testi toimumise protokolli koostamine"), h.url('sisestamine_protokollid', toimumisaeg_id=c.testikoht.toimumisaeg_id))}
${h.crumb(c.testikoht.tahised, h.url('sisestamine_protokoll_osalejad', toimumisprotokoll_id=c.toimumisprotokoll.id))}
${h.crumb(_("Testil osalejad"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>


<%def name="draw_before_tabs()">
<%include file="tprotokoll.before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="tprotokoll.tabs.mako"/>
</%def>

<%def name="tabs_label()">
## kui soorituskohas on mitu toimumisprotokolli, 
## siis lingime teistele sama soorituskoha protokollidele
<% teisedprot = (c.testiruum or c.testikoht).toimumisprotokollid %>
% if len(teisedprot) > 1:
  % for mpr in teisedprot:
    % if mpr == c.toimumisprotokoll:
      ${mpr.lang_nimi}
    % else:
      ${h.link_to(mpr.lang_nimi, h.url('sisestamine_protokoll_osalejad', toimumisprotokoll_id=mpr.id))}
    % endif
  % endfor
% endif
## kui tahad midagi kuvada lipikuterea paremas servas
</%def>

${h.form_save(None, disablesubmit=True)}
% if c.test.testityyp in (const.TESTITYYP_EKK, const.TESTITYYP_AVALIK):
## konsultatsiooni sooritajaid ei sisestata
% if c.testimiskord.prot_tulemusega:
<%include file="/ekk/sisestamine/protokoll.osalejad_tulemusega_list.mako"/>
% else:
<%include file="/ekk/sisestamine/protokoll.osalejad_list.mako"/>
% endif
% endif

% if not c.testimiskord.prot_tulemusega:
<%include file="protokoll.labiviijad_list.mako"/>
${_("Märkused")}
% else:
${_("Kooli käskkirja number, eksamikomisjoni liikmete eriarvamused, märkused")}
% endif

${h.textarea('markus', c.toimumisprotokoll.markus, rows=5)}
<br/>

% if c.is_edit:
<% checked = c.toimumisprotokoll.staatus in (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD) %>
${h.checkbox('kinnitatud', True, checked=checked, label=_("Protokoll kinnitatud"))}
<br/>
${h.submit()}
% endif

% if c.toimumisprotokoll.id and c.toimumisprotokoll.has_file:
<%
  ext = c.toimumisprotokoll.fileext
%>
% if ext in (const.BDOC, const.DDOC, const.ASICE):
  <%  img = ' <img src="/static/images/bdoc.png" alt="BDOC" class="pl-2" border="0"/>' %>
  ${h.btn_to(_("Laadi alla") + h.literal(img), h.url('sisestamine_protokoll_format', format=ext, id=c.toimumisprotokoll.id))}
% else:
  ${h.btn_to(_("Laadi alla"), h.url('sisestamine_protokoll_format', format=ext, id=c.toimumisprotokoll.id), mdicls='mdi-file-pdf')}  
% endif

% endif

${h.end_form()}

${h.form_search(h.url('sisestamine_protokollid'))}
${h.hidden('toimumisaeg_id',c.testikoht.toimumisaeg_id)}

${_("Järgmise soorituskoha tähis")}: ${h.text('tk_tahis', c.tk_tahis, size=15,
class_=c.focus and 'initialfocus' or None)}
${h.button(_("Järgmine"), id='otsi', onclick='this.form.submit()')}
${h.end_form()}


