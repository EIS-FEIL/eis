## Kirjavahemärkide lisamine
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<%
   c.bkysimus1 = c.block.give_baaskysimus(seq=1)  
   choiceutils.choices(c.bkysimus1, c.bkysimus1.valikud, 'v1', toolbar='gapmatch', valista=True, gentype='K01', caption=_("Laused"))
%>
## muude sisuplokkide kysimuste koodid ära toodud selleks, et uue kysimuse lisamisen mitte panna sama kood 
% for ind, valista_kood in enumerate(c.ylesanne.get_kysimus_koodid(c.block)):
${h.hidden('valista%d' % ind, valista_kood, class_='valista')}
% endfor
% if c.block.sisuvaade:
<div class="p-3 my-3 border border-base-radius ylesanne mt-3" id="block_${c.block_prefix}">
  <h3>${_("Eelvaade")}
  % if c.is_edit or c.is_tr:
  (${_("uueneb salvestamisel")})
    % endif
  </h3>
  <div class="ylesanne eelvaade mb-3" style="position:relative">
    ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
  </div>
</div>
<script>
  ${self.block_view_js(True)}
</script>
% endif
</%def>

<%def name="block_print()">
  <div class="ylesanne mb-3" style="position:relative">
    <% buf = (c.block.tran(c.lang).sisuvaade or '').replace('contenteditable="true"','contenteditable="false"') %>
    ${h.literal(c.block.replace_img_url(buf, lang=c.lang))}
  </div>
</%def>

<%def name="block_view()">
${c.block.sisuvaade}
% for k in c.block.pariskysimused:
${h.hidden(k.result, '', class_="blockresult")}
${h.hidden(k.result + '_a_', '', class_="blockresult")}
% endfor
<% 
if c.on_copy_resp_prefixes == '':
   c.on_copy_resp_prefixes = []
c.on_copy_resp_prefixes.append((c.y_prefix, c.block_prefix))
%>
</%def>

<%def name="block_view_js(is_compose=False)">
CKEDITOR.disableAutoInline = true;
$(function(){
  % for k in c.block.pariskysimused:
  % if k.min_vastus or k.max_vastus:
  $('.sisuplokk#sp_${c.block.get_prefix()} .ipunkt-sent[data-kood="${k.kood}"]')
    % if k.min_vastus:
      .attr('data-min', ${k.min_vastus})
    % endif
    % if k.max_vastus:
      .attr('data-max', ${k.max_vastus})
    % endif
      ;
% endif
  % endfor
  % if c.block_correct or c.block.naide:
    ${self.js_show_response(c.correct_responses)}
  % else:
    ${self.js_show_response(c.responses)}
  % endif

% if is_compose:
  $('.sisuplokk#sp_${c.block.get_prefix()}').find('[contenteditable="true"]').prop('contenteditable', false);
% else:
<%
  icons = (c.block.get_json_sisu() or {}).get('icons') or []
  all_icons = {r['name']: r['value'] for r in c.opt.get_ipunkt_icons()}
  if icons:
     charlist = [all_icons.get(icon) or '' for icon in icons]
     toolbar = '[[%s]]' % (','.join([f"'ipunkt{s}'" for s in icons]))
  else:
     charlist = list(all_icons.values())
     toolbar = 'null'
  chars = ''.join(['\\' + ch for ch in charlist if ch])
  %>
ipunkt_setup("${c.block_prefix}", "${const.RPREFIX}", "${chars}", ${toolbar});
% endif

 is_response_dirty = false;
});

## vastuste kandmine vastuste väljadele
function on_copy_resp_${c.block_prefix}()
{
  $('.sisuplokk#sp_${c.block_prefix} .ipunkt-sent').each(function(){
     ipunkt_copy_resp($(this), '${const.RPREFIX}');
  });
}
</%def>

<%def name="js_show_response(responses, for_resp=True)">
% for k in c.block.pariskysimused:
<% kv = responses.get(k.kood) %>
% if kv:
<%
  tulemus = k.tulemus
  kvsisud = kv.get_kvsisud()
  ks_analyze = kv.get_kvsisu(const.SEQ_ANALYSIS)
  li_resp = []
%>
## vastuste lisamine nähtavasse teksti
var snt = $('.sisuplokk#sp_${c.block.get_prefix()} .ipunkt-sent[data-kood="${k.kood}"]');
% for ks in kvsisud:
<%
  seq, txt = ks.koordinaat, ks.sisu
  li_resp.append(f'{seq}:{txt} ') # lõppu lisatyhik, nagu ckeditor paneb
  # asendame tyhiku nbsp-ga, et see ckeditoris säiliks
  txt = txt.replace(' ','\xa0')
%>
snt.find('.interpunkt-pos[data-seq="${seq}"]').text('${h.js_str1(txt)}')
   .addClass('responded')
  % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
   .addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, True, for_resp)}')
  % endif
;
% endfor

## vastuste lisamine postitamise väljale
% if li_resp:
<% s_resp = '|'.join(li_resp) %>
$('input[name="${c.block_result}_${k.kood}"]').val('${h.js_str1(s_resp)}');
% endif
% if ks_analyze:
$('input[name="${c.block_result}__${k.kood}"]').val('${h.js_str1(ks_analyze.sisu)}');
% endif

% endif
% endfor

</%def>
