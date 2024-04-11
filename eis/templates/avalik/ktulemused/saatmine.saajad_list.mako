% if c.items:
<table class="table table-borderless table-striped tablesorter">
  <thead>
    <tr>
      <th sorter="false" width="20px">
        ${h.checkbox1('all', 1, checked=c.all)}
      </th>
      % for sort_field, title in c.header:
        % if sort_field:
        ${h.th_sort(sort_field, title)}
        % else:
        ${h.th(title)}
        % endif
      % endfor
    </tr>
  </thead>
  <tbody>   
    % for n, rcd in enumerate(c.items):
    <%
     item = c.prepare_item(rcd, n)
     sooritaja, epost = rcd
    %>
    <tr>
      <td>
        % if epost:
        ${h.checkbox('j', sooritaja.id)}
        % endif
      </td>
      % for ind, s in enumerate(item):
      <td>
        % if ind == 2:
        % for buf in s.split(';'):
        <div>${buf}</div>
        % endfor
        % else:
        ${s}
        % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
<script>
  $('input#all').click(function(){
     $('input[name="j"]').prop('checked', this.checked);
  });
  $('input[name="j"],input#all').click(function(){
     $('button.jchecked').toggleClass('disabled', $('input[name="j"]:checked').length==0);
  });
  $(function(){
     $('button.jchecked').toggleClass('disabled', $('input[name="j"]:checked').length==0);
  });
</script>
% endif
