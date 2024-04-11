<%namespace name="choiceutils" file='choiceutils.mako'/>
<%include file="/common/message.mako"/>
<%
  items = c.hm_items
  n_offset = 0
  if items:
     counter = c.hm_items.item_count
     if c.page and c.page == '0':
        items = c.hm_items.items
     elif c.page and c.hm_items.item_count > c.hm_items.items_per_page:
        n_offset = (int(c.page) - 1) * c.hm_items.items_per_page
     is_last_page = c.page == '0' or items.page >= items.page_count
  else:
     counter = 0
     is_last_page = True

  matheditor = c.baastyyp == const.BASETYPE_MATH 
  wmatheditor = c.baastyyp == const.BASETYPE_MATHML
  is_rtf = c.kysimus.rtf 
  can_rtf = is_rtf
  heading1 = heading2 = _("Vastus")
  kood1 = True
  kood2 = None
  kood1_cls = kood2_cls = None

  tableid = '%s_mapping%s' % (c.prefix, c.maatriks) 
  formulaname = '%s.valem' % c.prefix
  if c.block.tyyp in (const.INTER_MATCH3, const.INTER_ORDER, const.INTER_GR_ORDER):
      hm_prefix = '%s.hmx-%s.hm' % (c.prefix, c.maatriks-1)
  else:
      hm_prefix = '%s.hm%s' % (c.prefix, c.maatriks)
  idprefix = hm_prefix.replace('.','')
  toolbar = 'supsub'

  if c.block.tyyp == const.BLOCK_FORMULA:
     heading1 = _("Vastus")
  elif c.block.tyyp == const.INTER_ASSOCIATE:
     kood1 = kood2 = c.kysimus.valikud_opt
     kood1_cls = kood2_cls = 'vkood'
  elif c.block.tyyp == const.INTER_COLORAREA:
     heading1 = _("Värv")
     kood1 = c.block.give_baaskysimus().valikud_opt     
  elif c.block.tyyp == const.INTER_COLORTEXT:
     heading2 = _("Värv")
     kood1 = c.kysimus.valikud_opt
     kood2 = c.block.give_baaskysimus().valikud_opt
     kood2_cls = 'vkood'
  elif c.block.tyyp == const.INTER_CHOICE:
     kood1 = c.block.kysimus.valikud_opt
     kood1_cls = 'vkood'
  elif c.block.tyyp == const.INTER_MCHOICE:
     kysimus2 = c.block.get_baaskysimus(seq=2)
     kood1 = kysimus2.valikud_opt
     kood1_cls = 'vkood'
  elif c.block.tyyp == const.INTER_CROSSWORD:
     heading1 = _("Vastus")
  elif c.block.tyyp == const.INTER_SELECT2:
     heading1 = _("Piirkonna ID")
     kood1 = c.block.give_baaskysimus(1).valikud_opt
     model.log.debug('VALIKUD=%s'  % kood1)
     kood1_cls = 'hskood'
  elif c.block.tyyp == const.INTER_POS2:
     heading1 = _("Piirkonna ID")
     kood1 = c.block.give_baaskysimus(1).valikud_opt
     kood1_cls = 'hskood'
  elif c.block.tyyp == const.INTER_TXPOS2:
     heading1 = _("Piirkonna ID")
     kood1 = c.block.give_baaskysimus(2).valikud_opt
     kood1_cls = 'hskood'
  elif c.block.tyyp == const.INTER_TXGAP:
     heading1 = _("Piirkonna ID")
     kood1 = c.block.give_baaskysimus(2).valikud_opt
     kood1_cls = 'hskood'
  elif c.block.tyyp == const.INTER_TXASS:
     heading1 = _("Piirkonna ID")
     kood1 = c.block.give_baaskysimus(2).valikud_opt
     kood1_cls = 'hskood'
  elif c.block.tyyp == const.INTER_GAP:
     heading1 = _("Valiku ID")
     kood1 = c.block.kysimus.valikud_opt + [('', _("Tühi"))]
     kood1_cls = 'vkood'
  elif c.block.tyyp == const.INTER_PUNKT:
     ## korraga kuvatakse yhe lynga (kood1) read, seetõttu kood1 ei kuvata, ainult kood2
     heading2 = _("Vastus")
     kood1 = True
     kood2 = False
     can_rtf = is_rtf = True
     toolbar = 'ipunkt'
  elif c.block.tyyp == const.INTER_GR_ASSOCIATE:
     kood1 = kood2 = c.kysimus.valikud_opt
     kood1_cls = kood2_cls = 'hskood'
  elif c.block.tyyp == const.INTER_GR_GAP:
     heading1 = _("Pildi ID")
     heading2 = _("Piirkonna ID")
     kood1 = c.block.piltobjektid_opt
     kood2 = c.block.kysimus.valikud_opt
     kood2_cls = 'hskood'
  elif c.block.tyyp == const.INTER_GR_ORDASS:
     if c.kysimus.seq == 2:
         # valede vastuste arv
         heading1 = _("Vastuste arv")
     else:
         heading1 = _("Piirkond")
         kood1 = c.block.kysimus.valikud_opt
         kood1_cls = 'hskood'
  elif c.block.tyyp == const.INTER_HOTSPOT:
     heading1 = _("Piirkond")  
     kood1 = c.block.kysimus.valikud_opt
     kood1_cls = 'hskood'
  elif c.block.tyyp == const.INTER_HOTTEXT:
     heading1 = _("Tekstiosa ID")
     kood1 = c.kysimus.valikud_opt
  elif c.block.tyyp == const.INTER_INL_TEXT:
     heading1 = _("Vastus")
  elif c.block.tyyp == const.INTER_INL_CHOICE:
     heading1 = _("Vastus")
     sisukysimused = c.block.get_sisukysimused(c.kysimus.kood)
     if sisukysimused:
        sisukysimus = sisukysimused[0]
        kood1 = [v.kood for v in sisukysimus.valikud]
     else:
        kood1 = []
     kood1_cls = 'vkood'
  elif c.block.tyyp == const.INTER_MATCH2:
     kysimus1 = c.block.give_baaskysimus(seq=1) 
     kysimus2 = c.block.give_baaskysimus(seq=2)
     if kysimus1.ridu == 2:
        khulk, vhulk = kysimus2, kysimus1
        kood1_cls = 'v1kood'
     else:
        khulk, vhulk = kysimus1, kysimus2
        kood1_cls = 'v2kood'
     kood1 = vhulk.valikud_opt
  elif c.block.tyyp == const.INTER_MATCH3:
     _heading1 = _("Hulk 1")
     _heading2 = _("Hulk 2")
     _heading3 = _("Hulk 3")
     _kysimus1 = c.block.get_kysimus(seq=1)
     _kysimus2 = c.block.get_kysimus(seq=2) 
     _kysimus3 = c.block.get_kysimus(seq=3)
     if c.maatriks == 2:
            heading1, kood1, kood1_cls = _heading2, _kysimus2.valikud_opt, 'v2kood'
            heading2, kood2, kood2_cls = _heading3, _kysimus3.valikud_opt, 'v3kood'
     elif c.maatriks == 3:
            heading1, kood1, kood1_cls = _heading1, _kysimus1.valikud_opt, 'v1kood'
            heading2, kood2, kood2_cls = _heading3, _kysimus3.valikud_opt, 'v3kood'
     else: # c.maatriks == 1:
            heading1, kood1, kood1_cls = _heading1, _kysimus1.valikud_opt, 'v1kood'
            heading2, kood2, kood2_cls = _heading2, _kysimus2.valikud_opt, 'v2kood'

  elif c.block.tyyp == const.INTER_MATCH3A:
     k_kood = c.kysimus.kood
     if k_kood.endswith('_H3'):
         v_kood = k_kood[:-3]
         _kysimus3 = c.block.get_baaskysimus(seq=3)
         heading1, kood1, kood1_cls = _("Hulk 3"), _kysimus3.valikud_opt, 'v3kood'
         c.hm_caption = _("Valiku {s} seosed kolmanda hulgaga").format(s=v_kood)
     elif k_kood.endswith('_H1'):
         v_kood = k_kood[:-3]
         _kysimus1 = c.block.get_baaskysimus(seq=1)
         heading1, kood1, kood1_cls = _("Hulk 1"), _kysimus1.valikud_opt, 'v1kood'
         c.hm_caption = _("Valiku {s} seosed esimese hulgaga").format(s=v_kood)

  elif c.block.tyyp == const.INTER_MATCH3B:
     _kysimus1 = c.block.get_baaskysimus(seq=1)
     _kysimus2 = c.block.get_baaskysimus(seq=2)
     _kysimus3 = c.block.get_baaskysimus(seq=3)
     _heading1 = _("Hulk 1")
     _heading2 = _("Hulk 2")
     _heading3 = _("Hulk 3")
     if _kysimus1.ridu == 2:
         heading1, kood1, kood1_cls = _heading1, _kysimus1.valikud_opt, 'v1kood'
         heading2, kood2, kood2_cls = _heading3, _kysimus3.valikud_opt, 'v3kood'
     else:
         heading1, kood1, kood1_cls = _heading2, _kysimus2.valikud_opt, 'v2kood'
         heading2, kood2, kood2_cls = _heading3, _kysimus3.valikud_opt, 'v3kood'

  elif c.block.tyyp == const.INTER_MATH:
     heading1 = _("Vastus")  
  elif c.block.tyyp == const.INTER_SLIDER:
     heading1 = _("Vastus")
  elif c.block.tyyp == const.INTER_ORDER:
     kood1 = c.block.kysimus.valikud_opt
     kood1_cls = 'vkood'
  elif c.block.tyyp == const.INTER_TEXT:
     heading1 = _("Vastus")
  
  if c.hm_caption:
     caption = c.hm_caption
  elif c.block.tyyp in (const.INTER_MATCH3, const.INTER_MATCH3A):
     caption = _("Hindamismaatriks {n}").format(n=c.maatriks)
  else:
     caption = _("Hindamismaatriks")
