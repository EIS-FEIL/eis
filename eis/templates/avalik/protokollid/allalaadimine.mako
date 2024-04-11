## -*- coding: utf-8 -*- 
## $Id: allalaadimine.mako 857 2016-09-14 17:31:06Z ahti $         
<%inherit file="/common/formpage.mako"/>

<%def name="page_title()">
${_("Testi ülesannete laadimine keskserverist kohalikku serverisse")} | ${c.toimumisprotokoll.tahistus}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Testi toimumise protokolli koostamine'), h.url('protokollid'))}
${h.crumb_sep()}
${h.crumb(c.toimumisprotokoll.tahistus, h.url('protokoll_osalejad', toimumisprotokoll_id=c.toimumisprotokoll.id))}
${h.crumb_sep()}
${h.crumb(_('Ülesannete laadimine'))}
</%def>

<%def name="draw_before_tabs()">
<%include file="/avalik/protokollid/before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="/avalik/protokollid/tabs.mako"/>
</%def>

${h.form_save(None)}

% if not c.app_eksam:
See pole kohalik eksamiserver
% else:

## oleme kohalikus eksamiserveris, kuhu ülesanded tõmmatakse keskserverist

<table class="table" width="100%" border="0">
  <tr>
    <td class="fh">${_("Ülesanded")}</td>
    <td colspan="5">
        % if len(c.testiosa.testiylesanded) == 0:
          ${_("Ülesanded on keskserverist alla laadimata.")}
          ${h.submit_dlg(_('Laadi ülesanded'))}
        % else:
          ${_("Ülesanded on keskserverist alla laaditud.")}
          ${h.submit_dlg(_('Korda laadimist'))}
        % endif
    </td>
  </tr>
</table>
% endif

${h.end_form()}
