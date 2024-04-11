## Hindamise analüüs
## Seatud on c.item (ylesanne) ja c.block (sisuplokk) 
## ja c.testiosa ja võibolla isegi c.toimumisaeg
<%
   kysimused = [k for k in c.block.kysimused if k.tulemus_id]
%>
% for ind, c.kysimus in enumerate(kysimused):
  <hr class="my-2"/>
  <div class="d-flex flex-wrap">
    <h3 class="mr-3">${_("Küsimus")} ${h.qcode(c.kysimus, ah=True)}</h3>
    % if c.kysimus.selgitus:
    <div class="flex-grow-1 d-flex align-items-center">
      ${c.kysimus.selgitus}
    </div>
    % endif
  </div>
<!-- kysimus ${c.kysimus.id} testiosa ${c.testiosa.id} ${c.toimumisaeg and 'ta %s ' % c.toimumisaeg.id} -->
  <div class="div-stat-k">
    <%include file="analysis.kysimus.mako"/>
  </div>
% endfor
<script>
  ## vastuse märkimisel kuvatakse nupp "Lisa hindamismaatriksisse"
  function toggle_lisahm(fld)
  {
     var scope = $(fld).parents('.analysis-k');
     var visible = (scope.find('input:checked[name="kst_id"]').length > 0);
     scope.find('div.lisahm').toggle(visible);
  }
  $(function(){
    ## vastuse märkimisel käivitub
    $('body').on('change', 'input[name="kst_id"]',
        function(){toggle_lisahm(this);});
  });
</script>
