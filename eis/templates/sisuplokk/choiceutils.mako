## Abifunktsioonid sisuplokkide jaoks

<%def name="choice_text(kysimus, item, prefix, wysiwyg=True)">
## valikvastuse tekst
        % if c.lang:
          ${h.lang_orig(h.literal(item.nimi))}<br/>
          ${h.lang_tag()}
        % endif
        <% 
           if c.lang:
              nimi = item.tran_nimi or item.tran(c.lang).nimi
           else:
              nimi = item.nimi
           ronly = not c.is_tr and not c.is_edit or bool(c.block.ylesanne and c.block.ylesanne.lukus)
        %>
     % if ronly:
        % if kysimus.rtf:
          ${h.literal(nimi)}
        % else:
          ${nimi}
        % endif
     % elif wysiwyg:
        % if kysimus.rtf:
          ${h.textarea('%s.nimi' % (prefix), nimi, cols=80, rows=3, ronly=ronly, class_='editable rowfocus')}
          ##${h.text('%s.nimi' % (prefix), '', ronly=ronly, class_='editable', style="display:none")}
        % else:
          ${h.text('%s.nimi' % (prefix), nimi, ronly=ronly, class_='editable rowfocus')}
        % endif
        % else:
          ${h.text('%s.nimi' % (prefix), nimi, ronly=ronly, class_='editable rowfocus')}
          <span id="${prefix}nimi">
        % if kysimus.rtf:
           ${h.literal(nimi)}
        % endif
          </span>
     % endif
</%def>          

<%def name="khdr_text(kysimus, block, wysiwyg=True)">
## mitme valikuga tabeli kysimuse veeru päise sisu
        % if c.lang:
          ${h.lang_orig(h.literal(block.sisuvaade))}<br/>
          ${h.lang_tag()}
        % endif
        <% 
           if c.lang:
              nimi = block.tran(c.lang).sisuvaade
           else:
              nimi = block.sisuvaade
           ronly = not c.is_tr and not c.is_edit or bool(c.block.ylesanne and c.block.ylesanne.lukus)
        %>
     % if ronly:
        % if kysimus.rtf:
          ${h.literal(nimi)}
        % else:
          ${nimi}
        % endif
     % elif wysiwyg:
        % if kysimus.rtf:
          ${h.textarea('f_sisuvaade', nimi, cols=80, rows=3, ronly=ronly, class_='editable')}
        % else:
          ${h.text('f_sisuvaade', nimi, ronly=ronly, class_='editable')}
        % endif
     % else:
          ${h.text('f_sisuvaade', nimi, ronly=ronly, class_='editable')}
          <span id="${prefix}nimi">
        % if kysimus.rtf:
           ${h.literal(nimi)}
        % endif
          </span>
     % endif
</%def>          

<%def name="row_choices_mchoice_valikud(item, prefix)">      
      <%
        v_kysimus = c.block.get_kysimus(kood=item.kood)
        v_tulemus = v_kysimus and v_kysimus.tulemus
        v_correct = []
        if v_tulemus:
           for v_hm in v_tulemus.hindamismaatriksid:
              if v_hm.pallid > 0:
                  v_correct.append(v_hm.kood1)
      %>
      % for ind_v in range(c.block.laius or 1):
      <td class="checkboxparent" align="center">
        <%
          ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
          item_v = ind_v < len(c.v2_valikud) and c.v2_valikud[ind_v] or c.new_item(kood=ascii_uppercase[ind_v])
          v_kood = item_v.kood
        %>
          ${h.checkbox1('%s.oigekood' % (prefix), value=v_kood, checked=v_kood in v_correct,
          class_="checkboxchild oigekood-k%s" % (v_kysimus and v_kysimus.id))}
      </td>
      % endfor
</%def>      

<%def name="row_choices(kysimus, item, baseprefix, cnt, seosed, toolbar='basic', size=80, wysiwyg=True, txpos=False, joondus=False, fikseeritud=False)">
## Ühe valikvastuse sisestamine
    <% prefix = '%s%s' % (baseprefix, cnt) %>
    <tr>
      <td valign="center" width="100px">
        ${h.text('%s.kood' % (prefix), item.kood, class_='%skood identifier' % baseprefix, size=10,
                  onchange="refresh_text_options('%skood');" % baseprefix)}
        % if not c.is_edit and (c.is_tr or c.lang):
        ${h.hidden('%s.kood' % (prefix), item.kood)}
        % endif
        % if c.block.tyyp == const.INTER_PUNKT and item.id:
        <% vkysimus = c.block.get_kysimus(item.kood) %>
        % if vkysimus:
        <% tulemus = vkysimus.tulemus %>
        ${h.btn_to_dlg(_("Hindamise seaded"), h.url('ylesanne_sisuplokk_edit_kysimus', id=vkysimus.kood, ylesanne_id=c.item.ylesanne_id,sisuplokk_id=c.block.id, lang=c.lang), level=2, class_="m-1")}
        <span class="kysimus-kood" data-kood="${item.kood}"></span>
        % if tulemus.max_pallid is not None:
        ${h.fstr(tulemus.max_pallid)}p
        % endif
        % endif
        % endif
      </td>
      % if c.block.tyyp in (const.INTER_COLORAREA, const.INTER_COLORTEXT):
      <td>
        % if c.is_edit:
        ${h.text('%s.varv' % (prefix), item.varv, class_='spectrum', datafield=False)}
        % else:
        ${h.text('%s.varv_readonly' % (prefix), item.varv, class_='spectrum', ronly=False, disabled="disabled", datafield=False)}
        ${h.hidden('%s.varv' % (prefix), item.varv)}
        % endif
      </td>
      % endif
      <td>
        ${self.choice_text(kysimus, item, prefix, wysiwyg)}
      </td>
      % if c.block.tyyp == const.INTER_MCHOICE:
      ${self.row_choices_mchoice_valikud(item, prefix)}
      % endif
      % if not c.lang:
      <td>
        % if c.is_tr:
        ${item.selgitus}
        % else:
        ${h.text('%s.selgitus' % (prefix), item.selgitus, maxlength=255, class_='selgitus')}
        % endif
      </td>
      % endif
      % if joondus:
      <td nowrap>
      <%
         justifies = ((const.JUSTIFY_LEFT,_("Vasakul")),
                      (const.JUSTIFY_CENTER,_("Keskel")),
                      (const.JUSTIFY_RIGHT,_("Paremal")),
                      ##(const.JUSTIFY_BLOCK,_("Justified")),
                     )
      %>
      ${h.select_radio('%s.joondus' % (prefix), item.joondus or const.JUSTIFY_LEFT, justifies)}
      </td>
      % endif
      % if fikseeritud:
      <td>
        ${h.checkbox1('%s.fikseeritud' % (prefix), 1, checked=item.fikseeritud)}
      </td>
      % endif
      % if txpos:
      <td width="70px">
        ${h.posint5('%s.min_vastus' % (prefix), item.min_vastus)}
      </td>
      <td width="200px">
        <div class="d-flex flex-wrap">
          ${h.posint5('%s.max_vastus' % (prefix), item.max_vastus, class_="mr-2")}
          % if c.block.tyyp in (const.INTER_TXPOS2, const.INTER_TXGAP, const.INTER_TXPOS):          
          <div style="white-space:nowrap">
            ${h.checkbox1('%s.eraldi' % (prefix), 1, checked=item.eraldi, label=_("Kuva eraldi"))}
          </div>
          % endif
        </div>
      </td>
      % elif seosed:
      <td width="70px">
        ${h.posint5('%s.min_vastus' % (prefix), item.min_vastus)}
      </td>
      <td width="70px">
        % if c.block.tyyp == const.INTER_MATCH3B and kysimus.seq == 2:
        ## teine hulk on kysimuste hulk, mille valikuid võib siduda 1 valikuga 1. hulgast + 1 valikuga 3. hulgast
        ${h.posint5('%s.max_vastus' % (prefix), item.max_vastus, maxvalue=2)}
        % else:
        ${h.posint5('%s.max_vastus' % (prefix), item.max_vastus)}
        % endif
      </td>
      % endif
        % if c.block.tyyp == const.INTER_CHOICE:
        % if c.ylesanne.lahendada_lopuni:
        <td>
            ${h.text('%s.kohustuslik_kys' % prefix, item.kohustuslik_kys, maxlength=70, size=10)}
        </td>
        % endif
        <td>
            ${h.text('%s.sp_peida' % prefix, item.sp_peida, maxlength=70, size=10)}
        </td>
        <td>
            ${h.text('%s.sp_kuva' % prefix, item.sp_kuva, maxlength=70, size=10)}
        </td>
        % endif
        % if c.block.tyyp == const.INTER_MCHOICE:
      <td>
        % if item.id:
        ${h.btn_to_dlg(_("Hindamismaatriks"),
        h.url('ylesanne_sisuplokk_edit_kysimus', ylesanne_id=c.ylesanne.id, sisuplokk_id=c.block.id, lang=c.lang, id=item.kood),
        title=_("Hindamismaatriks"), width=900)}
        % endif
      </td>
        % endif
      <td width="20px">
        % if c.is_edit:
        ${h.grid_remove("refresh_text_options('%skood');" % baseprefix)}
        % endif
        ${h.hidden('%s.id' % prefix, item.id)}
      </td>
    </tr>
</%def>

<%def name="choices_rtf_setup(kysimus, prefix, can_rtf, toolbar, wysiwyg, ck_height)">
## CKeditori seaded valikute tabeli jaoks
## wysiwyg - kas kasutada kireva teksti jaoks ckeditori või kirjutatakse HTML käsitsi
## can_rtf - kas lubada kirevat teksti
<%
  is_rtf = kysimus.rtf
  rtf_enter = kysimus.rtf_enter
  if toolbar in ('basic', 'span', 'gapmatchspan', 'html2png', 'meta', 'hottext', 'inlinetext', 'inlinechoice', 'gapmatch') and c.user.has_permission('srcedit', const.BT_UPDATE):
      toolbar = toolbar + '_src'   
%>
<script>
% if wysiwyg and is_rtf:
   var ck_attr = {toolbar:'${toolbar}', language:'${request.localizer.locale_name}',height: ${ck_height or 'null'}, enterMode:${rtf_enter or 'null'}};
   % if c.is_edit and not c.lang:
   ck_attr['on'] = {
      'blur': function(evt){
          ## valiku teksti väljalt lahkudes kopeeritakse tekst selgituseks, kui selgituse lahter on tyhi
          var desc = $(evt.editor.element.$).closest('tr').find('input.selgitus');
          if(desc.length && desc.val() == '')
          {
             var val = evt.editor.getData()
                .replace(/<[^>]*>/g,'')
                .replace(/&nbsp;/g,' ')
                .replace(/&lt;/g,'<')
                .replace(/&gt;/g,'>')                            
                .replace(/&amp;/g,'&')                            
                .replace(/\s+/g, ' ')
                .trim().substr(0, 255);
             desc.val(val);
          }
       }
    }
    % endif