%>
<div class="d-flex flex-wrap">
  % if not c.hm_caption_off:
  <h3 class="flex-grow-1">${caption}</h3>
  % endif
  <div>
    % if c.block.tyyp == const.INTER_PUNKT:
    <div>${_("Küsimus")} ${c.kysimus.kood}</div>
    <div>${_("Lünk")} ${c.kood2}</div>
    % endif
  </div>
</div>
${h.pager(c.hm_items, listdiv='.listdiv-hm%s' % c.kysimus.id, form='', list_url=c.hm_list_url, is_all='hmall', msg_not_found=_("Hindamismaatriks on tühi"), msg_found_one=_("Hindamismaatriksis on 1 rida"), msg_found_many=_("Hindamismaatriksis on {n} rida"))}
${h.hidden('%s.page' % c.prefix, c.page)}
% if can_rtf:
<script>
$(function(){
      toggle_ckeditor('${idprefix}', false, null, {toolbar:'${toolbar}',language:'${request.localizer.locale_name}',enterMode:${c.kysimus.rtf_enter or 'null'}}, '${tableid}', 'l.rtf', '${formulaname}');
});
</script>
<div id="${idprefix}_ckeditor_top"></div>
% endif

<table width="600px" id="${tableid}" class="table table-borderless table-striped lh-11 hmlist" border="0"  counter="${counter}">
        <thead>
          <tr>
            <th>${_("Jrk")}</th>
            % if kood1 or kood1_cls:
            <th>${h.flb(heading1, rq=True)}</th>
            % endif
            % if kood2 or kood2_cls:
            <th>${h.flb(heading2, rq=True)}</th>
            % elif matheditor:
            <th>
              ${_("Vahemiku lõpp (arvu korral)")}
            </th>
            % else:
            <th class="basetype basetype-integer basetype-float" style="display:none">
              ${_("Vahemiku lõpp")}
            </th>
            % endif
            % if matheditor:
            <th>${_("Valem")}</th>
            <th>${_("Lihtsusta")}</th>
            <th>${_("Võrdle ainult tekstina")}</th>            
            % endif          
            <th>${_("Tingimus")}</th>
            <th>${h.flb(_("Punktid"), rq=True)}</th>
            <th>${_("Õige")}</th>
            % if c.block.tyyp==const.INTER_GR_GAP:
            <th>${_("Tabamuste arv")}</th>
            % endif
            % if c.block.tyyp != const.BLOCK_FORMULA:
            <th>${_("Tabamuste loendur")}</th>
            % endif
            <th></th>
          </tr>
        </thead>
        <tbody>
          % if c._arrayindexes != '' and not c.is_tr:
          ## valideerimisvigade korral
          %   for cnt in c._arrayindexes.get(hm_prefix) or []:
                   ${choiceutils.map_entry(c.kysimus, hm_prefix, cnt, c.new_item(), 
                     kood1, kood2, kood1_cls, kood2_cls,
                     can_rtf=can_rtf, is_rtf=is_rtf, matheditor=matheditor, wmatheditor=wmatheditor)}
          %   endfor
          % elif items:
            ## tavaline kuva
          %     for cnt, item in enumerate(items):
          ${choiceutils.map_entry(c.kysimus, hm_prefix, cnt + n_offset, item, 
          kood1, kood2, kood1_cls, kood2_cls,
          can_rtf=can_rtf, is_rtf=is_rtf, matheditor=matheditor, wmatheditor=wmatheditor)}
          %     endfor
          %   endif
        </tbody>
        % if can_rtf:
        <tfoot>
          <tr><td colspan="7" id="${idprefix}_ckeditor_bottom"></td></tr>
        </tfoot>
        % endif
       % if c.is_edit and not c.lang and is_last_page:
      <tfoot id="sample_${tableid}" class="d-none sample">
        ${choiceutils.map_entry(c.kysimus, hm_prefix, '__cnt__', c.new_item(), 
        kood1, kood2, kood1_cls, kood2_cls, 
        can_rtf=can_rtf, is_rtf=is_rtf, matheditor=matheditor, wmatheditor=wmatheditor)}
      </tfoot>
      % endif
