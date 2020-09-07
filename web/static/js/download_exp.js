"use_strict";

function download_img()
{
    var url = $("#img").attr("src");
    let a = document.createElement('a');
    a.href = url;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

$(document).ready(function ()
{
    var exp_id = $('#exp-id').html().trim();
    var shown_index = 1;
    //$('#index').val(shown_index);

    /*
     * Ranges sliders
     */
    $( "#red-slider-range").slider(
    {
        range: true,
        min: 0,
        max: 10000,
        values: [sections_ranges[0], sections_ranges[1]],
        slide: function(event, ui)
        {
            $("#red-range").val(ui.values[0] + " - " + ui.values[1]);
            $("#index").trigger("input");
        }
    });

    $("#red-range").val($("#red-slider-range").slider("values", 0) +
        " - " + $("#red-slider-range").slider("values", 1));

    $( "#green-slider-range").slider(
    {
        range: true,
        min: 0,
        max: 10000,
        values: [sections_ranges[2], sections_ranges[3]],
        slide: function(event, ui)
        {
            $("#green-range").val(ui.values[0] + " - " + ui.values[1]);
            $("#index").trigger("input");
        }
    });

    $("#green-range").val($("#green-slider-range").slider("values", 0) +
        " - " + $("#green-slider-range").slider("values", 1));

    $( "#blue-slider-range").slider(
    {
        range: true,
        min: 0,
        max: 10000,
        values: [sections_ranges[4], sections_ranges[5]],
        slide: function(event, ui)
        {
            $("#blue-range").val(ui.values[0] + " - " + ui.values[1]);
            $("#index").trigger("input");
        }
    });

    $("#blue-range").val($("#blue-slider-range").slider("values", 0) +
        " - " + $("#blue-slider-range").slider("values", 1));

    /*
     * Fetching images
     */
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

        var img_url = "http://api.brain-map.org/api/v2/projection_image_download/" +
            sections_id[shown_index - 1] +
            "?downsample=10&range=";

        var tmp_range = $("#red-range").val().split(" - ");
        img_url = img_url + tmp_range[0] + "," + tmp_range[1] + ",";
        var tmp_range = $("#green-range").val().split(" - ");
        img_url = img_url + tmp_range[0] + "," + tmp_range[1] + ",";
        var tmp_range = $("#blue-range").val().split(" - ");
        img_url = img_url + tmp_range[0] + "," + tmp_range[1];

        $('#img').attr("src", img_url);
        // link example:
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

    // download volumes
    $(".volume").on('click', function()
    {
        newRequest();
        var volume_type = this.value;
        var resolution = $('#res-proj').val();
        $.ajax(
        {
            type: 'POST',
            url: "/experiments/forms/experiment_volume/",
            data:
            {
                'experiment': exp_id,
                'volume_type': volume_type,
                'resolution': resolution
            },
            xhrFields:
            {
                responseType: 'blob'
            },
            success: function(data)
            {
                var a = document.createElement('a');
                var url = window.URL.createObjectURL(data);
                a.href = url;
                a.download = exp_id + '_' + volume_type + '_' + resolution + '.nii';
                document.body.append(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            },
            complete: function()
            {
                requestOver()
            }
        });
    });
});
