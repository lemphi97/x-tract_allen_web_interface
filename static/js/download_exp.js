"use_strict";

exp_id = 0;

function download_grid_data(id, img, res)
{
    var url = "http://api.brain-map.org/grid_data/download_file/" + id + "?image=" + img + "&resolution=" + res;
    let a = document.createElement('a');
    a.href = url;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

/*
available :
    - projection_density
    - projection_energy
    - injection_fraction
    - injection_density
    - injection_energy
    - data_mask
*/

function download_projection_density()
{
    download_grid_data(exp_id, "projection_density", $('#res-nrrd').val());
}

function download_projection_energy()
{
    download_grid_data(exp_id, "projection_energy", $('#res-nrrd').val());
}

function download_injection_fraction()
{
    download_grid_data(exp_id, "injection_fraction", $('#res-nrrd').val());
}

function download_injection_density()
{
    download_grid_data(exp_id, "injection_density", $('#res-nrrd').val());
}

function download_injection_energy()
{
    download_grid_data(exp_id, "injection_energy", $('#res-nrrd').val());
}

function download_data_mask()
{
    download_grid_data(exp_id, "data_mask", $('#res-nrrd').val());
}

$(document).ready(function ()
{
    exp_id = $('#exp-id').html().trim();
    var shown_index = 1;
    //$('#index').val(shown_index);
    $('#nb-img').text("1 to " + sections_id.length + " images");

    $('#index').on('input', function()
    {
        var req_index = parseInt($('#index').val());

        if (isNaN(req_index) || req_index < 1)
        {
            shown_index = 1;
        }
        else if (req_index > sections_id.length)
        {
            shown_index = sections_id.length;
        }
        else
        {
            shown_index = req_index;
        }

        $('#index').val(shown_index);

        // TODO change img
        var img_url = "http://api.brain-map.org/api/v2/projection_image_download/" +
            sections_id[shown_index - 1] +
            "?downsample=10&range=";

        sections_ranges.forEach(function(item, index)
        {
            img_url = img_url + item;
            if (index < sections_ranges.length - 1)
            {
                img_url = img_url + ',';
            }
        });

        //img_url.concat(".jpg");
        $('#img').attr("src", img_url);
        // http://api.brain-map.org/api/v2/projection_image_download/180719423?downsample=4&range=0,1321,1861,3722,0,4095
    });


    $('#prev').on('click', function()
    {
        if (shown_index > 1)
        {
            $('#index').val(parseInt($('#index').val()) - 1);
            $("#index").trigger("input");
        }
    })

    $('#next').on('click', function()
    {
        if (shown_index < sections_id.length)
        {
            $('#index').val(parseInt($('#index').val()) + 1);
            $("#index").trigger("input");
        }
    })

    $("#index").trigger("input");
});
