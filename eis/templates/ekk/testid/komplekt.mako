<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Komplekti tähis"), 'f_tahis')}
    <div class="col-md-9">
      ${h.text5('f_tahis', c.item.tahis)}
    </div>
  </div>
  % if c.testiosa.on_alatestid:
  <div class="form-group row">
    <%
      label = _("Alatestid")
      if c.kursus:
          label += ' (%s)' % (model.Klrida.get_str('KURSUS', c.kursus, ylem_kood=c.test.aine_kood))
    %>
    ${h.flb3(label, 'td_alatestid')}
    <div class="col-md-9" id="td_alatestid">
    % if c.item.id:
      ${c.item.komplektivalik.str_alatestid}
      ${h.hidden('komplektivalik_id', c.item.komplektivalik_id)}
    % else:
      <script>
        function change_komplektivalik(f)
        {
## kui klikitakse alatestil, mis on juba mõnes komplektivalikus, 
## siis peavad kõik selle komplektivaliku alatestid olema korraga valitud või valimata
## ja muude komplektivalikute alatestid ega komplektivalikuta alatestid ei tohi olla valitud
          $('td.td_alatestid input[name="komplektivalik_id"][value="'+f.value+'"]').prop('checked',f.checked);
          $('td.td_alatestid input[name="komplektivalik_id"][value!="'+f.value+'"]').prop('checked',false);
          $('td.td_alatestid input[name="alatest_id"]').prop('checked', false);
        }
        function change_alatestivalik()
        {
          $('td.td_alatestid input[name="komplektivalik_id"]').prop('checked',false);
        }
      </script>
      % for alatest in c.testiosa.alatestid:
        % if alatest.kursus_kood == c.kursus or not alatest.kursus_kood:
        % if alatest.komplektivalik_id:
        ${h.checkbox('komplektivalik_id', alatest.komplektivalik_id, 
      checkedif=c.item.komplektivalik_id, onchange="change_komplektivalik(this)",
      label=alatest.tahis or alatest.nimi)}
        % else:
      ${h.checkbox('alatest_id', alatest.id, onchange="change_alatestivalik()",
      label=alatest.tahis or alatest.nimi)}
        % endif
        % endif
      % endfor
    % endif
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${h.flb3(_("Komplekti ülesannete keel(ed)"))}
    <div class="col-md-9">
      <% k_keeled = c.item.keeled %>
      % for lang in c.testiosa.test.keeled:
      ${h.checkbox('skeel', value=lang, checked=lang in k_keeled, label=model.Klrida.get_str('SOORKEEL', lang))}
      <br/>
      % endfor
    </div>
  </div>
</div>

<div class="text-right">
  <span id="progress"></span>
  ${h.submit_dlg()}
</div>
${h.end_form()}
