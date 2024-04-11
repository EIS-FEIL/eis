<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="skannid.tabs.mako"/>
</%def>
<%def name="page_title()">
${_("Tellitud eksamitööd")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Skannitud eksamitööd"), h.url('muud_skannid_taotlemised'))}
${h.crumb(_("Tellitud eksamitööd"))}
</%def>
<%def name="require()">
<% c.includes['dropzone'] = True %>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"), 'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id, c.opt.testsessioon, empty=True)}

      <script>
        $(document).ready(function(){
         $('select#sessioon_id').change(function(){
           data = {'sessioon_id': $('select#sessioon_id').val(), 
                  };
           update_options(null, 
                          "${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                          null, // arg_name
                          $('select#test_id'), // target
                          data);
         });
        });
      </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Test"),'test_id')}
        ${h.select('test_id', c.test_id,
        model.Test.get_opt(c.sessioon_id),
        empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE'), empty=True)}
      </div>
    </div>
##    <div class="col-12 col-md-4 col-lg-3">
##      <div class="form-group">
##        ${h.checkbox('soovib_p', 1, checked=c.soovib_p, label=_("Tutvub Harnos"))}
##        <br/>
##        ${h.checkbox('soovib_skanni', 1, checked=c.soovib_skanni, label=_("Skannitud koopia"))}
##      </div>
##    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.checkbox('valjaotsitud', 1, checked=c.valjaotsitud, label=_("Välja otsitud"))}
        <br/>
        ${h.checkbox('valjaotsimata', 1, checked=c.valjaotsimata, label=_("Välja otsimata"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.checkbox('laaditud', 1, checked=c.laaditud, label=_("Üles laaditud"))}
        <br/>
        ${h.checkbox('laadimata', 1, checked=c.laadimata, label=_("Üles laadimata"))}
      </div>
    </div>

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
        ${h.flb(_("Taotluse esitamise kuupäev"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("kuni"), 'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("Väljasta PDF"), id='pdf')}
        ${h.submit(_("Väljasta CSV"), id='csv')}

        % if c.user.has_permission('skannid', const.BT_UPDATE):
        ${h.btn_to_dlg(_("Lisa taotlus"), h.url('muud_skannid_new_tellimine'), title=_("Eksamitööga tutvumise taotlus"), width=600)}
        % endif
      </div>
    </div>
  </div>
</div>

${h.end_form()}

${h.form_save(None)}
${h.hidden('sub', 'index')}
<div class="listdiv">
<%include file="skannid.tellimised_list.mako"/>
</div>

% if c.items:
<br/>
${h.submit(_("Salvesta väljaotsitud"))}
% endif
${h.end_form()}

