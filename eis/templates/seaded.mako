<%inherit file="/common/page.mako"/>
% if c.is_test and c.app_ekk:
${h.form_save(None)}
##<h2>${_("Kasutajaliidese kohandamine")}</h2>
<div class="form container" style="margin-bottom:10px">
  <div class="form-group row">
    ${h.flb(_("Kasutajaliides"), 'inst')}
    <div class="col-sm-3 col-xs-8">
      <%
        inst_name = c.my_inst_name or c.inst_name
        if inst_name not in ('test','prelive','live','clone'): inst_name = 'live'
      %>
      ${h.radio('inst', 'test', checkedif=inst_name, class_="nosave",
      label="Testkeskkond")}
      <br/>
      ${h.radio('inst', 'prelive', checkedif=inst_name, class_="nosave",
      label="Pre-live keskkond")}      
      <br/>
      ${h.radio('inst', 'live', checkedif=inst_name, class_="nosave",
      label="Toodangukeskkond, eis.ekk.edu.ee")}      
      <br/>
      ${h.radio('inst', 'clone', checkedif=inst_name, class_="nosave",
      label="Kloon, testid.edu.ee")}      
      <br/>
      <script>
        $('input[name="inst"]').click(function(){ dirty=false; this.form.submit();});
      </script>
    </div>
  </div>
</div>
${h.end_form()}
% endif

${h.form_save(None)}
${h.hidden('sub', 'forget')}
<div class="form container">
  <div class="row">
    <div class="col-12 fh">
      ${h.submit(_("Unusta meelde jäetud otsinguparameetrid"))}
    </div>
  </div>
</div>
${h.end_form()}

