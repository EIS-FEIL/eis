## -*- coding: utf-8 -*- 
## $Id: soorituskohad.mako 9 2015-06-30 06:34:46Z ahti $

<div id="div_tree">
  ${self.treedata(model.Piirkond.get_tree(), [])}
</div>

<%def name="treedata(items, kohad)">
  % if len(items) or len(kohad):
  <ul>
    % for rcd in kohad:
    <li id="${rcd.id}"> 
      ##<input type="checkbox" name="koht_id" 
        <input type="radio" name="koht_id" 
          % if rcd.id == c.koht_id:
             checked="checked"
          % endif
             value="${rcd.id}"/>
      <a>${rcd.nimi}</a>
    </li>  
    % endfor

    % for rcd in items:
    <li id="${rcd.id}"> <a>${rcd.nimi}</a>
      ${self.treedata(rcd.alamad, rcd.kohad)}
    </li>
    % endfor
  </ul>
  % endif
</%def>

<script>
$(document).ready(function(){
  $('div#div_tree').jstree({
  % if c.limit:
        "ui": {
           "select_limit":${c.limit}
        },
  % endif
		"plugins" : [ "themes", "html_data"]
  });

});
</script>

