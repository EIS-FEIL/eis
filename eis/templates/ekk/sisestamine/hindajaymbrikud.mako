<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Hindamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Kirjalike testitööde ümbrike hindajatele väljastamine'),
h.url('sisestamine_valjastamine', sessioon_id=c.toimumisaeg.testimiskord.testsessioon_id))}
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi,
c.toimumisaeg.millal), h.url('sisestamine_valjastamine_hindamispaketid', toimumisaeg_id=c.toimumisaeg.id))} 
% if c.hindaja2:
${h.crumb('%s, %s' % (c.hindaja1.kasutaja.nimi, c.hindaja2.kasutaja.nimi))}
% else:
${h.crumb(c.hindaja1.kasutaja.nimi)}
% endif
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>


<%include file="valjastamine.before_tabs.mako"/>

<table width="100%" class="table table-borderless table-striped">
  <tr>
    <th>${_("Läbiviija")}</th>
    <th>${_("Õppeasutus")}</th>
    <th></th>
  </tr>
  <tr>
    <td>
      ${c.hindaja1.kasutaja.isikukood}
      ${c.hindaja1.kasutaja.nimi}
    </td>
    <td>
      <% c.kasutaja = c.hindaja1.kasutaja %>
      <%include file="/admin/kasutaja.ametikohad.mako"/>
    </td>
    <td>
      ${h.form_save(None)}
      ${h.hidden('sub', 'amet')}
      ${h.submit(_('Uuenda hindajate õppeasutuse andmed'))}
      ${h.end_form()}
    </td>
  </tr>
  % if c.hindaja2:
  <tr>
    <td>
      ${c.hindaja2.kasutaja.isikukood}
      ${c.hindaja2.kasutaja.nimi}
    </td>
    <td>
      <% c.kasutaja = c.hindaja2.kasutaja %>
      <%include file="/admin/kasutaja.ametikohad.mako"/>
    </td>
    <td></td>
  </tr>
  % endif
</table>
<br/>

<div class="listdiv">
  <%include file="hindajaymbrikud_list.mako"/>
</div>

## vormi nime muudame ära, et reavahetus käivitaks submiti
${h.form_save(None, form_name='form_search')}
<table class="table table-responsive">
  <tr>
    <td class="fh">${_("Sisesta ümbriku tähis")}</td>
    <td>
      ${h.text('tahised', c.tahised, size=30, class_='initialfocus')}
    </td>
    <td>
      ${h.button(_('Lisa'), id='otsi', onclick="register_no(this.form, $('div.listdiv'))")}
    </td>
    <td id="message"></td>
  </tr>
</table>
${h.end_form()}

<script>
var last_ts = null;
function register_no(form, container)
{
## topeltkliki kontroll
    var ts = (new Date()).getTime();
    if(last_ts && (ts - last_ts < 1000) && (container.find('.spinner-wrapper').length > 0))
    {
       ## spinner veel käib ja alles klikiti (skanner vist saadab kaks reavahetust järjest)
       return;
    }
    last_ts = ts;

    url = form.action;
    data = $(form).serialize();

    set_spinner_dlg(container);
    $('td#message').html('');

    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success:function(data){
            err = data[0];
            msg = data[1];
            body = data[2];
            $('input#tahised').val('');
            if(err) 
            {
               beep();
               alert_dialog(msg, eis_textjs.error);
            }
            else
            {
               container.html(body);
               block_is_ready(container);
               $('td#message').html(msg);
               $('input#tahised').focus();
            }
        },
        error:function(data){
           alert_dialog('Andmevahetuse viga', eis_textjs.error);
        },
        complete:function(request){
            remove_spinner();
        }
    })
}
</script>

