${h.not_top()}
<%include file="/common/message.mako" />

${h.form_search(url=h.url('ylesanne_koostamine_isikud', ylesanne_id=c.ylesanne_id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Isikukood"))}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    % if c.user.has_permission('ylesanderoll', const.BT_CREATE, gtyyp=const.USER_TYPE_EKK):
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    % endif
    <div class="col-12">
      <div class="form-group text-right">
        ${h.button(_("Otsi"), onclick="var url='%s?'+$(this.form).serialize();dialog_load(url);" % h.url('ylesanne_koostamine_isikud', ylesanne_id=c.ylesanne_id))}
      </div>
    </div>
  </div>
</div>

${h.end_form()}
% if c.items:
${h.form(h.url('ylesanne_koostamine_isikud', ylesanne_id=c.ylesanne_id), method='put')}
      <table border="0"  class="table table-borderless table-striped multipleselect tablesorter" id="table_isikud">
        <thead>
          <tr>
            <th sorter="false" width="20px"></th>
            ${h.th_sort('nimi', _("Nimi"))}
            ${h.th_sort('epost', _("E-post"))}
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            <td>${h.checkbox('oigus', rcd.id, onclick="toggle_add()", title=_("Vali rida"))}</td>
            <td>${rcd.nimi}</td>
            <td>${rcd.epost or ''}</td>
          </tr>
          % endfor
        </tbody>
      </table>

<script>
  $(document).ready(function(){
     $('table#table_isikud').tablesorter();
  });
  function toggle_add()
  {
         var visible = ($('input:checked[name="oigus"]').length > 0);
         if(visible)
         { 
           $('table.add.invisible').removeClass('invisible');
         }
         else
         {
           $('table.add').filter(':not(.invisible)').addClass('invisible');
         }
  };
</script>

<table class="add invisible" style="width:100%">
  <tr>
    <td width="50%">
      <div style="margin:7px 0">
      ${h.select('kasutajagrupp_id', '', c.opt.ylesandegrupp)}
      </div>
      <div>
        ${_("Kehtib kuni")} ${h.date_field('kehtib_kuni', '')}
      </div>
    </td>
    <td style="padding-right:7px;text-align:right" valign="bottom">
      <span id="add_isik">
        ${h.submit_dlg()}
      </span>
    </td>
  </tr>
</table>

${h.end_form()}
% endif
