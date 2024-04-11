<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
  c.includes['ckeditor'] = True
  c.includes['subtabs'] = True
  c.includes['sortablejs'] = True
%>
</%def>
<%def name="draw_tabs()">
<% c.tab1 = 'sisu' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<% c.tab2 = None %>
<%include file="sisuplokk.tabs.mako"/>
</%def>

<%def name="page_title()">
${c.item.nimi} | ${_("Sisu")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))}
${h.crumb(c.item.nimi or c.item.id, h.url('ylesanne', id=c.item.id))}
${h.crumb(_("Sisu"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<%def name="page_headers()">
<style>
  .pane-0 .panemover { float: right;}
  .pane-1 .panemover { float: left;}

## mathsettings.mako
.icon-setting {
    display:inline-block;
    margin:1px;
    border:3px solid transparent;
}
.icon-setting.active {
    border:3px solid #dd7f26;
    border-radius: 5px;
}
</style>
</%def>
<% 
c.ylesanne = c.item

if c.lang and c.user.has_permission('ylesanded-tolkimine', const.BT_UPDATE,c.ylesanne):
   # tõlkimise ajal on ainult tõlkeväljad kirjutatavad
   c.can_tr = True
   c.is_tr = c.is_edit
   c.is_edit = False
elif not c.lang and \
    not c.user.has_permission('ylesanded', const.BT_UPDATE,c.ylesanne) and \
    c.user.has_permission('ylesanded-toimetamine', const.BT_UPDATE,c.ylesanne):
   # toimetaja tohib ainult tekstivälju kirjutada
   c.can_tr = True
   c.is_tr = c.is_edit
   c.is_edit = False
else:
   c.can_update = c.user.has_permission('ylesanded', const.BT_UPDATE,c.item)

c.can_update_sisu = c.can_update and not c.ylesanne.lukus
c.can_update_hm = c.can_update and c.ylesanne.lukus_hm_muudetav
c.can_tr_sisu = c.can_tr and not c.ylesanne.lukus
c.can_tr_hm = c.can_tr and c.ylesanne.lukus_hm_muudetav

c.edit_tahemargid = c.is_edit and c.user.has_permission('ylesandetahemargid', const.BT_UPDATE, c.item)  
c.show_tahemargid = c.edit_tahemargid or c.user.has_permission('ylesandetahemargid', const.BT_VIEW, c.item)
%>
${h.form_save(c.item.id)}
##${h.hidden('order', '')}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)}

<%include file="sisuplokk.lang.mako"/>
% if c.item.lukus:
${h.alert_warning(c.item.lukus_nimi, False)}
% endif

${h.rqexp()}
<div class="form-wrapper mb-1">
  <div class="form-group row">
    ${h.flb3(_("Ülesande nimetus"), 'f_nimi', 'text-md-right', rq=True)}
    <div class="col-lg-8">
      % if c.lang:
      ${h.lang_orig(c.item.nimi, c.item.lang)}<br/>
      ${h.text('f_nimi', c.item.tran(c.lang).nimi, ronly=not c.is_tr, maxlength=256)}
      % else:
      ${h.text('f_nimi', c.item.nimi, ronly=not c.is_tr and not c.is_edit)}
      % endif
    </div>
  </div>

  % if c.lang:
  <div class="form-group row">
    ${h.flb3(_("Otsingu märksõnad"), 'f_marksonad')}
    <div class="col-lg-8">
      ${h.lang_orig(c.item.marksonad, c.item.lang)}<br/>
      ${h.textarea('f_marksonad', c.item.tran(c.lang).marksonad, ronly=not c.is_tr, rows=2, maxlength=256)}            
    </div>
  </div>
  % endif

  <div class="row mb-3">
    <% saab_lisada_sp = c.is_edit and c.can_update_sisu and not c.item.is_encrypted %>
    % if saab_lisada_sp:
    <div class="col-md-3 col-lg-4 large-card bg-gray-50">
      ${self.uue_sisuploki_valik()}
    </div>
    % endif
    
    <div class="${saab_lisada_sp and 'col-md-9 col-lg-8' or 'col-12'} large-card">      
        
    % if c.item.is_encrypted:
    ${h.alert_notice(_("Ülesande sisu on krüptitud"), False)}
    % else:
    %   if c.item.salastatud:
    ${h.alert_notice(_("Ülesande sisu on salastatud"), False)}
    %   endif
    ${self.sisuplokid()}
    % endif 
    </div>
  </div>

  ${self.lisavalikud()}
</div>

<div class="d-flex flex-wrap">
  % if not c.item.is_encrypted:

  % if c.user.has_permission('ylesanded',const.BT_SHOW, c.item):
  ${h.btn_to(_("Ekspordi"), h.url('ylesanded_formatted_export', id=c.item.id, format='raw', lang=c.lang), level=2)}
  ${h.btn_to(_("Ekspordi QTI"), h.url('ylesanded_formatted_export', id=c.item.id, format='qti', lang=c.lang), level=2)}
  ${h.button(_("Ekspordi kujundamiseks"), onclick="window.open('%s')" % h.url('ylesanded_formatted_export', id=c.item.id, format='html', lang=c.lang), level=2)}
  % endif
  
  ${h.btn_to_dlg(_("Lisa testi"), h.url('ylesanne_lisatesti', ylesanne_id=c.item.id),
  title=_("Lisa ülesanne testi"), width=700, level=2)}
  
  <div class="flex-grow-1 text-right">
    % if c.is_edit or c.is_tr:
    ${h.btn_to(_("Vaata"), h.url('ylesanded_sisu', id=c.item.id, lang=c.lang), method='get', level=2)}
    ${h.submit()}
    % elif c.can_update_hm or c.can_tr:
    ${h.btn_to(_("Muuda"), h.url('ylesanded_edit_sisu', id=c.item.id, lang=c.lang, is_tr=c.can_tr), method='get')}
    % endif
  </div>
</div>
${h.end_form()}

% if c.dialog_markus:
<div id="div_dialog_markus">
  <%include file="plokimarkus.mako"/>
</div>
<script>
  $(function(){
  open_dialog({'contents_elem': $('#div_dialog_markus'), 'title': '${_("Märkus")}'});
  });
</script>
% endif

% if c.dialog_markused:
<div id="div_dialog_markused">
  <%include file="plokimarkused.mako"/>
</div>
<script>
  $(function(){
  open_dialog({'contents_elem': $('#div_dialog_markused'), 'title':'${_("Märked")}'});
  });
</script>
% endif

% endif

<%def name="uue_sisuploki_valik()">
  <h3>${_("Lisa ülesandele sisuplokk")}</h3>
  
          <%
             opt_block = c.opt.interaction_block
             if not c.user.has_permission('srcedit', const.BT_UPDATE):
                opt_block = [r for r in opt_block if r[0] != const.BLOCK_HEADER]
             opt_interaction = c.opt.interaction
             #if c.user.handler.is_live:
             # vana sobitamise tyypi enam ei kasutata
             opt_interaction = [r for r in opt_interaction if r[0]!=const.INTER_MATCH3]
             categories = [(_("Ülesande sisend"), opt_block),
                           (_("Ülesande/vastuse tüüp"), opt_interaction),
                           (_("Ülesande väljund"), c.opt.interaction_output)]             
          %>
 % for category_label, opt_i in categories:
          <h4 class="mb-1">${category_label}</h4>
          <div class="row mb-4">
          % for tyyp, title in opt_i:
          <a class="col-md-12 col-lg-6 card" href="${h.url('ylesanne_new_sisuplokk', ylesanne_id=c.item.id, tyyp=tyyp)}">
            <div class="card-body p-1">
              <div class="card-text">
                ${title}
             </div>
            </div>
          </a>
          % endfor
          </div>
 % endfor          
</%def>


<%def name="sisuplokid()">
      <%
        sisuplokid = list(c.item.sisuplokid)
        on_sisuplokid = len(sisuplokid) > 0
      %>
% if not on_sisuplokid:
      ${h.alert_notice(_("Ülesande sisu ei ole veel loodud"))}
% else:
      <h3>${_("Sisuplokid")}</h3>
% endif

      % if c.is_edit and c.can_update_sisu:
      <div class="d-flex flex-wrap">
        % if c.opt_mall:
        <div class="mr-2">${_("Mall")}</div>
        ${h.select('mall_id', '', c.opt_mall, wide=False, empty=True, class_="nosave mx-2")}
        ${h.submit(_("Kasuta malli"), id="kasutamalli", level=2)}
        % else:
        ${h.alert_notice(_("Ülesannet ei saa koostada malliga, sest malle pole loodud"))}
        % endif
      </div>
      % endif

% if on_sisuplokid:      
      <table id="blocks" width="100%">
        <tr>
          <%
            paanide_arv = c.item.paanide_arv or 1
            sp_ind = 0
          %>
          % for ind_paan in range(paanide_arv):
          <td valign="top" class="ul-pane pane-${ind_paan} sortables" id="paan_${ind_paan}" width="${100/(c.item.paanide_arv or 1)}%">
              % for item in sisuplokid:
              <% i_seq = item.paan_seq or 0 %>
              % if i_seq == ind_paan or ind_paan == paanide_arv - 1 and i_seq > ind_paan:
              <div id="i_${item.id}" class="sortable card card-drag mb-1">
                ${self.table_sisuplokk(item, ind_paan, paanide_arv, sp_ind)}
                <% sp_ind += 1 %>
              </div>
              % endif
              % endfor      
              ${h.hidden('order_%s' % (ind_paan), '', class_='order')}
          </td>
          % endfor
        </tr>
      </table>
     
      % if c.is_edit and c.can_update_sisu:
      <script>
        function ser_order(sortables){
            var order = '';
            sortables.find('.sortable').each(function(){ order += ',' + this.id; });
            sortables.find('input.order').val(order);
        }
        $(function(){
     $('.sortables').each(function(n, sortables){      
       new Sortable(sortables, {
         animation: 150,
         group: 'shared',
         onUpdate: function(ev){
            ser_order($(sortables));
            dirty = true;
         },
         onChange: function(ev){
            if(sortables.id == 'paan_0')
              $(sortables).find('i.mdi-arrow-left').removeClass('mdi-arrow-left').addClass('mdi-arrow-right');
            else
              $(sortables).find('i.mdi-arrow-right').removeClass('mdi-arrow-right').addClass('mdi-arrow-left');
            $.each($('.sortables'), function(n, item){
              ser_order($(item));
            });
            dirty = true;        
         }
       });
    });

  $(".panemover").click(function(){
    var sp = $(this).closest('.sortable');
    var cur_pane = $(this).closest('.ul-pane');
    var next_pane = $(".ul-pane[id!='" + cur_pane.attr('id') + "']");
    next_pane.append(sp);
    if(next_pane.attr('id') > cur_pane.attr('id'))
       $(this).find('i.mdi').removeClass('mdi-arrow-right').addClass('mdi-arrow-left');
    else
       $(this).find('i.mdi').removeClass('mdi-arrow-left').addClass('mdi-arrow-right');

    $.each($('.sortables'), function(n, item){
      ser_order($(item));
    });
    dirty = true;
  });
  
  $("#blocks").disableSelection();
})

      </script>
      % endif
% endif
</%def>
        
<%def name="table_sisuplokk(item, ind_paan, paanide_arv, sp_ind)">
<div class="card-header">
  <div>
    <div class="d-flex float-left mr-4">
      % if c.is_edit and c.can_update_sisu:
      <i class="mdi mdi-drag-vertical mdi-24px gray-300" aria-hidden="true"></i>
      % endif

      <p class="card-text my-0 ml-2 mr-2">
        <b class="brown">
        % if item.tahis:
        ${item.tahis} (${item.seq})
        % else:
        ${item.seq}
        % endif
        </b>
      </p>
      
      <p class="card-text my-0 ml-1">
        ${item.tyyp_nimi}
        % if item.naide:
        (näide)
      % endif
      </p>
    </div>
    
    <div class="float-right justify-content-end">

      % if c.can_update and not c.ylesanne.lukus:
      ${h.btn_to(_("Kopeeri"), h.url('ylesanne_create_sisuplokid', ylesanne_id=item.ylesanne_id, 
      sisuplokk_id=item.id, sub='kopeeri', edit=c.is_edit and 1 or 0), method='post', level=2)}
      % endif

      % if c.can_update_sisu:
      ${h.btn_to(_("Kustuta"), h.url('ylesanne_delete_sisuplokk', id=item.id,
      ylesanne_id=item.ylesanne_id), method='delete', level=2)}
      % endif

      % if c.user.has_permission('ylesanded-markused',const.BT_UPDATE, c.item):
      ${h.btn_to_dlg(_("Lisa märge"), 
      h.url('ylesanded_edit_sisu', id=c.item.id, sub='markus',partial=True,lang=c.lang,sisuplokk_id=item.id), level=2,
      title=_("Märkus"), width=600)}
      % endif

      % if len(item.plokimarkused):
      ${h.btn_to_dlg(_("Märked") + ' (%s)' % len(item.plokimarkused), 
      h.url_current('show', id=c.item.id, sub='markus',partial=True,sisuplokk_id=item.id), level=2,
      title=_("Märked"), width=600)}
      % endif
      ${h.btn_to(_("Vaata"), h.url('ylesanne_sisuplokk',
      id=item.id, ylesanne_id=item.ylesanne_id, lang=c.lang))}

      % if c.can_update_hm or c.can_tr_hm:
      ${h.btn_to(_("Muuda"), h.url('ylesanne_edit_sisuplokk',
      id=item.id, ylesanne_id=item.ylesanne_id, lang=c.lang, is_tr=c.can_tr))}
      % endif

    </div>

  </div>
</div>

<div class="card-body">
  <div class="ylesanne">
    ${item.ctrl.preview()}
  </div>
</div>

<div class="card-footer">
  % if c.show_tahemargid: 
  <% tr_item = not c.lang and item or item.tran(c.lang, False) %>
  <div>
    % if c.edit_tahemargid:
    ${h.hidden('sp-%d.id' % sp_ind, item.id)}
    % endif
    % if tr_item and tr_item.tahemargid is not None:
    <small>${_("{n} tähemärki").format(n=tr_item.tahemargid)}</small>
    % endif
  </div>
  % endif
        
  % if paanide_arv == 2 and c.is_edit:
  <%
    mdicls = ind_paan == 0 and 'mdi-arrow-right' or 'mdi-arrow-left'
    btntext = f'<i class="mdi {mdicls}"> </i>'
  %>
  ${h.button(btntext, class_='panemover', level=2, htmlvalue=True)}
  % endif
  </div>
</div>
</%def>

<%def name="lisavalikud()">

<%
   on_rtf_kysimusi = on_imath = on_wmath = False
   for sp in c.item.sisuplokid:
      if sp.on_rtf_kysimusi:
         on_rtf_kysimusi = True
      if sp.on_math_kysimusi:
         on_imath = True
      if sp.tyyp == const.INTER_WMATH:
         on_wmath = True
%>
% if on_rtf_kysimusi or on_imath or on_wmath:
  <div class="d-flex justify-content-end">
        % if on_rtf_kysimusi:
        ${h.btn_to_dlg(_("Lahendaja tekstitoimeti seaded"),
        h.url('ylesanded_edit_editorsettings', id=c.item.id, partial=True), title=_("Lahendaja tekstitoimeti seaded"), width=800, level=2)}
        % endif
        % if on_rtf_kysimusi or on_imath:
        ${h.btn_to_dlg(_("Lahendaja matemaatikaredaktori seaded"),
        h.url('ylesanded_edit_mathsettings', id=c.item.id, partial=True), title=_("Lahendaja matemaatikaredaktori seaded"), width=800, level=2)}
        % endif
        % if on_wmath:
        ${h.btn_to_dlg(_("Lahendaja MathType redaktori seaded"),
        h.url('ylesanded_edit_wmathsettings', id=c.item.id, partial=True), title=_("Lahendaja MathType redaktori seaded"), width=800, level=2)}
        % endif
  </div>
% endif
% if not c.item.is_encrypted:
  <div class="form-group row">
    ${h.flb3(_("Lahendusjuhis"))}
    <div class="col-12">
        % if c.lang:
           ${h.lang_orig(h.literal(c.item.get_juhis()), c.item.lang)}<br/>
           ${h.lang_tag()}
           ${h.ckeditor('j_juhis', c.item.get_juhis(c.lang), ronly=not c.is_tr, height=150)}
        % else:
           ${h.ckeditor('j_juhis', c.item.get_juhis(), ronly=not c.is_tr and not c.is_edit, height=150)}
        % endif
    </div>
  </div>
  
  % if c.show_tahemargid: 
  <% item = c.ylesanne.lahendusjuhis %>
  % if c.edit_tahemargid or item:
  <% tr_item = not c.lang and item or item and item.tran(c.lang, False) %>
  <div>
    % if item and tr_item and tr_item.tahemargid is not None:
    <span class="brown">${_("{n} tähemärki").format(n=tr_item.tahemargid)}</span>
    % endif
  </div>
  % endif
  % endif

    <% tr_item = not c.lang and c.item or c.item.tran(c.lang, False) %>
    % if tr_item and tr_item.tahemargid is not None:
    <div class="mb-1">
      <span class="brown">${_("Ülesandes on {n} tähemärki").format(n=tr_item.tahemargid)}</span>
    </div>
    % endif
  % endif

    <div class="form-group row">
      <div class="col-md-4">
        ${h.checkbox('f_paanide_arv', 2, checked=c.item.paanide_arv==2, label=_("Sisuplokid rühmitatakse kaheks ekraanipooleks"),
        onchange="set_paanidega()")}
        % if c.is_edit:
        <script>
          function set_paanidega()
          {
          $('span.paanidega').toggle($('input#f_paanide_arv:checked').length > 0);
          }
          function set_paan1()
          {
            var width = 100 - parseInt($('input#f_paan1_laius').val());
            if(width > 0 && width < 100) $('input#paan2_laius').val(width);
          }
          $(document).ready(set_paanidega);
        </script>
        % endif
      </div>
      <div class="col-md-4 paanidega" ${c.item.paanide_arv != 2 and 'style="display:none"' or ''}>
          ${_("Vasak pool:")} ${h.posint5('f_paan1_laius', c.item.paan1_laius or 50, maxvalue=85, onchange="set_paan1()")}%
      </div>
      <div class="col-md-4 paanidega" ${c.item.paanide_arv != 2 and 'style="display:none"' or ''}>      
          ${_("Parem pool:")} ${h.posint5('paan2_laius', 100 - (c.item.paan1_laius or 50), disabled=True)}%
      </div>
    </div>

    <div class="form-group">
        ${h.checkbox('f_lahendada_lopuni', 1, checked=c.item.lahendada_lopuni, label=_("Poolikut vastust ei lubata kinnitada"))}
    </div>

    <div class="form-group">
        ${h.checkbox('f_valimata_vastused', 1, checked=c.item.valimata_vastused, label=_("Arvestada valede ja õigete vastuste arvus ka valimata vastuseid"))}
    </div>

    <div class="form-group">
      ${h.checkbox('f_spellcheck', 1, checked=c.item.spellcheck, label=_("Luba sisestusväljades kasutada brauseri spellerit"))}
    </div>

    <div class="form-group">
      ${h.checkbox('f_dlgop', 1, checked=c.item.dlgop_tekst, label=_("Kui testi tegija ei alusta vastamist, kuvatakse dialoogiaknas küsimus"), class_="dlgop")}

        <script>
          $(function(){
              $('.dlgop-param').toggle($('input.dlgop:checked').length > 0);  
              $('input.dlgop').change(function(){
                $('.dlgop-param').toggle($('input.dlgop:checked').length > 0);
              });
          });
        </script>

        <% ch = h.colHelper('col-md-5', 'col-md-5') %>
        <div class="dlgop-param ml-5 mt-1">
          <div class="form-group row">
            ${ch.flb(_("Mitu sekundit oodata enne dialoogi avamist"), 'f_dlgop_aeg')}
            <div class="col-md-7">
              ${h.posint5('f_dlgop_aeg', c.item.dlgop_aeg)}
            </div>
          </div>
          <div class="form-group row">
            ${ch.flb(_("Dialoogiakna küsimuse tekst"), 'f_dlgop_tekst')}
            <div class="col-md-7">
              % if c.lang:
              ${h.lang_orig(h.literal(c.item.dlgop_tekst), c.item.lang)}<br/>
              ${h.lang_tag()}
              ${h.text('f_dlgop_tekst', c.item.tran(c.lang).dlgop_tekst, ronly=not c.is_tr)}
              % else:
              ${h.text('f_dlgop_tekst', c.item.dlgop_tekst)}
              % endif
            </div>
          </div>
          <div class="form-group row">
            ${ch.flb(_("Mitme ülesande võrra edasi liikuda eitava vastuse korral"), 'f_dlgop_ei_edasi')}
            <div class="col-md-7">
              ${h.int5('f_dlgop_ei_edasi', c.item.dlgop_ei_edasi)}
            </div>
          </div>
        </div>  
      </div>

    <% sisuplokid = list(c.item.sisuplokid) %>
    % if len(sisuplokid) > 1:
    <div class="form-group d-flex flex-wrap">
        ${h.checkbox1('f_segamini', 1, checked=c.item.segamini, label=_("Sisuplokkide segamine"))}
        <div id="spfixpos" class="ml-4">
        ${_("Kindla asukohaga sisuplokid:")}
        % for sp in sisuplokid:
        ${h.checkbox('fixpos', sp.id, checked=sp.fikseeritud, label=sp.tahis or sp.seq)}
        % endfor
        <script>
        $(function(){
        $('#f_segamini').click(function(){ $('#spfixpos').toggle(this.checked); });
        $('#spfixpos').toggle($('#f_segamini').prop('checked'));
        });
        </script>
        </div>
    </div>
    % endif

    % if not c.item.arvutihinnatav:   
    <div class="form-group">
        ${h.checkbox('f_fixkoord', 1, checked=c.item.fixkoord, label=_("Fikseeritud koordinaatidega kujundus (hindamise välju ei või ülesande sisse paigutada)"))}
    </div>
    % elif c.is_edit:
    ${h.hidden('f_fixkoord', c.item.fixkoord and 1 or '')}
    % endif
    <div class="form-group">
        ${h.radio('f_disain_ver', const.DISAIN_EIS1, checkedif=c.item.disain_ver, label=_("Vana disain"))}
        ${h.radio('f_disain_ver', const.DISAIN_HDS, checkedif=c.item.disain_ver, label=_("Uus disain"))}
    </div>
      
</%def>