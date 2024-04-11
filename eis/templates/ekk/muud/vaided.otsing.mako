<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Vaided")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

<h1>${_("Vaided")}</h1>
${h.form_search(url=h.url('muud_vaided'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testisessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id, c.opt.testsessioon, empty=True)}

      <script>
        $(function(){
         $('select#sessioon_id').change(function(){
           data = {'sessioon_id': $('select#sessioon_id').val(), 
                  };
           update_options(null, 
                          "${h.url('pub_formatted_valikud', kood="TEST", format='json')}", 
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
        ${h.select('test_id', c.test_id, model.Test.get_opt(c.sessioon_id), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE'), empty=True, onchange="onchange_aine()")}
            <script>
              function onchange_aine()
              {
              var url="${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}";
              var target=$('select#keeletase');
              update_options($('#aine'), url, 'ylem_kood', target);
              }
            </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Keeleoskuse tase"),'keeletase')}
        ${h.select('keeletase', c.keeletase,
        c.opt.klread_kood('KEELETASE', ylem_kood=c.aine,
        ylem_required=True, empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Vaide olek"),'staatus')}
        ${h.select('staatus', c.staatus, c.opt.V_STAATUS_OPT, empty=True)}
        <script>
          $('select#staatus').change(function(){
           $('div.menetlemisel').toggleClass('invisible',$(this).val()!='${const.V_STAATUS_MENETLEMISEL}');
          });
        </script>
      </div>
    </div>
    <% mcls = c.staatus != const.V_STAATUS_MENETLEMISEL and 'invisible' or '' %>
    <div class="col-12 col-md-4 col-lg-3 ${mcls} menetlemisel">
      <div class="form-group">
        ${h.checkbox('valjaotsitud', 1, checked=c.valjaotsitud, label=_("Välja otsitud"))}
        <br/>
        ${h.checkbox('valjaotsimata', 1, checked=c.valjaotsimata, label=_("Välja otsimata"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${mcls} menetlemisel">
      <div class="form-group">
        ##${h.checkbox('hinnatud', 1, checked=c.hinnatud, label=_("Hinnatud"))}
        ##<br/>
        ${h.checkbox('hindamata', 1, checked=c.hindamata, label=_("Hindamata"))}
        <br/>
        ${h.checkbox('eelnouta', 1, checked=c.eelnouta, label=_("Hinnatud, eelnõu loomata"))}
        <br/>
        ${h.checkbox('arakuulamisel', 1, checked=c.arakuulamisel, label=_("Otsuse eelnõu ärakuulamisel"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${mcls} menetlemisel">
      <div class="form-group">    
        ${h.checkbox('allkirjastatud', 1, checked=c.allkirjastatud, label=_("Allkirjastatud"))}
        <br/>
        ${h.checkbox('allkirjastamata', 1, checked=c.allkirjastamata, label=_("Allkirjastamata"))}
      </div>
    </div>
  </div>
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
        ${h.flb(_("Esitamise kuupäev"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>

    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        <span class="filter">
      ${h.submit(_("Väljasta PDF"), id='pdf', class_="filter", level=2)}
      ${h.submit(_("Väljasta CSV"), id='csv', class_="filter", level=2)}
      ${h.submit(_("Vaidlustatud tulemuste hindajad (CSV)"), id='hindajad_csv', level=2)}
      ${h.btn_search()}
      </span>
      <script>
        $(function(){
          $('#hindajad_csv').toggle($('#test_id').val()!='');
          $('#test_id').change(function(){
             $('#hindajad_csv').toggle($('#test_id').val()!='');
          });
        });
      </script>

      % if c.user.has_permission('vaided', const.BT_UPDATE):
      ${h.btn_to(_("Lisa vaie"), h.url('muud_new_vaie'))}
      % endif
      </div>
    </div>
  </div>
</div>
${h.end_form()}

${h.form_save(None)}
${h.hidden('sub', 'index')}
<div class="listdiv">
<%include file="vaided.otsing_list.mako"/>
</div>

% if c.items:
<br/>
${h.button(_("Vali kõik"), onclick="$('input.vaie_id').prop('checked', true);")}
${h.button(_("Tühista valik"), onclick="$('input.vaie_id').prop('checked', false);")}
${h.submit(_("Salvesta väljaotsitud"))}
% endif
${h.end_form()}
