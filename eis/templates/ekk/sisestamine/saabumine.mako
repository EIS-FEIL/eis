<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Turvakottide ja testitööde ümbrike saabumise registreerimine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>

<h1>${_("Turvakottide ja testitööde saabumise registreerimine")}</h1>
<div class="gray-legend p-3">
  <div class="form-group row">
    ${h.flb(_("Sisesta turvakotinumber"),'kotinr')}
    <div>
      ## vormi nimi ei tohi olla form_save, sest enter peab käivitama submiti
      ${h.form_save(None, form_name='form_search')}
      ${h.text('kotinr', c.kotinr, size=12, maxlength=11)}
      ${h.button(_('Kinnita'), id='otsi', onclick="register_no(this.form, $(this.form).find('span#message'))")}
      <br/>
      <span id="message"></span>
      ${h.end_form()}
    </div>
  </div>
  <div class="m-1">${_("või")}</div>
  <div class="form-group row">
    ${h.flb(_("Sisesta testitööde ümbriku tähis"),'y_tahis')}
    <div>
      ${h.form_save(None, form_name='form_search')}            
      ${h.text('y_tahis', c.y_tahis, size=30, class_=c.focus and 'initialfocus' or None)}
      ${h.button(_('Kinnita'), id='otsi', onclick="register_no(this.form, $(this.form).find('span#message'))")}
      <br/>
      <span id="message"></span>
      ${h.end_form()}
    </div>
  </div>
</div>

<script>
var last_ts = null;
function register_no(form, container)
{
## koti või ymbriku saabumise registreerimine

## topeltkliki kontroll
    var ts = (new Date()).getTime();
    if(last_ts && (ts - last_ts < 1000) && ($('img#spinner').length > 0))
    {                          
       ## spinner veel käib ja alles klikiti (skanner vist saadab kaks reavahetust järjest)
       return;
    }
    last_ts = ts;

    container.html('');
    set_spinner_dlg(container);
    url = form.action;
    data = $(form).serialize();

## nr saadetakse serverisse
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success:function(data){
            err = data[0];
            msg = data[1];
            container.toggleClass('error', err);
            if(err == false) 
            {
## kui pole viga, siis kuvatakse teade ja nr sisestamise väli saab fookuse uue sisestamiseks
               container.html(msg);
               $(form).find('input[type="text"]').val('').focus();
            }
            else
            {
## kui on viga, siis kuvatakse see dialoogiaknas
               $(form).find('input[type="text"]').val('');
               beep();
               alert_dialog(msg, eis_textjs.error);
            }
        },
        error:function(data){
            container.html(eis_textjs.error)
        },
        complete:function(request){
            remove_spinner();
        }
    })
}
</script>

