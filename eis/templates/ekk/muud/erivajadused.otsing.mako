<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eritingimuste andmete väljastamine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>
<h1>${_("Eritingimused")}</h1>
${h.form_search(url=h.url('muud_erivajadused'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testisessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id, c.opt_sessioon)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Toimumisaeg"), 'tahis')}
        ${h.text('tahis', c.tahis)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppeaine"),'aine_kood')}
        ${h.select('aine_kood', c.aine_kood, c.opt.klread_kood('AINE'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi ID"),'test_id')}
        ${h.posint('test_id', c.test_id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Maakond"),'maakond_kood')}
        ${h.select('maakond_kood', c.maakond_kood,
            model.Aadresskomponent.get_opt(None),
            empty=True,onchange="changed_maakond()")}
<script>
  function changed_maakond()
  {
     var url = "${h.url('pub_formatted_valikud', kood='SOORITUSKOHT',format='json')}";
     var data = {ylem_tasekood: $('select#maakond_kood').val()};
     var target = $('select.koht_id');
     update_options(null, url, null, target, data, null, true);
  }
</script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Soorituskoht"),'soorituskoht_id')}
<% 
   if c.maakond_kood:
      opt_kohad = model.Aadresskomponent.get_by_tasekood(c.maakond_kood).get_soorituskoht_opt()
   else:
      opt_kohad = model.Koht.get_soorituskoht_opt()
%>
        ${h.select('soorituskoht_id', c.soorituskoht_id, opt_kohad, empty=True, class_='koht_id')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppimiskoht"),'oppimiskoht_id')}
        ${h.select('oppimiskoht_id', c.oppimiskoht_id, opt_kohad, empty=True, class_='koht_id')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Eritingimus"),'erivajadus')}
        ${h.select('erivajadus', c.erivajadus, c.opt.erivajadused, empty=True, multiple=True)}
      </div>
    </div>
  </div>
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.checkbox('kinnitatud', 1, checked=c.kinnitatud,
        label=_("Näita ainult kinnitatuid"),
        onchange="$('input#kinnitamata').prop('checked',false);")}
        <br/>
        ${h.checkbox('kinnitamata', 1, checked=c.kinnitamata,
        label=_("Näita ainult kinnitamata"),
        onchange="$('input#kinnitatud').prop('checked',false);")}            
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.checkbox('vaadatud', 1, checked=c.vaadatud,
        label=_("Näita ainult üle vaadatuid"),
        onchange="$('input#vaatamata').prop('checked',false);")}
        <br/>
        ${h.checkbox('vaatamata', 1, checked=c.vaatamata,
        label=_("Näita ainult üle vaatamata"),
        onchange="$('input#vaadatud').prop('checked',false);")}            
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.checkbox('kordus', 1, checked=c.kordus, label=_("Saada ka kordusteateid"))}
      </div>
    </div>

    <div class="col d-flex justify-content-end filter align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("Excel"), id='xls', class_="filter", level=2)}
        ${h.submit(_("Saada teated"), id='mail', level=2)}
      </div>
    </div>
  </div>    
</div>
${h.end_form()}

<div class="listdiv">
<%include file="erivajadused.otsing_list.mako"/>
</div>
