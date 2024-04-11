<table class="table table-striped tablesorter" >
  <caption>${_("Õpilased")}</caption>
  <col width="20px"/>
  <thead>
    <tr>
      <th sorter="false">${h.checkbox1('all', 1, title=_("Vali kõik"))}</th>
      <th>${_("Isikukood")}</th>
      <th>${_("Eesnimi")}</th>
      <th>${_("Perekonnanimi")}</th>
      <th>${_("Paralleel")}</th>
      % if c.data:
      <th>${_("Parool")}</th>
      % endif
      <th>${_("Parooli omistamine")}</th>
    </tr>
  </thead>
  <tbody>
  % for rcd in c.items:
  <tr>
    <td>
      % if not rcd.kasutaja or (not rcd.kasutaja.on_kehtiv_ametnik and not rcd.kasutaja.on_labiviija):
        ${h.checkbox('isikukood', rcd.isikukood, checkedif=c.isikukoodid, class_="isikukood", onclick="toggle_add()", title=_("Vali rida {s}").format(s=rcd.isikukood))}
      % endif
    </td>
    <td>${rcd.isikukood}</td>
    <td>${rcd.eesnimi}</td>
    <td>${rcd.perenimi}</td>
    <td>${rcd.paralleel}</td>
    % if c.data:
    <td>
      <% r = c.data.get(rcd.id) %>
      % if r:
      <% pwd, err = r %>
      % if pwd:
      ${h.roxt(pwd)}
      % else:
      <i style="color:red">${err}</i>
      % endif
      % endif
    </td>
    % endif
    <td>
         <% 
           item = None 
           kasutaja = rcd.kasutaja
         %>
         % if kasutaja:
            % if len(kasutaja.kasutajaajalood):
              <% item = kasutaja.kasutajaajalood[0] %>
              ${h.str_from_datetime(item.modified)}
            % endif
         % endif
         % if item is None:
            <i>${_("Parooli pole omistatud")}</i>
         % endif
   </td>
  </tr>
  % endfor
  </tbody>
</table>

<script>
  function toggle_add(){
   var visible = ($('input:checked.isikukood').length > 0);
   $('span#add').toggleClass('invisible', !visible);
  }
  $(function(){
     $('table#table_isikud').tablesorter();
     toggle_add();

     $('#all').click(function(){
        $('input.isikukood').prop('checked', this.checked);
        toggle_add();
     });
  });
</script>

<div class="text-right">
<span id="add" class="invisible">
${h.button(_("Genereeri püsiparoolid"), id="genpwd")}
% if c.data:
${h.button(_("Trüki"), id="printpwd")}
% endif
</span>
</div>

<script>
  $('#genpwd').click(function(){
  var f = $('form#form_save');
  dialog_load(f.attr('action'), f.serialize(), 'POST', $('.listdiv'));
  });
% if c.data:
  $('#printpwd').click(function(){
    var iframe = $('iframe#iprint');
    iframe.contents().find('body').html($('#iprint_contents').html());
    iframe[0].contentWindow.print();
  });
% endif
</script>

% if c.data:
<p>
  ${h.alert_success(_("Genereeritud {n} parooli").format(n=c.npwd))}
</p>
<div id="iprint_contents" style="display:none">
  <%include file="klassiparoolid.print.mako"/>
</div>
<iframe width="900" id="iprint" style="display:none"></iframe>
% endif

