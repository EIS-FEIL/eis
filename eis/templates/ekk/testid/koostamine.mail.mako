## isikutele kirjade saatmine
## sama vormi kasutavad testid/koostamine.py ja ylesanded/koostamine.py
${h.form(h.url_current('update', id=c.item.id), method='put')}
${h.hidden('sub', 'mail')}

<div class="form-group">
  ${h.flb(_("Teate pealkiri"), 'subject')}
  ${h.text('subject', c.subject)}
</div>

<div class="form-group">
  ${h.flb(_("Teate sisu"), 'body')}
  ${h.textarea('body', c.body, rows=7)}
</div>

<div class="form-group">
  ${h.flb(_("Adressaadid"), 'adressaadid')}
  <table class="table table-borderless table-striped" id="adressaadid">
    <col width="20px"/>
    <thead>
      <tr>
        <th></th>
        <th>${_("Nimi")}</th>
        <th>${_("Aadress")}</th>
        <th>${_("Roll")}</th>
      </tr>
    </thead>
    <tbody>
      <% has_epost = False %>
      % for rcd in c.item.get_kasutajad():
      <tr>
        <td>
        % if rcd.epost:
        <% has_epost = True %>
        ${h.checkbox('k_id', rcd.id, onclick="toggle_saada()", class_="mailto")}
        % endif
        </td>
        <td>${rcd.nimi}</td>
        <td>${rcd.epost}</td>
        <td>${', '.join([i.nimi for i in rcd.testigrupid])}</td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>

% if has_epost == False:
${h.alert_error(_("Teadet ei saa saata, sest pole ühtegi e-posti aadressi."))}
% endif

<script>
  function toggle_saada()
  {
     var visible = ($('input:checked.mailto').length > 0);
     $('div#add').toggleClass('d-none', !visible);
  }
  $(function(){  toggle_saada(); });
</script>

<div id="add" class="d-none">
${h.submit(_("Saada"))}
</div>
${h.end_form()}
