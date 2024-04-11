<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} | ${_("Sarnased vastused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Hindamise analüüs"), h.url('hindamine_analyys_protokollid', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Sarnased vastused"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'analyys' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="analyys.tabs.mako"/>
</%def>

<h3>${_("Samas ruumis sooritajad, kellel on sarnased valevastused")}</h3>

${h.form_search(url=h.url_current('index'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testikoht"),'testikoht_id')}
        ${h.select('testikoht_id', c.testikoht_id,
        c.toimumisaeg.get_testikohad_opt(), onchange="this.form.submit()", empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testiruum"),'testiruum_id')}
        <% c.testikoht = c.testikoht_id and model.Testikoht.get(c.testikoht_id) %>
        ${h.select('testiruum_id', c.testiruum_id,
        c.testikoht and c.testikoht.get_testiruumid_opt() or [], empty=True)}
      </div>
    </div>

        <%
            kvalikud = c.toimumisaeg.testiosa.komplektivalikud
            if len(kvalikud) == 1:
                c.komplektivalik = kvalikud[0]
        %>
        % if len(kvalikud) > 1:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Alatestid"),'komplektivalik_id')}
        ${h.select('komplektivalik_id', c.komplektivalik_id, 
            c.toimumisaeg.testiosa.get_opt_komplektivalikud(True, naita_kursus=True), 
            onchange="this.form.submit()", ronly=False, empty=True)}
      </div>
    </div>
        % endif
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Ülesandekomplekt"),'komplekt_id')}
            <% opt_komplektid = c.komplektivalik and c.komplektivalik.get_opt_komplektid(c.toimumisaeg) or [] %>
            ${h.select('komplekt_id', c.komplekt_id, opt_komplektid, 
            ronly=False, empty=len(opt_komplektid)!=1)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Samu vigu vähemalt"),'samuvigu')}<br/>
        ${h.posint5('samuvigu', c.samuvigu or 10, maxlength=3, size=2)}% 
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("Väljasta PDF"), id='pdf', level=2)}
        ${h.submit(_("CSV"), id='csv', level=2)}
      </div>
    </div>
  </div>

</div>
${h.end_form()}

<div class="listdiv">
<%include file="sarnasedvastused_list.mako"/>
</div>
<br/>
