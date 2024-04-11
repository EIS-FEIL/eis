<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Lõpetamise kontroll")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>
<h1>${_("Lõpetamise kontroll")}</h1>
${h.form_search()}
% if c.debug:
${h.hidden('debug', 1)}
% endif
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Aasta"),'aasta')}
        ${h.posint('aasta', c.aasta, maxlength=4)}
      </div>
    </div>
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ## kui isikukood on antud, siis tehakse yheainsa isiku kontroll
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">        
          ${h.submit(_("Kuva"))}
          ${h.button(_("Kontrolli"), id="kontrolli")}
          <script>
            $('#kontrolli').click(function()
            {
            $('form#form_save input[name="aasta"]').val($('form#form_search input[name="aasta"]').val());
            $('form#form_save input[name="isikukood"]').val($('form#form_search input[name="isikukood"]').val());
            $('form#form_save').submit();
            });
          </script>
      </div>
    </div>
  </div>
</div>

<%
c.url_refresh = h.url('muud_lopetamised', aasta=c.aasta, sub='progress')
%>

<%include file="/common/arvutusprotsessid.mako"/>

% if len(c.arvutusprotsessid):
% if not c.pooleli and c.mitu_lopetajat != '':
<table  class="table">
  <tr>
    <td class="fh">${_("Lõpetamise tingimused täidetud")}</td>
    <td width="80px">${c.mitu_lopetajat}</td>
  </tr>
  <tr>
    <td class="fh">${_("Lõpetamise tingimused täitmata")}</td>
    <td>${c.mitu_lopetamata}</td>
    % if c.mitu_lopetamata:
    <td class="fh">
      ${h.submit(_("Lõpetamata"), id='lopetamata')}
    </td>
    % endif
  </tr>
</table>
% endif
% endif

${h.end_form()}

${h.form_save(None)}
${h.hidden('aasta', '')}
% if c.debug:
## debug=1 korral ei käivitata eraldi protsessi
${h.hidden('debug', 1)}
% endif
${h.hidden('isikukood', c.isikukood)}
${h.end_form()}

% if c.items:
<div class="listdiv">
<%include file="lopetamised_list.mako"/>
</div>
% endif

