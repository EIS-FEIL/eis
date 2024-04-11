<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testidele registreerimine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

<h1>${_("Registreerimine")}</h1>
${h.form_search(url=h.url('regamised'))}

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood)}
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
        ${h.checkbox('erivajadused', 1, checked=c.erivajadused, 
        label=_("Näita eritingimusi"))}
        ${h.checkbox('lisatingimused', 1, checked=c.lisatingimused, 
        label=_("Näita lisatingimusi"))}            
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id,
        c.opt.testsessioon, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi liik"),'testiliik')}
        ${h.select('testiliik', c.testiliik, c.opt.testiliik, empty=True)}
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
        ${h.flb(_("Testimiskord"),'testimiskord_id')}
        ${h.select('testimiskord_id', c.testimiskord_id,
            model.Testimiskord.get_opt(c.sessioon_id, c.testiliik, c.test_id),
            empty=True)}
      <script>
        $(function(){
         $('select#testiliik').change(function(){
           $('#test_id').val('');
         });
         $('#test_id').change(function(){
           $('#testiliik').val('');
         });
         $('select#sessioon_id,select#testiliik,input#test_id').change(function(){
           data = {'sessioon_id': $('select#sessioon_id').val(), 
                   'testiliik':$('select#testiliik').val(),
                   'test_id':$('#test_id').val()
                  };
           update_options(null, 
                          "${h.url('pub_formatted_valikud', kood='TESTIMISKORD', format='json')}", 
                          null, // arg_name
                          $('select#testimiskord_id'), // target
                          data);
         });
        });
      </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Registreerinud kool"),'kool_id')}
        ${h.select('kool_id', c.kool_id,
        model.Koht.get_soorituskoht_opt(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">
        ${h.flb(_("Registreerimise aeg"),'reg_alates')}
        <div class="row">
          <div class="col-md-5">
            ${h.date_field('reg_alates', h.str_from_date(c.reg_alates))}
          </div>
          <div class="col-md-1">
            ${_("kuni")}
          </div>
          <div class="col-md-5">
            ${h.date_field('reg_kuni', h.str_from_date(c.reg_kuni))}
          </div>
        </div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
            ${h.checkbox('regamata', 1, checked=c.regamata, 
            label=_("Näita ainult pooleli registreeringuid"))}
            <br/>
            ${h.checkbox('tasumata', 1, checked=c.tasumata, 
            label=_("Näita ainult tasumise kinnitamise ootel"))}
            <br/>
            ${h.checkbox('tyhistatud', 1, checked=c.tyhistatud, 
            label=_("Näita ainult tühistatud registreeringuid"))}
      </div>
    </div>
  </div>
  <div class="d-flex flex-wrap justify-content-end align-items-end">    
    <div class="flex-grow-1">
        % if c.regamata:
        <span id="b_regamata" style="display:none" class="mr-2">
        ${h.button(_("Kinnita registreerimine"), id="kinnita", level=2)}
        ${h.checkbox('regteade2', 1, checked=True, class_="regteade2", label=_("Saada registreerimise teade"))}
        </span>
        % endif

        % if c.tasumata:
        ${h.btn_to_dlg(_("Saada meeldetuletus"), h.url('regamine_new_meeldetuletus'), id="b_tasumata",
        title=_("Saada meeldetuletus"), form="$('form#form_list')", width=800, level=2, style="display:none")}
        % endif

      ${h.btn_to(_("Sisesta registreerimise avaldus"), h.url('regamine_new_avaldus'),
      class_=c.focus_avaldus and 'initialfocus' or None)}
      ${h.btn_to(_("Laadi registreerimise nimistu"), h.url('regamine_nimistu_testivalik'),
      class_=c.focus_nimistu and 'initialfocus' or None)}
    </div>
    <div>
      ${h.submit(_("Excel"), id='xls', class_="filter", level=2)}
      ${h.btn_search()}
    </div>
  </div>
</div>

${h.end_form()}

% if c.regamata:
<script>
  $('#kinnita').click(function(){
  var fl = $('form#form_list');
  fl.find('input.regteade').val($('input.regteade2').prop('checked') ? '1' : '');
  open_dialog({'title':"${_("Kinnitamine")}", 'url': "${h.url_current('create', sub='kinnitamine')}", 'form': fl, 'method': 'post'});
  });
</script>
% endif

<div class="listdiv">
<%include file="otsing_list.mako"/>
</div>
