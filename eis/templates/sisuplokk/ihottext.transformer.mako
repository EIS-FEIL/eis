## -*- coding: utf-8 -*- 

  <% on_kysimused = len(c.block.pariskysimused) > 0 %>       
  % if not on_kysimused:
       ${h.button(_("Jaga tekst osadeks"), id="opentransform", level=2)}
       ${h.hidden('transform', '')}
  % elif c.item.id:
       ${h.submit(_("Tühista osadeks jaotamine"), id="undotransform", level=2)}       
  % endif
  <div id="transformer_parent" style="display:none"></div>
  
<script>
  $('#opentransform').click(function(){
    var nkood = '';
    for(var i=65; i<=90; i++){
               var kood = String.fromCharCode(i);
               if(!is_kood_inuse(kood))
               {
                  nkood = kood;
                  break;
               }
         }
    var url = "${h.url_current('new', sub='transform')}&kood=" + nkood;
    open_dialog({url: url, 'size':'md', 'title': "${_("Tekstiosadeks jagamine")}"});
   });
</script>
