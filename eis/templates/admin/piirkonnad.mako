<%inherit file="/common/page.mako"/>
<%def name="require()">
<% c.includes['jstree'] = True %>
</%def>
<%def name="page_title()">
${_("Piirkonnad")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Soorituspiirkonnad"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("Soorituspiirkonnad")}</h1>
% if c.user.has_permission('piirkonnad', const.BT_UPDATE):
${h.form_save(None)}
${h.hidden('changed_data','')}
<div class="mb-3">
  ${h.button(_("Salvesta"), onclick="save_tree()")}
</div>
${h.end_form()}
% endif

<div id="div_tree" data-href="${h.url('pub_piirkonnad', format='json')}">
</div>
<script>
var changes = [];
var current_node = null;
$(document).ready(function(){
    var new_id = -1;
    var href = $('div#div_tree').attr('data-href');
    var default_menu = $.jstree.defaults.contextmenu.items();
    var contextmenu_items = {
        "create" : {
            "separator_before"  : false,
            "separator_after"   : true,
            "label"             : "Lisa uus",
			"action"			: function (data) {
				var inst = $.jstree.reference(data.reference),
					obj = inst.get_node(data.reference);
                if(obj.a_attr.class == 'koht')
                {
                    alert_dialog("${_("Soorituskoha alla ei saa piirkondi luua")}");
                    return;
                }
                var node_id = new_id--;
                changes.push([node_id, obj.id, '']);
				inst.create_node(obj, {'id': node_id}, "last", function (new_node) {
					try {
						inst.edit(new_node);
					} catch (ex) {
						setTimeout(function () { inst.edit(new_node); },0);
					}
				});
			}
        },
        "rename" : {
                "separator_before"  : false,
                "separator_after"   : false,
                "label"             : "Nimeta ümber",
				"action"			: function (data) {
					var inst = $.jstree.reference(data.reference),
						obj = inst.get_node(data.reference);
                    if(obj.a_attr.class == 'koht')
                    {
                        alert_dialog("${_("Ainult piirkondi saab ümber nimetada")}");
                        return;
                    }
					inst.edit(obj);
                }
                
        },
        "remove" : {
                "separator_before"  : false,
                "icon"              : false,
                "separator_after"   : false,
                "label"             : "Eemalda",
                "action"            : function (data) {
					var inst = $.jstree.reference(data.reference),
						obj = inst.get_node(data.reference);
                    if(obj.children.length)
                    {
                        alert_dialog("${_("Ainult tühja piirkonda saab eemaldada")}");
                        return;
                    }
                    if(obj.a_attr.class == 'koht')
                    {
                        alert_dialog("${_("Soorituskohti ei saa eemaldada")}");
                        return;
                    }
                    if(!obj.state.opened)
                    {
                        alert_dialog("${_("Enne kustutamist ava piirkond veendumaks, et see on tühi")}");
                        return;
                    }
					if(inst.is_selected(obj)) {
						inst.delete_node(inst.get_selected());
					}
					else {
						inst.delete_node(obj);
					}
                    changes.push([obj.id,'DELETED','']);
                }
        }
    };
    $('div#div_tree').jstree({
            "core": {
                "data": {
                    "url" : href,
                    "data" : function (n) { 
						return { 
							"operation" : "get_children", 
                            "op": "kohad",
							"id" : n.id != '#' ? n.id : "-" 
						}; 
                    }
                },
                'force_text' : true,
                'check_callback' : true,
                'themes' : {
                    'responsive' : false
                },
                "strings": {
		            'Loading ...' : 'laadin...',
                    'New node': 'Uus piirkond',
                }
            },
            "contextmenu": {
                'items': contextmenu_items
            },
		    "plugins": ["contextmenu","dnd"]
        })
        .on("move_node.jstree", function(e,data){
            if(data.parent[0] == 'K'){
                alert_dialog("${_("Soorituskoha alla ei saa paigutada, seda muudatust ei salvestata")}");
                return;
            }
            changes.push([data.node.id, data.parent, data.node.text]);
        })
        .on("rename_node.jstree", function(e,data){
            changes.push([data.node.id, data.node.parent, data.node.text]);
        })
});
// changes on list kirjetest: [objekti id, vanema id, objekti nimi]
// kui objekti nimi on tühi string, siis kasutatakse vana nime edasi
// kui vanema id on DELETED, siis on objekt kustutatud
function save_tree()
{
  var buf = '';
  for(var i=0; i<changes.length; i++)
  {
      var id = changes[i][0];
      var parent_id = changes[i][1];
      var name = changes[i][2];
      buf += id + ':' + parent_id + ':' + name + '\n';
  }
  $('#changed_data').val(buf);
  $('#form_save').submit();
}
</script>