% endif

  $(function(){
% if can_rtf:
% if wysiwyg and is_rtf:
   toggle_ckeditor('${prefix}', false, null, ck_attr);
% elif not wysiwyg:
  toggle_html('${prefix}', false, null);
% endif
% endif
% if c.block.tyyp in (const.INTER_COLORAREA, const.INTER_COLORTEXT):
$("input.spectrum").spectrum({
    preferredFormat: "hex",
    showInput: true,
    showPalette: true,
    palette: [
    ["#000000", "#434343", "#666666", "#999999", "#b7b7b7", "#cccccc", "#d9d9d9", "#efefef", "#f3f3f3", "#ffffff"],
    ["#980000", "#ff0000", "#ff9900", "#ffff00", "#00ff00", "#00ffff", "#4a86e8", "#0000ff", "#9900ff", "#ff00ff"],
    ["#e6b8af", "#f4cccc", "#fce5cd", "#fff2cc", "#d9ead3", "#d0e3e6", "#c9daf8", "#cfe2f3", "#d9d2e9", "#ead1dc"],
    ["#dd7e6b", "#ea9999", "#f9cb9c", "#ffe599", "#b6d7a8", "#a2c4c9", "#a4c2f4", "#9fc5e8", "#b4a7d6", "#d5a6bd"],
    ["#cc4125", "#e06666", "#f6b26b", "#ffd966", "#93c47d", "#76a5af", "#6d9eeb", "#6fa8dc", "#8e7cc3", "#c27ba0"],
    ["#a61c00", "#cc0000", "#e69138", "#f1c232", "#6aa84f", "#45818e", "#3c78d8", "#3d85c6", "#674ea7", "#a64d79"],
    ["#85200c", "#990000", "#b45f06", "#bf9000", "#38761d", "#134f5c", "#1155cc", "#0b5394", "#351c75", "#741b47"],
    ["#5b0f00", "#660000", "#783f04", "#7f6000", "#274e13", "#0c343d", "#1c4587", "#073763", "#20124d", "#4c1130"]
    ]
});        
% endif
% if c.is_edit and not c.lang:
  % if not wysiwyg or not is_rtf:
    ## valiku teksti väljalt lahkudes kopeeritakse tekst selgituseks, kui selgituse lahter on tyhi 
    $('table.choicetbl').on('change', 'input[name$=".nimi"],textarea[name$=".nimi"]', function() {
      var fdesc = $(this).closest('tr').find('input.selgitus');
      if(fdesc.val()=='')
      {
         var val = $(this).val();
         if($('input[name="v_rtf"]').prop('checked'))
         {
             ## eemaldada HTML
             val = val.replace(/<[^>]*>/g,'').replace(/\s+/g, ' ').trim();
         }
         fdesc.val(val.substr(0,255));
      }
   });
  % endif
% endif
});
</script>
</%def>

<%def name="choices_rtf_settings(kysimus, prefix, can_rtf, wysiwyg, can_txt=True)">
<% is_rtf = kysimus.rtf %>
     % if wysiwyg and can_rtf:
        % if not can_txt:
          ${h.hidden('%s_rtf_old' % prefix, is_rtf and '1' or '')}
          ${h.hidden('%s_rtf' % prefix, 1)}

        % elif c.is_edit and not c.lang:
          <% onclick = "$(this).closest('td').find('.needsave').show()" %>
          ${h.hidden('%s_rtf_old' % prefix, is_rtf and '1' or '')}
          ${h.checkbox1('%s_rtf' % prefix, 1, checked=is_rtf, onclick=onclick, label=_("Kirev tekst"))}
          <span class="needsave brown" style="display:none">${_("Muudatus rakendub peale salvestamist")}</span>
       % else:
          ${h.checkbox1('%s_rtf' % prefix, 1, checked=is_rtf, label=_("Kirev tekst"),
        disabled=True, onclick="toggle_html('%s', true, null)" % (prefix))}
        % endif

        <span id="${prefix}_dock_span" style="display:${is_rtf and 'inline' or 'none'}">
        % if c.is_edit or c.is_tr:
        ${h.checkbox1('%s_dock' % prefix, 1, checked=None, ronly=False, disabled=False,
        label=_("Nupurea lukustamine"),
        onclick="$('table#choicetbl_%s').find('div#%s_ckeditor_top').toggleClass('dock-top')" % (prefix,prefix))}
        % endif
        </span>

        <div id="${prefix}_ckeditor_top"></div>
      % elif can_rtf:
        % if c.is_edit and not c.lang:
        ${h.checkbox1('%s_rtf' % prefix, 1, checked=is_rtf,
        label=_("HTMLi kujul sisestamine"),
        onclick="toggle_html('%s', true, null)" % (prefix))}
        % else:
        ${h.checkbox1('%s_rtf' % prefix, 1, checked=is_rtf, disabled=True,
        label=_("HTMLi kujul sisestamine"))}
        % endif
      % endif
</%def>        

<%def name="choices(kysimus, valikud, prefix, seosed=False, size=80, caption=None, gentype='A', toolbar='basic', wysiwyg=True, txpos=False, ck_height=None, joondus=False, valista=False, fikseeritud=False, can_rtf=True, valikud_x=None)">
${self.choices_rtf_setup(kysimus, prefix, can_rtf, toolbar, wysiwyg, ck_height)}
<%
  if caption is None:
      caption = _("Valikud")
  MAXCOLS = 12
%>
<div class="d-flex flex-wrap">
  <div class="h3 flex-grow-1">
    ${caption}
  </div>
  <div>
    % if c.block.tyyp == const.INTER_MCHOICE:
    ${h.checkbox('segamini', 1, checked=kysimus.segamini, label=_("Küsimuste segamine"))}    
    % elif c.block.tyyp in (const.INTER_CHOICE, const.INTER_GAP, const.INTER_ORDER):
    ${h.checkbox('l.segamini', 1, checked=kysimus.segamini, label=_("Valikute segamine"))}
    % endif
  </div>
</div>
<table id="choicetbl_${prefix}" class="table choicetbl lh-11"
% if c.block.tyyp == const.INTER_MCHOICE:
       width="100%"
% endif
       > 
  <col width="100px"/>
  % if c.block.tyyp in (const.INTER_COLORAREA, const.INTER_COLORTEXT):
  <col width="60px"/>
  <col width="300px"/>
  % elif c.block.tyyp == const.INTER_MCHOICE:
  <col width="25%"/>
  <%
    laius = c.block.laius or 1
    width = min(45, laius * 25) / laius
  %>
  % for ind_v in range(laius):
  <col width="${width}%"/>
  % endfor
  % else:
  <col width="500px"/>  
  % endif
  % if not c.lang:
  ## selgitus
  <col width="200px"/>
  % endif
  % if joondus:
  <col width="300px"/>
  % endif
  % if fikseeritud:
  <col/>
  % endif  
  <thead>
    <tr>
      <th colspan="${MAXCOLS}">
        <% can_txt = c.block.tyyp != const.INTER_PUNKT %>
        ${self.choices_rtf_settings(kysimus, prefix, can_rtf, wysiwyg, can_txt)}
      </th>
    </tr>
    % if c.block.tyyp == const.INTER_MCHOICE:
      <%
        prefix_v = 'v2'
        c.v2_valikud = list(c.kysimus2.valikud)
      %>
      ${self.choices_mchoice_header1(kysimus, prefix_v)}
    % endif
    <tr>
      <th>${_("ID")}</th>
      % if c.block.tyyp in (const.INTER_COLORAREA, const.INTER_COLORTEXT):
      <th>${_("Värv")}</th>
      % endif
      % if c.block.tyyp == const.INTER_MCHOICE:
      <th>${_("Küsimuse tekst")}</th>
      % elif txpos:
      <th>${_("Tekst")}</th>
      % else:
      <th>${_("Nimetus")}</th>
      % endif
      % if c.block.tyyp == const.INTER_MCHOICE:
      % for ind_v in range(c.block.laius or 1):
      <%
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        item_v = ind_v < len(c.v2_valikud) and c.v2_valikud[ind_v] or c.new_item(kood=ascii_uppercase[ind_v])
      %>
      <th align="center">
        ${item_v.kood}
        ${h.hidden('%s-%d.kood' % (prefix_v, ind_v), item_v.kood)}
      </th>
      % endfor
      % endif
      % if not c.lang:
      <th>${_("Selgitus")}</th>
      % endif
      % if joondus:
      <th>${_("Positsioon")}</th>
      % endif
      % if fikseeritud:
      <th>${_("Fikseeritud")}</th>
      % endif
      % if txpos:
      <th>${_("Minimaalne valikute arv")}</th>
      <th>${_("Arv")}</th>
      % elif seosed:
      <th>${_("Kasutus min")}</th>
      <th>${_("Kasutus max")}</th>
      % endif
      % if c.block.tyyp == const.INTER_CHOICE:
      % if c.ylesanne.lahendada_lopuni:
      <th>${_("Kohustuslikud küsimused")}</th>
      % endif
      <th>${_("Peida sisuplokid")}</th>
      <th>${_("Kuva sisuplokid")}</th>
      % endif
      % if c.block.tyyp == const.INTER_MCHOICE:
      <th></th>
      % endif
      <th></th>
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_choices(kysimus, c.new_item(),prefix,'-%s' % cnt, seosed,
                           size=size, toolbar=toolbar, wysiwyg=wysiwyg, txpos=txpos, joondus=joondus, fikseeritud=fikseeritud)}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(valikud):
        ${self.row_choices(kysimus, item,prefix,'-%s' % cnt, seosed,
                           size=size, toolbar=toolbar, wysiwyg=wysiwyg, txpos=txpos, joondus=joondus, fikseeritud=fikseeritud)}
  %   endfor
  % endif
  </tbody>
  <tfoot>
    <tr>
      <td colspan="${MAXCOLS}" id="${prefix}_ckeditor_bottom">
      </td>
    </tr>
% if c.is_edit and not c.lang:
    <tr>
      <td colspan="${MAXCOLS}">
    <%
       if wysiwyg and kysimus.rtf:
          toggle_rtf = "toggle_ckeditor('%s', false, -1, ck_attr)" % (prefix);
       elif not wysiwyg and can_rtf:
          toggle_rtf = "toggle_html('%s', false, -1)" % (prefix)
       else:
          toggle_rtf = ''
    %>
${h.button(_("Lisa"), onclick=f"grid_addrow('choicetbl_{prefix}', '{prefix}kood', '{gentype}', null, {valista and 'true' or 'false'});refresh_text_options('{prefix}kood');{toggle_rtf}; ", level=2, mdicls='mdi-plus')}
<div id="sample_choicetbl_${prefix}" class="invisible">
<!--
   ${self.row_choices(kysimus, c.new_item(kood='__kood__'),prefix, '__cnt__',seosed,
                      size=size, toolbar=toolbar, wysiwyg=wysiwyg, txpos=txpos, joondus=joondus, fikseeritud=fikseeritud)}
-->
</div>
      </td>
    </tr>
% endif
  </tfoot>
</table>
<br/>
</%def>

<%def name="choices_mchoice_header1(kysimus, prefix_v)">
    <tr>
      <th align="right">${_("Veeru päis")}</td>
      <th>
        ${self.khdr_text(kysimus, c.block)}                
      </th>
      % for ind_v in range(c.block.laius or 1):
      <% item_v = ind_v < len(c.v2_valikud) and c.v2_valikud[ind_v] or c.new_item() %>
      <th>
        ${self.choice_text(kysimus, item_v, '%s-%d' % (prefix_v, ind_v))}        
        ${h.hidden('%s-%d.id' % (prefix_v, ind_v), item_v.id)}
        ${h.hidden('%s-%d.removed' % (prefix_v, ind_v), '', class_="v2-removed", data_ind=ind_v)}
      </th>
      % endfor
      <th colspan="3"></th>
    </tr>
    % if not c.lang:
    <tr>
      <th align="right">${_("Selgitus")}</th>
      <th></th>
      <% valikute_arv = c.block.laius or 1 %>
      % for ind_v in range(valikute_arv):
      <% item_v = ind_v < len(c.v2_valikud) and c.v2_valikud[ind_v] or c.new_item() %>
      <th>
        ${h.text('%s-%d.selgitus' % (prefix_v, ind_v), item_v.selgitus)}
      </th>
      % endfor
      <th colspan="3"></th>
    </tr>
    <tr>
      <th align="right">${_("Veeru laius")}</th>
      <%
        data = c.block.get_json_sisu() or {}
        colwidths = data.get('colwidths') or []
        if len(colwidths) <= valikute_arv:
            colwidths = colwidths + [''] * (valikute_arv + 1 - len(c.colwidths))
      %>
        % for ind_v in range(valikute_arv+1):
        <th>${h.text('mch.colwidth-%d' % (ind_v), colwidths[ind_v], size=7, pattern='[0-9][0-9]*(px|%|)')}</th>
        % endfor
        <th colspan="3"></th>
    </tr>
    % endif
