## -*- coding: utf-8 -*- 

${h.form_search(url=h.url('nimekiri_isikud', testimiskord_id=c.testimiskord_id))}
${h.hidden('sub', 'ehis')}

<table width="100%" class="search" >
  <tr>
    <td>${_("Õppeasutus")}</td>
    <td colspan="4">${h.roxt(c.user.koht_nimi)}</td>
  </tr>
  <tr>
    <td>${_("Klass")}</td>
    <td>
      <% opt_kr = c.opt.opt_klassid_ryhmad(c.user.koht) %>
      ${h.select('klass', c.klass, opt_kr, wide=False)}
    </td>
    <td>${_("Paralleel")}</td>
    <td>${h.text5('paralleel', c.paralleel)}</td>
    <td class="field-header">
      ${h.submit_dlg(_("Otsi"))}
    </td>
  </tr>
</table>

${h.end_form()}
<br/>
<span id="progress"></span>
<%include file="/common/message.mako"/>
% if c.items:
${h.form(h.url('nimekiri_sooritajad', testimiskord_id=c.testimiskord_id), method='post', disablesubmit=True)}
<div class="listdiv">
      <table border="0"  class="table table-striped tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <th sorter="false">
              ${h.checkbox1('all', 1, title=_("Vali kõik"))}
            </th>
            ${h.th(_("Isikukood"))}
            ${h.th(_("Nimi"))}
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
            <% c.keel = c.keel or rcd.lang %>
          <tr>
            <td>${h.checkbox('oid', rcd.id, onclick="toggle_add()", class_="oigus", title=_("Vali rida {s}").format(s=rcd.isikukood))}</td>
            <td>${rcd.isikukood}</td>
            <td>
              ${rcd.eesnimi} ${rcd.perenimi}
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
<script>
  $(function(){
     $('table#table_isikud').tablesorter();
     $('input#all').click(function(){
      $('input.oigus').prop('checked', this.checked); toggle_add();
     });
  });

  function toggle_add(){   
     var visible = ($('input:checked.oigus').length > 0);
     $('span#add').toggleClass('invisible', !visible);
  }
</script>

<span id="add" class="invisible">
    <% opt_keeled = c.testimiskord and c.testimiskord.opt_keeled or c.test.opt_keeled %>
    % if len(opt_keeled) > 0:
      ${_("Soorituskeel")}:
      % if len(opt_keeled) > 1:
      ${h.select('keel', c.keel, opt_keeled, wide=False)}    
      % else:
      ${opt_keeled[0][1]}
      ${h.hidden('keel', opt_keeled[0][0])}
      % endif
    % endif

    <% opt_kursused = c.test.opt_kursused %>
    % if len(opt_kursused):
    &nbsp; &nbsp;
   ${_("Kursus")}:  ${h.select('kursus', None, opt_kursused, wide=False)}    
    % endif

    &nbsp; &nbsp;    
    ${h.submit(_("Salvesta"), id='add_isik', clicked=True)}
</span>
</div>

${h.end_form()}

% endif

