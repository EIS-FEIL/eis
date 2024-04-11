<% 
   testiosa = c.item.testiosa or model.Testiosa.get(c.item.testiosa_id) 
   alatestid_id = [a.id for a in c.item.alatestid]
%>
<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.hidden('komplekt_id', c.komplekt_id)}
<div class="form-wrapper mb-2">
  <div class="form-group row">
    <%
      label = _("Alatestid")
      if c.item.kursus_kood:
         label += ' (%s)' % (c.item.kursus_nimi)
    %>
    ${h.flb3(label, 'alatestid')}
    <div class="col-md-9" id="alatestid">
      % for alatest in testiosa.alatestid:
      % if alatest.kursus_kood == c.item.kursus_kood:
      <%
         kv = alatest.komplektivalik
         disabled = kv and kv.id != c.item.id and len(kv.komplektid) > 0
      %>
      ${h.checkbox('alatest_id', alatest.id, checkedif=alatestid_id, disabled=disabled,
      label=alatest.tahis or alatest.nimi)}
      % endif
      % endfor
    </div>
  </div>
</div>
${h.submit_dlg()}
<span id="progress"></span>
${h.end_form()}
