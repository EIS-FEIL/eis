## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Avalike ülesannete lahendamine")}
</%def>
<%def name="require()">
<meta name="description" content="E-ülesanded õppuritele harjutamiseks"/>
</%def>
<%def name="breadcrumbs()">
##${h.crumb(_("Avalikud ülesanded"))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'lahendamine' %>
</%def>

<h1>${_("Avalikud ülesanded")}</h1>
${h.form_search(url=h.url('lahendamine'))}

<div class="gray-legend p-3 filter-w">

  <div class="row">
    <div class="col-12 col-md-4 col-lg-3 filter">
      <div class="form-group">
        ${h.flb(_("ID"), 'id')}
        ${h.posint('id', c.id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.aine)}">
      <div class="form-group">
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.aste)}">
      <div class="form-group">
        ${h.flb(_("Kooliaste"),'aste')}
        ${h.select('aste', c.aste, c.opt.klread_kood('ASTE', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.kvaliteet)}">
      <div class="form-group">
        ${h.flb(_("Kvaliteedimärk"),'kvaliteet')}
        ${h.select('kvaliteet', c.kvaliteet, c.opt.klread_kood('KVALITEET'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.teema)}">
      <div class="form-group">
        ${h.flb(_("Teema"),'teema')}
        ${h.select('teema', c.teema,
          c.opt.klread_kood('TEEMA',c.aine,empty=True,ylem_required=True), names=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.alateema)}">
      <div class="form-group">
        ${h.flb(_("Alateema"),'alateema')}
        ${h.select('alateema', c.alateema,
        c.opt.klread_kood('ALATEEMA',ylem_id=c.teema_id, ylem_required=True,empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.ylkogu_id)}">
      <div class="form-group">
        ${h.flb(_("E-kogu"),'ylkogu_id')}
        ${h.select('ylkogu_id', c.ylkogu_id, c.opt.ylkogud(c.aine, avalik_y=True, pedagoog=c.user.on_pedagoog),empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.testiliik)}">
      <div class="form-group">
        ${h.flb(_("Testi liik"),'testiliik')}
        ${h.select('testiliik', c.testiliik,
        c.opt.klread_kood('TESTILIIK', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.keeletase)}">
      <div class="form-group">
        ${h.flb(_("Keeleoskuse tase"),'keeletase')}
        ${h.select('keeletase', c.keeletase, c.opt.klread_kood('KEELETASE', ylem_kood=c.aine, ylem_required=True, empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.lang)}">
      <div class="form-group">    
        ${h.flb(_("Keel"),'lang')}
        ${h.select('lang', c.lang, c.opt.klread_kood('SOORKEEL', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.kysimus)}">
      <div class="form-group">        
        ${h.flb(_("Ülesandetüüp"),'kysimus')}
        ${h.select('kysimus', c.kysimus, c.opt.interaction_empty)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
        ${h.toggle_filter(True)}        
        ${h.btn_search()}
    </div>
  </div>
</div>

  <script>
      $(function(){

         $('select#aine').change(function(){update_teema();});
         $('select#aste').change(function(){update_teema();});
         $('select#teema').change(function(){update_alateema();});
         $('select#aine').change(
           callback_select("${h.url('pub_formatted_valikud', kood=c.user.on_pedagoog and 'YLKOGUyp' or 'YLKOGUya', format='json')}", 
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
           var subtarget = $('select#alateema');
           update_options(aine_field, url, 'ylem_kood', target, data, subtarget, true);
      }
      function update_alateema()
      {
           var teema_id = $('select#teema option:selected').attr('name');
           if(teema_id)
           {
              var url = "${h.url('pub_formatted_valikud', kood='ALATEEMA',format='json')}";
              var target = $('select#alateema');
              var data = {ylem_id: teema_id};
              update_options(null, url, null, target, data);
           }
      }
  </script>

${h.end_form()}

<div class="listdiv">
<%include file="avalikotsing_list.mako"/>
</div>
