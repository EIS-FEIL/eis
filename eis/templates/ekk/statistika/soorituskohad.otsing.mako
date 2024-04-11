<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Soorituskohad")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Soorituskohad")}</h1>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Piirkond"),'piirkond_id')}
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
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
     var target = $('select#koht_id');
     update_options(null, url, null, target, data, null, true);
  }
</script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Asukoht"),'koht_id')}
<% 
   if c.maakond_kood:
      opt_kohad = model.Aadresskomponent.get_by_tasekood(c.maakond_kood).get_soorituskoht_opt()
   else:
      opt_kohad = model.Koht.get_soorituskoht_opt()
%>
        ${h.select('koht_id', c.koht_id, opt_kohad, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testsessioon"),'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id,
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
        ${h.flb(_("Testi nimetus"),'test_nimi')}
        ${h.text('test_nimi', c.test_nimi)}
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
            model.Testimiskord.get_opt(c.testsessioon_id, c.testiliik, c.test_id), empty=True)}

      <script>
        $(function(){
         $('select#testiliik').change(function(){
           $('#test_id').val('');
         });
         $('#test_id').change(function(){
           $('#testiliik').val('');
         });
         $('select#testsessioon_id,select#testiliik,input#test_id').change(function(){
           data = {'sessioon_id': $('select#testsessioon_id').val(), 
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
        ${h.flb(_("Registreerimise viis"),'regviis')}
        ${h.checkbox('regviis', value=const.REGVIIS_SOORITAJA, checkedif=c.regviis,
        label=_("Sooritaja (EISi kaudu)"))}
        ${h.checkbox('regviis', value=const.REGVIIS_XTEE, checkedif=c.regviis,
        label=_("Sooritaja (eesti.ee kaudu)"))}
        ${h.checkbox('regviis', value=const.REGVIIS_KOOL_EIS, checkedif=c.regviis,
        label=_("Õppeasutus (EISi kaudu)"))} 
        ${h.checkbox('regviis', value=const.REGVIIS_EKK, checkedif=c.regviis, 
        label=_("Eksamikeskus"))}
      </div>
    </div>
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">    
        ${h.checkbox('sooritajad',1,checked=c.sooritajad, 
        label=_("Näita sooritajate arvu"))}  
        <br/>
        ${h.checkbox('suunatudkoolid',1,checked=c.suunatudkoolid, 
        label=_("Näita koos suunatud koolidega"))}  
        <br/>
        ${h.checkbox('vaatlejad',1,checked=c.vaatlejad, 
        label=_("Näita vaatlejate arvu"))}  
        <br/>
        ${h.checkbox('ruumid',1,checked=c.ruumid, 
        label=_("Näita ruumide arvu päevade lõikes"))}  
      </div>
    </div>
  <div class="col d-flex justify-content-end align-items-end">
    <div class="form-group">
      ${h.btn_search()}
      ${h.submit(_("PDF"), id='pdf', level=2)}
      ${h.submit(_("CSV"), id='csv', level=2)}      
    </div>
  </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid andmeid ei leitud")}
  % elif c.items:
  <%include file="soorituskohad.list.mako"/>
  % endif 
</div>
