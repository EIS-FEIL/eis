<%include file="/common/message.mako"/>
% if not c.items:
${_("Valitud testiliigiga teste, kuhu saaks registreerida, praegu rohkem ei ole.")}
% else:
${h.form(h.url_current('create'), method='post', disablesubmit=True)}
${h.hidden('testiliik', c.testiliik)}
<div class="listdiv">
  ${h.rqexp()}
  <table border="0"  class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
    <thead>
      <tr>
        <th></th>
        ${h.th(_("Test"))}
        ${h.th(_("Testimiskord"))}
        ${h.th(_("Toimumise aeg"))}
        ${h.th(_("Testi liik"))}
        ${h.th(_("Soorituskeel"))}
        ${h.th(_("Piirkond"), rq=True)}
      </tr>
    </thead>
    <tbody>
      % for n, rcd in enumerate(c.items):
      <tr>
        <%
           test = rcd.test
           opt_kursused = test.opt_kursused
           on_tseis = test.on_tseis
        %>
        <td rowspan="${on_tseis and 2 or 1}">
          ${h.checkbox('valik_id', rcd.id, class_='valik_id')}
        </td>
        <td rowspan="${on_tseis and 2 or 1}">
          ${test.nimi}

          % if len(opt_kursused):
          ${h.select('kursus_%d' % rcd.id, None, opt_kursused)}
          % endif

          % if on_tseis:
          <br/>
          ${h.checkbox('soovib_konsultatsiooni_%d' % rcd.id, 1, label=_("Soovib konsultatsiooni"))}
          % endif
        </td>
        <td>${rcd.tahised}</td>
        <td><span class="d-none">${rcd.alates and rcd.alates.isoformat() or ''}</span>${rcd.millal}</td>
        <td>${rcd.test.testiliik_nimi}</td>
        <td>${h.select('lang_%d' % rcd.id, None, rcd.opt_keeled)}</td>
        <td>
            <%
               c.piirkond_id = None
               c.piirkond_field = 'piirkond_id_%d' % rcd.id
               c.piirkond_filtered = rcd.get_piirkonnad_id()
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
        </td>
      </tr>
      % if on_tseis:
      <tr>
        <td class="frh">${_("Sooritaja märkused")}</td>
        <td colspan="4">
          ${h.text('reg_markus_%s' % rcd.id, '')}
        </td>
      </tr>
      % endif
      % endfor
    </tbody>
  </table>
<br/>
<script>
  $(function(){
    $('table#table_isikud').tablesorter();
    $('input.valik_id').click(toggle_add);
    toggle_add();
  });
  function toggle_add(){   
     var visible = ($('input.valik_id:checked').length > 0);
     $('span#add').toggleClass('invisible', !visible);
  }
</script>
</div>

<span id="add" class="invisible">
  ${h.submit_dlg(_("Salvesta"))}
</span>

${h.end_form()}

% endif

