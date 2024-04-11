<%
  ch = h.colHelper('col-md-4', 'col-md-8')
  fgcls = 'form-group col-12 col-lg-6'
  noedit = not (c.is_edit or c.is_tr) and 'noedit' or ''
  
%>
${h.rqexp()}
<div class="form-wrapper ${noedit} mb-2">
   <div class="row">
    <div class="${fgcls} row">
      ${ch.flb(_("Testi nimetus"), 't_nimi', rq=True)}
      <div class="col-md-8">
        % if c.lang:
        ${h.lang_orig(c.test.nimi)}<br/>
        ${h.lang_tag()}
        ${h.text('t_nimi', c.test.tran(c.lang).nimi,ronly=not c.is_tr)}
        % else:
        ${h.text('t_nimi', c.test.nimi, ronly=not c.is_tr and not c.is_edit)}
        % endif
      </div>
    </div>
    <div class="${fgcls} row">
      ${ch.flb(_("Testiosa jrk"), 'seq')}
      <div class="col-md-8">
        ${h.posint5('seq', c.item.seq)}
      </div>
    </div>
  </div>
  <div class="row">
    <div class="${fgcls} row">
      ${ch.flb(_("Testiosa nimetus"), 'f_nimi', rq=True)}
      <div class="col-md-8">
        % if c.lang:
        ${h.lang_orig(c.item.nimi)}<br/>
        ${h.lang_tag()}
        ${h.text('f_nimi', c.item.tran(c.lang).nimi, ronly=not c.is_tr)}
        % else:
        ${h.text('f_nimi', c.item.nimi, ronly=not c.is_tr and not c.is_edit)}
        % endif
      </div>
    </div>

    <div class="${fgcls} row">
      ${ch.flb(_("Testiosa tähis"), 'f_tahis', rq=True)}
      <div class="col-md-8">
        ${h.text5('f_tahis', c.item.tahis)}
      </div>
    </div>

    <div class="${fgcls} row">
      ${ch.flb(_("Ülesannete arv"), 'f_ylesannete_arv')}
      <div class="col-md-8">
        ${h.int5('f_ylesannete_arv', c.item.ylesannete_arv, ronly=True)}
      </div>
    </div>

    <div class="${fgcls} row">
      ${ch.flb(_("Hindepallide arv"), 'f_max_pallid')}
      <div class="col-md-8">
        ${h.float5('f_max_pallid', c.item.max_pallid, ronly=True)}
      </div>
    </div>
  </div>
  
  <div class="row">
    <div class="${fgcls} row">
      ${ch.flb(_("Vastamise vorm"), 'f_vastvorm_kood')}
      <div class="col-md-8">
        % if c.test.diagnoosiv:
        ${c.item.vastvorm_nimi}
        ${h.hidden('f_vastvorm_kood', c.item.vastvorm_kood or const.VASTVORM_KE)}
        % else:
        ${h.select('f_vastvorm_kood',
        c.item.vastvorm_kood,c.opt.klread_kood('VASTVORM', vaikimisi=c.item.vastvorm_kood))}
        % endif
      </div>
    </div>
  </div>
  <div class="row">
    % if c.is_edit or c.item.piiraeg:
    <div class="${fgcls} row">
      ${ch.flb(_("Lahendamise piiraeg"), 'piiraeg')}
      <div class="col-md-8">
        <span class="mr-2">
        ${h.timedelta_min('piiraeg', c.item.piiraeg, wide=False,
        onchange="if($(this).val()!='' && $('#hoiatusaeg').val()=='')$('#hoiatusaeg').val('5');")}
        </span>
        ${h.checkbox('f_piiraeg_sek', 1, checked=c.item.piiraeg_sek, label=_("Kuva sekundid"))}
      </div>
    </div>
    % endif
    % if c.is_edit or c.item.hoiatusaeg:
    <div class="${fgcls} row">
      ${ch.flb(_("Hoiatus enne lõppu"), 'hoiatusaeg')}
      <div class="col-md-8">
        ${h.posint5('hoiatusaeg', c.item.id and c.item.hoiatusaeg and c.item.hoiatusaeg/60)} ${_("minutit")}
      </div>
    </div>
    % endif

    % if c.is_edit or c.item.skoorivalem:
    <div class="${fgcls} row">
      ${ch.flb(_("Tulemuse arvutamise valem"), 'f_skoorivalem')}
      <div class="col-md-8">
        ${h.text('f_skoorivalem', c.item.skoorivalem, maxlength=256)}
      </div>
    </div>
    % endif
    % if c.is_edit or c.item.rvosaoskus_id:
    % if c.test.testiliik_kood == const.TESTILIIK_RV and c.test.rveksam:
    <div class="${fgcls} row">
      ${ch.flb(_("Osaoskus tunnistusel"), 'f_rvosaoskus_id')}
      <div class="col-md-8">
            <%
               opt_osaoskused = [(r.id, r.nimi) for r in c.test.rveksam.rvosaoskused]
            %>
            ${h.select('f_rvosaoskus_id', c.item.rvosaoskus_id, opt_osaoskused, empty=True)}
      </div>
    </div>
    % endif
    % endif
  </div>
  <div class="row">
    % if (c.is_edit or c.item.tulemus_tunnistusele) and not c.test.diagnoosiv:
    <div class="${fgcls}">
      ${h.checkbox('f_tulemus_tunnistusele', c.item.tulemus_tunnistusele, label=_("Tulemus tunnistusele"))}
    </div>
    % endif

    % if c.is_edit or c.item.yl_jrk_alatestiti:
    <div class="${fgcls}">
      ${h.checkbox('f_yl_jrk_alatestiti', 1, checked=c.item.yl_jrk_alatestiti,            
      label=_("Ülesannete järjekorranumbrid algavad igas alatestis uuesti 1st"))}
    </div>
    % endif
    % if c.is_edit or c.item.lotv:
    <div class="${fgcls}">    
      ${h.checkbox('f_lotv', 1, checked=c.item.lotv, label=_("Lõtv struktuur"))}
    </div>
    % endif
    % if c.is_edit or c.item.naita_max_p:
    <div class="${fgcls}">    
      ${h.checkbox('f_naita_max_p', 1, checked=c.item.naita_max_p, label=_("Hindepallid kuvatakse lahendajale"))}
    </div>
    % endif

    % if c.is_edit or c.item.lopetatav:
    <div class="${fgcls}">
      ${h.checkbox('f_lopetatav', 1, checked=c.item.lopetatav,            
      label=_("Sooritajal on alati testi lõpetamise nupp"))}
    </div>
    % endif
    % if c.is_edit or c.item.katkestatav:
    <div class="${fgcls}">    
      ${h.checkbox('f_katkestatav', 1, checked=c.item.katkestatav,
      label=_("Sooritajal on testi katkestamise nupp"))}
    </div>
    % endif
    % if c.is_edit or c.item.aeg_peatub:
    <div class="${fgcls}">       
      ${h.checkbox('f_aeg_peatub', 1, checked=c.item.aeg_peatub, label=_("Testi katkestamisel aeg peatub"))}
    </div>
    % endif
    % if c.is_edit or c.item.yl_lahendada_lopuni:
    <div class="${fgcls}">           
      ${h.checkbox('f_yl_lahendada_lopuni', 1, checked=c.item.yl_lahendada_lopuni, label=_("Poolikult lahendatud ülesandelt ei lubata edasi minna"))}
    </div>
    % endif
    % if c.is_edit or c.item.peida_pais:
    <div class="${fgcls}">
      ${h.checkbox('f_peida_pais', 1, checked=c.item.peida_pais,
      label=_("Peida süsteemi päis ja jalus"))}
    </div>
    % endif
    % if c.is_edit or not c.item.pos_yl_list:
    <div class="${fgcls}">    
      ${h.checkbox('peida_yl_list', 1, checked=not c.item.pos_yl_list,
      label=_("Peida ülesannete loetelu"))}      
    </div>
    % endif
    % if c.is_edit or c.item.yhesuunaline:
    <div class="${fgcls}">        
      ${h.checkbox('f_yhesuunaline', 1, checked=c.item.yhesuunaline,
      onchange="if(this.checked) $('#f_yl_lahk_hoiatus').prop('checked', true);",
      label=_("Ühesuunaline lahendamine"))}
    </div>
    % endif
    % if (c.is_edit or c.item.yl_segamini) and not c.item.on_alatestid:
    <div class="${fgcls}">        
      ${h.checkbox('f_yl_segamini', 1, checked=c.item.yl_segamini,
      label=_("Ülesannete segamine"))}
    </div>
    % endif
    % if c.is_edit or c.item.kuva_yl_nimetus:
    <div class="${fgcls}">
      ${h.checkbox('f_kuva_yl_nimetus', 1, checked=c.item.kuva_yl_nimetus,
      label=_("Kuva sooritajale järjekorranumbri asemel ülesande nimetus"))}
    </div>
    % endif
    % if c.is_edit or c.item.peida_yl_pealkiri:
    <div class="${fgcls}">    
      ${h.checkbox('f_peida_yl_pealkiri', 1, checked=c.item.peida_yl_pealkiri,
      label=_("Ära kuva sooritajale ülesande pealkirja (ülesande kohal)"))}
    </div>
    % endif
    % if c.is_edit or c.item.yl_lahk_hoiatus:
    <div class="form-group col-12 col-md-6 yl_lahk_hoiatus">
      ${h.checkbox('f_yl_lahk_hoiatus', 1, checked=c.item.yl_lahk_hoiatus, 
      label=_("Lahendajale kuvatakse ühesuunalise alatesti ülesandelt lahkumisel hoiatus"))}
    </div>
    % endif
    % if c.is_edit or c.item.yl_pooleli_hoiatus:
    <div class="form-group col-12 col-md-6 yl_lahk_hoiatus">
      ${h.checkbox('f_yl_pooleli_hoiatus', 1, checked=c.item.yl_pooleli_hoiatus, 
      label=_("Lahendajale kuvatakse ühesuunalise alatesti pooleliolevalt ülesandelt lahkumisel hoiatus"))}            
    % if c.is_edit:
    <script>
              $(function(){
              $('#f_yl_lahk_hoiatus').click(function(){ $('#f_yl_pooleli_hoiatus').prop('checked', false); });
              $('#f_yl_pooleli_hoiatus').click(function(){ $('#f_yl_lahk_hoiatus').prop('checked', false); });              
              });
    </script>
    % endif
    </div>
    % endif
    % if c.is_edit or c.item.ala_lahk_hoiatus:
    <div class="form-group col-12 col-md-6 yl_lahk_hoiatus">
      ${h.checkbox('f_ala_lahk_hoiatus', 1, checked=c.item.ala_lahk_hoiatus,
            label=_("Lahendajale kuvatakse ühekordse alatesti avamisel või sellelt lahkumisel hoiatus"))}
    </div>
    % endif
  </div>

  <div class="row">
    % if c.is_edit or c.is_tr or c.item.alustajajuhend:
    <div class="${fgcls}">
      ${h.flb(_("Juhised sooritajale (enne alustamist)"))}
      ${self.tran_editable('alustajajuhend', c.item, 'f_')}
    </div>
    % endif
    % if c.is_edit or c.is_tr or c.item.sooritajajuhend:
    <div class="${fgcls}">
      ${h.flb(_("Juhised sooritajale (sooritamise ajal)"))}
      ${self.tran_editable('sooritajajuhend', c.item, 'f_')}
    </div>
    % endif
  </div>
</div>
    
      
<%def name="tran_editable(key, item, prefix)">
<%
  orig_val = item and item.__getattr__(key)
  if c.lang:
     tran = item and item.tran(c.lang, False)
     tran_val = tran and tran.__getattr__(key) or ''
%>
% if c.lang:
<div>
  ${h.lang_orig(h.literal(orig_val), c.test.lang)}
</div>
${h.lang_tag()}
% if c.is_tr:
${h.textarea(prefix + key, tran_val, ronly=False, class_="editable")}
% else:
${tran_val}
% endif
% else:
% if c.is_edit or c.is_tr:
${h.textarea(prefix + key, orig_val, ronly=False, class_="editable")}
% else:
<div>${orig_val}</div>
% endif
% endif
</%def>
