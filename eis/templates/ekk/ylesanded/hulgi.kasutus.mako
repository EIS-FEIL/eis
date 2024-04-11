${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', 'kasutus')}

<div class="table">
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">
      ${_("Ülesande kasutus")}
    </div>
    <div class="col-sm-10 col-xs-8">
      <%
        selected = []
        opt_kasutliik = c.opt.klread_kood('KASUTLIIK')
      %>
      ${h.select_checkbox('kasutliik_kood', selected, opt_kasutliik)}
    </div>
  </div>
</div>

${h.submit()}
${h.end_form()}