</%def>

<%def name="hotspot(item, baseprefix, cnt, invisible, maxvastus, minvastus1=None, maaramata=False, kood1_cls=None)">
## Piirkonna rida piirkondade tabelis
## item on piltobjekt 
<%
  prefix = '%s%s' % (baseprefix, cnt)
  if kood1_cls is None:
     # kood, mille järgi hindamismaatriksis valikvälja jaoks siit tabelist valikud leitakse
     kood1_cls = '%skood' % baseprefix
%>
       <tr id="${item.kood or prefix.replace('.','')}" name="${prefix}">
         % if c.is_edit or c.is_tr:
         <td>
           ${h.checkbox('hsrow', 1, class_="selectrow", id='hsrow%s' % item.id)}
         </td>
         % endif
         <td>
           % if c.is_edit or c.is_tr:
           ${h.text("%s.kood" % (prefix), item.kood, class_='%s identifier' % kood1_cls,
           onchange="refresh_text_options('%s');" % kood1_cls)}
           % else:
           ${item.kood}
           ${h.hidden('%s.kood' % (prefix), item.kood, class_=kood1_cls)}
           % endif
         </td>
         <td nowrap>
           ##${h.text("%s.koordinaadid" % (prefix), item.koordinaadid, readonly=True)}
           ${h.text("%s.koordinaadid" % (prefix), item.koordinaadid,
                    onchange='sketchpads.sketchpad_%s.change_shape("%s", "%s")' % (c.block_prefix, item.kood or prefix, prefix))}
         </td>
         % if invisible:
         <td>
           ${h.checkbox1("%s.nahtamatu" % (prefix), 1, checked=item.nahtamatu)}
         </td>
         % endif
         % if minvastus1:
         <td>
           ${h.checkbox1("%s.min_vastus" % (prefix), 1, checked=item.min_vastus)}
         </td>
         % endif
         % if maxvastus:
         <td>
           ${h.posint5('%s.max_vastus' % (prefix), item.max_vastus)}
           % if not c.is_edit and c.lang:
           ${h.hidden('%s.max_vastus' % (prefix), item.max_vastus)}
           % endif
         </td>
         % endif
         <td>
           % if c.is_tr:
           ${item.selgitus}
           % else:
           ${h.text('%s.selgitus' % (prefix), item.selgitus, maxlength=255)}
           % endif
         </td>
         <td nowrap>
           % if not maaramata or item.koordinaadid:
           <a href='#' id='zoom_${prefix}'
              onclick='sketchpads.sketchpad_${c.block_prefix}.activate_shape("${item.kood or prefix}");return false;' title="${_("Näita")}">
             ${h.mdi_icon('mdi-image-search-outline')}
           </a>
           % endif
           ${h.hidden('%s.id' % prefix, item.id)}
           ${h.hidden('%s.kujund' % (prefix), item.kujund)}
           % if c.is_edit:
             <% 
               js_extra = "refresh_text_options('%skood');" % baseprefix
               js_extra += "sketchpads.sketchpad_%s.remove_shapeNode('%s');" % (c.block_prefix, item.id and item.kood or 'hs__cnt__')
             %>
           ${h.grid_remove(js_extra)}
           % endif
         </td>
       </tr>
</%def>

<%def name="area_map_entry(item, baseprefix, cnt, is_sallivus=False)">
## Hindamismaatriksi rida, kus vastus antakse piirkonna koordinaatidena
## item on hindamismaatriks
       <% prefix = '%s%s' % (baseprefix, cnt) %>
       ## eeldatakse, et baseprefixi lõpp on "hs"
       ## baseprefix ise võib olla kujul "am-N.hs"
       <tr id="${item.id or prefix.replace('.','')}" name="${prefix}">
         <td nowrap width="20px">
           <a href='#' title="${_("Näita")}"
              onclick='sketchpads.sketchpad_${c.block_prefix}.activate_shape("${item.id or prefix}");return false;'>
             <i class="mdi mdi-image-search-outline mdi-36px"></i>
           </a>
         </td>
         <td>
           ##${h.text("%s.koordinaadid" % (prefix), item.koordinaadid, readonly=True)}
           ${h.text("%s.koordinaadid" % (prefix), item.koordinaadid,
                    onchange='sketchpads.sketchpad_%s.change_shape("%s", "%s")' % (c.block_prefix, item.id or prefix, prefix))}
         </td>
         % if is_sallivus:
         <td>
           ${h.posint5('%s.sallivus' % (prefix), item.sallivus or 20)}
         </td>
         % endif
         <td>${h.text('%s.tingimus' % prefix, item.tingimus)}</td>
         <td>
           ${h.float5('%s.pallid' % (prefix), item.pallid)}
         </td>
         <td>
           ${h.checkbox1('%s.oige' % (prefix), 1, checked=item.oige)}
         </td>
         % if c.block.tyyp in (const.INTER_GR_GAP, const.INTER_POS):
         <td>
           ${h.posint5('%s.tabamuste_arv' % (prefix), item.tabamuste_arv)}
         </td>
         % endif
         <td>
           ${h.text('%s.tahis' % (prefix), item.tahis, maxlength=25, size=15)}
         </td>
         <td>
           ${h.text('%s.selgitus' % (prefix), item.selgitus, maxlength=255, size=30)}
         </td>
         <td>
           ${h.hidden('%s.id' % prefix, item.id)}
           ${h.hidden('%s.kujund' % (prefix), item.kujund)}
           ${h.hidden('%s.deleted' % prefix, '', class_="deleted")}           
           % if c.is_edit and item.id:
           ${h.grid_hide()}
           % elif c.is_edit:
           ${h.grid_remove()}           
           % endif
         </td>
       </tr>
</%def>

<%def name="trail_map_entry(item, baseprefix, cnt, is_sallivus=False)">
## Hindamismaatriksi rida, kus vastus antakse teekonnana
## item on hindamismaatriks
       <% prefix = '%s%s' % (baseprefix, cnt) %>
       ## eeldatakse, et baseprefixi lõpp on "hs"
       ## baseprefix ise võib olla kujul "am-N.hs"
       <tr id="${item.id or prefix.replace('.','')}" name="${prefix}">
         <td>
           ${h.text("%s.kood1" % (prefix), item.kood1, class_='koordinaadid')}
           % if not c.is_edit:
           ## teeme välja, et maatriksi real klikkides saaks siit lugeda raja ja seda esitada
           ${h.hidden('%s.kood1_view' % prefix, item.kood1, class_='koordinaadid')}
           % endif
         </td>
         <td>${h.text('%s.tingimus' % prefix, item.tingimus)}</td>
         <td>
           ${h.float5('%s.pallid' % (prefix), item.pallid)}
         </td>
         <td>
           ${h.checkbox1('%s.oige' % (prefix), 1, checked=item.oige)}
         </td>
         <td>
           ${h.hidden('%s.id' % prefix, item.id)}
           ${h.hidden('%s.deleted' % prefix, '', class_="deleted")}           

           <a href='#' class="hmzoom" title="${_("Näita")}">
             <i class="mdi mdi-image-search-outline mdi-24px"></i>
           </a>

           % if c.is_edit and item.id:
           ${h.grid_hide()}
           % elif c.is_edit:
           ${h.grid_remove()}           
           % endif
         </td>
       </tr>
</%def>

<%def name="edit_hotspots(sisuplokk, invisible=False, maxvastus=False, minvastus1=False, kysimus=None, yle=False)">
## Piirkondade tabel muutmisresiimis
<%
  prefix = 'hs'
  kood1_cls = 'hskood'
  if kysimus is None:
     kysimus = sisuplokk.kysimus
  if sisuplokk.tyyp == const.INTER_COLORAREA:
     valikupiirkonnad = [k.valikud[0] for k in sisuplokk.pariskysimused if len(k.valikud)]
  else:
     valikupiirkonnad = list(kysimus.valikud)

  valikud_x = []
  if yle:
     ## ylejäänud ala valik, mida koostaja ei saa sisestada, aga mis on vastuste analyysis vajalik  
     valikud = []
     for v in valikupiirkonnad:
         if v.kood == const.VALIK_X:
             valikud_x.append(v)
         else:
             valikud.append(v)
     if not valikud_x:
         valikud_x = [c.new_item(kood=const.VALIK_X, selgitus=_("Määramata ala"), nahtamatu=True)]
     valikupiirkonnad = valikud
%>
  <div class="floatleft mb-3">
    <table width="${invisible and 600 or 450}px" id="choicetbl" class="table singleselect lh-11 mb-1">
      
        <caption>${_("Piirkonnad")}</caption>
        <thead>
          <tr>
            % if c.is_edit or c.is_tr:
            <th width="20px"></th>
            % endif
            <th width="100px">ID</th>
            <th>${_("Koordinaadid")}</th>
            % if invisible:
            <th>${_("Nähtamatu")}</th>
            % endif
            % if minvastus1:
            <th>${_("Kohustuslik")}</th>
            % endif
            % if maxvastus:
            <th>
              % if sisuplokk.tyyp in (const.INTER_TXPOS2, const.INTER_TXGAP, const.INTER_TXASS):
              ${_("Maksimaalne tekstide arv")}
              % else:
              ${_("Maksimaalne kujundite arv")}
              % endif
            </th>            
            % endif
            <th>${_("Selgitus")}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          % if c._arrayindexes != '' and not c.is_tr:
          ## valideerimisvigade korral
          %   for cnt in c._arrayindexes.get(prefix) or []:
            ${self.hotspot(c.new_item(), prefix, '-%s' % (cnt), invisible, maxvastus, minvastus1, kood1_cls=kood1_cls)}
          %   endfor
          % else:
          ## tavaline kuva
          %   if tulemus:
          %     for cnt, item in enumerate(valikupiirkonnad):
                 ${self.hotspot(item, prefix, '-%s' % cnt, invisible, maxvastus, minvastus1, kood1_cls=kood1_cls)}
          %     endfor
          %   endif
          % endif
        </tbody>
        % if valikud_x:
        ## määramata ala
        <%
          prefix_x = '%s_x' % prefix
          is_edit, is_tr = c.is_edit, c.is_tr
          c.is_edit, c.is_tr = False, False
        %>
        <tfoot>
          %     for cnt, item in enumerate(valikud_x):
                 ${self.hotspot(item, prefix_x, '-%s' % cnt, invisible, maxvastus, minvastus1, maaramata=True, kood1_cls=kood1_cls)}
          %     endfor
        </tfoot>
        <%
          c.is_edit, c.is_tr = is_edit, is_tr
        %>
        % endif
      </table>
      % if c.is_edit and not c.lang:
      ${h.button(_("Lisa piirkond"), onclick=f"grid_addrow('choicetbl', '{prefix}kood');refresh_text_options('{prefix}kood');", level=2, mdicls='mdi-plus')}
      <div id="sample_choicetbl" class="invisible">
        <!--
        ${self.hotspot(c.new_item(kood='__kood__'), prefix, '__cnt__', invisible, maxvastus, minvastus1, kood1_cls=kood1_cls)}
        -->
      </div>
      % endif

      <div id="debug"></div>
      <script>
       $(function(){
        $('#choicetbl').on('change', 'input.selectrow', function(){
             if(this.checked){
                var tr = $(this).closest('tr'), id = tr.attr('id'), prefix = tr.attr('name');
                sketchpads.sketchpad_${c.block_prefix}.set_shape_id(id, prefix+"koordinaadid", prefix+"kujund");
             } else {
                sketchpads.sketchpad_${c.block_prefix}.set_shape_id('','','');
             }
        });
       });
      </script>
  </div>
