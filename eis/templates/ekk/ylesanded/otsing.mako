<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Ülesandepank")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<h1>${_("Ülesandepank")}</h1>
${h.form_search(url=h.url('ylesanded'))}

<div class="gray-legend p-3 filter-w">

  <div class="row">
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 filter">
      <div class="form-group">
        ${h.flb(_("ID"),'id')}
        ${h.text('idr', c.idr)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.alates)}">
      <div class="form-group">
        ${h.flb(_("Loodud alates"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.kuni)}">
      <div class="form-group">
        ${h.flb(_("Loodud kuni"),'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.marksona)}">
      <div class="form-group">
        ${h.flb(_("Märksõna"),'marksona')}
        ${h.text('marksona', c.marksona)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.koostaja)}">
      <div class="form-group">
        ${h.flb(_("Koostaja"),'koostaja')}
        ${h.text('koostaja', c.koostaja)}
      </div>
    </div>

    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.vastvorm)}">
      <div class="form-group">
        ${h.flb(_("Vastamise vorm"),'vastvorm')}
        <% opt_vahendid = model.Abivahend.get_opt() %>
        ${h.select('vastvorm', c.vastvorm, opt_vahendid, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.vahend)}">
      <div class="form-group">
        ${h.flb(_("Vahend"),'vahend')}
        ${h.select('vahend', c.vahend, c.opt.klread_kood('VAHEND', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.kvaliteet)}">
      <div class="form-group">
        ${h.flb(_("Kvaliteedimärk"),'kvaliteet')}
        ${h.select('kvaliteet', c.kvaliteet, c.opt.klread_kood('KVALITEET'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.aine)}">
      <div class="form-group">
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.aste)}">
      <div class="form-group">
        ${h.flb(_("Kooliaste"),'aste')}
        ${h.select('aste', c.aste, c.opt.astmed(), empty=True)}        
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.teema)}">
      <div class="form-group">
        ${h.flb(_("Teema"),'teema')}
        ${h.select('teema', c.teema, 
        c.opt.klread_kood('TEEMA',c.aine,ylem_required=True,bit=c.opt.aste_bit(c.aste, c.aine),empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.alateema)}">
      <div class="form-group">
        ${h.flb(_("Alateema"),'alateema')}
        ${h.select('alateema', c.alateema, c.opt.klread_kood('ALATEEMA',ylem_id=c.teema_id,ylem_required=True,bit=c.opt.aste_bit(c.aste, c.aine),empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.opitulemus_id)}">
      <div class="form-group">
        ${h.flb(_("Õpitulemus"),'opitulemus_id')}
        <% opt_opitulemus = c.opt.opitulemused(c.aine, False) %>
        ${h.select2('opitulemus_id', c.opitulemus_id, opt_opitulemus, empty=True, allowClear=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.mote)}">
      <div class="form-group">
        ${h.flb(_("Mõtlemistasand"),'mote')}
        ${h.select('mote', c.mote, c.opt.klread_kood('MOTE', empty=True))}    
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.ylkogu_id)}">
      <div class="form-group">
        ${h.flb(_("E-kogu"),'ylkogu_id')}
        ${h.select('ylkogu_id', c.ylkogu_id, c.opt.ylkogud(c.aine),empty=True)}        
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.oskus)}">
      <div class="form-group">
        ${h.flb(_("Oskus"),'oskus')}
        ${h.select('oskus', c.oskus, c.opt.klread_kood('OSKUS',c.aine,ylem_required=True,empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.keeletase)}">
      <div class="form-group">
        ${h.flb(_("Keeleoskuse tase"),'keeletase')}
        ${h.select('keeletase', c.keeletase, c.opt.klread_kood('KEELETASE',ylem_kood=c.aine,ylem_required=True,empty=True))}    
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.lang)}">
      <div class="form-group">
        ${h.flb(_("Keel"),'lang')}
        ${h.select('lang', c.lang, c.opt.klread_kood('SOORKEEL', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 col-xl-2 ${h.hidefilter(c.kysimus)}">
      <div class="form-group">
        ${h.flb(_("Ülesandetüüp"),'kysimus')}
          <%
            opt_i = c.opt.interaction_empty
            if c.is_debug or c.is_devel:
               opt_i = opt_i + c.opt.interaction_block
          %>
          ${h.select('kysimus', c.kysimus, opt_i)}
      </div>
    </div>
  </div>
  <div class="row">
    <%
      koik_st = c.opt.klread_kood('Y_STAATUS')
      s_st_av = list(map(str, const.Y_ST_AV))
      opt_staatus = []
      if c.user.has_permission('ylesanded', const.BT_INDEX, gtyyp=const.USER_TYPE_EKK):
         opt_staatus.extend([r for r in koik_st if r[0] not in s_st_av])
      if c.user.has_permission('ylesanded', const.BT_INDEX, gtyyp=const.USER_TYPE_AV):
         opt_staatus.extend([r for r in koik_st if r[0] in s_st_av])
    %>
    % for value, label, o_id in opt_staatus:
    <% checked = value in map(str, c.staatus or []) %>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(checked)}">
      <div class="form-group my-0">
        ${h.checkbox('staatus', value, label, checked=checked)}
      </div>
    </div>
    % endfor
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.ptest)}">
      <div class="form-group my-0">
            ${h.checkbox('ptest', 1, checked=c.ptest, label=_("P-testiks sobivad"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.etest)}">
      <div class="form-group my-0">    
        ${h.checkbox('etest', 1, checked=c.etest, label=_("E-testiks sobivad"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.adaptiivne)}">
      <div class="form-group my-0">    
        ${h.checkbox('adaptiivne', 1, checked=c.adaptiivne, label=_("Adaptiivseks testiks sobivad"))}
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col d-flex flex-wrap justify-content-end align-items-end">
      <div class="flex-grow-1">
      % if   c.user.has_permission('yhisfailid', const.BT_UPDATE):
      ${h.btn_to(_("Ühised failid"), h.url('ylesanne_yhisfailid'), level=2)}
      % endif
      % if c.user.has_permission('ylesanded', const.BT_CREATE, gtyyp=const.USER_TYPE_EKK):
      ${h.btn_to(_("Impordi"), h.url('ylesanded_import'), level=2)}
      ${h.btn_to(_("Uus p-testi ülesanne"), h.url('ylesanne_new_psisu'), level=2)}
      % endif
      % if c.user.has_permission('ylesanded', const.BT_CREATE):
      ${h.btn_new(h.url('new_ylesanne'))}
      % endif      
      </div>
      ${h.toggle_filter(True)}
      ${h.submit(_("CSV"), id='csv', level=2)}
      ${h.btn_search()}
    </div>
    </div>
  </div>
</div>  


      <script>
      $(function(){
         ## yldandmete lipikul aine muutmisel muudetagu valdkondade valikud
         $('select#aine').change(function(){update_teema(); update_opitulemus();});
         $('select#teema').change(function(){update_alateema();});
         $('select#aine').change(
           callback_select("${h.url('pub_formatted_valikud', kood='OSKUS', format='json')}", 
                           'ylem_kood', 
                           $('select#oskus'))
           );
         $('select#aine').change(
           callback_select("${h.url('pub_formatted_valikud', kood='YLKOGU', format='json')}", 
                           'aine', 
                           $('select#ylkogu_id'))
           );
         $('select#aine').change(
           callback_select("${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}", 
                           'ylem_kood', 
                           $('select#keeletase'))
           );
      });

      function update_teema()
      {
           var aine_field = $('select#aine');
           var aste_kood = $('select#aste').val();
           var url = "${h.url('pub_formatted_valikud', kood='TEEMA', format='json')}";
           var data = {aste: aste_kood};
           var target = $('select#teema');
           var subtarget = $('select#alateema,select#opitulemus_id');
           update_options(aine_field, url, 'ylem_kood', target, data, subtarget, true);
      }
      function update_alateema()
      {
           var teema_id = $('select#teema option:selected').attr('name');
           if(teema_id)
           {
              var aine_kood = $('select#aine').val();
              var aste_kood = $('select#aste').val();      
              var url = "${h.url('pub_formatted_valikud', kood='ALATEEMA', format='json')}";
              var data = {ylem_id: teema_id, aste: aste_kood, aine: aine_kood};
              var target = $('select#alateema');
              update_options(null, url, null, target, data);
           }
      }
      function update_opitulemus()
      {
      var aine_kood = $('select#aine').val();
      var url = "${h.url('pub_formatted_valikud', kood='OPITULEMUS', format='json')}";
      var data = {aine: aine_kood};
      var target = $('select#opitulemus_id');
      update_options(null, url, null, target, data);
      }     
    </script>


${h.end_form()}

<div class="listdiv">
<%include file="otsing_list.mako"/>
</div>
