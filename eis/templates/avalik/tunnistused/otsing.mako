<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eksamitunnistused")}
</%def>      
<%def name="breadcrumbs()">
% if c.user.is_authenticated:
${h.crumb(_("Muud"))}
${h.crumb(_('Eksamitunnistused'), h.url('tunnistused'))}
% endif
</%def>
<%def name="active_menu()">
<% c.menu1 = c.user.is_authenticated and 'muud' or 'tunnistused' %>
</%def>

<h1>${_("Eksamitunnistused")}</h1>

${h.form_search(url=h.url('tunnistused'))}
<div class="gray-legend p-3 filter-w">

% if c.user.id:
<ul class="nav nav-pills" role="tablist">
  <li class="nav-item" role="tab" aria-controls="tab1"
      aria-selected="${not c.minu and 'true' or 'false'}">
    <a class="nav-item nav-link ${not c.minu and 'active' or ''}"
      id="first-tab" data-toggle="tab" href="#tab1">${_("Tunnistused")}</a>
  </li>
  <li class="nav-item" role="tab" aria-controls="tab2"
      aria-selected="${c.minu and 'true' or 'false'}">
    <a class="nav-item nav-link ${c.minu and 'active' or ''}"
      onclick="$('#minu').click()"
      id="second-tab" data-toggle="tab" href="#tab2">${_("Minu tunnistused")}</a>
  </li>
</ul>
<div class="tab-content" id="ttabs">
  <div class="tab-pane rounded-0 border-0 fade ${not c.minu and 'show active' or ''}"
    id="tab1"
    role="tabpanel"
    aria-labelledby="first-tab">
    ${self.filter()}
  </div>
  <div class="tab-pane rounded-0 border-0 fade ${c.minu and 'show active' or ''}"
    id="tab2"
    role="tabpanel"
    aria-labelledby="second-tab">
    ${h.submit(_('Näita'), id='minu', style="display:none")}
  </div>
</div>
% else:
${self.filter()}
% endif

</div>
${h.end_form()}

<br/>

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid tunnistusi ei leitud")}
  % elif c.items:
  <%include file="otsing_list.mako"/>
  % endif 
</div>

<%def name="filter()">
  ${h.rqexp(True)}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"), 'isikukood', rq=True)}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Tunnistuse nr"), 'tunnistusenr', rq=True)}
        ${h.text('tunnistusenr', c.tunnistusenr)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Sisesta pildil kuvatud kood"), 'captcha', rq=True)}
        <div class="d-flex">
          ${h.text('captcha', '')}<br/>
          ${h.image(h.url('tunnistused', sub='captcha'), alt='CAPTCHA')}
        </div>
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
      ${h.btn_search()}
      </div>
    </div>
  </div>
</%def>
