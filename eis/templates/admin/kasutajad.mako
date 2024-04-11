<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testide läbiviimisega seotud isikud")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Testide läbiviimisega seotud isikud"), h.url('admin_kasutajad'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("Testide läbiviimisega seotud isikud")}</h1>
${h.form_search(url=h.url('admin_kasutajad'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("E-posti aadress"),'epost')}
        ${h.text('epost', c.epost)}
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
        ${h.flb(_("Roll testis"),'roll_id')}
        <% opt_roll = c.opt.labiviijagrupp_empty + [(const.GRUPP_T_ADMIN, _("Testi administraator"))] %>
        ${h.select('roll_id', c.roll_id, opt_roll)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Roll koolis"),'kroll_id')}
        ${h.select('kroll_id', c.kroll_id, c.opt.kooligrupp, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Läbiviija tähis"),'tahis')}
        ${h.posint('tahis', c.tahis)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.checkbox('kasped', 1, checked=c.kasped, label=_("Käsitsi pedagoogiks lisatud"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testsessioon"),'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id,
        model.Testsessioon.get_opt(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 sessioon">
      <div class="form-group">    
        ${h.flb(_("Test"),'test_id')}
            <%
               opt_test = model.Test.get_opt(c.testsessioon_id or -1) or []
               if c.test_id and int(c.test_id) not in [r[0] for r in opt_test]:
                  c.test_id = None
            %>
            ${h.select('test_id', c.test_id, opt_test, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 sessioon">
      <div class="form-group">    
        ${h.checkbox('nousolek', 1, checked=c.nousolek,
        label=_("Testsessioonil/testil osalemiseks nõusoleku andnud isikud"))}
        <br/>
        ${h.checkbox('maaratud', 1, checked=c.maaratud,
        label=_("Testsessioonil/testil läbiviijaks määratud isikud"))}
      </div>
      <script>
              function change_sessioon(){
                var b = $('select#testsessioon_id').val() != '';
                $('.sessioon,input#ametikohad').toggle(b);
                if(b && ($('input#nousolek,input#maaratud').filter(':checked').length==0))
                   $('input#maaratud').prop('checked', true);
              }
              $(document).ready(function(){
                 $('select#testsessioon_id').change(
                 callback_select("${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                                'sessioon_id', 
                                $('select#test_id')));
                 change_sessioon();
                 $('select#testsessioon_id').change(change_sessioon);
              });
      </script>
    </div>
  </div>
  <div class="d-flex justify-content-end align-items-end">
    <div class="form-group">
      ${h.btn_search()}
      ${h.btn_new(h.url('admin_new_kasutaja'))}
      ${h.btn_to(_("Uuenda EHISest"), h.url('admin_kasutajad_ehisopetajad'), level=2)}
      ${h.submit(_("Väljasta CSV"), id="csv", level=2)}
      
      <span style="float:right">
        ${h.btn_to(_("Koolituste laadimine"), h.url('admin_koolitused'), level=2)}
        ${h.btn_to(_("Käskkirja laadimine"), h.url('admin_kaskkirjad'), level=2)}
        ${h.btn_to(_("Läbiviijate laadimine"), h.url('admin_labiviijalaadimine'), level=2)}
      </span>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  <%include file="kasutajad_list.mako"/>
</div>
