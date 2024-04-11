## Ühe ülesande vastuste analüüs
## Vt ka:
##  lib/block.py (assessment_analysis)
##  templates/sisuplokk/analysis.mako

<div class="d-flex flex-wrap justify-content-between p-3 bg-gray-50">
  <div class="item mr-5">
    <b>ID ${c.item.ylesanne_id}</b>
  </div>
  <div class="item mr-5">
    <h3>${c.item.ylesanne.nimi}</h3>
  </div>
  % if c.app_ekk:
  <div class="item mr-5">
      ${h.form_search(h.url_current('show'))}
      ${h.hidden('vy_id', c.item.id)}
      ${h.hidden('partial',1)}
      ${_("Vastuste järjestus")}
      <%
         opt_order = (('arv', _("vastuste arvu järgi")),
                      ('sisu', _("vastuse sisu järgi")),
                      ('oige', _("õigsuse järgi")))        
      %>
      ${h.select('kvst_order', c.kvst_order, opt_order, wide=False)}
      ${h.end_form()}
      <script>
        $('select#kvst_order').change(function(){ submit_dlg(this, $('#itemdiv')); });
      </script>
  </div>
  <div class="spinner-pos"></div>
  % endif
  % if c.app_ekk or c.app_eis and c.user.has_permission('avylesanded', const.BT_UPDATE, obj=c.ylesanne):
  <div class="item mr-5">
    ${h.blink_to(_("Ülesande koostamine..."), h.url('ylesanded_sisu', id=c.item.ylesanne_id), level=2)}
  </div>
  % endif
</div>
<div class="ylesanne" id="y${c.item.ylesanne.id}">
  ##style="max-width:1200px">
  ${c.item_html}
</div>
