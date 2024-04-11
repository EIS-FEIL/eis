<%include file="/common/message.mako" />
<%
   c.kirjeldus_nimetus = lambda kood: kood == 'ASPEKT' and _("Hindamisjuhis") or kood == 'VAHEND' and _("Sisu") or None
%>
<%def name="row(prefix, item, on_kirjeldus=False, level=0)">
<%
   # kas võib klassifikaatori rea kustutada
   in_use = not c.is_edit or c.item.kood == 'SPTYYP' or item.in_use
%>
    <tr>
      <td nowrap class="align-top">
        % if in_use:
        ${item.kood}
        ${h.hidden('%s.kood' % prefix, item.kood)}
        % else:
          <%
             if c.item.kood in (const.KL_KOOLITYYP, const.KL_OMANDIVORM, const.KL_ALAMLIIK, const.KL_KAVATASE):
                size = 25
             else:
                size = 10
          %>
        ${h.text('%s.kood' % prefix, item.kood, size=10)}
        % endif
          ${h.hidden('%s.id' % prefix, item.id)}
      </td>
% if c.item.kood == 'KODAKOND':
      <td class="align-top">
        ${h.text('%s.kood2' % prefix, item.kood2)}
      </td>
% endif
      <td class="align-top">
        <span class="d-none">${item.nimi}</span>
        % if c.item.kood == const.KL_HTUNNUS:
        <table width="100%">
          <col width="75"/>
          <tr>
            <td class="frh">nimetus</td>
            <td>${h.text('%s.nimi' % prefix, item.nimi)}</td>
          </tr>
          <tr>
            <td class="frh">ilma isikuta</td>
            <td>${h.textarea('%s.kirjeldus' % prefix, item.kirjeldus)}</td>
          </tr>
          <tr>
            <td class="frh">2. isikus</td>
            <td>${h.textarea('%s.kirjeldus2' % prefix, item.kirjeldus2)}</td>
          </tr>
          <tr>
            <td class="frh">3. isikus</td>
            <td>${h.textarea('%s.kirjeldus3' % prefix, item.kirjeldus3)}</td>
          </tr>
          <tr>
            <td class="frh">tasemete kirjeldus</td>
            <td>${h.textarea('%s.kirjeldus_t' % prefix, item.kirjeldus_t, rows=5)}</td>
          </tr>
        </table>
        % elif c.item.kood == 'KEELETASE' and c.ylem_id:
        ${item.nimi}
        ${h.hidden('%s.nimi' % prefix, item.nimi)}
        % elif c.item.kood == 'TOOKASK':
        ${h.hidden('%s.nimi' % prefix, '-')}
        ${h.textarea('%s.kirjeldus' % prefix, item.kirjeldus, maxlength=512, rows=3)}        
        % else:
        ${h.text('%s.nimi' % prefix, item.nimi)}
        % endif
        
        % if on_kirjeldus:
          % if c.is_edit and item.kood:
                  ${h.btn_to_dlg(_("Muuda kirjeldus"), 
                  h.url('admin_edit_klassifikaator', id=item.id, sub='kirjeldus', partial=True), 
                  title=c.kirjeldus_nimetus(c.item.kood), width=800, mdicls='mdi-file-edit')}             
          % endif
          % if item.kirjeldus:
              ${h.literal(item.kirjeldus)}
          % endif
         % endif
         % if item.ylem_id and item.hkood and c.is_debug:     
              <div style="margin-top:5px"><span class="debuginfo">${item.hkood}</span></div>
         % endif
      </td>
% if c.item.kood in (const.KL_TEEMA, const.KL_ALATEEMA, 'TOOKASK'):
      % for r in c.opt_aste:
      <td class="align-top">
      <%
        aste_bit = c.opt.aste_bit(r[0])
        aste_checked = item.bitimask and item.bitimask & aste_bit
        if c.item.kood in (const.KL_ALATEEMA,):
           aste_disabled = not ((c.ylem.bitimask or 0) & aste_bit)
        else:
           aste_disabled = False
      %>
        ${h.checkbox('%s.bit' % prefix, aste_bit,
          checked=aste_checked, disabled=aste_disabled)}
      </td>
      % endfor
% elif c.item.kood == const.KL_NULLIPOHJ:
      % for b in (const.NULLIP_BIT_P, const.NULLIP_BIT_E):
      <td class="align-top">
      <%
        checked = item.bitimask and item.bitimask & b
      %>
        ${h.checkbox('%s.bit' % prefix, b, checked=checked)}
      </td>
      % endfor
% elif c.item.kood == const.KL_AINE:
      <td class="align-top">
        <span class="d-none">${item.ainevald_nimi}</span>
        <% opt_ainevald = c.opt.klread_kood('AINEVALD') %>
        ${h.select('%s.ryhm_kood' % prefix, item.ryhm_kood, opt_ainevald, empty=True)}
      </td>
      <td class="align-top">
        <span class="d-none">${item.bitimask}</span>
        ${h.checkbox('%s.bit' % prefix, 1, checked=item.bitimask)}
      </td>
