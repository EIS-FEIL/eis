% if c.items != '' and not c.items:
${h.alert_notice(_("Hindajaid ei määrata"), False)}
% elif c.items:

% if c.tab2 == 'tab2':
## hindamiskogumite kaupa

<table class="table table-borderless table-striped tablesorter">
  <thead>
    <tr>
      % for r in c.header:
      <% k, v = r[:2] %>
      <th>${v}
        <% helpable_id = len(r) > 2 and r[2] or None %>
        % if helpable_id:
        <span class="helpable" id="${helpable_id}"></span>
        % endif
      </th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, item in enumerate(c.items):
    <%
      rcls = ''
      hindajate_arv = item[1]
      if hindajate_arv == 0:
          rcls="tr-warn"
    %>
    <tr class="${rcls}">
      % for ind, value in enumerate(item):
      <td>
        % if ind == 1 and value == 0:
        ${_("Määramata")}
        % else:
        ${value}
        % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>

% else:
## hindajate kaupa

${h.pager(c.items)}

<table class="table table-borderless table-striped tablesorter">
  <thead>
    <tr>
      <th sorter="false"></th>
      % for r in c.header:
      <% k, v = r[:2] %>
      <th>${v}
        <% helpable_id = len(r) > 2 and r[2] or None %>
        % if helpable_id:
        <span class="helpable" id="${helpable_id}"></span>
        % endif
      </th>
      % endfor
      <th sorter="false">
        <span class="helpable" id="nupud"></span>        
      </th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
      item = c.prepare_item(rcd, True)
      rcls = ''
      hk, hindaja1, hindaja2 = rcd
      hk_id = hk.id
      hkasutaja1 = hindaja1 and hindaja1.kasutaja
      hkasutaja2 = hindaja2 and hindaja2.kasutaja
      hindaja = hindaja1 or hindaja2
      alustamata = (not hindaja1 or not hindaja1.toode_arv) and (not hindaja2 or not hindaja2.toode_arv)      
      if not hkasutaja1 and not hkasutaja2:
         rcls="tr-warn"
    %>
    <tr class="${rcls}">
      <td>
        ${h.btn_to_dlg('', h.url_current('index', sub='otsihindaja', lang=hindaja and hindaja.lang or None, hk_id=hk_id), title=_("Lisa hindaja"), level=0, mdicls='mdi-account-plus', size='lg')}
      </td>
      % for ind, value in enumerate(item):
      <td>
        ${value}
      </td>
      % endfor
      <td>
        % if hindaja:
        ${h.btn_to_dlg('', h.url_current('edit', id=hindaja.id), title=_("Muuda"), level=0, mdicls='mdi-account-edit')}
        % if alustamata:
        ${h.remove(h.url('korraldamine_delete_hindaja', testikoht_id=c.testikoht.id, id=hindaja.id), icon='mdi-account-remove', confirm_id="confirm_h_%s" % hindaja.id)}
        <span id="confirm_h_${hindaja.id}" style="display:none">
          % if hkasutaja1 and hkasutaja2:
          ${_("Kas oled kindel, et soovid hindajate paari {nimi1} ja {nimi2} eemaldada?").format(nimi1=hkasutaja1.nimi, nimi2=hkasutaja2.nimi)}
          % elif hkasutaja1:
          ${_("Kas oled kindel, et soovid hindaja {nimi} eemaldada?").format(nimi=hkasutaja1.nimi)}
          % elif hkasutaja2:
          ${_("Kas oled kindel, et soovid hindaja {nimi} eemaldada?").format(nimi=hkasutaja2.nimi)}
          % endif
        </span>

        % endif
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>

% endif

% endif