</table>

% if c.is_edit and not c.lang and is_last_page:
        <%
           ## lisataval real koodide valikvälja uuendamine 
           ## vastavalt kasutaja tehtud muudatustele valikute seas
           buf_refresh = "grid_addrow('%s');" % tableid  
           if c.is_edit_orig:
              ## c.is_edit_orig=True, kui valikud on ka muudetavad
              if kood1_cls:
                 buf_refresh += "refresh_text_options('%s',-1);" % kood1_cls
              if kood2_cls and kood2_cls != kood1_cls:
                 buf_refresh += "refresh_text_options('%s',-1);" % kood2_cls
              if basetype_opt:
                 buf_refresh += "showbasetype($(this).closest('.hindamismx').find('select.baastyyp'));"
           if can_rtf:
              buf_refresh += "toggle_ckeditor('%s', false, -1, {toolbar:'%s', language:'%s', enterMode:%s}, '%s', 'l.rtf', '%s')" % (idprefix, toolbar, request.localizer.locale_name, c.kysimus.rtf_enter or 'null', tableid, formulaname)
        %>
        ${h.button(value=_("Lisa"), class_='button1', onclick=buf_refresh, name='lisa', id='lisa_%s' % tableid, level=2, mdicls='mdi-plus')}
% endif

% if c.is_edit and (kood1_cls or kood2_cls):
      <script>
        $(function(){
        % if c.is_edit and kood1_cls:
        refresh_text_options('${kood1_cls}');
        % endif
        % if c.is_edit and kood2_cls and kood2_cls != kood1_cls:
        refresh_text_options('${kood2_cls}');
        % endif
        });
      </script>
% endif
