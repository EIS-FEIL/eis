<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Ülesanded")} | ${_("Importimine")}
</%def> 
<%def name="breadcrumbs()">
${h.crumb(_("Ülesanded"), h.url('ylesanded'))}
${h.crumb(_("Importimine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>
<h3>${_("Ülesannete ja testide importimine")}</h3>
${h.form_save(None, multipart=True)}     
<div class="form-wrapper mb-2">
  <div class="form-group row">
    ${h.flb3(_("Fail"), 'f_filedata', rq=True)}
    <div class="col">
      ${h.file('f_filedata', value=_("Vali fail"))}
      <script>
      $(function(){
        $('input#f_filedata').change(function(e){
          var ext = $('#f_filedata').val().split('.').pop().toLowerCase();
          $('.csv-import,.gift-import').hide();
          if(ext == 'csv') $('.csv-import').show();
          else if(ext == 'gift') $('.gift-import').show();
        });
        $('.csv-import,.gift-import').hide();
        % if c.ext == 'csv':
        $('.csv-import').show();
        % elif c.ext == 'gift':
        $('.gift-import').show();
        % endif
      });
      </script>
      <div class="csv-import">
        ${h.checkbox('utf8', 1, checked=c.utf8, label="UTF-8")}
      </div>
    </div>
  </div>
  <div class="csv-import">
    <div class="form-group row">
      ${h.flb3(_("Pildifailid"))}
      <div class="col">
        ${self.imgfiles()}
      </div>
    </div>
  </div>
  <div class="csv-import gift-import">
    <div class="form-group row">
      ${h.flb3(_("Õppeaine"))}
      <div class="col">
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE'))}
      </div>
    </div>
    <div class="form-group row">
      ${h.flb3(_("Keel"))}
      <div class="col">
        ${h.select('lang', c.lang, c.opt.klread_kood('SOORKEEL'))}
      </div>
    </div>
  </div>
</div>

<div class="text-right my-2">
  ${h.submit(_("Impordi"))}
</div>
${h.end_form()}


% if c.messages:
  % for tu in c.messages:
    % if tu[0]:
       <p>${h.literal(tu[1])}</p>
    % else:
       ${h.alert_error(h.literal(tu[1]))}
    % endif
  % endfor
% endif

% if c.items:
<table class="table table-borderless table-striped" width="100%" >
  <caption>
   ${_("Importimise tulemus")}
  </caption>
  <tbody>
    % for rcd in c.items:
    <%
      if isinstance(rcd, model.Ylesanne):
         liik = _("Ülesanne")
         label = '%s %s' % (liik, rcd.id) 
         item_url = h.url('ylesanne', id=rcd.id)
      elif isinstance(rcd, model.Test):
         liik = _("Test")
         label = '%s %s' % (liik, rcd.id) 
         item_url = h.url('test', id=rcd.id)
      elif isinstance(rcd, model.Rveksam):
         liik = _("RV eksam")
         label = '%s %s' % (liik, rcd.id) 
         item_url = h.url('admin_rveksam', id=rcd.id)
      elif isinstance(rcd, model.Klassifikaator):
         liik = _("Klassifikaator")
         label = '%s %s' % (liik, rcd.kood) 
         item_url = h.url('admin_klassifikaator', id=rcd.kood)
      else:
         liik = rcd.__class__.__name__
         label = '%s %s' % (liik, rcd.id) 
         item_url = None
    %>
    <tr>
      <td>
        % if item_url:
        ${h.link_to(label, item_url)}
        % else:
        ${label}
        % endif
        % if isinstance(rcd, model.Ylesanne) and rcd.kood:
        (${rcd.kood})
        % endif
      </td>
      <td>
        % if item_url:
        ${h.link_to(rcd.nimi, item_url)}
        % else:
        ${rcd.nimi}
        % endif
      </td>
      <td>
        % if isinstance(rcd, model.Ylesanne):
        ${rcd.lahendusjuhis}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

<%def name="imgfiles()">
  <% prefix = 'files' %>
  <table id="imgfiles" class="list-whiteborder list" border="0" >
    <tbody>
          % if c._arrayindexes != '':
          ## valideerimisvigade korral
          %   for cnt in c._arrayindexes.get(prefix) or []:
                  ${self.row_imgfiles('%s-%s' % (prefix,cnt), c.new_item())}
          %   endfor
          % else:
          %   for cnt in range(1):
                  ${self.row_imgfiles('%s-%s' % (prefix,cnt), c.new_item())}
          %   endfor
          % endif
    </tbody>
  </table>
  <div id="sample_imgfiles" class="invisible">
        <!--
        ${self.row_imgfiles('%s__cnt__' % prefix, c.new_item())}
        -->
  </div>
  % if c.is_edit:
  <div style="padding:4px">
    ${h.button(_("Lisa"), onclick="grid_addrow('imgfiles');", level=2, mdicls='mdi-plus')}
  </div>
  % endif
</%def>

<%def name="row_imgfiles(prefix, item)">
       <tr id="${prefix}">
         <td nowrap>
           ${h.file('%s.filedata' % (prefix), multiple="multiple")}
         </td>
         <td>
           % if c.is_edit:
           ${h.grid_remove()}
           % endif
         </td>
       </tr>
</%def>
