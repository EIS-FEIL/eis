<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
  c.includes['subtabs'] = True 
  c.includes['subtabs_label'] = True
%>
</%def>
<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} |
${_("Eksperthindamise tööd")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Eksperthindamine"), h.url('hindamine_eksperttood', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Hinnatavad tööd"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'ekspert' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="ekspert.tabs.mako"/>
</%def>

<%def name="subtabs_label()">
  ${h.flb(_("Hindamise liik"),'hliik')}
  <span class="brown ml-1" id="hliik">
    % if c.toimumisaeg.tulemus_kinnitatud:
    ${_("Vaide korral hindamine")}
    % else:
    ${_("IV hindamine")}
    % endif
  </span>
</%def>

${h.form_search(url=h.url('hindamine_eksperttood', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testitöö tähis"), 'tahised')}<br/>
        ${c.toimumisaeg.tahised}-${h.text('tahised', c.tahised, size=8, pattern='\d+-\d+')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppeasutus"),'kool_koht_id')}
            <%
               q = model.SessionR.query(model.Koht.id, model.Koht.nimi).\
                   filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id).\
                   join(model.Sooritus.sooritaja).\
                   join(model.Sooritaja.kool_koht)
               q = q.order_by(model.Koht.nimi).distinct()
               opt_koolid = [(k_id, k_nimi) for (k_id, k_nimi) in q.all()]
            %>
            ${h.select('kool_koht_id', c.kool_koht_id, opt_koolid, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindaja"),'h_kasutaja_id')}
        ${h.select('h_kasutaja_id', c.h_kasutaja_id, c.opt_h_kasutajad, empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("CSV"), id='csv', level=2)}
      </div>
    </div>
  </div>
</div>


<div class="gray-legend p-3">
  <div class="row filter">
  % if c.toimumisaeg.testimiskord.tulemus_kinnitatud and c.test.testiliik_kood != const.TESTILIIK_RV:
  <div class="col-md-4">
      ${h.radio('probleem', 'lahendamata', checkedif=c.probleem,
      onclick="$('#form_search').submit()",
      label=_("Lahendamata vaidlustused") + ' (%s)' % c.cnt_lahendamata)}
  </div>
  <div class="col-md-4">  
      ${h.radio('probleem', 'vaided', checkedif=c.probleem,
      onclick="$('#form_search').submit()",
      label=_("Vaidlustatud tööd") + ' (%s)' % c.cnt_vaided)}
  </div>
  <div class="col-md-4">  
      ${h.radio('probleem', 'pole', checkedif=c.probleem, 
      onclick="$('#form_search').submit()",
      label=_("Kõik testitööd"))}
  </div>
  % else:
  <div class="col-md-3">    
      ${h.radio('probleem', 'erinevus', checkedif=c.probleem,
      onclick="$('#form_search').submit()",
      label=_("Hindamiserinevused IV hindamiseta") + ' (%s)' % c.cnt_erinevus)}
  </div>
  <div class="col-md-3">      
      ${h.radio('probleem', 'pooleli', checkedif=c.probleem,
      onclick="$('#form_search').submit()",
      label=_("Lõpetamata eksperthindamised") + ' (%s)' % c.cnt_pooleli)}
  </div>
  <div class="col-md-3">      
      ${h.radio('probleem', 'ekspert', checkedif=c.probleem,
      onclick="$('#form_search').submit()",
      label=_("Eksperthindamised") + ' (%s)' % c.cnt_ekspert)}
  </div>
  <div class="col-md-3">      
      ${h.radio('probleem', 'pole', checkedif=c.probleem, 
      onclick="$('#form_search').submit()",
      label=_("Kõik testitööd"))}
  </div>
  % endif
  </div>
</div>
${h.end_form()}

${h.form_save(None)}
${h.hidden('juhus','1')}
<table  width="100%">
  <tr>
    <td>${_("Eksperthindamiste protsent")}
      <span class="brown">${h.fstr(c.ekspertprotsent)}%</span>
      % if not c.toimumisaeg.tulemus_kinnitatud:
      ${h.submit(_("Vali juhuslikult"))}
      % endif
    </td>
  </tr>
</table>
${h.end_form()}

<div class="listdiv">
<%include file="ekspert.tood_list.mako"/>
</div>
