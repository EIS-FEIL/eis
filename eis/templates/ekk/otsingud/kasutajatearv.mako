<%inherit file="/common/page.mako" />
<%def name="page_title()">
${_("Kasutamise statistika")}
</%def>
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>

<h1>${_("Kasutamise statistika")}</h1>

${h.form_search()}
</div>

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Aeg"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Samm"),'step')}
          <%
            opt_step = [(1, _("Päev")),
                        (7, _("7 päeva")),
                        (30, _("Kuu")),
                        (100, _("Kokku")),
                       ]
          %>
          ${h.select('step', c.step or 1, opt_step)}
      </div>
    </div>
    <div class="col-12">
      ${h.flb(_("Kuvada veerud"), 'kuvadaveerud')}
      <div id="kuvadaveerud">
             ${h.checkbox('b_users', 1, checked=c.b_users, label=_("Sisselogimiste arv"))}
             ${h.checkbox('b_kokku_sooritused', 1, checked=c.b_kokku_sooritused, label=_("Testisoorituste arv (e-testid ja p-testid)"))}
             ${h.checkbox('b_e_sooritused', 1, checked=c.b_e_sooritused, label=_("Lahendatud e-testide arv"))}
             ${h.checkbox('b_toosooritused', 1, checked=c.b_toosooritused, label=_("Lahendatud isesesivate tööde arv"))}
             ${h.checkbox('b_pankyl', 1, checked=c.b_pankyl, label=_("Lahendatud e-ülesannete arv ülesandepangas"))}
             ${h.checkbox('b_tooyl', 1, checked=c.b_tooyl, label=_("Lahendatud e-ülesannete arv iseseisvate tööde koosseisus"))}
             ${h.checkbox('b_pedag', 1, checked=c.b_pedag, label=_("Sisseloginud õpetajate arv"))}
             ${h.checkbox('b_opil', 1, checked=c.b_opil, label=_("Sisseloginud õpilaste arv"))}
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-end align-items-end">
    <div class="form-group">
    ${h.btn_search()}
    ${h.submit(_("CSV"), id="csv", class_="filter", level=2)}      
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="kasutajatearv_list.mako" />
</div>
