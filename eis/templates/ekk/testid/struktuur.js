$(function(){
    function toggle_grp(){   
        $('.addgrp').toggleClass('d-none', $('input[name="vy_id"]:checked').length == 0);
        $('.deltasks').toggleClass('d-none', $('input[name="vy_id"]:checked').length == 0);        
## kui on valitud grupp, siis muudame grupi ylesannete loetelu
        var curr_g = $('div.grupid-list tr.selected');
        if(curr_g.length > 0)
        {
            var vyy_id = $('input[name="vy_id"]:checked')
                .map(function(){return this.value}).get();            
            curr_g.find('input[name$="vyy_id"]').val(vyy_id.join());
            curr_g.find('.len_grp').text(vyy_id.length+'*');
            curr_g.find('.save_grp_cmd').removeClass('d-none');
        }
    }
    function on_update(ev){
        var row = $(ev.item);
        var row_type = row.find('input#type').val();
        var row_id = row.find('input#id').val();
        var prev = row.prev()[0];
        var prev_type = (prev != null ? $(prev).find('input#type').val() : null);
        var next = row.next()[0];
        var next_type = (next != null ? $(next).find('input#type').val() : null);
        
        if(row_type == "testiylesanne")
            {
               var testiplokk_id = null;
               if(prev_type == "testiylesanne")
               {
                   alatest_id = $(prev).find('input#alatest_id').val();
                   testiplokk_id = $(prev).find('input#testiplokk_id').val();
               }
               else if(prev_type == "testiplokk")
               {
                   testiplokk_id = $(prev).find('input#id').val();
                   alatest_id = $(prev).find('input#alatest_id').val();
               }
               else if(prev_type == "alatest")
               {
                   if(next_type == "testiplokk")
                   {
                      alert_dialog('${_("Ülesanne peab kuuluma testiplokki")}');
                      return false;
                   }
                   testiplokk_id = "";
                   alatest_id = $(prev).find('input#id').val();
               }
               else if(prev_type == null)
               {
                   if(next_type != null && next_type != "testiylesanne")
                   {
                      alert_dialog('${_("Ülesanne peab kuuluma testiplokki või testiplokkideta alatesti")}');
                      return false;
                   }
               }
               else
               {
                   alert_dialog('${_("Ülesanne peab kuuluma testiplokki")}');
                   return false;
               }
               row.find('input#testiplokk_id').val(testiplokk_id);
            }
        else if(row_type == "testiplokk")
        {
               var alatest_id = null;
               if(next_type == "testiylesanne")
               {
                  alert_dialog('${_("Üht testiplokki ei saa teise testiploki sisse panna")}');
                  return false;
               }
               else if(prev_type == null)
               {
                   alert_dialog('${_("Testiplokk peab kuuluma alatesti")}');
                   return false;
               }
               else if(prev_type == "alatest")
                  alatest_id = $(prev).find('input#id').val();
               else if(prev_type == "testiplokk")
                  alatest_id = $(prev).find('input#alatest_id').val();

               ## liigutame alamad ka
               var li = $('tbody.sortables .sortable').has('input#testiplokk_id[value="'+row_id+'"]');
               for(var n=li.length-1; n>=0; n--) $(row).after(li[n]);
  
               ## muudame alamate ja enda vanema id
               li.find('input#alatest_id').val(alatest_id);
               $(row).find('input#alatest_id').val(alatest_id);
        }
        else if(row_type == "alatest")
        {
               var alatest_id = null;
               if(next_type == "testiplokk" || next_type == "testiylesanne")
               {
                   alert_dialog('${_("Alatest ei saa kuuluda teise alatesti sisse")}');
                   return false;
               }
               ## liigutame alamad ka
               var li = $('tbody.sortables .sortable').has('input#alatest_id[value="'+row_id+'"]');
               for(var n=li.length-1; n>=0; n--) $(row).after(li[n]);
        }
        $('button#save_order.d-none').removeClass('d-none');
        
        var order = '';
        $.each($('tbody.sortables>.sortable'), function(i, sortable){
            if(i>0) order += ',';
            order += sortable.id;
        });
        $('input#order').val(order);
    }
                  
    $('input[name="vy_id"]').change(toggle_grp);
    $('tbody.sortables').each(function(n, sortables){
        new Sortable(sortables, {
            animation: 150,
            onUpdate: on_update
        });
    });
    $("tbody.sortables").disableSelection();
})
