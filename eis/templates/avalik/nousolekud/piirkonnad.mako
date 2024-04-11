${h.form_save(None)}
${h.hidden('sub', 'prk')}
${h.hidden('piirkonnad', '')}

<%
 c.open_parents = set()
 for item in c.kasutaja.kasutajapiirkonnad:
     c.open_parents = c.open_parents | set(item.piirkond.get_parents())
%>

<div id="div_tree" class="mb-2"></div>

<%def name="json_data(ylem_id)">
 % for n, rcd in enumerate(model.Piirkond.query.filter_by(ylem_id=ylem_id).order_by(model.Piirkond.nimi)):
   % if n > 0:
    ,
   % endif
    {"id":${rcd.id},
     "text":"${rcd.nimi}",
     "children": [${self.json_data(rcd.id)}],
     "state": {"opened": ${rcd in c.open_parents and 'true' or 'false'}}
    }
 % endfor
</%def>

<script>
$(document).ready(function(){
$('div#div_tree').jstree({
       "core" : {
                "data" : [${self.json_data(None)}],
                'force_text' : true,
                'check_callback' : true,
                'themes' : {
                    'responsive' : false
                },
                "strings": {
		            'Loading ...' : 'laadin...',
                }
			},
		"plugins" : ["checkbox" ]
      })
  % for rcd in c.kasutaja.kasutajapiirkonnad:
   .jstree('check_node', '#${rcd.piirkond_id}')
  % endfor
  ;
hold_dlg_height(null, true, $('div#div_tree'));
});
function save_tree(ctrl)
{
  var li = $('#div_tree').jstree('get_checked');
  buf = '';
  for(var i=0; i< li.length; i++) buf += ','+li[i];
  $('#piirkonnad').val(buf);  
  var form = $(ctrl).parents('form')[0];
  form.submit();
}
</script>

<div class="d-flex flex-wrap">
  ${h.button(_('Vali kõik'), onclick="$('#div_tree').jstree('check_all')", level=2)}
  <div class="flex-grow-1 text-right">
    ${h.button(_('Salvesta'), onclick="save_tree(this)")}
  </div>
</div>
${h.end_form()}
