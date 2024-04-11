${h.form_search()}
${h.hidden('partial','1')}

<% subitems = c.tvorm and list(c.tvorm.alamosad) %>
% if subitems:
<div class="row content-wrapper flex-wrap">
  ${self.aside_parts(subitems)}
  <section class="col-12 col-md-9">
    <div class="form-group">
      <div class="flex-column flex-md-row">
        ${self.filter()}
        ${self.list_results()}
      </div>
    </div>
  </section>
</div>
% else:
${self.filter()}
${self.list_results()}
% endif
${h.end_form()}

<%def name="filter()">
<div class="gray-legend p-3 filter-w">
  <div class="form-group">
    <div class="row">
      % if c.klassidID:
      <div class="col-9">
        <div class="d-flex flex-wrap">
          <div class="mr-3">
            ${h.flb(_("Klass"), 'klassid')}
          </div>
          <div id="klassid">
            % for klassID in c.klassidID:
            <% checked = not c.klassid_id or (klassID.id in c.klassid_id) %>
            ${h.checkbox('klassid_id', klassID.id, checked=checked, label=klassID.name or _("Klass puudub"))}
            % endfor
          </div>
        </div>
      </div>
      % endif
      % if c.opt_opetajad:
      <div class="col-9">
        <div class="d-flex flex-wrap">
          <div class="mr-3">
            ${h.flb(_("Aineõpetaja"), 'aineop')}
          </div>
          <div id="aineop">
            % for (op_id, op_nimi) in c.opt_opetajad:
            <% checked = not c.op_id or (op_id in c.op_id) %>
            ${h.checkbox('op_id', op_id, checked=checked, label=op_nimi)}
            % endfor
            </div>
        </div>
      </div>
      % endif
      <div class="col">
        <div class="d-flex justify-content-end align-items-end">
        % if c.klassidID or c.opt_opetajad:
        ${h.submit_dlg(_("Näita"), container="$('#kl_listdiv')")}
        % endif
        ${h.submit(_("PDF"), id='pdf', level=2)}
        % if c.can_xls:
        ${h.submit(_("Excel"), id='xls', level=2)}
        % endif
        </div>
      </div>
    </div>
  </div>
</div>
</%def>

<%def name="list_results()">
<div class="listdiv" id="kl_listdiv">
<%include file="gruppidetulemused_list.mako"/>
</div>
</%def>

<%def name="aside_parts(subitems)">
  <aside class="sidebar-menu col-12 col-md-3 mr-0 d-block">
    <nav aria-label="Külgmenüü" class="mb-5 mr-4">
      <ul class="nav level-1">
        % for subitem in subitems:
        ${self.aside_parts_item(subitem, 2)}
        % endfor
        <script>
          $('.fbrpartfilter').click(function(){
            $('.fbrpart#fbrpart_'+this.value).toggle(this.checked);
          });
        </script>
      </ul>
    </nav>
  </aside>
</%def>

<%def name="aside_parts_item(item, level)">
        <li class="nav-item dropdown show">
          <a class="nav-link" role="button">
          <span class="text-truncate pl-2 pt-1">
            ${h.checkbox('osa_%s' % item.id, value=item.id, class_="fbrpartfilter", label=item.nimi)}
          </span>
          </a>
          <% alamosad = list(item.alamosad) %>
          <ul class="nav level-${level}">
            % for subitem in item.alamosad:
            ${self.aside_parts_item(subitem, level+1)}
            % endfor
          </ul>
        </li>
</%def>

