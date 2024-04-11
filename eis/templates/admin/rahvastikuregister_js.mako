## Rahvastikuregistrist päringu tegemine ja aadressi kasutamine
<script>
## väljad, kus jäetakse RR aadress meelde (enne vormil asendamist)
var rr_adr_id = null;
var rr_koodid = [];
var rr_normimata = ''

## RR päringu tegemine
function query_rr(kasutaja_id, isikukood)
{
    var tr_container = $('#tr_rr_aadress');
    var container = tr_container.find('#rr_taisaadress');
    container.text('');
    tr_container.find('button#rraa').hide();
    tr_container.removeClass('d-none');
    set_spinner_dlg(container);

    // teeme päringu
    data = {kasutaja_id: kasutaja_id, isikukood: isikukood};
    $.ajax({
        type: 'GET',
        url: '${c.rr_query_url}',
        data: data,
        dataType: 'json',
        success:function(data){
            var err = data['error'];
            if(err) 
            {
               tr_container.addClass('d-none');
               alert_dialog(err);
            }
            else
            {
               $('input#k_eesnimi').val(data['eesnimi']);
               $('input#k_perenimi').val(data['perenimi']);
               $('span#k_nimi').text(data['eesnimi']+' '+data['perenimi']);
               ##$('input#k_synnikpv').val(data['synnikpv']);
               ##$('input#k_sugu').val(data['sugu']);
               rr_adr_id = data['adr_id'];
               rr_koodid = data['koodid'];
               rr_normimata = data['normimata'];
               if(data['taisaadress'])
               {
                  tr_container.find('button#rraa').show();
                  $('#rr_taisaadress').text(data['taisaadress']);
               }
               if(data['kodakond_nimi'])
               {
                  $('#dkodakond').text(data['kodakond_nimi']);
               }
            }
        },
        error:function(data){
            alert_dialog('${_("Midagi on valesti")}')
        },
        complete:function(request){
            remove_spinner();
        }
    })
}

## RR aadressi kasutuselevõtt: asendatakse aadresskomponendid
function use_rr_aadress()
{
   set_adrkomp(0, rr_koodid, rr_normimata, rr_adr_id);
}
</script>
