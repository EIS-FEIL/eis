<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Tulemuste teavitused")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Tulemuste teavitused")}</h1>

${h.form_search(url=h.url('otsing_tulemusteteavitused'))}
${h.hidden('naita', c.naita)}
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
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group d-flex flex-wrap">
        ${h.checkbox('kordus', 1, checked=c.kordus, label=_("Saada ka kordusteateid"))}
        <div>
          % if c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS):
            <% 
               if not c.sooritusteated and not c.mittesooritusteated:
                   c.sooritusteated = c.mittesooritusteated = True
            %>
            ${h.checkbox(u'sooritusteated', 1, 
            checked=c.sooritusteated!=False, label=_("Sooritusteated"))}
            <br/>
            ${h.checkbox(u'mittesooritusteated', 1, 
            checked=c.mittesooritusteated!=False, label=_("Mittesooritusteated"))}
            <br/>
         % endif
        </div>
        <div>
          ${h.submit(_("Otsi saadetavad teated"), id='saatmata')}

          ${h.button(_("Saadetud teadete ülevaade"),
          onclick="this.form.action='%s';this.form.sort.value='';this.form.submit();" % (h.url('otsing_teated')))}
        </div>
      </div>
    </div>
  </div>
</div>
${h.end_form()}

% if c.arv_epost != '' and c.search_args:
${h.form(h.url_current('create', **c.search_args), method='post', id='form_post')}
##<div class="data-box mb-5">
<div class="form-wrapper-lineborder mb-5">
  <div class="form-group row">
    <div class="column col-md-3">
      ${h.flb(_("Täiendav info (lisatakse teatele)"),'taiendavinfo')}
    </div>
    <div class="column col-md-9">
      ${h.textarea('taiendavinfo', c.taiendavinfo)}
    </div>
  </div>
  <div class="form-group row">
    <div class="column col-md-3 fh">
      ${h.flb(_("E-posti teel väljastatavaid teateid"), 'd_epost')}
    </div>
    <div class="column col-md-1" id="d_epost">
      ${c.arv_epost}
    </div>
    <div class="column col-md-8">    
      % if c.arv_epost:
      ${h.submit(_("Väljasta"), id="epost")}
      ${h.btn_to(_("Näita"), h.url_current('index', naita="epost", **c.search_args), method='get')}

      ${h.submit(_("Saada testkiri"), id="testkiri")}
      ${h.text('testaadress', c.testaadress, size=50,
      title=not c.testaadress and _("testkirja saaja aadress"))}          
      % endif            
    </div>
  </div>
  % if c.on_tseis:
  <div class="form-group row">
    <div class="column col-md-3 fh">
      ${h.flb(_("Posti teel kirjana väljastatavaid teateid"), 'd_tpost')}
    </div>
    <div class="column col-md-1" id="d_tpost">
      ${c.arv_tpost}
    </div>
    <div class="column col-md-8">
      % if c.arv_tpost:
      ${h.submit(_("Väljasta"), id="tpost")}
      % endif
      % if c.arv_tpost:
      ${h.btn_to(_("Näita"), h.url_current('index', naita="tpost", **c.search_args), method='get')}
      % endif
    </div>
  </div>
  % endif
  <div class="form-group row">
    <div class="column col-md-3 fh">
      ${h.flb(_("Aadress puudub (ainult süsteemisisene teade)"), 'd_puudu')}
    </div>
    <div class="column col-md-1" id="d_puudu">
      ${c.arv_puudu}
    </div>
    <div class="column col-md-8">
      % if c.arv_puudu:
      ${h.submit(_("Väljasta"), id="puudu")}
      ${h.btn_to(_("Näita"), h.url_current('index', naita="puudu", **c.search_args))}
      % endif
    </div>
  </div>
</div>
${h.end_form()}
% endif

<% 
  c.protsessid_no_empty = True
  c.url_refresh = h.url_current('index', sessioon_id=c.sessioon_id, sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>

<div class="listdiv">
<%include file="tulemusteteavitused_list.mako"/>
</div>

