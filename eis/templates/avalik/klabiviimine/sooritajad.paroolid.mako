## -*- coding: utf-8 -*- 
${h.form_save(c.testiruum.id, form_name="form_save_pwd")}
${h.hidden('sub', 'parool')}
<table width="100%" class="table table-borderless table-striped tablesorter" >
  <thead>
    <tr>
      <th sorter="false">${h.checkbox('all', '', checked=True, title=_("Vali kõik"))}</th>
      <th>${_("Isikukood")}</th>
      <th>${_("Eesnimi")}</th>
      <th>${_("Perekonnanimi")}</th>
      <th>${_("Testiparooli omistamine")}</th>
    </tr>
  </thead>
  <tbody>
  % for rcd in c.items:
  <%
    sooritaja = rcd.sooritaja
    kasutaja = sooritaja.kasutaja

    # kas testiparool on juba olemas?
    has_cls = ''
    item = None
    for r in sooritaja.testiparoolilogid:
       item = r
       has_cls += 'haspwd'
       break
  %>
  <tr>
    <td>
      ${h.checkbox('pwd_id', rcd.id, checked=True, onclick="toggle_add()", class_=has_cls,
      title=_("Vali rida {s}").format(s=kasutaja.isikukood))}
    </td>
    <td>${kasutaja.isikukood}</td>
    <td>${sooritaja.eesnimi}</td>
    <td>${sooritaja.perenimi}</td>
    <td>
         % if item:
              ${h.str_from_datetime(item.modified)} ${c.opt.kasutaja_nimi(item.creator)}
         % else:
            <i>${_("Testiparooli pole omistatud")}</i>
         % endif
   </td>
  </tr>
  % endfor
  </tbody>
</table>

<div class="text-right">
  ${h.button(_("Genereeri testiparoolid"), id="genereeri")}
</div>
<script>
  $(function(){
     $('input[name="all"]').click(function(){
        $('input[name="pwd_id"]').prop('checked', $(this).prop('checked'));
        toggle_add();
     });
     toggle_add();

     $('button#genereeri').click(function(){
        var btn = this;
        var run = function(){
           close_confirm_dialog();
           submit_dlg(btn, null, null, true);
        };
        if($('input.haspwd:checked').length > 0)
        {
           ## valitute seas on keegi, kellel juba on parool
           var msg = "${_("Kas oled kindel, et soovid loodud testiparoolid tühistada ja luua uued?")}";
           confirm_dialog(msg, run);
        }
        else
        {
           ## kõik on uued paroolid
           run();
        }
     });
  });
  function toggle_add(){   
     $('input[id="genereeri"]').toggle($('input[name="pwd_id"]:checked').length > 0);
  }
</script>
${h.end_form()}
