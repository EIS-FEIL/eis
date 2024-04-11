<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testisoorituskoha teadete väljastamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Päringud"))}
${h.crumb(_("Testisoorituskoha teated"), h.url('otsing_kohateated'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>

<h1>${_("Testisoorituskohateadete väljastamine")}</h1>
${h.form_search(url=h.url('otsing_kohateated'))}
${h.hidden('naita', c.naita)}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <% c.on_rv = c.on_sisse = c.on_ke = True %>
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
            <% if not c.kirityyp: c.kirityyp = model.Kiri.TYYP_SOORITUSKOHATEADE %>
            ${h.radio('kirityyp', model.Kiri.TYYP_SOORITUSKOHATEADE, checkedif=c.kirityyp, label=_("Soorituskohateade"), class_="kirityyp")}
            <br/>
            ${h.radio('kirityyp', model.Kiri.TYYP_MUU, checkedif=c.kirityyp, label=_("Muu kiri"), class_="kirityyp")}
            <script>
              $(function(){ $('input.kirityyp').click(function(){ $('.searchres').hide(); }); });
            </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        <div>${h.checkbox('kordus', 1, checked=c.kordus, label=_("Saada ka kordusteateid"))}</div>
        <div>${h.checkbox('kons', 1, checked=c.kons, label=_("Ainult konsultatsiooni soovijad"))}</div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        <div>${h.checkbox('kool', 1, checked=c.kool, label=_("Saada teated õppeasutuse poolt registreeritutele"))}</div>
        <div>${h.checkbox('ise', 1, checked=c.ise, label=_("Saada teated ise registreerinutele"))}</div>
      </div>
    </div>
    <div class="col d-flex justify-content-end filter align-items-end">
      <div class="form-group">
        ${h.submit(_("Otsi saadetavad teated"), id='saatmata')}
        ${h.button(_("Saadetud teadete ülevaade"),
        onclick="this.form.action='%s';this.form.sort.value='';this.form.submit();" % (h.url('otsing_teated')))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

% if c.arv_epost != '' and c.search_args:
<div class="searchres">
${h.form(h.url_current('create', **c.search_args), method='post', id='form_post')}



<div class="form-wrapper-lineborder">
  <div class="form-group row">
    % if c.kirityyp == model.Kiri.TYYP_MUU:
    ${h.flb3(_("Teate sisu"), 'taiendavinfo')}
    <div class="col-md-9">
      ${h.textarea('taiendavinfo', c.taiendavinfo, rows=6)}
    </div>
    % else:
    ${h.flb3(_("Täiendav info (lisatakse teatele)"), 'taiendavinfo')}
    <div class="col-md-9">
      ${h.textarea('taiendavinfo', c.taiendavinfo)}
    </div>
    % endif
  </div>
  <div class="form-group row">
    ${h.flb3(_("E-posti teel väljastatavaid teateid"),'d_epost')}
    <div class="col-md-1" id="d_epost">
      ${c.arv_epost}
    </div>
    <div class="col-md-8">
      % if c.arv_epost:
      ${h.submit(_("Väljasta"), id="epost")}
      ${h.btn_to(_("Näita"), h.url_current('index', naita="epost", **c.search_args))}
      <span class="ml-4">
        ${h.submit(_("Saada testkiri"), id="testkiri")}
        ${h.text('testaadress', c.testaadress, size=50,
        title=not c.testaadress and _("testkirja saaja aadress"))}
      </span>
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Posti teel kirjana väljastatavaid teateid"), 'd_tpost')}
    <div class="col-md-1" id="d_tpost">
      ${c.arv_tpost}
    </div>
    <div class="col-md-8">
      % if c.arv_tpost:
      ${h.submit(_("Väljasta"), id="tpost")}
      ${h.btn_to(_("Näita"), h.url_current('index', naita='tpost', **c.search_args))}            
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Aadress puudub (ainult süsteemisisene teade)"), 'd_puudu')}
    <div class="col-md-1" id="d_puudu">
      ${c.arv_puudu}
    </div>
    <div class="col-md-8">
      % if c.arv_puudu:
      ${h.submit(_("Väljasta"), id="puudu")}      
      ${h.btn_to(_("Näita"), h.url_current('index', naita='puudu', **c.search_args))}
      % endif
    </div>
  </div>
</div>

${h.end_form()}
</div>
% endif


<% 
  c.protsessid_no_empty = True
  c.url_refresh = h.url_current('index', sessioon_id=c.sessioon_id, sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>


<div class="listdiv">
<%include file="kohateated_list.mako"/>
</div>
