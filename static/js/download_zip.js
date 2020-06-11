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

function get_urls(id_array, img_array, res)
{
    url_array = [];
    var i;
    if (img_array.length != 0)
    {
        for (i = 0; i < id_array.length; i++)
        {
            var j;
            for (j = 0; j < img_array.length; j++)
            {
                url_array.push(
                    "http://api.brain-map.org/grid_data/download_file/" +
                    id_array[i] +
                    "?image=" + img_array[j] +
                    "&resolution=" + res
                );
            }
        }
    }
    return url_array;
}

$(document).ready(function ()
{
    $('#download-all-nrrd').click(function()
    {
        // `getColumn` and `table` are from table.js
        var id_array = getColumn(table, 0);

        var img_array = get_img();

        var urls = get_urls(id_array, img_array, $('#res-nrrd').val());

        if (urls.length != 0)
        {
            // For test on localhost, port must be the same as app
            // Otherwise you'll run into CORS issue
            var socket = io.connect('http://127.0.0.1:5000/socket');
            socket.emit('req_download', urls);
            // TODO disable download btn
            socket.on('req_answer', function(url)
            {
                console.log("download is ready at " + url);
                // TODO enable download button
                let a = document.createElement('a');
                a.href = url;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });
        }
    });
});