## Hindamine
## On antud:
## - c.alatest - kui on alatest valitud
## - c.komplekt - valitud komplekt
## - c.sooritusylesanded
## - c.ty
## - c.vy

<%  
   #c.is_edit = True # vaatamise korral on c.read_only
   sooritaja = c.sooritus.sooritaja
   if sooritaja:
       # kui ei ole testi eelvaade, siis on olemas sooritaja
       c.testimiskord = sooritaja.testimiskord
%>
<div id="status_table_pos"></div>

<div id="hindamine_p_div" class="d-flex">
  <div style="flex:1;overflow:auto;" id="hindamine_hk_div" class="mb-4 mr-3">
    ## soorituse ylesandevastuse sisu
    ${self.hindamine_ylesanne()}
  </div>
  <div style="flex:1;overflow:auto;" id="hindamine_r_div">
    ## lahendamine, õige vastus, hindamisjuhend, hindamiskysimused
    ## siia laaditakse hiljem hindamine_r_tabs.mako 
  </div>
</div>

<%def name="hindamine_ylesanne()">
<%include file="hindamine.ylesanne.mako"/>
</%def>

<script>
## kui hindamise divi kõrgus on suurem kui akna kõrgus, siis määratakse mõlemale
## hindamise divi poolele kõrgus, et mõlemat poolt saaks eraldi kerida (ES-2748)
var hkh_resize = function()
{
  var p_height = $('#hindamine_p_div').height(),
      w_height = Math.max(window.innerHeight - 50, 200);
  if((p_height > w_height) || $('#hindamine_p_div').hasClass('hkh-resized'))
  {
     $('#hindamine_hk_div,#hindamine_r_div').height(w_height)
        .css('border','1px solid #ddd');
     $('#hindamine_p_div').addClass('hkh-resized');
  }
}
$(function(){
  hkh_resize();
  $(window).resize(hkh_resize);
});
</script>
