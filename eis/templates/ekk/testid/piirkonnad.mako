${h.form_save(c.item.id)}
${h.hidden('sub', 'prk')}

<%
 c.open_parents = set()
 for item in c.item.piirkonnad:
     c.open_parents = c.open_parents | set(item.get_parents())
 endfor 
%>
<div id="div_tree"></div>

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
        "checkbox": {
           "three_state": false // ylema valides ei valita automaatselt alam
        },
		"plugins" : ["checkbox" ]
      })
  % for rcd in c.item.piirkonnad:
   .jstree('check_node', '#${rcd.id}')
  % endfor
  ;
hold_dlg_height(null, true, $('div#div_tree'));
});
function save_tree(ctrl)
{
  var li = $('#div_tree').jstree('get_checked');
  buf = '';
  for(var i=0; i< li.length; i++) buf += ','+li[i];
  var form = $(ctrl).parents('form');
  var data = form.serialize() + '&piirkonnad=' + buf;                
  dialog_load(form.attr('action'), data, 'post', form.parent());
  ##form.submit();
}
</script>

${h.button(_("Salvesta"), onclick="save_tree(this)")}
${h.button(_("Vali kõik"), onclick="$('#div_tree').jstree('check_all')")}
${h.end_form()}
