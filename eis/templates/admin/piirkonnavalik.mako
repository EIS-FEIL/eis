## Ühe piirkonna valimise viis mitmest valikväljast
## enne include peab olema seatud c.piirkond_id ja c.piirkond_field
## võib olla seatud c.piirkond_on_change ja c.piirkond_filtered
## ja c.piirkond_maxtase
<%
  suffix = c.piirkond_suffix
  c.piirkonnavalik_id = f'piirkonnavalik_{h.rnd()}'
%>
<span id="${c.piirkonnavalik_id}">
${h.hidden(c.piirkond_field, c.piirkond_id)}
<% ylemad = model.Piirkond.get_ylemad_n(c.piirkond_id,3) %>

% for prk_cnt in range(c.piirkond_maxtase or 3):
<%
  if prk_cnt == 0:
      prk_ylem = None
  else:
      prk_ylem = ylemad[prk_cnt-1]

  opt_prk = model.Piirkond.get_opt_prk(prk_ylem, 
                                       filtered=c.piirkond_filtered or None)
  visible = len(opt_prk) == 0 and ' d-none' or ''
%>
${h.select(f'prk_id{suffix}', ylemad[prk_cnt], opt_prk, id=f'prk_id{suffix}_{prk_cnt}',
  empty=True, class_=f'prk_id {visible}')}
% endfor

<script>
$(function(){
  $('span#${c.piirkonnavalik_id} select.prk_id').change(function(){
    ## piirkonna valimise abifunktsioon, mis täidab teisi valikvälju
    var url = "${h.url('pub_formatted_valikud', kood='PIIRKOND', format='json')}";
    var valikud = 'span#${c.piirkonnavalik_id} select.prk_id';
    var tulemus = $('span#${c.piirkonnavalik_id} input[id="${c.piirkond_field}"]');

    ## kui ei ole optioneid, siis muutume nähtamatuks
    if($(this).find('option').length<=1) 
    {
       $(this).addClass('d-none');
       return;
    }
    if($(this).hasClass('d-none'))
    {
       $(this).removeClass('d-none');
    }

    $(this).nextAll(valikud).addClass('d-none').
       find('option[value!=""]').remove();

    if($(this).val() == '')
    {
       ## pole valitud
       var ylem_id = $(this).prevAll(valikud).last().val();
       tulemus.val(ylem_id).change();
    }
    else
    {
       var ylem_id = $(this).val();
       tulemus.val(ylem_id).change();
       ${c.piirkond_on_change}
       var data = {ylem_id: ylem_id};
% if c.piirkond_filtered:
       data['filtered'] = "${','.join([str(k) for k in c.piirkond_filtered])}";
% endif
       var target = $(this).nextAll(valikud).first();
       update_options(null, url, null, target, data, null, true);
    }
  });
});
</script>
</span>