</%def>

<%def name="hindamismaatriks_pt(kysimus, baseprefix, piltobj=None, is_sallivus=False, naidis=False, naidis_naha=False, maatriks=True)">
## Hindamismaatriks, milles vastused antakse piirkondade koordinaatidena
  <% 
     prefix = '%s.hs' % baseprefix 
     c.is_edit_orig = c.is_edit
     c.is_edit = c.is_edit_hm
     tulemus = kysimus.tulemus or c.new_item(kood=kysimus.kood, arvutihinnatav=True)
  %>
  <div class="d-flex flex-wrap mt-1 mb-1 gbox hmtable overflow-auto">
    <div class="bg-gray-50 p-3">
      ${h.hidden('%s.kysimus_id' % baseprefix, kysimus.id)}
      ${self.tulemus(kysimus, tulemus, '%s.' % baseprefix, piltobj, maatriks=maatriks)}
    </div>
    % if maatriks:
    <div class="flex-grow-1 p-3">
      <% choicetbl_id = "choicetbl_%s" % (baseprefix.replace('-','').replace('.','')) %>
      <table width="820px" id="${choicetbl_id}" class="table table-borderless table-striped singleselect lh-11">
        <caption>${_("Hindamismaatriks")}</caption>
        <thead>
          <tr>
            <th colspan="2">${_("Koordinaadid")}</th>
            % if is_sallivus:
            <th>${_("Sallivus")}</th>
            % endif
            <th>${_("Tingimus")}</th>
            <th>${_("Punktid")}</th>
            <th>${_("Õige")}</th>
            % if c.block.tyyp == const.INTER_POS:
            <th>${_("Tabamuste arv")}</th>
            % endif
            <th>${_("Tabamuste loendur")}</th>
            <th>${_("Selgitus")}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          % if c._arrayindexes != '' and not c.is_tr:
          ## valideerimisvigade korral
          %   for cnt in c._arrayindexes.get(prefix) or []:
            ${self.area_map_entry(c.new_item(), prefix, '-%s' % (cnt), is_sallivus)}
          %   endfor
          % else:
          ## tavaline kuva
          %   if tulemus:
          %     for cnt, item in enumerate(tulemus.hindamismaatriksid):
            ${self.area_map_entry(item, prefix, '-%s' % (cnt), is_sallivus)}
          %     endfor
          %   endif
          % endif
        </tbody>
      </table>
      % if c.is_edit and not c.lang:
      ${h.button(_("Lisa"), onclick=f"grid_addrow('{choicetbl_id}')", level=2, mdicls='mdi-plus')}
      % if kysimus.seq == 2 and c.block.tyyp == const.INTER_TXPOS or kysimus.seq == 1 and c.block.tyyp == const.INTER_POS:
      ${h.submit(_("Kopeeri piirkonnad teistesse maatriksitesse"), id="copyarea")}
      % endif
      <div id="sample_${choicetbl_id}" class="invisible">
        <!--
        ${self.area_map_entry(c.new_item(), prefix, '__cnt__', is_sallivus)}
        -->
      </div>
      % endif
      <div id="debug"></div>
      <script>
     function ${choicetbl_id}_tr_click(){
          var id = $(this).attr('id'); 
          var prefix = $(this).attr('name'); 
          sketchpads.sketchpad_${c.block_prefix}.set_shape_id(id, prefix+"koordinaadid", prefix+"kujund");
      % if is_sallivus:
          var sallivus = $(this).find('input[name="'+prefix+'.sallivus"]').val();
          sketchpads.sketchpad_${c.block_prefix}.settings_normal['stroke-width'] = (sallivus ? sallivus : 2);
          sketchpads.sketchpad_${c.block_prefix}.settings_normal['stroke-opacity'] = 0.5;
      % endif
     }

     $(function(){
      $('#${choicetbl_id} tbody tr').click(${choicetbl_id}_tr_click);
     });
      </script>
    </div>
% endif
    % if naidis:
    <div class="flex-grow-1">
      ${self.naidisvastus(kysimus, tulemus, '%s.' % baseprefix, rows=3, naha=naidis_naha)}
    </div>
  % endif
  <%
     c.is_edit = c.is_edit_orig
  %>
  </div>
</%def>

<%def name="hindamismaatriks_trail(kysimus, baseprefix, piltobj=None, is_sallivus=False, naidis=False, naidis_naha=False, maatriks=True)">
## Hindamismaatriks, milles vastused antakse teekonna märkimisega
  <% 
     prefix = '%s.ht' % baseprefix 
     c.is_edit_orig = c.is_edit
     c.is_edit = c.is_edit_hm
     tulemus = kysimus.tulemus or c.new_item(kood=kysimus.kood, arvutihinnatav=True)
  %>
<div class="d-flex flex-wrap mt-2 mb-1 gbox hmtable overflow-auto">
  <div class="bg-gray-50 p-3">  
    ${h.hidden('%s.kysimus_id' % baseprefix, kysimus.id)}
    ${self.tulemus(kysimus, tulemus, '%s.' % baseprefix, piltobj, maatriks=maatriks)}
  </div>
  % if maatriks:
  <div class="flex-grow-1 p-3">
    <% choicetbl_id = "choicetbl_%s" % (piltobj and piltobj.id or '') %>
      <table width="530px" id="${choicetbl_id}" class="table table-borderless table-striped singleselect lh-11">
        <caption>${_("Hindamismaatriks")}</caption>
        <thead>
          <tr>
            <th colspan="1">${_("Teekond")}</th>
            <th>${_("Tingimus")}</th>
            <th>${_("Punktid")}</th>
            <th>${_("Õige")}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          % if c._arrayindexes != '' and not c.is_tr:
          ## valideerimisvigade korral
          %   for cnt in c._arrayindexes.get(prefix) or []:
            ${self.trail_map_entry(c.new_item(), prefix, '-%s' % (cnt), is_sallivus)}
          %   endfor
          % else:
          ## tavaline kuva
          %   if tulemus:
          %     for cnt, item in enumerate(tulemus.hindamismaatriksid):
            ${self.trail_map_entry(item, prefix, '-%s' % (cnt), is_sallivus)}
          %     endfor
          %   endif
          % endif
        </tbody>
      </table>
      % if c.is_edit and not c.lang:
      ${h.button(_("Lisa"), onclick=f"grid_addrow('{choicetbl_id}')", level=2, mdicls='mdi-plus')}
      <div id="sample_${choicetbl_id}" class="invisible">
        <!--
        ${self.trail_map_entry(c.new_item(), prefix, '__cnt__')}
        -->
      </div>
      % endif
      <div id="debug"></div>
      <script>
     function ${choicetbl_id}_tr_click(){
        var tr = $(this).closest('tr');
        tr.toggleClass('zselected');
        if(tr.is('.zselected'))
  % if c.is_edit:
          sketchpads.sketchpad_${c.block_prefix}.edit_trail(tr.find('input.koordinaadid'), false);
  % else:
          sketchpads.sketchpad_${c.block_prefix}.show_trail(tr.find('input.koordinaadid').val(), true);
  % endif
       else
          sketchpads.sketchpad_${c.block_prefix}.clear_trailables();
       return false;
     }

     $(function(){
      $('#${choicetbl_id} tbody tr .hmzoom').click(${choicetbl_id}_tr_click);
     });
      </script>
  </div>
% endif
  </div>
  <%
     c.is_edit = c.is_edit_orig
  %>
</%def>

<%def name="map_entry(kysimus, baseprefix, cnt, item, kood1=True, kood2=False, 
            kood1_cls=None, kood2_cls=None, can_rtf=False, is_rtf=None, matheditor=False, wmatheditor=False)">
## Tavalise hindamismaatriksi rida
## Vastus antakse koodina või vabatekstina või paarina või kolmikuna
##
## Kui kood2==False, siis ei ole tegu paariga
##
## Kui kood1 või kood2 on list, siis on vastaval väljal tegu valikväljaga
##
## Kood1_cls ja kood2_cls on klasside nimed, mida omavate tekstiväljade 
## väärtuste muutmisel muudetakse dünaamiliselt valikväljade sisu
<%
  if cnt == '__cnt__':
     prefix = '%s%s' % (baseprefix, cnt)
  else:
     prefix = '%s-%s' % (baseprefix, cnt)
