<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Läbiviijate aruanded")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Läbiviijate aruanded")}</h1>

${h.form_search(url=h.url('otsing_labiviijad'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi liik"),'testiliik')}
            <% 
               opt_testiliik = c.opt.testiliik
               if not c.testiliik: c.testiliik = [opt_testiliik[0][0]]
            %>
            ${h.select('testiliik', c.testiliik, opt_testiliik, multiple=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testsessioon"),'sessioon_id')}
            <% 
               opt_sessioon = model.Testsessioon.get_opt(c.testiliik)
               if c.sessioon_id:
                  c.sessioon_id = [r1 for r1 in c.sessioon_id if r1 and int(r1) in [r[0] for r in opt_sessioon]]
            %>
            ${h.select('sessioon_id', c.sessioon_id, opt_sessioon, empty=True, multiple=True)}
       <script>
         function fix_liik(){
           ## TE,SE ei saa koos teistega valida - eemaldame muud valikud
           for(v in {'${const.TESTILIIK_SEADUS}':1, '${const.TESTILIIK_TASE}': 2})
           {
              if($('select#testiliik option[value="' + v + '"]').prop('selected'))
              {
                 $('select#testiliik option:selected').filter(function(){
                     return ($(this).val() != v);
                 }).prop('selected',false);
                 break;
              }
           }
         }
        $(function(){
        $('select#testiliik').change(
           ## sessiooni valikute uuendamine
           callback_select("${h.url('pub_formatted_valikud', kood='SESSIOON', format='json')}", 
                           null,
                           $('select#sessioon_id'),
                           function(){ fix_liik(); return {'testiliik[]':$('#testiliik').val()};}));
         $('select#sessioon_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                           'sessioon_id', 
                           $('select#test_id'),
         function(){return {'testiliik[]':$('#testiliik').val()};}));
         $('select#test_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TOIMUMISAEG', format='json')}", 
                           'test_id', $('select#toimumisaeg_id'),
                           function(){return {'testiliik[]':$('#testiliik').val(), sessioon_id:$('select#sessioon_id').val()}}));
        });
      </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Test"),'test_id')}
            <%
               opt_test = model.Test.get_opt(testsessioonid_id=c.sessioon_id or [-1], keeletase=c.keeletase) or []
               if c.test_id and int(c.test_id) not in [r[0] for r in opt_test]:
                  c.test_id = None
            %>
            ${h.select('test_id', c.test_id, opt_test, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Toimumisaeg"),'toimumisaeg_id')}
        <%
          opt_ta = model.Toimumisaeg.get_opt(None,
                                             testsessioonid_id=c.sessioon_id or [-1],
                                             test_id=c.test_id or -1,
                                             keeletase=c.keeletase)
        %>
        ${h.select('toimumisaeg_id', c.toimumisaeg_id, opt_ta or [], empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
          ${h.flb(_("Isikukood"),'isikukood')}
          ${h.text('isikukood', c.isikukood, maxlength=50)}
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
        ${h.flb(_("Alates"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
                  ${h.checkbox('grupp_id', const.GRUPP_HINDAJA_K, 
                  checkedif=c.grupp_id, label=_("Hindajad (kirjalik)"))}
                  <br/>
                  ${h.checkbox('grupp_id', const.GRUPP_HINDAJA_S,
                  checkedif=c.grupp_id, label=_("Hindajad (suuline I)"))}
                  <br/>
                  ${h.checkbox('grupp_id', const.GRUPP_HINDAJA_S2,
                  checkedif=c.grupp_id, label=_("Hindajad (suuline II-...)"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
                  ${h.checkbox('grupp_id', const.GRUPP_INTERVJUU, checkedif=c.grupp_id, label=_("Intervjueerijad"))}
                  <br/>
                  ${h.checkbox('grupp_id', const.GRUPP_VAATLEJA, checkedif=c.grupp_id, label=_("Vaatlejad"))}
                  <br/>
                  ${h.checkbox('grupp_id', const.GRUPP_HINDAMISEKSPERT,
                  checkedif=c.grupp_id, label=_("Vaidehindajad"))}
                  <br/>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
                  ${h.checkbox('grupp_id', const.GRUPP_KOMISJON, checkedif=c.grupp_id, label=_("Komisjoniliikmed"))}
                  <br/>
                  ${h.checkbox('grupp_id', const.GRUPP_KONSULTANT, checkedif=c.grupp_id, label=_("Konsultandid"))}
                  <br/>
                  ${h.checkbox('grupp_id', const.GRUPP_T_ADMIN, checkedif=c.grupp_id, label=_("Läbiviijad"))}
      </div>
    </div>

    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit(_("Läbiviijate aruanne"), id='otsi')}
        ${h.submit(_("Sisestajate aruanne"), id='otsi_sisestaja', onclick="this.form.action='%s'" % h.url('otsing_labiviijad_sisestajad'))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

${h.form(url=h.url_current(), method='post')}
<div class="listdiv">
<%include file="labiviijad_list.mako"/>
</div>

% if c.items:
<div id="nupud">
${h.submit(_("Väljasta CSV (tööd)"), id='csv', level=2)}
% if not c.otsi_sisestaja:
${h.submit(_("Väljasta CSV (lepingud)"), id='csv2', level=2)}
% endif
${h.submit(_("Väljasta PDF"), id='pdf', level=2)}
% if c.aktimall:
##${h.submit(_("Väljasta aktid"), id='akt', level=2)}
##${h.submit(_("Saada teated"), id='mail', level=2)}
${h.button(_("Väljasta aktid"), id='akt', level=2)}
${h.button(_("Saada teated"), id='mail', level=2)}
% endif
% if c.otsi_sisestaja:
${h.submit(_("Väljasta sisestused tunnis (CSV)"), id='tcsv', level=2)}
% endif
</div>
% endif

${h.hidden('taiendavinfo', '')}
${h.hidden('op', '')}
${h.end_form()}

<div id="d_info" style="display:none">
  ${h.flb(_("Teatesse lisatav täiendav info"), 'info')}
  ${h.textarea('info', c.taiendavinfo, rows=5)}
</div>

<script>
  $('button#akt,button#mail').click(function(){
     var data = $('input[name="lv_id"]').serialize();
     if(!data)
     {
        alert_dialog("${_("Vali läbiviijad!")}");
        return;
     }
     var form = $(this.form), op = this.id, title = $(this).text();
     var f_ok = function(){
        $('#taiendavinfo').val($('#info').val());
        form.find('input[name="op"]').val(op);
        form.submit();
        close_dialog();
     };
     var buttons = {}
     buttons[title] = f_ok;                     
     open_dialog({'contents_elem': $('#d_info'),
                  'buttons': buttons});
     
  });
</script>
