<%
  tts = c.test.testitagasiside or c.new_item(ts_loetelu=True)
  if c.is_edit and c.lang:
     c.is_tr = True
  opt_kuva = [(str(const.KUVA_EI), _("Ei")), (str(const.KUVA_VER), _("üksteise all")), (str(const.KUVA_HOR), _("kõrvuti"))]

  # kontrollime, kas esimesel testiosal on olemas grupid
  on_ng = on_yg = False
  for osa in c.test.testiosad:
      for r in osa.nsgrupid:
          on_ng = True
          break
      for r in osa.ylesandegrupid:
          on_yg = True
          break
      break 
  %>
<b>${_("Õpilase ja grupi tagasiside ühised seaded")}</b>
<div class="table container p-2">
  <div class="row">
    <div class="col-sm-3 col-xs-6 frh">
      ${_("Kuva tekst loeteluna")}
    </div>
    <div class="col-sm-4 col-xs-6">
      % if c.is_edit and not c.is_tr:
      ${h.checkbox('f_ts_loetelu', 1, checked=tts.ts_loetelu)}
      % else:
      ${h.sbool(tts.ts_loetelu)}
      % endif
    </div>
  </div>
  <div class="row">
    <div class="col-sm-3 col-xs-6 frh">
      ${_("Kuva ülesandegrupid")}
    </div>
    <div class="col-sm-4 col-xs-6">
      % for value, label in opt_kuva:
         ${h.radio('f_ylgrupp_kuva', value, label=label,
          checkedif=tts.ylgrupp_kuva or 0,
          ronly=not c.is_edit or c.is_tr,
          disabled=value!=str(const.KUVA_EI) and not on_yg)}
      % endfor
      % if not on_yg:
      <div class="mb-2">${_("Ülesandegrupid puuduvad!")}</div>
      % endif
    </div>
    <div class="col-sm-3 col-xs-6 frh">
      ${_("Kuva ülesandegrupi nimetus")}
    </div>
    <div class="col-sm-2 col-xs-6">
      % if c.is_edit and not c.is_tr:
      ${h.checkbox('f_ylgrupp_nimega', 1, checked=tts.ylgrupp_nimega, disabled=not on_yg)}
      % else:
      ${h.sbool(tts.ylgrupp_nimega)}
      % endif
    </div>
  </div>
  <div class="row">
    <div class="col-sm-3 col-xs-6 frh">
      ${_("Kuva tagasiside grupid")}
    </div>
    <div class="col-sm-4 col-xs-6">
      % for value, label in opt_kuva:
         ${h.radio('f_nsgrupp_kuva', value, label=label,
          checkedif=tts.nsgrupp_kuva or 0,
          ronly=not c.is_edit or c.is_tr,
          disabled=value!=str(const.KUVA_EI) and not on_ng)}
      % endfor
      % if not on_ng:
      <div class="mb-2">${_("Tagasiside grupid puuduvad!")}</div>
      % endif
    </div>
    <div class="col-sm-3 col-xs-6 frh">
      ${_("Kuva tagasiside grupi nimetus")}
    </div>
    <div class="col-sm-2 col-xs-6">
      % if c.is_edit and not c.is_tr:
      ${h.checkbox('f_nsgrupp_nimega', 1, checked=tts.nsgrupp_nimega, disabled=not on_ng)}
      % else:
      ${h.sbool(tts.nsgrupp_nimega)}
      % endif
    </div>
  </div>
  <div class="row">
    <div class="col-sm-3 col-xs-6 frh">
      ${_("Kompaktne vaade")}
    </div>
    <div class="col-sm-4 col-xs-6">
      % if c.is_edit and not c.is_tr:
      ${h.checkbox('f_kompaktvaade', 1, checked=tts.kompaktvaade)}
      % else:
      ${h.sbool(tts.kompaktvaade)}
      % endif
    </div>
    <% tr_test = c.test.tran(c.lang, False) %>
    % if not c.is_edit and tr_test and tr_test.tahemargid is not None:
    <div class="col-12 frh">
      <span class="brown">${_("Testi andmetes kokku {n} tähemärki").format(n=tr_test.tahemargid)}</span>
    </div>
    % endif
  </div>
