<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="skannid.tabs.mako"/>
</%def>
<%def name="page_title()">
${_("Skannitud eksamitööde üles laadimine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Skannitud eksamitööd"), h.url('muud_skannid_taotlemised'))}
${h.crumb(_("Üles laadimine"), h.url('muud_skannid_laadimised'))}
</%def>
<%def name="require()">
<% c.includes['dropzone'] = True %>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

${h.form_save(None)}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"), 'sessioon_id')}
        <% 
               opt_sessioon = model.Testsessioon.get_opt()
               if c.sessioon_id and int(c.sessioon_id) not in [r[0] for r in opt_sessioon]:
                  c.sessioon_id = None
        %>
        ${h.select('sessioon_id', c.sessioon_id, opt_sessioon, empty=True, class_='nosave')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Test"), 'test_id')}
        <div>
          <%
              opt_test = model.Test.get_opt(c.sessioon_id or -1, vastvorm=const.VASTVORM_KP, disp_test_id=True) or []
              if c.test_id and int(c.test_id) not in [r[0] for r in opt_test]:
                  c.test_id = None
          %>
          ${h.select('test_id', c.test_id, opt_test, empty=True, class_='nosave')}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Toimumisaeg"),'toimumisaeg_id')}
        ${h.select('toimumisaeg_id', c.toimumisaeg_id,
        model.Toimumisaeg.get_opt(c.sessioon_id or -1, test_id=c.test_id or -1, vastvorm_kood=const.VASTVORM_KP) or [],
        empty=True, class_='nosave')}
      </div>
    </div>
  </div>
</div>

<div id="divload" class="mt-3" style="display:none">
  ${_("Failide nimed peavad olema kujul XXX-YYY.pdf või ABC.XXX-YYY.pdf, kus: <ul><li>XXX-YYY on töö kood valitud toimumisajal </li><li> ning ABC on suvaline tekst (mille sisu süsteem ei arvesta) </li></ul>")}
  <div class="dropzone"></div>
  <br/>
</div>
${h.end_form()}

<script>
$(function(){
  $('select#sessioon_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                           'sessioon_id', 
                           $('select#test_id'),
                           {vastvorm:"${const.VASTVORM_KP}", disp_test_id:1},
                           $('select#toimumisaeg_id')));
  $('select#test_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TOIMUMISAEG', format='json')}", 
                           'test_id', 
                           $('select#toimumisaeg_id'),
                           function(){return {sessioon_id:$('select#sessioon_id').val(),
                                              vastvorm:"${const.VASTVORM_KP}"};}
                          ));
  $('select#toimumisaeg_id').change(function(){
      $('div#divload').toggle($('select#toimumisaeg_id').val()!='');
      $('div#divload .dz-complete').remove();
  });
  $('div#divload').toggle($('select#toimumisaeg_id').val()!='');

  $('div.dropzone').dropzone({
     url: function(){ return $('form#form_save').attr('action') + '?' + $('form#form_save').serialize(); },
     dictDefaultMessage: "${_("Laadi failid")}",
     ##parallelUploads: 1,
     previewTemplate: $('.fz-template')[0].innerHTML,  
     acceptedFiles: ".pdf",
     error: function(file, err){
          var el = $(file.previewElement);
          el.find('.progress').hide();
          el.find('.error').text(_("Viga laadimisel")); 
     },
     success: function(file, response){
          var el = $(file.previewElement);
          el.find('.progress').hide();
          if(response.error)
              el.find('.error').text(response.error); 
          if(response.filename)
              el.find('.filename').text(response.filename);
          if(response.msg)
              el.find('.msg').text(response.msg);               
        }
  });
});
</script>

<div style="display:none" class="fz-template">
  <div style="display:inline-table;margin:5px;padding:5px;border:1px solid #cfcfcf;border-radius:6px;">
      <span class="filename"></span>
      <span class="size" style="padding-left:10px" data-dz-size></span>
      <div><strong class="error text-danger" data-dz-errormessage></strong></div>
      <div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
        <div class="progress-bar progress-bar-success" style="width:0%;" data-dz-uploadprogress></div>
      </div>
      <div class="msg"></div>
  </div>
</div>
      
