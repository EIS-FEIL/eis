## Teadete vormidel kasutatav otsingufilter testide kohta

    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi liik"),'testiliik')}
            <% 
               liigid = set([const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_TASE, const.TESTILIIK_SEADUS])
               if c.on_rv: liigid.add(const.TESTILIIK_RV)
               if c.on_pohikool: liigid.add(const.TESTILIIK_POHIKOOL)
               if c.on_sisse: liigid.add(const.TESTILIIK_SISSE)
               if c.on_ke: liigid.add(const.TESTILIIK_KUTSE)
               if c.on_eel: liigid.add(const.TESTILIIK_EELTEST)
               if c.on_d2: liigid.add(const.TESTILIIK_DIAG2)
               if c.on_tasemetoo: liigid.add(const.TESTILIIK_TASEMETOO)
               if c.testiliik: liigid.add(c.testiliik)
               opt_testiliik = [r for r in c.opt.testiliik if r[0] in liigid]
               if not c.testiliik and not c.testiliik_empty and opt_testiliik: c.testiliik = opt_testiliik[0][0]
            %>
            ${h.select('testiliik', c.testiliik, opt_testiliik, empty=c.testiliik_empty,
            onchange="this.form.submit()")}
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
      </div>
    </div>
    % if c.testiliik == const.TESTILIIK_TASE:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Keeleoskuse tase"),'keeletase')}
        ${h.select('keeletase', c.keeletase, 
        c.opt.klread_kood('KEELETASE', const.AINE_RK), empty=True)}
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

    % elif c.testiliik == const.TESTILIIK_SEADUS:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Test"),'test_id')}
            <% 
               opt_test = model.Test.get_opt(c.sessioon_id or -1) or []
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
        model.Toimumisaeg.get_opt(c.sessioon_id or -1, test_id=c.test_id or -1) or [],
        empty=True)}
      </div>
    </div>
    % else:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testimiskord"),'testimiskord_id')}
            <% 
               opt_testimiskord = model.Testimiskord.get_opt(c.sessioon_id or -1) or []
               if c.testimiskord_id and int(c.testimiskord_id) not in [r[0] for r in opt_testimiskord]:
                  c.testimiskord_id = None
            %>
            ${h.select('testimiskord_id', c.testimiskord_id, opt_testimiskord,
               empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Toimumisaeg"),'toimumisaeg_id')}
        ${h.select('toimumisaeg_id', c.toimumisaeg_id,
        model.Toimumisaeg.get_opt(c.sessioon_id or -1, testimiskord_id=c.testimiskord_id or -1) or [],
        empty=True)}
      </div>
    </div>
    % endif
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
        ${h.flb(_("Asukoht"),'koht_id')}
        <% c.piirkond = c.piirkond_id and model.Piirkond.get(c.piirkond_id) %>
        ${h.select('koht_id', c.koht_id, 
        c.piirkond and c.piirkond.get_opt_kohad() or [], empty=True)}

      <script>
        $(function(){
        
        % if c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_POHIKOOL, const.TESTILIIK_RV):
         $('select#sessioon_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TESTIMISKORD', format='json')}", 
                           'sessioon_id', 
                           $('select#testimiskord_id'),
                           function(){return {testiliik:"${c.testiliik}"}},
                           $('select#toimumisaeg_id')));
         $('select#testimiskord_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TOIMUMISAEG', format='json')}", 
                           'testimiskord_id', 
                           $('select#toimumisaeg_id'),
                           function(){return {sessioon_id:$('select#sessioon_id').val()}}));

        % elif c.testiliik == const.TESTILIIK_TASE:
         $('select#sessioon_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                           'sessioon_id', 
                           $('select#test_id'),
                           function(){return {testiliik:"${c.testiliik}",keeletase:$('select#keeletase').val()}},
                           $('select#toimumisaeg_id')));
         $('select#keeletase').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                           'keeletase', 
                           $('select#test_id'),
                           function(){return {sessioon_id:$('select#sessioon_id').val()}},
                           $('select#toimumisaeg_id')));
         $('select#test_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TOIMUMISAEG', format='json')}", 
                           'test_id', 
                           $('select#toimumisaeg_id'),
                           function(){return {sessioon_id:$('select#sessioon_id').val()}}));

        % elif c.testiliik == const.TESTILIIK_SEADUS:
         $('select#sessioon_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                           'sessioon_id', 
                           $('select#test_id'),
                           function(){return {testiliik:"${c.testiliik}"}},
                           $('select#toimumisaeg_id')));
         $('select#test_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TOIMUMISAEG', format='json')}", 
                           'test_id', 
                           $('select#toimumisaeg_id'),
                           function(){return {sessioon_id:$('select#sessioon_id').val()}}));
        % endif

         $('select.prk_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='PIIRKONNAKOHT', format='json')}", 
                           'ylem_id', 
                           $('select#koht_id')));

        });
      </script>
        
      </div>
    </div>
