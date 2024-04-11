## Desmos
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<%
  mo = c.block.meediaobjekt
  k = c.block.kysimus
  tulemus = k.tulemus or c.new_item(kood=k.kood)
  if not mo.laius:
     mo.laius = 600
  if not mo.korgus:
     mo.korgus = 400
  c.desmdata = c.block.get_json_sisu() or {}
  other_opts = c.desmdata.get('options') or {}
  opts = c.desmdata.get('uioptions') or {'degreeMode': True}
  try:
     opts.update(other_opts)
  except:
     pass
%>
${h.hidden('am1.kysimus_id', k.id)}
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row mb-1">
  <% name = 'mo.laius' %>
  ${ch.flb(_("Laius"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.int5('mo.laius', mo.laius, maxvalue=1500)}
  </div>

  <% name = 'mo.korgus' %>
  ${ch.flb(_("Kõrgus"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.int5('mo.korgus', mo.korgus)}
  </div>
</div>
<div class="row mb-1">
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('dmo_images', 1, checked=opts.get('images'), label=_("Luba pilte lisada"))}
  </div>
  <div class="col-md-6 col-xl-4">  
    ${h.checkbox('dmo_folders', 1, checked=opts.get('folders'), label=_("Luba avaldiste loetellu kaustu lisada"))}
  </div>
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('dmo_notes', 1, checked=opts.get('notes'), label=_("Luba avaldiste loetellu märkusi lisada"))}
  </div>
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('dmo_degreeMode', 1, checked=opts.get('degreeMode'), label=_("Funktsioonide argumendid kraadides (mitte radiaanides)"))}
  </div>
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('dmo_links', 1, checked=opts.get('links'), label=_("Luba märkustes ja kaustades lingid"))}
  </div>
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('dmo_settingsMenu', 1, checked=opts.get('settingsMenu'), label=_("Kuva graafiku seadistamise mutrivõti"))}
  </div>
</div>

<div class="row mb-1">
  ${ch.flb(_("Muud seaded"), 'desm_options')}
  <div class="col-md-9 col-xl-10">
    <span class="error" id="options_err"></span>
  ${h.textarea('desm_options', h.json.dumps(other_opts), rows=4, onchange="$('#options_err').text('');")}
  </div>
</div>

<div class="d-flex flex-wrap gbox hmtable overflow-auto mb-3">
  <div class="bg-gray-50 p-3">
    ${choiceutils.tulemus(k, tulemus, 'am1.', maatriks=False)}
  </div>
  <div class="flex-grow-1 p-3">
    ${choiceutils.naidisvastus(k, tulemus, 'am1.', rows=3, naha=False)}
  </div>
</div>

${h.hidden('desm_state', '')}
<%
  if mo.laius and mo.korgus:
     width = '%dpx' % mo.laius
     height = '%dpx' % (mo.korgus + 70)
  else:
     width = '100%'
     height = '%dpx' % ((mo.korgus or 700) + 70)
%>
<div id="applet_container_${c.block.id}" style="width:${width};height:${height}">
</div>
<script>
  ${self.create_applet_js(True)}
  
  $('form#form_save').submit(function(){
    ## vormi salvestamisel ekspordime andmed
    $('input[name="desm_state"]').val(JSON.stringify(desmos_${c.block.id}.getState()));
  });
</script>

</%def>

<%def name="block_view()">
<%
  kysimus = c.block.kysimus
  mo = c.block.meediaobjekt

  if c.block.naide or c.block_correct:
     responses = c.correct_responses
  else:
     responses = c.responses
  kv = responses.get(kysimus.kood)

  value = ''
  if kv and len(kv.kvsisud):
     ks = kv.kvsisud[0]
  else:
     ks = None
  if ks and ks.has_file:
     from eis.s3file import s3file_get
     filedata = s3file_get('kvsisu', ks)
     if filedata:
        value = filedata.decode('utf-8')
  if not c.desmdata or c.desmdata_id != c.block.id:
     c.desmdata = c.block.get_json_sisu() or {}
     c.desmdata_id = c.block.id
  width = mo.laius and '%dpx' % mo.laius or '100%'
  height = mo.korgus
  height = '%dpx' % (height or 700)
  
  if c.prepare_correct and ks and ks.on_hinnatud and not c.block.varvimata:
     corr_cls = model.ks_correct_cls(responses, kysimus.tulemus, kv, ks, False) or ''
  else:
     corr_cls = ''
%>
<div id="block_${c.block_prefix}" class="asblock">
  ${h.qcode(kysimus, nl=True)}
  <div id="applet_container_${c.block.id}" style="width:${width};height:${height}" class="${corr_cls}">
  </div>
  ${h.hidden(kysimus.result, value)}
<% 
if c.on_copy_resp_prefixes == '':
   c.on_copy_resp_prefixes = []
c.on_copy_resp_prefixes.append((c.y_prefix, c.block_prefix))
%>
</div>
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
${self.create_applet_js(False)}
is_response_dirty = false;
function on_copy_resp_${c.block_prefix}()
{
  var block = $('div#block_${c.block_prefix}');
  block.find('input[name="${kysimus.result}"]').val(JSON.stringify(desmos_${c.block.id}.getState()));
}
</%def>

<%def name="create_applet_js(editing)">
<%
  mo = c.block.meediaobjekt
  k = c.block.kysimus
  if not c.desmdata or c.desmdata_id != c.block.id:
     c.desmdata = c.block.get_json_sisu() or {}
     c.desmdata_id = c.block.id
  other_opts = c.desmdata.get('options') or {}
  opts = c.desmdata.get('uioptions') or {}
  try:
     opts.update(other_opts)
  except:
     pass
%>
var desmos_${c.block.id} = null;
$(function(){
var options = ${h.json.dumps(opts)};
var elt = $('#applet_container_${c.block.id}')[0];
desmos_${c.block.id} = Desmos.GraphingCalculator(elt, options);
var state = null, data = $('input[name="${k.result}"]').val();
if((data!='') && (typeof data === 'string'))
   state = data.replace(/[\r\n]/g,'');
% if c.desmdata.get('state'):
else
   state = ${str(c.desmdata['state'])};
% endif
if(state)
   desmos_${c.block.id}.setState(state);
});
</%def>

<%def name="block_print()">

</%def>

<%def name="block_entry()">
<div class="td-sis-value2">${_("Faili ei sisestata")}</div>
</%def>
