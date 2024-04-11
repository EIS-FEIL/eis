## -*- coding: utf-8 -*- 
<%include file="/common/message.mako"/>
% if c.is_saved:
<script>close_dialog()</script>
% endif
<%
  c.kasutaja = c.item.sooritaja.kasutaja
  c.testiosa = c.item.testiosa
%>
${h.form_save(c.item.id)}
<div>
  <div class="form-group row">
    ${h.flb(_("Nimi"))}
    <div class="col">
      ${c.kasutaja.nimi}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb(_("Test"))}
    <div class="col">
      ${c.testiosa.test.nimi}
      <br/>
      ${c.testiosa.nimi}
    </div>
  </div>


<div class="accordion my-2" id="tutv_acc">
  <div class="accordion-card card parent-accordion-card">
    <div class="card-header" id="heading_tutv1">
      <div class="accordion-title" style="background-color:transparent">
        <button class="btn btn-link" type="button"
                data-toggle="collapse"
                data-target="#detail_tutv1"
                aria-controls="detail_tutv1"
                aria-expanded="true"
                id="b_tutv1">
          <span class="btn-label">
            <i class="mdi mdi-chevron-down"></i>
            ${_("Eksamitööga tutvumine Haridus- ja Noorteametis")}
          </span>
        </button>
      </div>
    </div>
    <div id="detail_tutv1" class="show" aria-labelledby="heading_tutv1">
      <div class="card-body p-3">
        <div class="form-group">
          <%
            url_t = 'https://www.harno.ee/riigieksamid#tutvumine'
            if model.date.today() < model.date(2021,6,30):
               url_t = 'https://harno.ee/uudised/riigieksamitoodega-tutvumine-ja-apelleerimine'
          %>
          ${h.link_to(_("Soovin oma eksamitööga tutvuda Haridus- ja Noorteametis"), url_t, rel='noopener', target='_blank')}
        </div>
      </div>
    </div>
  </div>
  <div class="accordion-card card parent-accordion-card">
    <div class="card-header" id="heading_tutv2">
      <div class="accordion-title" style="background-color:transparent">
        <button class="btn btn-link" type="button"
                data-toggle="collapse"
                data-target="#detail_tutv2"
                aria-controls="detail_tutv2"
                aria-expanded="true"
                id="b_tutv2">
          <span class="btn-label">
            <i class="mdi mdi-chevron-down"></i>
            ${_("Eksamitööga tutvumine elektroonselt")}
          </span>
        </button>
      </div>
    </div>
    <div id="detail_tutv2" class="show" aria-labelledby="heading_tutv1">
      <div class="card-body p-3">
        <div class="form-group row">
          ${h.checkbox('soovib_skanni', 0, checked=c.item.soovib_skanni, label=_("Soovin oma eksamitööst skannitud koopiat"), class_="cb-soovib")}
        </div>
        <div class="form-group row">
          ${h.flb(_("E-post"))}
          <div class="col">
            ${h.text('k_epost', c.kasutaja.epost, size=50)}
          </div>
        </div>
        % if c.item.tutv_esit_aeg:
        <div class="row">
          ${_("Taotlus on esitatud {s}").format(s=h.str_from_date(c.item.tutv_esit_aeg))}
        </div>
        % endif
        <div class="soovib" style="display:none">
          ${h.submit_dlg(clicked=True)}
        </div>
      </div>
    </div>
  </div>
</div>

</div>
${h.end_form()}

<script>
  $(function(){
  $('input.cb-soovib').click(function(){
    $('div.soovib').toggle($('input.cb-soovib').filter(':checked').length > 0);
  });
  $('div.soovib').toggle($('input.cb-soovib').filter(':checked').length > 0);  
  });
</script>
