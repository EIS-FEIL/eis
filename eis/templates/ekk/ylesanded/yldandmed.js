// select2 jooksvate väärtuste kuvamise mall
function template_selection2(n){
    // viimane tase
    var divs = '<div class="col-sm-6">' + n.text + '</div>';
    if(n.p_text)
    {
        // teise taseme korral lisame esimese taseme
        divs = '<div class="col-sm-6">' + n.p_text + '</div>' + divs;
    }
    return $('<div class="row">' + divs + '</div>');
}
function update_opitulemused(el_opitulemused, aine)
{
    ## peale õppeaine muutmist muudame opitulemuste valiku
    var data = {'aine': aine};
    var url = "${h.url('pub_formatted_valikud', kood='OPITULEMUS2', format='json')}";
    $.getJSON(url, data,
                     function(data){
                         var old_value = el_opitulemused.val();
                         el_opitulemused.empty();
                         ${h.select2_js(None, old_value, [], data='data', multiple=True, multilevel=True, element='el_opitulemused')}
                         el_opitulemused.val(old_value).trigger('change.select2');
                     });
}
function update_teemad(el_teemad2, aine)
{
    if(!aine)
    {
        aine = el_teemad2.closest('div.ylesandeaine').find('select.aine').val();
    }
    var aste = $('#f_aste_kood').val();
    var data = {'aine': aine, 'aste': aste};
    var url = "${h.url('pub_formatted_valikud', kood='TEEMA2', format='json')}";
    $.getJSON(url, data,
                     function(data){
                         var old_value = el_teemad2.val();
                         el_teemad2.empty();
                         ${h.select2_js(None, old_value, [], data='data', multiple=True, multilevel=True, template_selection='template_selection2', element='el_teemad2')}
                         el_teemad2.val(old_value).trigger('change.select2');
                     });
}
function update_keeletase()
{
    var ained = [];
    $('select.aine').each(function(n, fld){
        var val = $(fld).val();
        if(val != '') ained.push(val);
    });
    var ainetasemed = ${model.json.dumps(c.opt.aine_keeletasemed)};
    var tasemed = [];
    for(var i=0; i<ainetasemed.length; i++)
    {
        if(ainetasemed[i][1].filter(function(n){ return ained.indexOf(n) !== -1; }).length > 0)
            tasemed.push(ainetasemed[i][0]);
    }
    $('#f_keeletase_kood').find('option').each(function(n, el){
        var value = $(el).attr('value');
        if(value != '')
        {
            var is_visible = tasemed.indexOf(value) > -1;
            if(!is_visible && $(el).is(':selected'))
            {
                $(el).prop('selected', false);
            }
            $(el).toggle(is_visible);
        }
    });
    $('div.keeletase').toggle(tasemed.length > 0);
}
function testiliik_by_ylkogu(){
## kui valitakse ylesandekogu, siis märgitakse automaatselt testiliigiks "ylesandekogu"
    $('input[name="tl.kood"][value="${const.TESTILIIK_YLKOGU}"]').prop('checked', true);
}
$(function(){
    ## uue õppeaine lisamine
    $('#addsubject').click(function(){
        var div_ained = $('div.ylesandeained');
        var seq = parseInt(div_ained.attr('counter'));
        div_ained.attr('counter', seq+1);
        var div_new = $('<div class="ylesandeaine"></div>').appendTo(div_ained);
        var href = $(this).attr('href');
        var aste = $('#f_aste_kood').val();
        dialog_load(href, 'seq='+seq+'&aste='+aste, 'GET', div_new);
    });

    $('div.ylesandeained').on('change', 'select.aine', function(){
        var div_aine = $(this).closest('div.ylesandeaine');
        var aine = $(this).val();
        ## teemade valik
        var el_teemad2 = div_aine.find('.teemad2');
        update_teemad(el_teemad2, aine);

        ## õpitulemused
        var opitul = div_aine.find('.opitulemused');
        update_opitulemused(opitul, aine);

        ## oskus
        var url = "${h.url('pub_formatted_valikud', kood='OSKUS', format='json')}";
        update_options(this, url, 'ylem_kood', div_aine.find('select.oskus'));

        update_keeletase();
    });
    update_keeletase();
    $('#f_aste_kood').change(function(){
        $('.teemad2').each(function(n, elem){
            update_teemad($(elem));
        });
    });
    $('#f_vastvorm_kood').change(function(){
        if(($(this).val() == '${const.VASTVORM_SH}') || ($(this).val() == '${const.VASTVORM_SP}'))
        {
            $('#f_hindamine_kood').val('${const.HINDAMINE_SUBJ}');
            $('#f_arvutihinnatav').val('');
            $('#f_etest').val('');
            $('#f_adaptiivne').val('');
        }
    });
    $('#f_hindamine_kood').change(function(){
        if($(this).val() == '${const.HINDAMINE_SUBJ}')
        {
            $('#f_arvutihinnatav').val('');
            $('#f_etest').val('');
        }
    });
    $('#f_arvutihinnatav').change(function(){
        if($(this).val() == '1')
        {
            $('#f_hindamine_kood').val('${const.HINDAMINE_OBJ}');
            var v = $('#f_vastvorm_kood').val();
            if(v != '${const.VASTVORM_KE}' && v != '${const.VASTVORM_SE}' && v != '${const.VASTVORM_I}' && v != '${const.VASTVORM_KP}')
                $('#f_vastvorm_kood').val('${const.VASTVORM_KE}');
            $('#f_etest').val('1');
        }
        else
        {
            $('#f_adaptiivne').val('');
        }
    });
    $('#f_etest').change(function(){
        if($(this).val() == '1')
        {
            var v = $('#f_vastvorm_kood').val();
            if(v != '${const.VASTVORM_KE}' && v != '${const.VASTVORM_SE}' && v != '${const.VASTVORM_I}')
                $('#f_vastvorm_kood').val('${const.VASTVORM_KE}');
        }
        else
        {
            $('#f_adaptiivne').val('');
            $('#f_nutiseade').val('');
        }
    });
    $('#f_adaptiivne').change(function(){
        if($(this).val() == '1')
        {
            $('#f_arvutihinnatav').val('1');
            $('#f_etest').val('1');
        }
    });
    $('#f_nutiseade').change(function(){
        if($(this).val() == '1')
        {
            $('#f_etest').val('1');
        }
    });
});
