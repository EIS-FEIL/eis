<%include file="/common/message.mako"/>
${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', 'kogu')}

<div class="table">
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">
      ${_("E-kogu")}
    </div>
    <div class="col-sm-10 col-xs-8">
      <%
        kogu_opt = [(r.id, r.nimi) for r in model.Ylesandekogu.query.order_by(model.Ylesandekogu.nimi).all()]
        selected_id = []
      %>
      ${h.select2('kogud_id', selected_id, kogu_opt, multiple=True)}
    </div>
  </div>
</div>

${h.submit_dlg()}
${h.end_form()}
