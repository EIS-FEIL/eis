<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${c.test.nimi} ${c.toimumisaeg.millal} | ${_("Läbiviijate juhendamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Läbiviijate juhendamine"), h.url('hindamine_juhendamised', toimumisaeg_id=c.toimumisaeg.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

${h.form_search(url=h.url('hindamine_juhendamised', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <% on_alatestid = c.testiosa.on_alatestid %>
    % if on_alatestid:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Alatest"),'komplektivalik_id')}
        ${h.select('komplektivalik_id', c.komplektivalik_id, c.toimumisaeg.testiosa.get_opt_komplektivalikud(False), 
            onchange="$('#komplekt_id').val('');this.form.submit();", ronly=False, empty=True)}
      </div>
    </div>
    % endif

    % if c.komplektivalik:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Ülesandekomplekt"),'komplekt_id')}
        ${h.select('komplekt_id', c.komplekt_id, c.komplektivalik.get_opt_komplektid(c.toimumisaeg), 
        onchange="this.form.submit();", ronly=False, empty=True)}
      </div>
    </div>
    % endif
    <div class="col-12 ${on_alatestid and 'col-md-4 col-lg-3' or 'col-md-5 col-lg-6'} d-flex align-items-end">
      <div class="form-group">
        ${h.checkbox('vastamata', 1, checked=c.vastamata,
        label=_("Vastamata küsimustega ülesanded"), ronly=False)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.btn_search()}
        ${h.submit(_("CSV"), id='csv', level=2)}
      </div>
    </div>
  </div>
</div>
${h.end_form()}


<table width="100%" >
  <tr>
    <td valign="top">
      ${self.show_index()}
    </td>
    <td valign="top">
      <div id="itemdiv">
        % if c.item:
        <%include file="juhendamine.ylesanne.mako"/>
        % endif
      </div>
    </td>
  </tr>
</table>

<%def name="show_index()">
<table width="100%"  class="table table-borderless table-striped">
  <tr>
    ${h.th(_("Testiül"))}
    ${h.th(_("Ülesanne"))}
    ${h.th(_("Komplekt"))}
    ${h.th(_("Vastamata küsimusi"))}
    ${h.th(_("Vastatud küsimusi"))}
  </tr>
  % for rcd in c.items:
  <% 
     ty_tahis, alatest_seq, ty_seq, y_nimi, vy_id, y_id, k_tahis, vastamata, vastatud = rcd 
  %>
  <tr>
    <td>
      ${ty_tahis}
    </td>
    <td>
      ${h.link_to(y_nimi, h.url('hindamine_juhendamine',
      toimumisaeg_id=c.toimumisaeg.id, id=vy_id, komplektivalik_id=c.komplektivalik_id, komplekt_id=c.komplekt_id))}
    </td>
    <td>${k_tahis}</td>
    <td>
      % if vastamata:
      <span style="color:red">${vastamata}</span>
      % endif
    </td>
    <td>
      % if vastatud:
      ${vastatud}
      % endif
    </td>
  </tr>
  % endfor
</table>
</%def>

