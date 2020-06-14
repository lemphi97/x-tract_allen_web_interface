"use_strict";

function get_img()
{
    img_array = [];
    if ($('#projection-density').prop('checked')) {
        img_array.push("projection_density");
    }
    if ($('#projection-energy').prop('checked')) {
        img_array.push("projection_energy");
    }
    if ($('#injection-fraction').prop('checked')) {
        img_array.push("projection_fraction");
    }
    if ($('#injection-density').prop('checked')) {
        img_array.push("projection_density");
    }
    if ($('#injection-energy').prop('checked')) {
        img_array.push("projection_energy");
    }
    if ($('#data-mask').prop('checked')) {
        img_array.push("data_mask");
    }
    return img_array;
}

$(document).ready(function ()
{
    $('#download-all-nrrd').click(function()
    {
        // `getColumn` and `table` are from table.js
        var id_array = getColumn(table, 0);

        var img_array = get_img();

        if (id_array.length != 0 && img_array.length != 0)
        {
            // For test on localhost, port must be the same as app
            // Otherwise you'll run into CORS issue
            var socket = io.connect('http://127.0.0.1:5000/request_zip');
            // TODO disable download btn

            socket.on('zip_ready', function(str)
            {
                console.log(str);
                socket.disconnect();
                // TODO enable download btn
            });

            socket.emit('req_download', id_array, img_array, parseInt($('#res-nrrd').val()));
        }
    });
});