%>
       <tr id="${prefix.replace('.','')}">
         <td>
           % if cnt == '__cnt__':
           __cnt__+1
           % else:
           ${cnt+1}
           % endif
         </td>
         % if kood1 or kood1_cls:
         <td>
           % if isinstance(kood1, list):
             % if c.lang:
             ${h.select("%s.kood1" % (prefix), item.kood1, kood1, class_=kood1_cls, ronly=True)}
             % else:
             ${h.select("%s.kood1" % (prefix), item.kood1, kood1, class_=kood1_cls, add_missing=True)}
             % endif
           % else:
             <%
                size = not kood2 and not kood2_cls and 45 or 25
                if c.lang:
                   ronly = not c.is_tr
                   value = item.tran(c.lang).kood1
                else:
                   ronly = not c.is_tr and not c.is_edit
                   value = item.kood1
                if c.block.tyyp == const.INTER_PUNKT:
                   # soovime, et tyhikud jääks alles (ckeditor kustutab tavalise tyhiku teksti algusest ära)
                   value = value.replace(' ', '\xa0')

                can_math = matheditor # latex, mathquill
                is_math = matheditor and not item.valem
                can_wmath = wmatheditor # mathml, wiris mathtype
                is_wmath = wmatheditor and not item.valem
             %>
             % if c.lang:
               ## tõlkimine
               % if is_wmath:
               ${h.lang_tag(c.orig_lang)}
               <span class="lang-orig mathml-view">${item.kood1}</span>
               % elif is_math:
               ${h.lang_tag(c.orig_lang)}
               <span class="lang-orig math-view">${h.html_lt(item.kood1)}</span>
               % else:
               ${h.lang_orig(item.kood1, rtf=is_rtf)}
               % endif
               <br/>
               ${h.lang_tag()}
             % endif
             % if ronly and is_wmath:
               <div id="mw_${h.toid(prefix)}" name="${prefix}.kood1" style="min-width:300px">${value}</div>

             % elif is_wmath:
               <div id="mw_${h.toid(prefix)}" name="${prefix}.kood1" style="min-width:300px;height:200px;" class="wmath-edit wmath-edit-poptoolbar" lang="${request.locale_name}"></div>
               ${h.text('%s.kood1' % prefix, value, id="inp_mw_%s" % h.toid(prefix), ronly=ronly, size=size, style="display:none")}             
             % elif can_wmath and not ronly:
               <div id="mw_${h.toid(prefix)}" name="${prefix}.kood1" style="min-width:300px;display:none;" class="wmath-edit wmath-edit-poptoolbar" lang="${request.locale_name}"></div>
               ${h.text("%s.kood1" % (prefix), value, id="inp_mw_%s" % h.toid(prefix), ronly=ronly, size=size, class_="wmath-editable")}               

             % elif ronly and is_math:
               <div id="me_${h.toid(prefix)}" name="${prefix}.kood1" style="min-width:300px" class="math-view">${h.html_lt(value)}</div>
               % if value:
                     <div class="math-hidden float-right">
                       <span class="math-hidden-latex" style="display:none">${h.html_lt(value)}</span>
                       <u style="cursor:pointer" onclick="$(this).prev('.math-hidden-latex').toggle()"><img src="/static/images/latex.png"/></u>
                     </div>
               % endif

             % elif is_math:
               <div id="me_${h.toid(prefix)}" name="${prefix}.kood1" math-toolbar="${kysimus.kood}" style="min-width:300px" class="math-edit">${h.html_lt(value)}</div>
               ${h.text('%s.kood1' % prefix, value, ronly=ronly, size=size, class_='math-editable', style="display:none")}             

               % if value:
                     <div class="math-hidden float-right">
                       <span class="math-hidden-latex" style="display:none">${h.html_lt(value)}</span>
                       <u style="cursor:pointer" onclick="var l=$(this).prev('.math-hidden-latex'),m=$(this).closest('td').find('input.math-editable');if(m.length)l.text(m.val());l.toggle()"><img src="/static/images/latex.png"/></u>
                     </div>
               % endif

             % elif can_math and not ronly:
               <div id="me_${h.toid(prefix)}" name="${prefix}.kood1" style="min-width:300px;display:none;" class="math-edit"></div>
               ${h.text("%s.kood1" % (prefix), value, ronly=ronly, size=size, class_='math-editable')}               

             % elif ronly and is_rtf:
                ${value}
             % elif can_rtf and is_rtf:
                ${h.textarea('%s.kood1_rtf' % (prefix), value, cols=size, rows=3, ronly=ronly, class_='editable')}
                ## vigade jaoks
                ${h.text('%s.kood1' % (prefix), '', ronly=ronly, size=size, class_='editable', style="display:none")}             
             % elif can_rtf:
                ${h.text('%s.kood1' % (prefix), value, ronly=ronly, size=size, class_='editable')}
             % elif c.block.tyyp==const.INTER_EXT_TEXT:
                ${h.textarea('%s.kood1' % (prefix), value, cols=size, rows=3, ronly=ronly)}               
             % elif c.block.tyyp==const.INTER_CROSSWORD:
                ${h.text("%s.kood1" % (prefix), value, ronly=ronly, size=size, style="text-transform:uppercase;")}
             % else:
                ${h.text("%s.kood1" % (prefix), value, ronly=ronly, size=size)}
             % endif
               
           % endif
         </td>
         % endif
         % if kood2 or kood2_cls:
         <td nowrap>
           % if isinstance(kood2, list):
             % if c.lang:
             ${h.select("%s.kood2" % (prefix), item.kood2, kood2, class_=kood2_cls, ronly=True)}
             % else:
             ${h.select("%s.kood2" % (prefix), item.kood2, kood2, class_=kood2_cls)}
             % endif
           % else:
             % if c.lang:
             ${h.lang_orig(item.kood2)}<br/>
             ${h.lang_tag()}
             ${h.text("%s.kood2" % (prefix), item.tran(c.lang).kood2, ronly=not c.is_tr)}
             % else:
             ${h.text("%s.kood2" % (prefix), item.kood2, ronly=not c.is_tr and not c.is_edit)}
             % endif
           % endif
         </td>
         % elif matheditor:
         <td nowrap>
             % if c.lang:
             ${h.lang_orig(item.kood2)}<br/>
             ${h.lang_tag()}
             <br/>
             ${h.text("%s.kood2" % (prefix), item.tran(c.lang).kood2, ronly=not c.is_tr)}
             % else:
             ${h.text("%s.kood2" % (prefix), item.kood2, ronly=not c.is_tr and not c.is_edit)}
             % endif
         </td>
         % else:
         <td nowrap class="basetype basetype-integer basetype-float" style="display:none">
             % if c.lang:
             ${h.lang_orig(item.kood2)}<br/>
             ${h.lang_tag()}
             <br/>
             ${h.text("%s.kood2" % (prefix), item.tran(c.lang).kood2, ronly=not c.is_tr)}
             % else:
             ${h.text("%s.kood2" % (prefix), item.kood2, ronly=not c.is_tr and not c.is_edit)}
             % endif
         </td>
         % endif
         % if matheditor:
         <td>${h.checkbox1('%s.valem' % prefix, 1, checked=item.valem, class_="math-valem")}</td>
         <td>${h.checkbox1('%s.teisendatav' % prefix, 1, checked=item.teisendatav, class_="math-teisendatav")}</td>
         <td>${h.checkbox1('%s.vrd_tekst' % prefix, 1, checked=item.vrd_tekst, class_="math-vrd_tekst")}</td>         
         % endif
         <td>${h.text('%s.tingimus' % prefix, item.tingimus)}</td>
         <td>
           ${h.float5("%s.pallid" % (prefix), item.pallid)}
           % if not c.is_edit and c.lang:
           ## väli on vajalik selleks, et inline lünga dialoogiaknast saaks ckeditorisse kõik andmed edasi anda
           ${h.hidden('%s.pallid' % prefix, item.pallid)}
           % endif           
         </td>
         <td>
           ${h.checkbox1('%s.oige' % (prefix), 1, checked=item.oige)}
         </td>
         % if c.block.tyyp == const.INTER_GR_GAP:
         <td>
           ${h.posint5('%s.tabamuste_arv' % (prefix), item.tabamuste_arv)}
         </td>
         % endif
         % if c.block.tyyp != const.BLOCK_FORMULA:
         <td>
           ${h.text('%s.tahis' % (prefix), item.tahis, maxlength=25, size=15)}
         </td>
         % endif
         <td>
           ${h.hidden('%s.id' % prefix, item.id)}
           ${h.hidden('%s.deleted' % prefix, '', class_="deleted")}           
           % if c.is_edit and item.id:
           ${h.grid_hide()}
           % elif c.is_edit:
           ${h.grid_remove()}           
           % elif c.is_edit_orig and c.is_sp_analysis and c.can_edit_hm and c.app_ekk:
           <% del_url = h.url('hindamine_analyys_vastused_kysimus_delete_maatriks', toimumisaeg_id=c.toimumisaeg.id, kysimus_id=c.kysimus.id, id=item.id, maatriks=item.maatriks, page=c.page) %>
           <a class="menu2 xclose" style="cursor:pointer;" onclick="var pel=$(this).parents('.listdiv');confirm_dialog(eis_textjs.confirm_delete, function(){ dialog_load('${del_url}', null, 'POST', pel); close_this_dialog(this);})">&times;</a>                      
           % endif
         </td>
       </tr>
</%def>

<%def name="naidisvastus(kysimus, tulemus, prefix, rows=3, naha=True, floating=True)">
##<div style="min-width:530px">
  <div>
    <div class="d-flex flex-wrap">
      <h3>${_("Näidisvastus või hindamisjuhend")}</h3>
      % if naha:
      <div class="flex-grow-1 text-right">
      ${h.checkbox1('%snaidis_naha' % prefix, checked=tulemus and tulemus.naidis_naha,
        label=_("Näita õige vastusena"))}
      </div>
      % endif
	</div>
          <div>
              % if c.lang and tulemus.naidisvastus:
              <div class="juhend-scroll">
                ${h.lang_orig(tulemus.naidisvastus)}
              </div>
              ${h.lang_tag()}
              % endif			  
              <% naidis_text = tulemus and tulemus.tran(c.lang).naidisvastus or '' %>
              ${h.ckeditor('%snaidisvastus' % prefix, naidis_text,
              ronly=not c.is_tr and not c.is_edit or bool(c.block.ylesanne and c.block.ylesanne.lukus),
              entermode=kysimus.rtf_enter or 'null')}
          </div>
</div>
</%def>

<%def name="tulemus(kysimus, tulemus, prefix, piltobj=None, basetype_opt=None, ordered=False, maatriks=True, fix_kood=False, f_toggle_ckeditor=None, caption=None, common=False, nocommon=False)">
<%
  extra = lambda v: not v and 'extra nodisplay2' or ''
  # klass "ctulemus" on nendel väljadel, millel on mõte
  # ainult tulemusega küsimuste korral ja mida ei kuvata näiteküsimustes
  # klass "extra" on nendel väljadel, mis on tühjad ja mida vaikimisi ei kuvata, 
  # vaid mis kuvatakse ainult siis, kui kasutaja klikib noolel "Rohkem"
  # common - mitme kysimuse yhiste seadete vorm (ei ole kysimuse koodi)
  # nocommon - nende kysimuste koodide vorm, mille muud seaded on yhisel vormil
%>
## Hindamismaatriksi andmed, mis on tulemuse tabelis
  <div class="hindamismx mr-3 d-inline-block" style="max-width:760px">
  % if common:
${h.hidden('%skood' % prefix, 'common')}
% elif nocommon:
<%
  ## tulemuse kirje väljad on nähtavad, aga read-only,
  ## sest neid muudetakse mujal
  is_edit = c.is_edit
  c.is_edit = False
%>
% endif

  <h3>${caption or _("Vastuse hindamine")}</h3>
  <% ch = h.colHelper('col-md-6', 'col-md-6') %>
% if not common:
  <div class="form-group row">
    <% name = '%skood' % prefix %>
    ${ch.flb(_("Küsimuse ID"), name, rq=True)}
    <div class="col-md-6">
      % if piltobj is None and not fix_kood:
        ${h.text('%skood' % prefix, tulemus.kood, class_="identifier")}
        % if not c.is_edit:
        ${h.hidden('%skood' % prefix, tulemus.kood)}
        % endif
      % else:
        <b>${tulemus.kood}</b>
        ${h.hidden('%skood' % prefix, tulemus.kood, class_="obj-kood")}

        % if c.block.tyyp == const.INTER_HOTTEXT:
        &nbsp;
        ${h.checkbox1('%snaide' % prefix, 1, checked=tulemus.naide, label=_("Näide"),
        class_="toggle-ctulemus")}
        % endif

        % if piltobj and c.block.tyyp not in (const.INTER_POS, const.INTER_POS2):

        <img src="${piltobj.get_url(c.lang, c.url_no_sp)}" ${h.width(piltobj)} ${h.height(piltobj)}/>
##        ${h.image(h.url('ylesanne_sisufail', id='%s.%s' % (piltobj.id, piltobj.fileext), lang=c.lang), 'Pilt', width=piltobj.laius, height=piltobj.korgus)}
         % endif
      % endif
    </div>
  </div>
  <div class="form-group row ctulemus ${extra(kysimus.selgitus)}">
    <% name = '%sk_selgitus' % prefix %>
    ${ch.flb(_("Selgitus"), name)}
    <div class="col-md-6">
        % if c.block.tyyp in (const.INTER_MATCH2, const.INTER_TXPOS, const.INTER_COLORAREA):
        ${kysimus.selgitus}
        % else:
        ${h.text('%sk_selgitus' % prefix, kysimus.selgitus, maxlength=255)}
        % endif
    </div>
  </div>
