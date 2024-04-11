<%include file="/common/message.mako"/>

${h.form_search(url=h.url('test_nimekiri_otsisooritajad', test_id=c.test_id, nimekiri_id=c.nimekiri_id))}
${h.hidden('sub', 'ryhm')}
% if not c.opt_ryhmad:
<div>${_("Sa ei ole ühtki õpilaste rühma loonud!")}</div>
<div class="text-right">
  ${h.btn_to(_("Õpilaste rühmad"), h.url('opperyhmad'))}
</div>
% else:
<div class="gray-legend p-3">
  <div class="row filter">
    <div class="col">
      ${h.flb(_("Õpilaste rühm"), 'ryhm_id', 'pr-2')}
      ${h.select('ryhm_id', c.ryhm_id, c.opt_ryhmad, empty=True)}
    </div>
  </div>
</div>
% endif
${h.end_form()}

% if c.items:
${h.form(h.url('test_nimekiri_sooritajad', test_id=c.test_id, nimekiri_id=c.nimekiri_id), method='post', disablesubmit=True)}
<div id="listdiv_r">
      <table border="0" class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
        <col width="20px"/>
        <thead>
          <tr>
            <th sorter="false">${h.checkbox('all_id', 1, checked=True, title=_("Vali kõik"))}</th>
            ${h.th(_('Isikukood'))}
            ${h.th(_('Nimi'))}
            ${h.th(_('Klass'))}
          </tr>
        </thead>
        <tbody>
          % for (k_id, k_nimi, k_ik, lang, klass, paralleel) in c.items:
            <% c.keel = c.keel or lang %>
          <tr>
            <td>${h.checkbox('k_id', k_id, checked=True, title=_("Vali rida {s}").format(s=k_nimi))}</td>
            <td>${k_ik}</td>
            <td>${k_nimi}</td>
            <td>${klass}${paralleel}</td>
          </tr>
          % endfor
        </tbody>
      </table>

<div id="add" class="d-flex flex-wrap">
    <% opt_keeled = c.testimiskord and c.testimiskord.opt_keeled or c.test.opt_keeled %>
    % if len(opt_keeled) > 0:
    <div class="mr-4">
      ${_("Soorituskeel:")}
      % if len(opt_keeled) > 1:
      ${h.select('keel', c.keel, opt_keeled, wide=False)}    
      % else:
      ${opt_keeled[0][1]}
      ${h.hidden('keel', opt_keeled[0][0])}
      % endif
    </div>
    % endif

    <% opt_kursused = c.test.opt_kursused %>
    % if len(opt_kursused):
    <div class="mr-4">
      ${_("Kursus:")}  ${h.select('kursus', None, opt_kursused, wide=False)}
    </div>
    % endif

    % if c.test.testiliik_kood in (const.TESTILIIK_KOOLIPSYH, const.TESTILIIK_LOGOPEED):
    <div class="mr-4">
    ${h.checkbox('vanem_nous', 1, label=_('Vanema nõusolek'))}
    </div>
    % endif

    ${h.submit(_('Salvesta'), id='add_isik')}
</div>
</div>

${h.end_form()}

% endif

<script>
function toggle_add_r(){   
    var visible = ($('div#listdiv_r input:checked[name="k_id"]').length > 0);
    $('div#listdiv_r #add').toggleClass('invisible', !visible);
}
$(function(){
  $('select#ryhm_id').change(function(){
     submit_dlg(this);
  });
  $('div#listdiv_r').on('click', 'input[name="k_id"]', toggle_add_r);
  $('div#listdiv_r').on('click', 'input[name="all_id"]', function(){
        $(this).closest('table').find('input[name="k_id"]').prop('checked', this.checked);
        toggle_add_r();
  });
});
</script>
