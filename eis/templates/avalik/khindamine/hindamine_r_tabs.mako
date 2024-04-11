<%namespace name="tab" file='/common/tab.mako'/>
<%
  yid = c.ylesanne and c.ylesanne.id or ''
%>
% if not c.inint:
## intervjuus on ainult lahendamise sakk ja muid sakke ei kuva
<ul class="nav nav-pills mb-3 hindamine_r_tabs" data-yid="${yid}" role="tablist">
  <% c.tabs_mode = 'subli' %>
  % for tabname, url, label in c.r_tabs_data:
  ${tab.subdraw(tabname, url, label, c.r_tab)}
  % endfor

  % if not c.indlg:
  ## saki sisu sulgemise nupp
  <li class="nav-item flex-grow-1 text-right r_body_hider" role="tab">
    ${h.mdi_icon('mdi-close hide_r', style='cursor:pointer', title=_("Peida"))}
  </li>
  % endif
</ul>
<script>
% if not c.indlg:
    ## sakkide sisu peitmine/avamine
    var hide_r_body = function(hide){
       $('#hindamine_p_div').toggleClass('hidden-r', hide);
    }
    $('#hindamine_r_div i.hide_r').click(function(){
      hide_r_body(true);
    });
% endif
  
## kui kasutaja klikib sakil
    $('.hindamine_r_tabs a.nav-link').click(function(){
% if not c.indlg:
      ## avame saki sisu
      hide_r_body(false);
% endif
      if(!$(this).is('.active'))
      {
         ## kui ei klikitud jooksval sakil, siis laadime serverist sisu
% if c.indlg:
        var container = $(this).closest('.modal-body');
% else:
        var container = $('#hindamine_r_div');
% endif
        ## sooritus_id on vajalik tekstianalyysi tabi korral
        ## (0 siis, kui toimub ylesande vaatamine, sooritust pole)
        var data = 'sooritus_id=' + ($('input#n_sooritus_id').val()||'0');
        dialog_load(this.href, data, 'get', container);
      }
      return false;
    });
  $(function(){
% if c.indlg:
  ## juhul, kui oleme modaalaknas, siis peab bodyl olema klass modal-open,
  ## et kerimisriba keriks modaali, mitte põhiakent
      $('body').addClass('modal-open');
% else:
      hkh_resize();
% endif
  });

</script>
## inint end
% endif
