<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Statistika")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="require()">
<%
  c.includes['plotly'] = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Tulemuste statistika")}</h1>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi ID"),'test_id')}
        ${h.posint('test_id', c.test_id)}
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
        ${h.flb(_("Testi liik"),'testiliik')}
        ${h.select('testiliik', c.testiliik, c.opt.testiliik)}
            <script>
              $(function(){
                $('select#aine').change(function(){
                  if($(this).val()=='${const.AINE_RK}') $('select#testiliik').val('${const.TESTILIIK_TASE}');
                  if($(this).val()=='${const.AINE_C}') $('select#testiliik').val('${const.TESTILIIK_SEADUS}');
                });
                $('select#testiliik').change(function(){
                  if($(this).val()=='${const.TESTILIIK_TASE}') $('select#aine').val('${const.AINE_RK}');
                  if($(this).val()=='${const.TESTILIIK_SEADUS}') $('select#aine').val('${const.AINE_C}');
                });
              });
            </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Keeleoskuse tase"),'keeletase_kood')}
        ${h.select('keeletase_kood', c.keeletase_kood,
          c.opt.klread_kood('KEELETASE', ylem_kood=const.AINE_RK, empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Aasta alates"),'aasta_alates')}
        ${h.posint('aasta_alates', c.aasta_alates, maxlength=4)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"),'aasta_kuni')}
        ${h.posint('aasta_kuni', c.aasta_kuni, maxlength=4)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Eristada tulemus kuni"),'alla')}
        ${h.posfloat('alla', c.alla, maxvalue=100)} %
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("vähemalt"),'yle')}
        ${h.posfloat('yle', c.yle, maxvalue=100)} %
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.checkbox1('ositi', 1, checked=c.ositi, label=_("Võrdle osaoskuse piires"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.select('osanimi', c.osanimi, c.opt_osanimed)}
            <script>
              $(document).ready(function(){
                $('select#osanimi').toggle($('input#ositi').prop('checked'));
                $('input#ositi').change(function(){
                   $('select#osanimi').toggle($('input#ositi').prop('checked'));
                   if($(this).prop('checked')) $('input[name="ykord"]').prop('checked', false);
                });
                $('select#aine,select#testiliik,input#ositi,input#aasta_alates,input#aasta_kuni').change(function(){
                   if($('input#ositi').prop('checked'))
                   {
                      var data = $(this.form).serialize();
                      var url = "${h.url_current('index', sub='osanimed')}";
                      var target = $('select#osanimi');
                      update_options(null, url, null, target, data);
                   }
                });
              });
            </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
            ${h.checkbox1('yhisosa', 1, checked=c.yhisosa, label=_("Ainult ühisosa ülesanded"))}
            <script>
              $(document).ready(function(){
                 $('input[name="ykord"]').change(function(){
                   if($(this).prop('checked')){
                     $('input[name="yhisosa"]').prop('checked', true);
                     $('input[name="tkord"]').prop('checked', false);
                     $('input[name="ositi"]').prop('checked', false).change();
                   }
                 });
                 $('input[name="tkord"]').change(function(){
                   if($(this).prop('checked')){
                     $('input[name="ykord"]').prop('checked', false);
                   }
                 });
              });
            </script>
      </div>
    </div>
  </div>

  <hr class="m-2"/>
  
  <div class="row filter">
    <div class="col-md-1">
      ${h.flb(_("Jaotus"), 'jaotus')}
    </div>
    <div class="col-md-11" id="jaotus">
      <div class="row">
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">        
            ${h.checkbox1('sugu',1,checked=c.sugu, label=_("Soo järgi"))}  
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('koolityyp',1,checked=c.koolityyp, 
            label=_("Õppeasutuse tüübi järgi"))}  
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('oppekeel',1,checked=c.oppekeel, label=_("Õppekeele järgi"))}  
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('soorituskeel',1,checked=c.soorituskeel, label=_("Soorituskeele järgi"))}  
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('kool',1,checked=c.kool, label=_("Kooli järgi"))}  
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('piirkond',1,checked=c.piirkond, label=_("Piirkonna järgi"))}  
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('maakond',1,checked=c.maakond, label=_("Maakonna järgi"))}  
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('kov',1,checked=c.kov, label=_("KOV järgi"))}  
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('tkord',1,checked=c.tkord, label=_("Testimiskorra järgi"))}  
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('kursus',1,checked=c.kursus, label=_("Kursuse järgi"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('keeletase',1,checked=c.keeletase, label=_("Keeleoskuse taseme järgi"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('tvaldkond',1,checked=c.tvaldkond, label=_("Töövaldkonna järgi"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('amet',1,checked=c.amet, label=_("Ameti järgi"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('haridus',1,checked=c.haridus, label=_("Hariduse järgi"))}                          
          </div>
        </div>
      </div>
    </div>
  </div>

  <hr class="m-2"/>
  
  <div class="row filter">
    <div class="col-md-1">
      ${h.flb(_("Kuvada veerud:"), 'kuvadaveerud')}
    </div>
    <div class="col-md-11" id="kuvadaveerud">
      <div class="row">
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group">        
            ${h.checkbox1('col_regatud', 1, checked=c.col_regatud, label=_("Registreeritud"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_puudus', 1, checked=c.col_puudus, label=_("Puudus"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_kais', 1, checked=c.col_kais, label=_("Käis"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_eksaminandid', 1, checked=c.col_eksaminandid, label=_("Eksaminandid"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_maxpallid', 1, checked=c.col_maxpallid, label=_("Max võimalik pallide arv"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_keskmine', 1, checked=c.col_keskmine, label=_("Keskmine"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_keskminepr', 1, checked=c.col_keskminepr, label=_("Keskmine (%)"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_halve', 1, checked=c.col_halve, label=_("St hälve"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_mediaan', 1, checked=c.col_mediaan, label=_("Mediaan"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_minsaajad', 1, checked=c.col_minsaajad, label=_("Min punktide saajad"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_maxsaajad', 1, checked=c.col_maxsaajad, label=_("Max punktide saajad"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_min', 1, checked=c.col_min, label=_("Min"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_max', 1, checked=c.col_max, label=_("Max"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_alla20', 1, checked=c.col_alla20, label=_("Kuni {p}% pallidest").format(p=c.alla))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_alla20pr', 1, checked=c.col_alla20pr, label=_("Kuni {p}% pallidest (%)").format(p=c.alla))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_yle80', 1, checked=c.col_yle80, label=_("Vähemalt {p}% pallidest").format(p=c.yle))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_yle80pr', 1, checked=c.col_yle80pr, label=_("Vähemalt {p}% pallidest (%)").format(p=c.yle))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_edukus_pt', 1, checked=c.col_edukus_pt, label=_("Edukus"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_edukus_pr', 1, checked=c.col_edukus_pr, label=_("Edukuse %"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_kvaliteet_pt', 1, checked=c.col_kvaliteet_pt, label=_("Kvaliteet"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group mb-1">    
            ${h.checkbox1('col_kvaliteet_pr', 1, checked=c.col_kvaliteet_pr, label=_("Kvaliteedi %"))}
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-end filter align-items-end">
    <div class="form-group">
    ${h.btn_search()}
    ${h.submit(_("Excel"), id='csv', class_="filter", level=2)}
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid andmeid ei leitud")}
  % elif c.items:
  <%include file="tulemused.list.mako"/>
  % endif 
</div>

% if c.arvutusprotsessid:
<%
  c.url_refresh = h.url_current('index', sub='progress', csv=None)
  c.protsessid_no_pager = True
%>
<%include file="/common/arvutusprotsessid.mako"/>
% endif
