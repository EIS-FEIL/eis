<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testitulemuste avaldamine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>
<h1>${_("Tulemuste avaldamine")}</h1>
${h.form_search(url=h.url('muud_tulemused'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    ${h.flb3(_("Testsessioon"), 'sessioon_id', 'text-md-right')}
    <div class="col-md-9">
      ${h.select('sessioon_id', c.sessioon_id, c.opt_sessioon,
      onchange="this.form.submit()", wide=False)}
    </div>
  </div>
</div>
${h.end_form()}

${h.form_save(None)}
${h.hidden('sessioon_id', c.sessioon_id)}
${h.hidden('op', '')}
% if c.debug:
${h.hidden('debug',c.debug)}
% endif
<div class="listdiv">
<%include file="tulemused_list.mako"/>
</div>

<div id="add" class="d-none mb-4">
% if c.user.has_permission('tulemusteavaldamine', const.BT_UPDATE):
<div class="d-flex flex-wrap my-3">
  <div class="flex-grow-1">
    ${self.teavitamine()}
  </div>
  <div>
    ${h.btn_to_dlg(_("Muuda avaldamist"), h.url('muud_new_tulemus'), 
    title=_("Muuda avaldamist"), width=450, form="$('form#form_save')", id='avaldamine',
    confirm=_("Selle nupu vajutamisega saad muuta valitud testimiskordade tulemused avalikuks. Kas soovid jätkata?"))}
  </div>
</div>
% endif
</div>

${h.end_form()}

<% 
  c.protsessid_no_empty = True
  c.url_refresh = h.url_current('index', sessioon_id=c.sessioon_id, sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>

<%def name="teavitamine()">
<ul class="nav nav-pills">
  <li class="nav-item">
    <a class="nav-item nav-link active" id="first-tab" data-toggle="tab"
       aria-selected="true"       
       href="#tab1" role="tab" aria-controls="tab1" aria-selected="true">
      ${_("Sooritajate teavitamine")}
    </a>
  </li>
  <li class="nav-item">
    <a class="nav-item nav-link" id="second-tab" data-toggle="tab"
      href="#tab2" role="tab" aria-controls="tab2" aria-selected="false">
      ${_("Koolide teavitamine")}
    </a>
  </li>
</ul>
<div class="tab-content " id="exampleTabs">
  <div class="tab-pane rounded-0 border-0 fade show active"
    id="tab1" role="tabpanel"  aria-labelledby="first-tab">

    <div class="row mb-2">
      ${h.flb(_("E-post"), 'd_epost', 'col-md-2 col-lg-1')}
      <div class="col-md-10 col-lg-11" id="d_epost">
        ${h.submit_confirm(_("Saada e-postiga teated"), id='epost', class_="mr-1",
        confirm=_("Kas oled kindel, et soovid teavitusi saata?"), level=2)}
        ${h.submit(_("Saada testkiri (e-post)"), id='testkiri', class_="mr-3", level=2)}
        ${h.text('testaadress', c.testaadress, size=50,
        title=not c.testaadress and _("testkirja saaja aadress"))}
      </div>
    </div>

  </div>
  <div class="tab-pane rounded-0 border-0 fade"
    id="tab2" role="tabpanel" aria-labelledby="second-tab">
    <div class="row">
      ${h.flb(_("E-post"), 'd_kool', 'col-md-2 col-lg-1')}
      <div class="col-md-10 col-lg-11" id="d_kool">
        ${h.submit_confirm(_("Saada teated koolidele"), id='kool', class_="mr-1",
        confirm=_("Kas oled kindel, et soovid teavitusi saata?"), level=2)}
      </div>
    </div>

  </div>
</div>
</%def>
