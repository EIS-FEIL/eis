% if c.is_edit:
function gen_ranges(fld)
{
    ## vahemike genereerimise dialoogis vajutati genereerimise nupule
    var step;
    var block = $(fld).closest('div');
    var tehe = block.find('select#d_tehe').val();
    try {
        step = parseFloat(block.find('input#d_step').val());
    } catch {
        return;
    }
    if(step <= 0) return;
    var tbody = $('table#tbl_np_npts>tbody');
    var max_val = 100;
    if($('select.normikood').val() == '${const.NORMITYYP_PALLID}')
    {
        max_val = ${c.ylesanne.max_pallid or 0};
    }
    var min_val = 0;
    var len0 = tbody.children('tr').length;
    var cnt = Math.ceil(max_val / step); // mitu vahemikku on vaja
    var value = min_val;
    if(tehe == '>' || tehe == '>=')
    {
        // vahemikud kahanevas järjekorras
        value = max_val;
        step = 0 - step;
    }
    else if(tehe == '==')
    {
        value -= step;
        cnt += 1;
    }
    for(var ind = 0; ind < cnt; ind++)
    {
        console.log(ind+', value='+value);
        if(ind >= len0)
        {
            // lisame uue rea
            $('input.addnpts').click();
        }
        if((tehe != '==') && (ind == cnt - 1))
        {
            // viimane vahemik teistpidi märgiga
            if(tehe == '>') tehe = '<=';
            else if(tehe == '<') tehe = '>=';
            else if(tehe == '>=') tehe = '<';
            else if(tehe == '<=') tehe = '>';
        }
        else
        {
            // samm edasi
            value += step;
        }
        var tr = tbody.children('tr').eq(ind);
        tr.find('select.tingimus_tehe').val(tehe);
        tr.find('input.tingimus_vaartus').val(value);
    }
    while(ind < tbody.children('tr').length)
    {
        tbody.children('tr').last().remove();
    }
    close_dialog();
}
function on_addrow_npts(tableid)
{
    init_ckeditor_tbl('np', tableid, -1, '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}
## koodi valimisel kuvatakse või peidetakse valikväli või arvuväli sõltuvalt, kas valiti valiku kood
function ch_diag_kood(fld, set_default_op)
{
    var kood = fld.val();
    var block = fld.closest('div');
##    if(typeof choices[kood] != 'undefined')
##    {
##        // on valikud
##        block.find('.tingimus_vaartus').val('').hide();
##        block.find('.tingimus_valik').each(function(n, item){
##            var choice = $(item);
##            var old_value = choice.val();
##            choice.find('option').remove();
##            for(var i=0; i<choices[kood].length; i++)
##            {
##                choice.append($('<option/>')
##                              .attr('value', choices[kood][i][0])
##                              .text(choices[kood][i][1]));                    
##            }
##            choice.val(old_value);
##            choice.show();
##        });
##    }
##    else
    {
        block.find('.tingimus_vaartus').show();
        block.find('.tingimus_valik').val('').hide();
##        if(set_default_op) block.find('.tingimus_tehe').val('>');
    }
}
% endif
% if c.is_edit or c.is_tr:
function reinit_ckeditor()
{
    destroy_old_ckeditor();
    var inputs = $('table.nptagasisided>tbody textarea.editable,textarea.editable#f_yl_tagasiside');
    init_ckeditor(inputs, 'np_ckeditor_top', '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}
% endif
$(function(){
% if c.is_edit:
    $('.normikood').change(function(){
        ch_diag_kood($(this), true);
    });
    ch_diag_kood($('.normikood'), false);
    $('table.nptagasisided').on('click', '.ts-up', function(){
        ##var tr = $(this).closest('tr');
        ## if(tr.prev().length) tr.prev().insertAfter(tr);
        var tr = $(this).closest('tr')[0];
        if(tr.previousElementSibling)
        {
            tr.parentNode.insertBefore(tr, tr.previousElementSibling);
            reinit_ckeditor();
        }
    });
    $('table.nptagasisided').on('click', '.ts-down', function(){
        ##var tr = $(this).closest('tr');
        ##if(tr.next().length) tr.next().insertBefore(tr);
        var tr = $(this).closest('tr')[0];        
        if(tr.nextElementSibling)
        {
            tr.parentNode.insertBefore(tr.nextElementSibling, tr);
            reinit_ckeditor();
        }
    });
% endif
% if c.is_edit or c.is_tr:    
    reinit_ckeditor();
% endif
});
