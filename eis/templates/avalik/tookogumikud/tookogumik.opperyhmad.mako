<div class="mt-3" style="clear:both">
  <div class="d-flex flex-wrap mb-1">
    <h2 class="flex-grow-1">${_("Õpilaste rühmad")}</h2>
    ${h.blink_to(_("Loo uus"), h.url('opperyhmad'), level=2, mdicls='mdi-plus', style="float:right")}
  </div>
% if c.opperyhmad:
  <table width="100%" class="table table-striped" >
    <tbody>
      % for item in c.opperyhmad:
      <tr>
        <td>${h.link_to(item.nimi, h.url('edit_opperyhm', id=item.id))}</td>
      </tr>
      % endfor
    </tbody>
  </table>
% endif
</div>

