function gen_title()
{
    var title = '';
    if($('select#f_aine_kood').val())
    {
        title = $('select#f_aine_kood option:selected').text();
    }
    var sulud = '';
    if($('select#f_testiklass_kood').val())
    {
        sulud = $('select#f_testiklass_kood option:selected').text() + '. klassi ';
    }
    if($('select#f_testiliik_kood').val())
    {
        var liik = $('select#f_testiliik_kood option:selected').text();
        sulud += liik.toLowerCase() + ' ';
    }
    if($('select#f_periood_kood').val())
    {
        var periood = $('select#f_periood_kood option:selected').text();
        sulud += periood;
    }        
    if(sulud)
    {
        title += ' (' + $.trim(sulud) + ')';
    }
    $('input#f_nimi').val(title);
}
function toggle_kursus()
{
    $('td.kursus').toggleClass('d-none', ($('select.kursus').find('option').length<1));
}
function update_testikursus()
{
    update_options($('select#f_aine_kood'),
                   "${h.url('pub_formatted_valikud', kood='TUNNAINE', format='json')}",
                   'ylem_kood', $('select.tunnaine'));
    update_options($('select#f_aine_kood'),
                   "${h.url('pub_formatted_valikud', kood='KURSUS', format='json')}",
                   'ylem_kood', $('select.kursus'));
}
var kogu_data = ${h.json.dumps(c.kogu_data)};
function data_from_kogu()
{
    var li = $('#kogud_id').val();
    var kogu_id = (li ? li[0] : '');
    var aine = $('#f_aine_kood');
    var astmed = $('input[name="aste_kood"]');
    if(kogu_id)
    {
        var d = kogu_data[kogu_id];
        aine.val(d[0]);
        astmed.prop('checked', false);
        astmed.filter('[value="'+d[1]+'"]').prop('checked', true);
    }
    aine.prop('disabled', kogu_id);
    astmed.prop('disabled', kogu_id);
}
$(function(){
    ## ylesandekogu valimine määrab aine ja kooliastme
    $('#kogud_id').on('change', data_from_kogu);
    data_from_kogu();
    $('form#form_save').bind('submit', function () {
        $(this).find(':input').prop('disabled', false);
    });    

    $('select#f_aine_kood').change(function(){
        if($(this).val()=='${const.AINE_RK}') $('select#f_testiliik_kood').val('${const.TESTILIIK_TASE}');
        if($(this).val()=='${const.AINE_C}') $('select#f_testiliik_kood').val('${const.TESTILIIK_SEADUS}');
    });
    $('select#f_testiliik_kood').change(function(){
        if($(this).val()=='${const.TESTILIIK_TASE}') $('select#f_aine_kood').val('${const.AINE_RK}');
        if($(this).val()=='${const.TESTILIIK_SEADUS}') $('select#f_aine_kood').val('${const.AINE_C}');
        $('.diag2').toggle($(this).val()=='${const.TESTILIIK_DIAG2}');
        $('.riigi').toggle($(this).val()=='${const.TESTILIIK_RIIGIEKSAM}');
        if($(this).val()=='${const.TESTILIIK_KOOLIPSYH}') $('input[name="f_pallideta"]').prop('checked', true);
        if($(this).val()=='${const.TESTILIIK_DIAG2}'){
            $('input[name="f_pallideta"]').prop('checked', true);        
            $('input[name="f_diagnoosiv"]').prop('checked', true);
            $('.no-diag').hide();
            $('input[name="r_korduv_sooritamine"]').prop('checked', true);                    
        }
    });
    $('input[name="f_diagnoosiv"]').click(function(){
        $('.no-diag').toggle(!$('input[name="f_diagnoosiv"]').is(':checked'));
    });
    $('.diag2').toggle($('select#f_testiliik_kood').val()=='${const.TESTILIIK_DIAG2}');              
    $('.riigi').toggle($('select#f_testiliik_kood').val()=='${const.TESTILIIK_RIIGIEKSAM}');
    $('.no-diag').toggle(!$('input[name="f_diagnoosiv"]').is(':checked'));    
    if($('select#f_rveksam_id').length)
    {
        $('select#f_aine_kood').change(
            callback_select("${h.url('pub_formatted_valikud', kood='RVEKSAM', format='json')}", 
                            'aine_kood', 
                            $('select#f_rveksam_id'))
        );
        % if c._arrayindexes != '':
        $('select#f_aine_kood').change();
        % endif
    }

    $('select#f_aine_kood').change(update_testikursus);
    % if c._arrayindexes != '':
    toggle_kursus();
    % endif

    $('select#f_aine_kood').change(
        callback_select("${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}", 
                        'ylem_kood', 
                        $('select.keeletase'))
    );
    $('select.keeletase').eq(0).change(function(){
        $('div.keeletase').toggleClass('d-none', ($(this).find('option').length<=2));
    });
    $('div.keeletase').toggleClass('d-none', ($('select.keeletase').eq(0).find('option').length<=2));

    $('input[name="r_korduv_sailitamine"]').click(function(){
        if(this.checked) $('input[name="r_korduv_sooritamine"]').prop('checked', true);
    });
    $('input[name="r_korduv_sooritamine"]').click(function(){
        if(!this.checked) $('input[name="r_korduv_sailitamine"]').prop('checked', false);
    });        
    $('table#tbl_vahemikud input').change(function(){
        $(this).closest('tr').prev().find('span[id="vahemikulopp"]').text(parseInt(this.value)-1);
    });
    $('input#f_osalemise_peitmine').click(function(){
        if(this.checked) $('input#f_oige_naitamine').prop('checked', false);
    });
    $('input#f_oige_naitamine').click(function(){
        if(this.checked) $('input#f_osalemise_peitmine').prop('checked', false);
    });
    $('input#f_vastus_tugiisikule').click(function(){
        if(!this.checked) $('input#f_tulemus_tugiisikule').prop('checked', false);
    });
    $('input#f_tulemus_tugiisikule').click(function(){
        if(this.checked) $('input#f_vastus_tugiisikule').prop('checked', true);
    });
});
