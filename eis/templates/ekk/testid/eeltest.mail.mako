
${h.form(h.url('test_eeltest', test_id=c.test.id, id=c.item.id), method='put')}
${h.hidden('sub', 'mail')}
<table class="table"  width="100%">
  <tr>
    <td>
      ${_("Teate pealkiri")}<br/>
      ${h.text('subject', c.subject)}
    </td>
  </tr>
  <tr>
    <td>
      ${_("Teate sisu")}<br/>
      ${h.textarea('body', c.body, cols=80, rows=4)}
    </td>
  </tr>
</table>
<br/>
<table class="table table-borderless table-striped" width="100%" border="0" >
  <caption>${_("Adressaadid")}</caption>
  <col width="20px"/>
  <thead>
    <tr>
      <th></th>
      <th>${_("Nimi")}</th>
      <th>${_("Aadress")}</th>
    </tr>
  </thead>
  <tbody>
    <% has_epost = False %>
    % for rcd in c.avalik_test.get_korraldajad():
    <tr>
      <td>
        % if rcd.epost:
          <% has_epost = True %>
          ${h.checkbox('mailto', rcd.epost, onclick="toggle_saada()", class_="mailto")}
        % endif
      </td>
      <td>${rcd.nimi}</td>
      <td>${rcd.epost}</td>
    </tr>
    % endfor
  </tbody>
</table>

% if has_epost == False:
${h.alert_error(_("Teadet ei saa saata, sest pole ühtegi e-posti aadressi."))}
% endif

<script>
  function toggle_saada()
  {
         var visible = ($('input:checked.mailto').length > 0);
         if(visible)
         { 
           $('div#add.invisible').removeClass('invisible');
         }
         else
         {
           $('div#add').filter(':not(.invisible)').addClass('invisible');
         }
  }
  $(document).ready(function(){
     toggle_saada();
##     $('input#mailto').click(toggle_saada);
  });
</script>

<div id="add" class="invisible text-right">
${h.submit(_("Saada"))}
</div>
${h.end_form()}