% elif c.item.kood == 'ERIVAJADUS':
      <td class="align-top">
        ${h.text('%s.kirjeldus' % prefix, item.kirjeldus)}
      </td>
      <td class="align-top">
        ${h.checkbox('%s.kinnituseta' % prefix, value=1, checked=item.kinnituseta)}
      </td>
% endif
      <td class="align-top">
        <span class="d-none">${item.jrk}</span>
        % if c.item.kood == 'KEELETASE':
        ${h.hidden('%s.jrk' % prefix, value=item.jrk)}
        % else:
        ${h.posint5('%s.jrk' % prefix, value=item.jrk)}
        % endif
      </td>
      <td class="align-top">
        <%
          if c.item.kood == 'SPTYYP':
             item_kehtib = item.avalik
          elif c.item.kood == 'KEELETASE' and c.ylem_id and item.kood not in c.seostatud:
             item_kehtib = False
          else:
             item_kehtib = item.kehtib
        %>
        <span class="d-none">${item_kehtib}</span>
        ${h.checkbox('%s.kehtib' % prefix, value=1, checked=item_kehtib)}
      </td>
      <td width="20px" class="align-top">
        ##${h.hidden('%s.klassifikaator_kood' % prefix, item.klassifikaator_kood)}
        % if not in_use:
        ${h.grid_remove()}
        % endif
      </td>
    </tr>
</%def>

<table id="gridtbl" class="table table-striped tablesorter"  width="100%">
  <col width="60px"/>
  % if c.item.kood == 'KODAKOND':
  <col width="60px"/>
  % endif
  <col/>
  % if c.item.kood == const.KL_AINE:
  <col width="160px"/>
  % elif c.item.kood == const.KL_NULLIPOHJ:
  <col width="80px"/>
  <col width="80px"/>
  % elif c.item.kood == 'ERIVAJADUS':
  <col/>
  <col width="80px"/>
  % endif
  % if c.item.kood in (const.KL_TEEMA, const.KL_ALATEEMA, 'TOOKASK'):  
  <col width="40px"/>
  <col width="40px"/>
  <col width="40px"/>
  <col width="40px"/>
  <col width="40px"/>
  <col width="40px"/>
  % else:
  <col width="80px"/>
  <col width="40px"/>
  <col width="40px"/>  
  % endif

  <caption>${c.item.nimi}</caption>
  <thead>
    <tr>
      <th>${_("Kood")}</th>
% if c.item.kood == 'KODAKOND':
      <th>${_("ISO2")}</th>
% endif
      <th>
        % if c.item.kood == const.KL_HTUNNUS:
        ${_("Kirjeldus")}
        % else:
        ${_("Nimi")}
        % endif
        <br/>${c.kirjeldus_nimetus(c.item.kood)}
      </th>
% if c.item.kood in (const.KL_TEEMA, const.KL_ALATEEMA,'TOOKASK') and c.ylem_id:
      <%
         c.opt_aste = c.opt.astmed()
      %>
      % for r in c.opt_aste:
      <th>${r[1]}</th>
      % endfor
% elif c.item.kood == const.KL_NULLIPOHJ:
      <th>${_("P-test")}</th>
      <th>${_("E-test")}</th>
% elif c.item.kood == const.KL_AINE:      
      <th>${_("Ainevaldkond")}</th>
      <th>${_("Kooli poolt profiilitav")}</th>
% elif c.item.kood == 'ERIVAJADUS':
      <th>${_("Selgitus")}</th>
      <th>${_("Ei vaja kinnitamist")}</th>
% endif
      <th>${_("Järjestus")}</th>
      % if c.item.kood == 'SPTYYP':
      <th colspan="2">${_("Kehtiv avalikus vaates")}</th>
      % else:
      <th colspan="2">${_("Kehtiv")}</th>
      % endif
    </tr>
  </thead>
  <tbody>

  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get('k') or []:
        ${self.row('k-%d' % cnt, c.new_item(), c.kirjeldus_nimetus(c.item.kood))}
  %   endfor
  % else:
  ## tavaline kuva
  <% c.row_cnt = -1 %>
  %   for item in c.items:
        <% c.row_cnt += 1 %>
        ${self.row('k-%d' % c.row_cnt, item, c.kirjeldus_nimetus(c.item.kood))}
  %   endfor
  % endif

  </tbody>
</table>
<br/>
  % if c.is_edit and (c.item.kood != 'KEELETASE' or not c.ylem_id) and c.item.kood != 'SPTYYP':
<div id="sample_gridtbl" class="d-none">
<!--
   ${self.row('k__cnt__', c.new_item(kehtib=True), c.kirjeldus_nimetus(c.item.kood))}
-->
</div>
<script>$('button#lisa').show();</script>
  % else:
<script>$('button#lisa').hide();</script> 
  % endif

