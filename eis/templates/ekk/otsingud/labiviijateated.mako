<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Läbiviijate teated")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Läbiviijate teated")}</h1>

${h.form_search(url=h.url('otsing_labiviijateated'))}
${h.hidden('op','')}
${h.hidden('debug', c.debug)}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <% c.on_pohikool = c.on_rv = True %>
    <%include file="teated.otsing_test.mako"/>

    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Läbiviija roll"),'grupp_id')}
        <% opt_grupp = c.opt.labiviijagrupp_s12 %>
        ${h.select('grupp_id', c.grupp_id, opt_grupp, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Teate liik"),'ltyyp')}
            <%
               opt_ltyyp = [(model.Kiri.TYYP_LABIVIIJA_TEADE, _("Läbiviija teade")),
                            (model.Kiri.TYYP_LABIVIIJA_MEELDE, _("Läbiviija meeldetuletus")),
                            (model.Kiri.TYYP_LABIVIIJA_LEPING, _("Lepingu sõlmimise teavitus")),
                           ]
            %>
            ${h.select('ltyyp', c.ltyyp, opt_ltyyp)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
            ${h.checkbox(u'kordus', 1, checked=c.kordus, label=_("Saada ka kordusteateid"))}
      </div>
    </div>
  </div>
  <div class="col d-flex justify-content-end filter align-items-end">
    <div class="form-group">
    ${h.submit(_("Otsi saadetavad teated"), id='saatmata')}
    <br/>
    ${h.button(_("Saadetud teadete ülevaade"),
    onclick="this.form.action='%s';this.form.sort.value='';this.form.submit();" % (h.url('otsing_teated')))}
    </div>
  </div>
</div>

% if c.arv != '':
<div class="data-box mb-5">
  <div class="row">
    <div class="column col-md-3 fh">
      ${_("Saadetavate teadete arv")}
    </div>
    <div class="column col-md-1">
      ${c.arv}
    </div>
    <div class="column col-md-8">
            % if c.arv:
            ${h.button(_("Väljasta e-postiga"), onclick="$('#op').val('epost');submit_post(this)")}
            % if c.ltyyp != model.Kiri.TYYP_LABIVIIJA_LEPING:
            ${h.button(_("Väljasta väljatrükid"), onclick="$('#op').val('tpost');submit_post(this)")}
            % endif
            % endif
    </div>
  </div>
  % if c.arv and c.ltyyp == model.Kiri.TYYP_LABIVIIJA_LEPING:            
  <div class="row">
    <div class="column col-md-3">
      ${h.flb(_("Täiendav info (lisatakse teatele)"),'taiendavinfo')}
    </div>
    <div class="column col-md-9">
      ${h.textarea('taiendavinfo', c.taiendavinfo)}
    </div>
  </div>
  % endif
</div>
% endif
${h.end_form()}

<% 
  c.protsessid_no_empty = True
  c.url_refresh = h.url_current('index', sessioon_id=c.sessioon_id, sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>

<div class="listdiv">
<%include file="labiviijateated_list.mako"/>
</div>
