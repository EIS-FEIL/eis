<%include file="/common/message.mako"/>

${h.form_save(None)}
  
  <div class="form-group">
    ${h.flb(_("Pealkiri"), 'teema')}
    <div>
      ${h.text('teema', c.kiri.teema, maxlength=256)}
    </div>
  </div>
  <div class="form-group">
    ${h.flb(_("Sisu"), 'sisu')}
    <div>
      ${h.textarea('sisu', c.kiri.sisu, rows=10)}
    </div>
  </div>
  <div class="text-right">
    ${h.button(_("Saada e-postiga"), id="send_email", class_="jchecked", clicked=1000, onclick="sendmsg(this, 'email')")}
  </div>
  ${h.hidden('sooritajad_id', '')}
  ${h.hidden('op','')}
${h.end_form()}

  <script>
    function sendmsg(fld, op){
    if($(fld).hasClass('disabled')) return;
    var buf = '', sep = '';
    $('input[name="j"]:checked').each(function(n, elem){  buf += sep + elem.value; sep = ',';  });
    $('#sooritajad_id').val(buf);
    $('#op').val(op);
    submit_dlg(fld, $('#kirjasisu'));
    }
  </script>