</div>
<br/>

% if (c.is_edit or tts.sissejuhatus_opilasele or tts.kokkuvote_opilasele) and c.tvorm_id == 'F1':
<b>${_("Tagasiside õpilasele")}</b>
<table class="form tkokkuvote" style="margin:5px;width:100%;max-width:1000px;">
  <col width="80px"/>  
  % if c.is_edit or tts.sissejuhatus_opilasele:
  <tr>
    <td class="fh">${_("Sissejuhatus")}</td>
    <td style="position:relative">     
      ${self.tran_editable('sissejuhatus_opilasele', tts, 's_')}
    </td>
  </tr>
  % endif
  % if c.is_edit or tts.kokkuvote_opilasele:
  <tr>
    <td class="fh">${_("Kokkuvõte")}</td>
    <td style="position:relative">     
      ${self.tran_editable('kokkuvote_opilasele', tts, 's_')}      
    </td>
  </tr>
  % endif
</table>
% endif

% if (c.is_edit or tts.sissejuhatus_opetajale or tts.kokkuvote_opetajale) and c.tvorm_id in ('F2','F3','F4'):
<b>${_("Tagasiside õpetajale")}</b>
<table class="form tkokkuvote" style="margin:5px;width:100%;max-width:1000px;">
  <col width="80px"/>
  % if c.is_edit or (tts and tts.sissejuhatus_opetajale):
  <tr>
    <td class="fh">${_("Sissejuhatus")}</td>
    <td>
      ${self.tran_editable('sissejuhatus_opetajale', tts, 's_')}
    </td>
  </tr>
  % endif
  % if c.is_edit or (tts and tts.kokkuvote_opetajale):
  <tr>
    <td class="fh">${_("Kokkuvõte")}</td>
    <td>
      ${self.tran_editable('kokkuvote_opetajale', tts, 's_')}            
    </td>
  </tr>
  % endif
</table>
<div class="table container p-2">
  <div class="row">
    <div class="col-sm-3 col-xs-6 frh">
      ${_("Erista sugu")}
    </div>
    <div class="col-sm-4 col-xs-6">
      % if c.is_edit and not c.is_tr:
      ${h.checkbox('f_ts_sugu', 1, checked=tts.ts_sugu)}
      % else:
      ${h.sbool(tts.ts_sugu)}
      % endif
    </div>
  </div>
</div>
% endif

<div id="tts_ckeditor_top" class="ckeditor-top-float" style="z-index:100"></div>
<script>
function tts_reinit_ckeditor()
{
    destroy_old_ckeditor();
    var inputs = $('.tkokkuvote .editable, .nsgrupid>tbody .editable');
    init_ckeditor(inputs, 'tts_ckeditor_top', '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}

$(function(){
    tts_reinit_ckeditor();
});
</script>

<%def name="tran_editable(key, tts, prefix)">
<div class="body16">
<%
  orig_val = tts and tts.__getattr__(key)
  if c.lang:
     tran = tts and tts.tran(c.lang, False)
     tran_val = tran and tran.__getattr__(key) or ''
%>
% if c.lang:
% if c.is_tr:
<div class="cke_top_pos" name="${prefix + key}">
% else:
<div>
% endif
  ${h.lang_orig(h.literal(orig_val), c.test.lang)}
</div>
${h.lang_tag()}
% if c.is_tr:
${h.textarea(prefix + key, tran_val,
ronly=not c.is_tr, class_="editable editable70")}
% else:
${tran_val}
% endif
% else:
% if c.is_edit:
${h.textarea(prefix + key, orig_val,
ronly=not c.is_tr and not c.is_edit, class_="editable editable70")}
% else:
${orig_val}
% endif
% endif
</div>
</%def>
