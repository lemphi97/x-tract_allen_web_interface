"use_strict";

res_nrrd = 100;
exp_id = 0;

function download_grid_data(id, img, res)
{
    var url = "http://api.brain-map.org/grid_data/download_file/" + id + "?image=" + img + "&resolution=" + res;
    let a = document.createElement('a')
    a.href = url
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
}

/*
available :
    - projection_energy
    - projection_density
    - injection_fraction
    - injection_density
    - injection_energy
    - data_mask
*/

function download_projection_density()
{
    download_grid_data(exp_id, "projection_density", res_nrrd)
}

function download_projection_energy()
{
    download_grid_data(exp_id, "projection_energy", res_nrrd)
}

function download_injection_fraction()
{
    download_grid_data(exp_id, "injection_fraction", res_nrrd)
}

function download_injection_density()
{
    download_grid_data(exp_id, "injection_density", res_nrrd)
}

function download_injection_energy()
{
    download_grid_data(exp_id, "injection_energy", res_nrrd)
}

function download_data_mask()
{
    download_grid_data(exp_id, "data_mask", res_nrrd)
}

$(document).ready(function ()
{
    exp_id = $('#exp-id').html().trim();

    $('#res-nrrd').change(function()
    {
        res_nrrd = $('#res-nrrd').val();
    });
});