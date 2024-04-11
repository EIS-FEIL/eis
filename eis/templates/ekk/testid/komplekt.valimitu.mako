<%include file="/common/message.mako"/>
${h.form(h.url('test_komplekt_valimitu', test_id=c.test.id, testiosa_id=c.testiosa.id, komplekt_id=c.komplekt_id), id="form_search_y", method='post', multipart=True, target="form_dlg_target")}
${h.hidden('sub', 'upload')}

<div class="d-flex pb-2">
  <b class="mr-2">${_("Kuhu valitakse")}:</b>
  <div class="d-flex flex-grow-1 flex-wrap">
    <div class="mx-2">${_("Komplekt")}: ${c.komplekt.tahis}</div>
    <div class="mx-2">${_("Ülesannete arv")}: ${len(c.komplekt.valitudylesanded)}</div>
    <div class="mx-2">${_("Valimata ülesandeid")}: ${len([vy for vy in c.komplekt.valitudylesanded if not vy.ylesanne_id])}</div>
  </div>
</div>

<div class="rounded border p-2 d-flex justify-content-between">
  ${h.file('fail', value=_("Fail"))}
  ${h.button(_("Laadi"), onclick="$('form#form_search_y').submit();")}
</div>
${h.end_form()}


${h.form_save(None)}
${h.hidden('sub', 'add')}
<div class="listdiv">
% if c.items != '':
<%include file="komplekt.valimitu_list.mako"/>
% endif
</div>
${h.end_form()}

<iframe name="form_dlg_target" width="0" height="0" style="display:none" onload="if(typeof(move_to_dlg)=='function') move_to_dlg(this)">  
