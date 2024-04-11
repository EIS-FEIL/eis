<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Läbiviijate käskkirjad")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Läbiviijate käskkirjad")}</h1>

${h.form_search(url=h.url('otsing_labiviijakaskkirjad'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi liik"),'testiliik')}
            <% 
               opt_testiliik = c.opt.testiliik
               if not c.testiliik: c.testiliik = opt_testiliik[0][0]
            %>
            ${h.select('testiliik', c.testiliik, opt_testiliik, onchange="this.form.submit()")}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testsessioon"),'sessioon_id')}
            <% 
               opt_sessioon = model.Testsessioon.get_opt(c.testiliik)
               if c.sessioon_id and int(c.sessioon_id) not in [r[0] for r in opt_sessioon]:
                  c.sessioon_id = None
            %>
            ${h.select('sessioon_id', c.sessioon_id, opt_sessioon, empty=True)}
      <script>
        $(function(){
         $('select#sessioon_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                           'sessioon_id', 
                           $('select#test_id'),
                           function(){return {testiliik:"${c.testiliik}"}}));
         $('select#test_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TOIMUMISAEG', format='json')}", 
                           'test_id', $('select#toimumisaeg_id'),
                           function(){return {testiliik:"${c.testiliik}", sessioon_id:$('select#sessioon_id').val()}}));
        });
      </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Test"),'test_id')}
            <%
               opt_test = model.Test.get_opt(c.sessioon_id or -1, keeletase=c.keeletase) or []
               if c.test_id and int(c.test_id) not in [r[0] for r in opt_test]:
                  c.test_id = None
            %>
            ${h.select('test_id', c.test_id, opt_test, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Toimumisaeg"),'toimumisaeg_id')}
        ${h.select('toimumisaeg_id', c.toimumisaeg_id,
        model.Toimumisaeg.get_opt(c.sessioon_id or -1, test_id=c.test_id or -1, keeletase=c.keeletase) or [],
        empty=True)}
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
        ${h.flb(_("Piirkond"),'piirkond_id')}
            <%
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
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
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
            <% if not (c.nousolek or c.polenous or c.kaskkirjas or c.leping): c.labiviijad = True %>
            ${h.checkbox('nousolek', 1, checked=c.nousolek, label=_("Nõusoleku andnud"))}
            ${h.checkbox('polenous', 1, checked=c.polenous, label=_("Pole nõus"))}            
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
            ${h.checkbox('kaskkirjas', 1, checked=c.kaskkirjas, label=_("Käskkirja lisatud"))}
            ${_("alates")} ${h.date_field('kaskkirikpv', c.kaskkirikpv)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
            ${h.checkbox('leping', 1, checked=c.leping, label=_("Leping sõlmitud"))}
            ${_("alates")} ${h.date_field('lepingkpv', c.lepingkpv)}            
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
            ${h.checkbox('labiviijad', 1, checked=c.labiviijad, label=_("Läbiviijaks määratud"))}
      </div>
    </div>
  </div>
  <div class="col d-flex justify-content-end filter align-items-end">
    <div class="form-group">
    ${h.submit(_("Kirjalikud hindajad"), id='khindajad')}            
    ${h.submit(_("Suulised hindajad"), id='shindajad')}
    ${h.submit(_("Intervjueerijad"), id='intervjuu')}
    ${h.submit(_("Vaatlejad"), id='vaatlejad')}
    ${h.submit(_("Komisjoniliikmed"), id='komisjoniliikmed')}                              
    ${h.hidden('nupp', c.khindajad and 'khindajad' or c.shindajad and 'shindajad' or c.intervjuu and 'intervjuu' or c.vaatlejad and 'vaatlejad' or c.komisjoniliikmed and 'komisjoniliikmed' or '')}
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="labiviijakaskkirjad_list.mako"/>
</div>
  % if c.items:
  <%
     params = request.params.mixed()
     params['format'] = 'csv'
     url_csv = h.url_current('index', **params)
  %>
<br/>
${h.btn_to(_("Väljasta CSV"), url_csv, level=2)}
% endif