% endif

  % if ordered:
  <div class="form-group row ctulemus">
    <% name = '%skardinaalsus' % prefix %>
    ${ch.flb(_("Algoritm"), name)}
    <div class="col-md-6">
      ${h.select('%skardinaalsus' % prefix, tulemus.kardinaalsus, c.opt.cardinality_ordered)}
    </div>
  </div>
  % endif
  
  % if basetype_opt:
  <div class="form-group row ctulemus">
    <% name = '%sbaastyyp' % prefix %>
    ${ch.flb(_("Väärtuse tüüp"), name)}
    <div class="col-md-6">
      ${h.select(name, tulemus.baastyyp, basetype_opt, wide=False, 
              class_='baastyyp', onclick="showbasetype($(this))")}
        % if not c.is_edit:
        ${h.hidden('%sbaastyyp' % prefix, tulemus.baastyyp, class_='baastyyp')}
        % endif
        <script>
          function showbasetype(fld)
          {
             var cls = "basetype-${tulemus.baastyyp}";
             var val = fld.val();
             if(val == "${const.BASETYPE_STRING}")
                cls = 'basetype-string';
             if(val == "${const.BASETYPE_POSSTRING}")
                cls = 'basetype-string';
             else if(val == "${const.BASETYPE_FLOAT}")
                cls = 'basetype-float';
             else if(val == "${const.BASETYPE_INTEGER}")
                cls = 'basetype-integer';
             else if(val == "${const.BASETYPE_BOOLEAN}")
                cls = 'basetype-boolean';          
             ## tulemuse kirjelduse tabeli read - kuvatakse ainult siis, kui on sees "kuva rohkem"
             var tr_more = fld.closest('.hindamismx').find('.basetype');
             tr_more.filter(':not(.'+cls+')').addClass('nodisplay1');
             tr_more.filter('.'+cls).removeClass('nodisplay1');
             ## hindamismaatriksi tabeli veerud - kuvatakse alati
             var tr_hm = fld.closest('.hmtable').find('.hmlist .basetype');
             tr_hm.filter(':not(.'+cls+')').hide();
             tr_hm.filter('.'+cls).show();
          }
          $(function(){ showbasetype($('[name="${prefix}baastyyp"]'))});
        </script>
     </div>
    </div>
    % elif c.block.tyyp == const.INTER_INL_TEXT and tulemus.baastyyp == const.BASETYPE_MATH:
  ${h.hidden('%sbaastyyp' % prefix, tulemus.baastyyp, class_='baastyyp')}        
    % endif

  <div class="form-group row ctulemus ${extra(tulemus.min_pallid)}">
    <% name = '%smin_pallid' % prefix %>
    ${ch.flb(_("Küsimuse miinimumpunktid"), name)}
    <div class="col-md-6">
      ${h.float5(name, tulemus.min_pallid)}
        % if not c.is_edit:
        ${h.hidden(name, tulemus.min_pallid)}
        % endif
    </div>
  </div>
  <div class="form-group row ctulemus">
    <% name = '%smax_pallid' % prefix %>
    ${ch.flb(_("Küsimuse maksimumpunktid"), name)}
    <div class="col-md-6">
        ${h.float5('%smax_pallid' % prefix, tulemus.max_pallid)}
        % if tulemus.max_pallid_arv:
        (${_("arvutatud")} ${h.fstr(tulemus.max_pallid_arv)})
        % endif
        % if not c.is_edit:
        ${h.hidden('%smax_pallid' % prefix, tulemus.max_pallid)}
        % endif
    </div>
  </div>
  % if c.is_devel or c.is_debug:
  <div class="form-group row ctulemus extra nodisplay2">
    <% name = '%smax_pallid_vastus' % prefix %>
    ${ch.flb(_("Üksikvastuse maksimumpunktid"), name)}
    <div class="col-md-6" id="${name}">
      ${h.fstr(tulemus.max_pallid_vastus)}
    </div>
  </div>
  % endif
  
    % if c.block.tyyp in (const.INTER_MCHOICE, const.INTER_CHOICE):
  <div class="form-group row ctulemus ${extra(tulemus.oige_pallid)}">
    <% name = '%soige_pallid' % prefix %>
    ${ch.flb(_("Õige vastuse vaikimisi pallid"), name)}
    <div class="col-md-6">
        ${h.float5(name, tulemus.oige_pallid)}
    </div>
  </div>
    % endif
    % if c.block.tyyp == const.INTER_EXT_TEXT:
  <div class="form-group row ctulemus ${extra(tulemus.min_sonade_arv)}">
    <% name = '%smin_sonade_arv' % prefix %>
    ${ch.flb(_("Min sõnade arv"), name)}
    <div class="col-md-6">
      ${h.posint5(name, tulemus.min_sonade_arv)}
      % if c.is_edit:
      <script>
        ## selle kasutamine eeldab hybriid- või arvutihinnatavust
      $(function(){
        $('input[name="${name}"],input[name="${prefix}hybriidhinnatav"],input[name="${prefix}arvutihinnatav"]')
        .change(function(){
           if($('input[name="${name}"]').val() != ''){
             var hyb = $('input[name="${prefix}hybriidhinnatav"]'),
                 arv = $('input[name="${prefix}arvutihinnatav"]');        
             if(!hyb.is(':checked') && !arv.is(':checked'))
                 hyb.prop('checked', true);
           }
        });
      });
      </script>
      % endif
    </div>
  </div>
    % endif

  <%
        KASITSIHINNATAVAD = (const.INTER_TEXT, const.INTER_EXT_TEXT, const.INTER_INL_TEXT, const.INTER_DRAW, const.INTER_WMATH,
                             const.INTER_MATH, const.INTER_AUDIO, const.INTER_GEOGEBRA, const.INTER_DESMOS, const.INTER_UPLOAD,
                             const.BLOCK_FORMULA, const.INTER_KRATT)
  %>
  % if c.block.tyyp in KASITSIHINNATAVAD:
  <div class="form-group row ctulemus ${extra(tulemus.pintervall)}">
    <% name = '%spintervall' % prefix %>
    ${ch.flb(_("Punktide intervall"), name)}
    <div class="col-md-6">
      ${h.float5(name, tulemus.pintervall)}
    </div>
  </div>
  % endif
  
    % if maatriks:
  <div class="form-group row ctulemus ${extra(tulemus.vaikimisi_pallid)}">
    <% name = '%svaikimisi_pallid' % prefix %>
    ${ch.flb(_("Vaikimisi punktid vastuse eest, mida maatriksis pole"), name)}
    <div class="col-md-6">
      ${h.float5(name, tulemus.vaikimisi_pallid)}
        % if not c.is_edit and c.lang:
        ${h.hidden('%svaikimisi_pallid' % prefix, tulemus.vaikimisi_pallid)}
        % endif
    </div>
  </div>
    % endif
    % if c.block.tyyp in (const.INTER_TEXT, const.INTER_EXT_TEXT):
  <div class="form-group row ctulemus ${extra(tulemus.yhisosa_kood)}">
    <% name = '%syhisosa_kood' % prefix %>
    ${ch.flb(_("Kood ülesannete ühisosas"), name)}
    <div class="col-md-6">
      ${h.text('%syhisosa_kood' % prefix, tulemus.yhisosa_kood, size=10)}
    </div>
  </div>
    % endif

  % if c.block.tyyp == const.INTER_MATCH3A:
  <div class="form-group row ctulemus ${extra(kysimus.min_vastus)}">
    <% name = '%smin_vastus' % prefix %>
    ${ch.flb(_("Minimaalne valikute arv"), name)}
    <div class="col-md-6">
      ${h.posint5(name, kysimus.min_vastus)}
    </div>
  </div>
  <div class="form-group row ctulemus ${extra(kysimus.max_vastus)}">
    <% name = '%smax_vastus' % prefix %>
    ${ch.flb(_("Maksimaalne valikute arv"), name)}
    <div class="col-md-6">
      ${h.posint5(name, kysimus.max_vastus)}

      % if kysimus.max_vastus_arv is not None:
      (${kysimus.max_vastus_arv})
      % endif
    </div>
  </div>
  % endif
  
  % if tulemus.kardinaalsus == const.CARDINALITY_MULTIPLE and c.block.tyyp not in (const.INTER_MATCH2, const.INTER_MATCH3, const.INTER_MATCH3A, const.INTER_MATCH3B) and not (c.block.tyyp == const.INTER_GR_ORDASS and kysimus.seq==2):
  <div class="form-group row ctulemus ${extra(tulemus.max_vastus != None)}">
    <% name = '%smax_vastus' % prefix %>
    ${ch.flb(_("Vastuste arv, mida ületades antakse miinimumpallid"), name)}
    <div class="col-md-6">
      ${h.posint5(name, tulemus.max_vastus)}
      % if not c.is_edit and c.lang:
      ${h.hidden(name, tulemus.max_vastus)}
      % endif
    </div>
  </div>  
  <div class="form-group row ctulemus ${extra(tulemus.min_oige_vastus)}">
    <% name = '%smin_oige_vastus' % prefix %>
    ${ch.flb(_("Õigete vastuste vähim lubatud arv"), name)}
    <div class="col-md-6">
      ${h.posint5(name, tulemus.min_oige_vastus)}
      % if not c.is_edit and c.lang:
      ${h.hidden(name, tulemus.min_oige_vastus)}
      % endif
    </div>
  </div>  
  % endif
  % if (tulemus.baastyyp == const.BASETYPE_STRING or basetype_opt) and (c.block.tyyp != const.INTER_CROSSWORD):
  <div class="form-group row basetype basetype-string ctulemus ${extra(tulemus.tostutunne)}">
    <% name = '%stostutunne' % prefix %>
    ${ch.flb(_("Eristatakse suur- ja väiketähti"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=tulemus.tostutunne)}
    </div>
  </div>
  % endif
  % if (tulemus.baastyyp in (const.BASETYPE_STRING, const.BASETYPE_POSSTRING, const.BASETYPE_MATH) or basetype_opt) and (c.block.tyyp != const.INTER_CROSSWORD):  
  <div class="form-group row basetype basetype-string ctulemus ${extra(tulemus.tyhikud)}">
    <% name = '%styhikud' % prefix %>
    ${ch.flb(_("Arvestatakse tühikuid"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=tulemus.tyhikud)}
    </div>
  </div>
  % endif
  % if tulemus.baastyyp in (const.BASETYPE_STRING, const.BASETYPE_MATH) or basetype_opt:
  <div class="form-group row basetype basetype-string basetype-math ctulemus ${extra(tulemus.ladinavene)}">
    <% name = '%sladinavene' % prefix %>
    ${ch.flb(_("Ladina ja vene sama välimusega tähed võrdsed"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=tulemus.ladinavene)}
    </div>
  </div>
    % endif
    % if (tulemus.baastyyp in (const.BASETYPE_STRING,const.BASETYPE_MATH) or basetype_opt) and (c.block.tyyp not in (const.INTER_GR_ORDASS, const.INTER_CROSSWORD)) or (c.block.tyyp == const.INTER_GAP):
  <div class="form-group row ctulemus ${extra(tulemus.lubatud_tyhi)}">
    <% name = '%slubatud_tyhi' % prefix %>
    ${ch.flb(_("Lubatud tühi vastus"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=tulemus.lubatud_tyhi)}
    </div>
  </div>
    % endif
    % if c.block.tyyp == const.INTER_INL_TEXT:
  <div class="form-group row ctulemus ${extra(kysimus.min_vastus == 0)}">
    <% name = '%skht_min_vastus0' % prefix %>
    ${ch.flb(_("Lubatud mitte vastata"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=kysimus.min_vastus==0)}
      <script>
        $('input[name="${prefix}kht_min_vastus0"]').click(function(){ $('input[name="${prefix}lubatud_tyhi"]').prop('checked', false); });
        $('input[name="${prefix}lubatud_tyhi"]').click(function(){ $('input[name="${prefix}kht_min_vastus0"]').prop('checked', false); });
      </script>
    </div>
  </div>
    % endif  
    % if (tulemus.baastyyp == const.BASETYPE_STRING or basetype_opt) and (c.block.tyyp != const.INTER_CROSSWORD):    
  <div class="form-group row basetype basetype-string ctulemus ${extra(tulemus.regavaldis)}">
    <% name = '%sregavaldis' % prefix %>
    ${ch.flb(_("Võrdlemine regulaaravaldisega (kogu vastus)"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=tulemus.regavaldis)}
    </div>
  </div>

  <div class="form-group row basetype basetype-string ctulemus ${extra(tulemus.regavaldis_osa)}">
    <% name = '%sregavaldis_osa' % prefix %>
    ${ch.flb(_("Võrdlemine regulaaravaldisega (osa vastusest)"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=tulemus.regavaldis_osa)}
    </div>
  </div>
    % endif
    
    % if tulemus.baastyyp in (const.BASETYPE_STRING, const.BASETYPE_INTEGER, const.BASETYPE_FLOAT) or basetype_opt:
  <div class="form-group row basetype basetype-string basetype-float basetype-integer basetype-boolean ctulemus ${extra(tulemus.valem)}">
    <% name = '%svalem' % prefix %>
    ${ch.flb(_("Valem"), name)}
    <div class="col-md-6">
      <% onclick = "$(this).closest('td').find('.needsave').show()" %>
      ${h.checkbox1(name, 1, checked=tulemus.valem, onclick=onclick)}
      <span class="needsave brown" style="display:none">${_("Muudatus rakendub peale salvestamist")}</span>
    </div>
  </div>
    % endif
    % if tulemus.baastyyp == const.BASETYPE_MATH:
  <div class="form-group row basetype basetype-math ctulemus ${extra(tulemus.vordus_eraldab)}">
    <% name = '%svordus_eraldab' % prefix %>
    ${ch.flb(_("Võrdusmärk eraldab vastused"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=tulemus.vordus_eraldab, class_="vrderald",
      onclick="if(!this.checked)$(this).closest('table').find('input.koikoiged').prop('checked', false)")}
    </div>
  </div>
  <div class="form-group row basetype basetype-math ctulemus ${extra(tulemus.koik_oiged)}">
    <% name = '%skoik_oiged' % prefix %>
    ${ch.flb(_("Kõik võrdusmärkide vahelised osad peavad olema õiged"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=tulemus.koik_oiged, class_="koikoiged",
      onclick="if(this.checked)$(this).closest('table').find('input.vrderald').prop('checked', true)")}
    </div>
  </div>
    % endif
    % if tulemus.baastyyp == const.BASETYPE_FLOAT or basetype_opt:    
  <div class="form-group row basetype basetype-float ctulemus ${extra(tulemus.ymard_komakohad)}">
    <% name = '%symard_komakohad' % prefix %>
    ${ch.flb(_("Mitme komakohani on lubatud ümardada"), name)}
    <div class="col-md-6">
      ${h.posint5(name, tulemus.ymard_komakohad)}
    </div>
  </div>
  <div class="form-group row basetype basetype-float ctulemus ${extra(tulemus.ymardet)}">
    <% name = '%symardet' % prefix %>
    ${ch.flb(_("Maatriksis on ümardatud arvud"), name)}
    <div class="col-md-6">
      ${h.checkbox1(name, 1, checked=tulemus.ymardet)}
    </div>
  </div>
    % endif
    % if tulemus.baastyyp in (const.BASETYPE_FLOAT, const.BASETYPE_INTEGER) or basetype_opt:    
  <div class="form-group row basetype basetype-float basetype-integer ctulemus ${extra(tulemus.sallivusprotsent)}">
    <% name = '%ssallivusprotsent' % prefix %>
    ${ch.flb(_("Lubatud erinevus protsentides"), name)}
    <div class="col-md-6">
      ${h.posint5(name, tulemus.sallivusprotsent)}
    </div>
  </div>
    % elif tulemus.baastyyp == const.BASETYPE_MATH:
  <div class="form-group row basetype basetype-math ctulemus ${extra(tulemus.sallivusprotsent)}">
    <% name = '%ssallivusprotsent' % prefix %>
    ${ch.flb(_("Lubatud erinevus protsentides (arvu korral)"), name)}
    <div class="col-md-6">
      ${h.posint5(name, tulemus.sallivusprotsent)}
    </div>
  </div>
    % endif
    % if c.block.tyyp in (const.INTER_HOTTEXT, const.INTER_MCHOICE):
  <div class="form-group row ctulemus ${extra(kysimus.min_vastus)}">
    <% name = '%skht_min_vastus' % prefix %>
    ${ch.flb(_("Minimaalne valikute arv"), name)}
    <div class="col-md-6">
      ${h.posint5(name, kysimus.min_vastus)}
    </div>
  </div>
  <div class="form-group row ctulemus ${extra(kysimus.max_vastus)}">
    <% name = '%skht_max_vastus' % prefix %>
    ${ch.flb(_("Maksimaalne valikute arv"), name)}
    <div class="col-md-6">
      ${h.posint5(name, kysimus.max_vastus)}

      % if kysimus.max_vastus_arv is not None:
      (${kysimus.max_vastus_arv})
      % endif
    </div>
  </div>
    % endif
    % if c.block.tyyp in (const.INTER_GAP, const.INTER_PUNKT):
    <%
      bkysimus = c.block.give_kysimus(0)
      if bkysimus.gap_lynkadeta:
         # min vastuste arv kuvada siis, kui see pole 0 ega None
         is_extra = kysimus.min_vastus
      else:
         # min vastuste arv kuvada siis, kui see pole 1 ega None
         is_extra = kysimus.min_vastus != 1 and kysimus.min_vastus is not None
    %>
    <div class="form-group row ctulemus ${extra(is_extra)}">
      <% name = '%skht_min_vastus' % prefix %>
      ${ch.flb(_("Minimaalne vastuste arv"), name)}
      <div class="col-md-6">
        ${h.posint5(name, kysimus.min_vastus)}
      </div>
    </div>
    <div class="form-group row ctulemus ${extra(kysimus.max_vastus)}">
      <% name = '%skht_max_vastus' % prefix %>
      ${ch.flb(_("Maksimaalne vastuste arv"), name)}
      <div class="col-md-6">
        ${h.posint5(name, kysimus.max_vastus, class_="max_vastus")}
      </div>
    </div>
    % endif
    % if c.block.tyyp == const.INTER_GAP and kysimus.seq != 0:
    <div class="form-group row ctulemus">
      <% name = '%skardinaalsus' % prefix %>
      ${ch.flb(_("Vastuste järjekord"), name)}
      <div class="col-md-6">
        ${h.select(name, tulemus.kardinaalsus, c.opt.cardinality_igap, class_="kardinaalsus")}
        <script>
          $(function(){
          ## kardinaalsus=single saab olla parajasti siis, kui max_vastus=1
            $('select.kardinaalsus').change(function(){
               var mv = $(this).closest('table').find('input.max_vastus');
               if($(this).val()=="${const.CARDINALITY_SINGLE}") mv.val('1');
            });
            $('input.max_vastus').change(function(){
               var cr = $(this).closest('table').find('select.kardinaalsus');
               if($(this).val()=="1") cr.val("${const.CARDINALITY_SINGLE}");
               else if(cr.val()=='${const.CARDINALITY_SINGLE}') cr.val('${const.CARDINALITY_MULTIPLE}');
            });
          });
         </script>
      </div>
    </div>
    % endif
    <% li_oi = [t.kood for t in kysimus.oigsus_tulemused] %>
    % if li_oi:
    <div class="form-group row ctulemus">
      ${ch.flb(_("Koos hinnatavad küsimused"), 'doitul')}
      <div class="col-md-6" id="doitul">
        ${', '.join(li_oi)}
      </div>
    </div>
    % elif c.block.tyyp != const.BLOCK_FORMULA:
    <% opt_avk = (c.ylesanne or c.block.ylesanne).opt_kysimused(kysimus.id) %>
    % if opt_avk:
    <div class="form-group row ctulemus ${extra(tulemus.oigsus_kysimus_id)}">
      <% name = '%soigsus_kysimus_id' % prefix %>
      ${ch.flb(_("Vastuse õigsuse määramiseks kasutatav küsimus"), name)}
      <div class="col-md-6">
        ${h.select(name, tulemus.oigsus_kysimus_id,
        opt_avk, empty=True, wide=False, class_="oigsus_k")}
        <script>
          ## kui valitakse õigsuse kysimus, siis ei saa antud kysimust käsitsi hinnata ja see peab olema arvutihinnatav
          $(function(){
          $('select.oigsus_k').change(function(){
          if($(this).val()!='') $(this).closest('.hindamismx').find('input.arvutihinnatav').prop('checked',true);
          });
          });
        </script>
      </div>
    </div>  
    % endif
    % endif
    % if c.block.tyyp in (const.INTER_ORDER, const.INTER_GR_ORDER):
    <div class="form-group row ctulemus ${extra(tulemus.maatriksite_arv and tulemus.maatriksite_arv>1)}">
      <% name = '%smaatriksite_arv' % prefix %>
      ${ch.flb(_("Hindamismaatriksite arv"), name)}
      <div class="col-md-6">
        ${h.posint5(name, tulemus.maatriksite_arv or 1)}
      </div>
    </div>
    % endif

    % if c.block.tyyp in (const.INTER_INL_TEXT, const.INTER_TEXT, const.BLOCK_FORMULA, const.INTER_CHOICE, const.INTER_ORDER, const.INTER_EXT_TEXT):
    <div class="form-group row ctulemus ${extra(kysimus.evast_edasi)}">
      <% name = '%sk_evast_edasi' % prefix %>
      ${ch.flb(_("Kasuta vastuseid testi edasistes ülesannetes algseisuna"), name)}
      <div class="col-md-6">
        ${h.checkbox1(name, 1, checked=kysimus.evast_edasi)}
      </div>
    </div>
    % endif
    % if c.block.tyyp in (const.INTER_INL_TEXT, const.INTER_TEXT, const.INTER_CHOICE, const.INTER_ORDER, const.INTER_EXT_TEXT):    
    <div class="form-group row ctulemus ${extra(kysimus.evast_kasuta)}">
      <% name = '%sk_evast_kasuta' % prefix %>
      ${ch.flb(_("Kasuta testi varasemate ülesannete vastuseid algseisuna"), name)}
      <div class="col-md-6">
        ${h.checkbox1(name, 1, checked=kysimus.evast_kasuta)}
      </div>
    </div>
    % endif
    % if c.block.tyyp in (const.INTER_ORDER, const.INTER_EXT_TEXT):        
    <div class="form-group row ctulemus ${extra(kysimus.muutmatu)}">
      <% name = '%sk_muutmatu' % prefix %>
      ${ch.flb(_("Vastust ei saa muuta"), name)}
      <div class="col-md-6">
        ${h.checkbox1(name, 1, checked=kysimus.muutmatu)}
      </div>
    </div>
    % endif
    % if c.block.tyyp == const.BLOCK_FORMULA:
    <div class="form-group row basetype basetype-float basetype-integer ${extra(tulemus.vastus_pallid)}">
      <% name = '%svastus_pallid' % prefix %>
      ${ch.flb(_("Kasuta vastust punktide arvuna"), name)}
      <div class="col-md-6">
        ${h.checkbox1(name, 1, checked=tulemus.vastus_pallid)}
      </div>
    </div>
    % endif
    <div class="form-group row ctulemus ${extra(kysimus.ei_arvesta)}">
      <% name = '%sk_ei_arvesta' % prefix %>
      ${ch.flb(_("Ära arvesta vastust tulemustes"), name)}
      <div class="col-md-6">
        ${h.checkbox1(name, 1, checked=kysimus.ei_arvesta)}
      </div>
    </div>

    <div class="form-group row ctulemus">
      <div class="col-12">
      <%
        # tyybid, mis võivad olla käsitsihinnatavad (ES-1539)
        ah_ronly = tulemus.arvutihinnatav and c.block.tyyp not in KASITSIHINNATAVAD or None
      %>
      ## maatriksita kysimusi peab saama märkida arvutihinnatavaks (saavad alati 0p),
      ## et need ei muudaks ylesande käsitsihinnatavaks
      ${h.checkbox1('%sarvutihinnatav' % prefix, 1, onclick=maatriks and "toggle_hybridmark(this)" or None,
      checked=tulemus.arvutihinnatav or tulemus.arvutihinnatav=='',
      class_="arvutihinnatav", ronly=ah_ronly,
      label=_("Arvutihinnatav"))}
      % if ah_ronly:
      ${h.hidden('%sarvutihinnatav' % prefix, 2, id='h_arvutihinnatav_%s' % tulemus.id)}
      % endif
      % if maatriks:
        ## uue kirje lisamisel arvutihinnatav='' ja vaikimisi seame väärtuseks true
        % if c.block.tyyp == const.INTER_MATCH3:
        ${h.hidden('%smaatriksite_arv' % prefix, 3)}
        % endif
        <script>
          function toggle_hybridmark(ah)
          {
          var name = $(ah).attr('name').replace('arvutihinnatav','hybriidhinnatav');
          var hbr = $('input[name="' + name + '"]');
          if(ah.checked) hbr.prop('checked', false);
          hbr.prop('disabled', ah.checked);
          }
          if(typeof $ != 'undefined')
          ## kysimus.iframe.mako sisse sattudes on esmalt $ undefined, kuna sisu tõstetakse hiljem ymber
          $(function(){
            $.each($('input[type="checkbox"][name$="arvutihinnatav"]'), function(n, ah){
            toggle_hybridmark(ah);
            });
          });
        </script>

        ${h.checkbox1('%shybriidhinnatav' % prefix, 1,
        checked=not tulemus.arvutihinnatav and tulemus.hybriidhinnatav or tulemus.arvutihinnatav=='',
        label=_("Hübriidhinnatav"))}
        % endif
        <a class="float-right" style="cursor:pointer" title="${_("Näita rohkem")}" onclick="expand_extra(this)">
          <i class="mdi mdi-arrow-expand-down"></i>
        </a>
        <script>
          function expand_extra(fld){
          $(fld).find('.mdi')
          .toggleClass('mdi-arrow-expand-down')
          .toggleClass('mdi-arrow-collapse-up');
          $(fld).closest('.hindamismx').find('div.row.extra').toggleClass('nodisplay2');
          }
        </script>
      </div>
    </div>

</div>
<%
  if nocommon:
     c.is_edit = is_edit
%>
</%def>

<%def name="hindamismaatriks(kysimus, 
            kood1=True, kood1_cls=None, 
            kood2=False, kood2_cls=None,
            kood3=False, kood3_cls=None,
            heading1=None,
            heading2=None,
            heading3=None,
            basetype_opt=None,
            ordered=False, tulemus=None, prefix='am1',
            caption=None,
            naidis=False,
            naidis_all=False,
            naidis_naha=False,
            fix_kood=False,
            can_rtf=False,
            matheditor=False,
            basetype=None,
            f_toggle_ckeditor=None,
            piltobj=None,
            hm_caption=None,
            nocommon=False)">
## Tavaline hindamismaatriks
  <%
     if caption is None: caption = _("Vastuse hindamine")
     if not tulemus:
        tulemus = kysimus.tulemus
     if not tulemus:
        tulemus = c.new_item(kood=kysimus.kood, max_vastus=None)
     if not tulemus.id:
        # vaikimisi on arvutihinnatav siis, kui pole avatud tekst
        if c.block.tyyp in (const.INTER_TEXT, const.INTER_EXT_TEXT, const.INTER_DRAW,
                            const.INTER_MATH, const.INTER_AUDIO, const.INTER_GEOGEBRA, const.INTER_DESMOS, const.INTER_KRATT, const.INTER_UPLOAD): 
           tulemus.arvutihinnatav = False
        else:
           tulemus.arvutihinnatav = True
        if c.block.tyyp in (const.INTER_TEXT, const.INTER_EXT_TEXT, const.INTER_INL_TEXT,
                            const.INTER_CROSSWORD, const.INTER_MATH):
           tulemus.ladinavene = True
     if basetype:
        tulemus.baastyyp = basetype
     is_rtf = kysimus.rtf and not tulemus.valem
     c.is_edit_orig = c.is_edit
     c.is_edit = c.is_edit_hm

     if (kood1 == [] and not kood1_cls) or (kood2 == [] and not kood2_cls):
        mx_cnt = 0
     elif c.block.tyyp == const.INTER_MATCH3:
        mx_cnt = 3 # vana
     else:
        mx_cnt = tulemus.maatriksite_arv or 1
    %>
<div class="d-flex flex-wrap mt-1 mb-1 gbox hmtable overflow-auto">
  <div class="bg-gray-50 p-3">
  ${h.hidden('%s.kysimus_id' % prefix, kysimus.id)}
  ${self.tulemus(kysimus, tulemus, '%s.' % prefix, piltobj, basetype_opt=basetype_opt, ordered=ordered, fix_kood=fix_kood, f_toggle_ckeditor=f_toggle_ckeditor, caption=caption, nocommon=nocommon)}
  </div>
  
  % for maatriks in range(1, mx_cnt+1):
  <div class="flex-grow-1 p-3">
      <%
        _heading1, _heading2 = heading1, heading2        
      %>
      ${self.hindamismaatriks_tbl_pag(kysimus, 
                                  heading1=_heading1,
                                  heading2=_heading2,
                                  basetype_opt=basetype_opt, 
                                  ordered=ordered,
                                  tulemus=tulemus,
                                  prefix=prefix,
                                  maatriks=maatriks,
                                  can_rtf=can_rtf,
                                  is_rtf=is_rtf,
                                  hm_caption=hm_caption,
                                  matheditor=matheditor
                                  )}
  </div>
  % endfor

  % if naidis or naidis_all:
  <div class="flex-grow-1 p-3" style="min-width:300px">
    ${self.naidisvastus(kysimus, tulemus, '%s.' % prefix, rows=3, naha=naidis_naha)}
  </div>
  % endif
</div>
  <%
     c.is_edit = c.is_edit_orig
  %>
</%def>

<%def name="hindamismaatriks_tbl_pag(kysimus, 
            heading1=None, heading2=None,
            basetype_opt=None,
            ordered=False, tulemus=None, prefix='am1', maatriks=1,
            can_rtf=False, is_rtf=None,
            matheditor=False,
            wmatheditor=False,
            hm_caption=None,
            f_toggle_ckeditor=None)">
% if matheditor:
<script>
  $(function(){
    $(document).on('click', '.math-valem', function(){
       var is_math = !this.checked;
       var tr = $(this).closest('tr');
       var inp = tr.find('input.math-editable'), div = tr.find('div.math-edit');
       if(is_math == inp.is(':visible'))
       {
          inp.val();
       }
       inp.toggle(!is_math);
       div.toggle(is_math);
    });
  });
</script>
% elif wmatheditor:
<script>
  $(function(){
    $(document).on('click', '.math-valem', function(){
       var is_math = !this.checked;
       var tr = $(this).closest('tr');
       var inp = tr.find('input.wmath-editable'), div = tr.find('div.wmath-edit');
       if(is_math == inp.is(':visible'))
       {
          inp.val();
       }
       inp.toggle(!is_math);
       div.toggle(is_math);
    });
  });
</script>
% endif
<%
  # kuvamine lk kaupa
  if c.is_sp_analysis:
     from eis.handlers.ekk.hindamine.analyysmaatriksid import AnalyysmaatriksidController
     ctrl = AnalyysmaatriksidController(request, True)
     ctrl.c.toimumisaeg = c.toimumisaeg
  else:
     if c.app_ekk:
        from eis.handlers.ekk.ylesanded.hindamismaatriksid import HindamismaatriksidController
     else:
        from eis.handlers.avalik.ylesanded.hindamismaatriksid import HindamismaatriksidController
     ctrl = HindamismaatriksidController(request, True)
     ctrl.c.ylesanne = c.ylesanne
     ctrl.c.block = c.block
  ctrl.c.kysimus = kysimus
  ctrl.c.baastyyp = tulemus.baastyyp
  ctrl.c.maatriks = maatriks
  ctrl.c.prefix = prefix
  ctrl.c.lang = c.lang
  ctrl.c.page = request.params.get('%s.page' % prefix) or 1
  ctrl.c.is_edit = c.is_edit
  ctrl.c.is_edit_orig = c.is_edit_orig
  ctrl.c.hm_caption = hm_caption
  ctrl.get_items()
  ctrl.c._arrayindexes = c._arrayindexes
  ctrl.c.is_tr = c.is_tr
  if c.block.tyyp == const.INTER_PUNKT:
     ctrl.c.kood2 = c.kood2
%>
<div width="${c.block.tyyp in (const.INTER_GR_GAP, const.INTER_CHOICE, const.INTER_HOTTEXT) and 660 or 530}px" class="listdiv listdiv-hm${kysimus.id} de-ckeditor">
  ${ctrl._showlist().ubody}
</div>
</%def>

<%def name="joondus(kysimus)">
## lüngasisese joondamise valik
      <%
         justifies = ((const.JUSTIFY_LEFT,_("Vasakjoondus")),
                      (const.JUSTIFY_CENTER,_("Keskjoondus")),
                      (const.JUSTIFY_RIGHT,_("Paremjoondus")),
                      (const.JUSTIFY_BLOCK,_("Rööpjoondus")),        
                     )
      %>
      <table><tr>
      % for code, title in justifies:
      <td>
        <img src="/static/images/justify${code}.png" title="${title}" class="justify" id="justify_${code}"
             onmouseover="justify_over($(this))"
             onmouseout="justify_out($(this))"
             onclick="justify_click($(this))">
      </td>
      % endfor
      </tr></table>
      ${h.hidden('l.joondus', kysimus.joondus)}
      <script>
        function justify_over(img)
        {
           var code = img.attr('id').substr(8);
           if($('input[name="l.joondus"]').val() != code)
             img.closest('td').css('background-color','#d3e9f5');
        }
        function justify_out(img)
        {
           var code = img.attr('id').substr(8);        
           if($('input[name="l.joondus"]').val() != code)
              img.closest('td').css('background-color','#ffffff');
        }
        function justify_click(img, onoff)
        {
           var code = img.attr('id').substr(8);        
           $('img.justify').closest('td').css('background-color','#ffffff');
           if(onoff == null)
           {
              onoff = $('input[name="l.joondus"]').val() != code;
           }
           if(onoff)
           {
              $('input[name="l.joondus"]').val(code);
              img.closest('td').css('background-color','#6ab5de');
           }
           else
           {
              $('input[name="l.joondus"]').val('');              
           }
        }
        % if kysimus.joondus:
        $(document).ready(function(){
           justify_click($('img#justify_${kysimus.joondus}'), true);
        });
        % endif
      </script>
</%def>
