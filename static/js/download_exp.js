"use_strict";

res_nrrd = 100;
exp_id = 0;

function download_grid_data(id, img, res)
{
    var url = "http://api.brain-map.org/grid_data/download_file/" + id + "?image=" + img + "&resolution=" + res;
    //alert(url);
    let a = document.createElement('a')
    a.href = url
    //a.download = url.split('/').pop()
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
}

$(document).ready(function ()
{
    exp_id = $('#exp-id').html().trim();

    $('#res-nrrd').change(function()
    {
        res_nrrd = $('#res-nrrd').val();
    });
});