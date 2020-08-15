/**
 * Global variables
 */
// table
var table;

// include filters:
var includeIds = [""];
var includeNames = [""];
var includeAcronyms = [""];
var includeProducts = [""];
var includeLines = [""];
var includeMinVol = "NaN";
var includeMaxVol = "NaN";
var includeMinX = "NaN";
var includeMaxX = "NaN";
var includeMinY = "NaN";
var includeMaxY = "NaN";
var includeMinZ = "NaN";
var includeMaxZ = "NaN";
var includeGender = "ANY";
var includeCre = "ANY";
var includeContainsNameFilter = false;
var includeContainsAcronFilter = false;
var includeContainsProdFilter = false;
var includeContainsLineFilter = false;

// exclude filters:
var excludeIds = [""];
var excludeNames = [""];
var excludeAcronyms = [""];
var excludeProducts = [""];
var excludeLines = [""];
var excludeMinVol = "NaN";
var excludeMaxVol = "NaN";
var excludeMinX = "NaN";
var excludeMaxX = "NaN";
var excludeMinY = "NaN";
var excludeMaxY = "NaN";
var excludeMinZ = "NaN";
var excludeMaxZ = "NaN";
var excludeContainsNameFilter = false;
var excludeContainsAcronFilter = false;
var excludeContainsProdFilter = false;
var excludeContainsLineFilter = false;

// DOM parser
var parser = new DOMParser();

// switch between include and exclude filters
function showIncludeFilters()
{
    $("#exclude-filters").css("display", "none");
    $("#include-filters").css("display", "block");
}

function showExcludeFilters()
{
    $("#include-filters").css("display", "none");
    $("#exclude-filters").css("display", "block");
}

function getColumn(datatableVar, columnIndex)
{
    array_column_data = [];
    var i;
    for (i = 0; i < datatableVar.$('tr', {"filter":"applied"}).length; i++)
    {
        var value = datatableVar.$('tr', {"filter":"applied"})[i].cells[columnIndex].innerText;
        value = value.replace(/\n/g,'').trim();
        array_column_data.push(value);
    }
    return array_column_data;
}

function getRowColumn(datatableVar, rowIndex, columnIndex)
{
    return datatableVar.$('tr', {"filter":"applied"})[rowIndex].cells[columnIndex].innerText;
}

/*
 * Gets all the unique structures without the acronym from the column of the datatable
 */
function getUniqueStructures(column)
{
    var uniqueStruct = [];
    for (i = 0; i < column.length; i++)
    {
        var unorderedList = parser.parseFromString(column[i], 'text/html');
        var structures = unorderedList.getElementsByTagName('li');
        for (j = 0; j < structures.length; j++)
        {
            var struct = structures[j].innerHTML;
            var indexBeforeAcron = struct.indexOf("|");
            var structName = struct.substring(0, indexBeforeAcron).trim();
            if (indexBeforeAcron > 0 && ! uniqueStruct.includes(structName))
            {
                uniqueStruct.push(structName);
            }
        }
    }

    return uniqueStruct;
}

/*
 * Gets all the unique acronym from the column of the datatable
 */
function getUniqueAcronyms(column)
{
    var uniqueStruct = [];
    for (i = 0; i < column.length; i++)
    {
        var unorderedList = parser.parseFromString(column[i], 'text/html');
        var structures = unorderedList.getElementsByTagName('li');
        for (j = 0; j < structures.length; j++)
        {
            var struct = structures[j].innerHTML;
            var structAcron = struct.match(/\|[^\|]*\|/)[0];
            // remove `|` chars from acronym
            structAcron = structAcron.substring(1, structAcron.length - 1);
            if (structAcron.length > 0 && ! uniqueStruct.includes(structAcron))
            {
                uniqueStruct.push(structAcron);
            }
        }
    }

    return uniqueStruct;
}

/*
 * Check if array contains str without considering cases
 */
function caseInsensitiveArrayInclude(array, str)
{
    var included = false;
    for (i = 0; i < array.length; i++)
    {
        var elem = array[i].trim();
        if (elem != "" && str.toUpperCase().includes(elem.toUpperCase()))
        {
            included = true;
            break;
        }
    }
    return included;
}

function validateText(validTexts, text)
{
    var valid = true;
    if (! caseInsensitiveArrayInclude(validTexts, text))
    {
        valid = false;
    }
    return valid;
}

function validateProducts(product, AllowedProducts)
{
    var valid = true;
    if (! caseInsensitiveArrayInclude(AllowedProducts, product))
    {
        valid = false;
    }
    return valid;
}

/*
 * return true if value is between min and max
 */
function validateMinMax(value, includeMin, includeMax, excludeMin, excludeMax)
{
    var valid = (
        (isNaN(includeMin) && isNaN(includeMax)) ||
        (isNaN(includeMin) && value <= includeMax) ||
        (isNaN(includeMax) && includeMin <= value) ||
        (includeMin <= value && value <= includeMax)
    )
    &&
    (
        (isNaN(excludeMin) && isNaN(excludeMax)) ||
        (isNaN(excludeMin) && value > excludeMax) ||
        (isNaN(excludeMax) && excludeMin > value) ||
        ! (excludeMin <= value && value <= excludeMax)
    );
    return valid;
}

/*
 * return true if value match allowedValue
 */
function validateSelect(value, allowedValue)
{
    if (allowedValue.toUpperCase() == "ANY" ||
        allowedValue.toUpperCase() == value.toUpperCase())
    {
        return true;
    }
    return false;
}

/* Custom filtering function which will validate each lines */
$.fn.dataTable.ext.search.push
(
    function(settings, data, dataIndex)
    {
        var matchFilter = false;

        var columnExpId = data[0];
        var columnStruct = data[1].replace(/  /g,""); // remove as much whitespace as possible
        var columnProduct = data[2];
        var columnVolume = parseFloat(data[3]) || 0;
        var x = parseInt(data[4]) || 0;
        var y = parseInt(data[5]) || 0;
        var z = parseInt(data[6]) || 0;
        var columnLine = data[7];
        var columnSpecName = data[8];
        var columnGender = data[9];
        var columnCre = data[10];

        var structIsIncluded = false;
        var structIsExcluded = false;
        var structArray = columnStruct.substring(0, columnStruct.lastIndexOf('|') - 1).split('|');

        /**
         * only check for structIsIncluded in case structure is also excluded,
         * in which case include takes priority over exclude
         */
        for (i = 0; i < structArray && !structIsIncluded; i += 2)
        {
            var name = structArray[i];
            var acronym = structArray[i + 1];
            structIsIncluded = validateText(includeNames, name) ||
                               validateText(includeAcronyms, acronym);

            structIsExcluded = validateText(excludeNames, name) ||
                               validateText(excludeAcronyms, acronym);
            structArray
        }

        if (validateText(includeIds, columnExpId))
        {
            matchFilter = true;
        }
        else if (! validateText(excludeIds, columnExpId) &&
            (
                validateMinMax(columnVolume, includeMinVol, includeMaxVol, excludeMinVol, excludeMaxVol) &&
                validateMinMax(x, includeMinX, includeMaxX, excludeMinX, excludeMaxX) &&
                validateMinMax(y, includeMinY, includeMaxY, excludeMinY, excludeMaxY) &&
                validateMinMax(z, includeMinZ, includeMaxZ, excludeMinZ, excludeMaxZ) &&
                validateSelect(columnGender, includeGender) &&
                validateSelect(columnCre, includeCre) &&
                (
                    (! includeContainsNameFilter && ! includeContainsAcronFilter) ||
                    structIsIncluded
                )
                &&
                (
                    (! excludeContainsNameFilter && ! excludeContainsAcronFilter) ||
                    ! structIsExcluded
                )
                &&
                (
                    ! includeContainsProdFilter ||
                    validateProducts(columnProduct, includeProducts)
                )
                &&
                (
                    ! excludeContainsProdFilter ||
                    ! validateProducts(columnProduct, excludeProducts)
                )
                &&
                (
                    ! includeContainsLineFilter ||
                    validateText(includeLines, columnLine)
                )
                &&
                (
                    ! excludeContainsLineFilter ||
                    ! validateText(excludeLines, columnLine)
                )
            )
        ){
            matchFilter = true;
        }
        return matchFilter;
    }
);

$(document).ready(function ()
{
    var pageUrl = window.location.href.split('/');

    var depth_max = 13100;
    var height_max = 7800;
    var width_max = 11300;

    var includeCanvas = document.getElementById("include-brain-canvas").getContext("2d");
    var excludeCanvas = document.getElementById("exclude-brain-canvas").getContext("2d");
    var mouseBrainImg = document.getElementById("mouse-brain-img");
    includeCanvas.drawImage(mouseBrainImg, 0, 0, 600, 200);
    excludeCanvas.drawImage(mouseBrainImg, 0, 0, 600, 200);

    // activate datatable
    table = $('#experiments').DataTable(
    {
        "scrollX": true,
        lengthMenu: [[5, 10, 25, 50, 100, -1], [5, 10, 25, 50, 100, "All"]],
        columnDefs: [{
            render: function ( data, type, row )
            {
                //return data.match(/\d*.\d{5}/);
                return parseFloat(data).toFixed(5); // seems faster
            },
            targets: [3]
        }]
    });

    //
    // Sliders
    //

    // canvas must be 600x200 for it to work
    function drawSliders(isInclude)
    {
        var context = excludeCanvas;
        var prefix = "exclude";
        if (isInclude)
        {
            context = includeCanvas;
            prefix = "include";
        }

        // expected starting and ending pixels for drawing lines in canvas:
        var coronalAxisX = [20, 161];
        var coronalAxisY = [48, 145];
        var sagittalAxisX = [202, 390];
        var sagittalAxisY = [45, 145];
        var horizontalAxisX = [445, 578];
        var horizontalAxisY = [17, 180];

        // get sliders values
        var depthRatio = [
            $("#" + prefix + "-slider-range-depth").slider("values", 0) / depth_max,
            $("#" + prefix + "-slider-range-depth").slider("values", 1) / depth_max
        ];
        var heightRatio = [
            $("#" + prefix + "-slider-range-height").slider("values", 0) / height_max,
            $("#" + prefix + "-slider-range-height").slider("values", 1) / height_max
        ];
        var widthRatio = [
            $("#" + prefix + "-slider-range-width").slider("values", 0) / width_max,
            $("#" + prefix + "-slider-range-width").slider("values", 1) / width_max
        ];

        context.clearRect(0, 0, 600, 200);
        context.drawImage(mouseBrainImg, 0, 0, 600, 200);
        context.lineWidth = 2;
        var x = 0;
        var y = 0;

        // draw depth slider
        context.beginPath();
        context.strokeStyle = "red";
        x = sagittalAxisX[0] + (depthRatio[0] * (sagittalAxisX[1] - sagittalAxisX[0]));
        context.moveTo(x, sagittalAxisY[0]);
        context.lineTo(x, sagittalAxisY[1]);
        x = sagittalAxisX[0] + (depthRatio[1] * (sagittalAxisX[1] - sagittalAxisX[0]));
        context.moveTo(x, sagittalAxisY[0]);
        context.lineTo(x, sagittalAxisY[1]);
        y = horizontalAxisY[0] + (depthRatio[0] * (horizontalAxisY[1] - horizontalAxisY[0]));
        context.moveTo(horizontalAxisX[0], y);
        context.lineTo(horizontalAxisX[1], y);
        y = horizontalAxisY[0] + (depthRatio[1] * (horizontalAxisY[1] - horizontalAxisY[0]));
        context.moveTo(horizontalAxisX[0], y);
        context.lineTo(horizontalAxisX[1], y);
        context.stroke();

        // draw height slider
        context.beginPath();
        context.strokeStyle = "blue";
        y = coronalAxisY[0] + (heightRatio[0] * (coronalAxisY[1] - coronalAxisY[0]));
        context.moveTo(coronalAxisX[0], y);
        context.lineTo(coronalAxisX[1], y);
        y = coronalAxisY[0] + (heightRatio[1] * (coronalAxisY[1] - coronalAxisY[0]));
        context.moveTo(coronalAxisX[0], y);
        context.lineTo(coronalAxisX[1], y);
        y = sagittalAxisY[0] + (heightRatio[0] * (sagittalAxisY[1] - sagittalAxisY[0]));
        context.moveTo(sagittalAxisX[0], y);
        context.lineTo(sagittalAxisX[1], y);
        y = sagittalAxisY[0] + (heightRatio[1] * (sagittalAxisY[1] - sagittalAxisY[0]));
        context.moveTo(sagittalAxisX[0], y);
        context.lineTo(sagittalAxisX[1], y);
        context.stroke();

        // draw width slider
        context.beginPath();
        context.strokeStyle = "green";
        x = coronalAxisX[0] + (widthRatio[0] * (coronalAxisX[1] - coronalAxisX[0]));
        context.moveTo(x, coronalAxisY[0]);
        context.lineTo(x, coronalAxisY[1]);
        x = coronalAxisX[0] + (widthRatio[1] * (coronalAxisX[1] - coronalAxisX[0]));
        context.moveTo(x, coronalAxisY[0]);
        context.lineTo(x, coronalAxisY[1]);
        x = horizontalAxisX[0] + (widthRatio[0] * (horizontalAxisX[1] - horizontalAxisX[0]));
        context.moveTo(x, horizontalAxisY[0]);
        context.lineTo(x, horizontalAxisY[1]);
        x = horizontalAxisX[0] + (widthRatio[1] * (horizontalAxisX[1] - horizontalAxisX[0]));
        context.moveTo(x, horizontalAxisY[0]);
        context.lineTo(x, horizontalAxisY[1]);
        context.stroke();
    }

    // include filters sliders
    $("#include-slider-range-depth").slider(
    {
        range: true,
        min: 0,
        max: depth_max,
        values: [0, depth_max],
        slide: function(event, ui)
        {
            $("#include-anterior").val(ui.values[0]);
            $("#include-posterior").val(ui.values[1]);
            drawSliders(true);
        }
    });

    $("#include-slider-range-height").slider(
    {
        range: true,
        min: 0,
        max: height_max,
        values: [0, height_max],
        slide: function(event, ui)
        {
            $("#include-higher").val(ui.values[0]);
            $("#include-lower").val(ui.values[1]);
            drawSliders(true);
        }
    });

    $("#include-slider-range-width").slider(
    {
        range: true,
        min: 0,
        max: width_max,
        values: [0, width_max],
        slide: function(event, ui)
        {
            $("#include-left").val(ui.values[0]);
            $("#include-right").val(ui.values[1]);
            drawSliders(true);
        }
    });

    $("#include-anterior").val($("#include-slider-range-depth").slider("values", 0));
    $("#include-posterior").val($("#include-slider-range-depth").slider("values", 1));
    $("#include-higher").val($("#include-slider-range-height").slider("values", 0));
    $("#include-lower").val($("#include-slider-range-height").slider("values", 1));
    $("#include-left").val($("#include-slider-range-width").slider("values", 0));
    $("#include-right").val($("#include-slider-range-width").slider("values", 1));

    $("#include-anterior").keyup(function()
    {
        var val = parseInt($("#include-anterior").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#include-slider-range-depth").slider("values", 1))
        {
            $("#include-slider-range-depth").slider("values", 0, val);
            drawSliders(true);
        }
    });

    $("#include-posterior").keyup(function()
    {
        var val = parseInt($("#include-posterior").val(), 10);
        if (!isNaN(val) &&
            val <= depth_max &&
            val >= $("#include-slider-range-depth").slider("values", 0))
        {
            $("#include-slider-range-depth").slider("values", 1, val);
            drawSliders(true);
        }
    });

    $("#include-higher").keyup(function()
    {
        var val = parseInt($("#include-higher").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#include-slider-range-height").slider("values", 1))
        {
            $("#include-slider-range-height").slider("values", 0, val);
            drawSliders(true);
        }
    });

    $("#include-lower").keyup(function()
    {
        var val = parseInt($("#include-lower").val(), 10);
        if (!isNaN(val) &&
            val <= height_max &&
            val >= $("#include-slider-range-height").slider("values", 0))
        {
            $("#include-slider-range-height").slider("values", 1, val);
            drawSliders(true);
        }
    });

    $("#include-left").keyup(function()
    {
        var val = parseInt($("#include-left").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#include-slider-range-width").slider("values", 1))
        {
            $("#include-slider-range-width").slider("values", 0, val);
            drawSliders(true);
        }
    });

    $("#include-right").keyup(function()
    {
        var val = parseInt($("#include-right").val(), 10);
        if (!isNaN(val) &&
            val <= width_max &&
            val >= $("#include-slider-range-width").slider("values", 0))
        {
            $("#include-slider-range-width").slider("values", 1, val);
            drawSliders(true);
        }
    });

    drawSliders(true); // draw include sliders on load

    // exclude filters sliders
    $("#exclude-slider-range-depth").slider(
    {
        range: true,
        min: 0,
        max: depth_max,
        values: [0, 0],
        slide: function(event, ui)
        {
            $("#exclude-anterior").val(ui.values[0]);
            $("#exclude-posterior").val(ui.values[1]);
            drawSliders(false);
        }
    });

    $("#exclude-slider-range-height").slider(
    {
        range: true,
        min: 0,
        max: height_max,
        values: [0, 0],
        slide: function(event, ui)
        {
            $("#exclude-higher").val(ui.values[0]);
            $("#exclude-lower").val(ui.values[1]);
            drawSliders(false);
        }
    });

    $("#exclude-slider-range-width").slider(
    {
        range: true,
        min: 0,
        max: width_max,
        values: [0, 0],
        slide: function(event, ui)
        {
            $("#exclude-left").val(ui.values[0]);
            $("#exclude-right").val(ui.values[1]);
            drawSliders(false);
        }
    });

    $("#exclude-anterior").val($("#exclude-slider-range-depth").slider("values", 0));
    $("#exclude-posterior").val($("#exclude-slider-range-depth").slider("values", 1));
    $("#exclude-higher").val($("#exclude-slider-range-height").slider("values", 0));
    $("#exclude-lower").val($("#exclude-slider-range-height").slider("values", 1));
    $("#exclude-left").val($("#exclude-slider-range-width").slider("values", 0));
    $("#exclude-right").val($("#exclude-slider-range-width").slider("values", 1));

    $("#exclude-anterior").keyup(function()
    {
        var val = parseInt($("#exclude-anterior").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#exclude-slider-range-depth").slider("values", 1))
        {
            $("#exclude-slider-range-depth").slider("values", 0, val);
            drawSliders(false);
        }
    });

    $("#exclude-posterior").keyup(function()
    {
        var val = parseInt($("#exclude-posterior").val(), 10);
        if (!isNaN(val) &&
            val <= depth_max &&
            val >= $("#exclude-slider-range-depth").slider("values", 0))
        {
            $("#exclude-slider-range-depth").slider("values", 1, val);
            drawSliders(false);
        }
    });

    $("#exclude-higher").keyup(function()
    {
        var val = parseInt($("#exclude-higher").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#exclude-slider-range-height").slider("values", 1))
        {
            $("#exclude-slider-range-height").slider("values", 0, val);
            drawSliders(false);
        }
    });

    $("#exclude-lower").keyup(function()
    {
        var val = parseInt($("#exclude-lower").val(), 10);
        if (!isNaN(val) &&
            val <= height_max &&
            val >= $("#exclude-slider-range-height").slider("values", 0))
        {
            $("#exclude-slider-range-height").slider("values", 1, val);
            drawSliders(false);
        }
    });

    $("#exclude-left").keyup(function()
    {
        var val = parseInt($("#exclude-left").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#exclude-slider-range-width").slider("values", 1))
        {
            $("#exclude-slider-range-width").slider("values", 0, val);
            drawSliders(false);
        }
    });

    $("#exclude-right").keyup(function()
    {
        var val = parseInt($("#exclude-right").val(), 10);
        if (!isNaN(val) &&
            val <= width_max &&
            val >= $("#exclude-slider-range-width").slider("values", 0))
        {
            $("#exclude-slider-range-width").slider("values", 1, val);
            drawSliders(false);
        }
    });

    drawSliders(false); // draw exclude sliders on load

    /*
     * Apply filters on table and re-draw it
     */
    $('#apply').click(function()
    {
        // get include filters
        includeIds = $('#include-id').val().split(";");

        includeNames = $('#include-name').val().split(";");
        includeContainsNameFilter = false;
        for (i = 0; i < includeNames.length; i++)
        {
            if (includeNames[i].trim() != "")
            {
                includeContainsNameFilter = true;
                break;
            }
        }

        includeAcronyms = $('#include-acron').val().split(";");
        includeContainsAcronFilter = false;
        for (i = 0; i < includeAcronyms.length; i++)
        {
            if (includeAcronyms[i].trim() != "")
            {
                includeContainsAcronFilter = true;
                break;
            }
        }

        includeProducts = $('#include-prod-id').val().split(";");
        includeContainsProdFilter = false;
        for (i = 0; i < includeProducts.length; i++)
        {
            if (includeProducts[i].trim() != "")
            {
                includeContainsProdFilter = true;
                break;
            }
        }

        includeLines = $('#include-line').val().split(";");
        includeContainsLineFilter = false;
        for (i = 0; i < includeLines.length; i++)
        {
            if (includeLines[i].trim() != "")
            {
                includeContainsLineFilter = true;
                break;
            }
        }

        includeMinVol = parseFloat($('#include-min-vol').val(), 10);
        includeMaxVol = parseFloat($('#include-max-vol').val(), 10);
        includeMinX = parseInt($("#include-slider-range-depth").slider("values", 0), 10);
        includeMaxX = parseInt($("#include-slider-range-depth").slider("values", 1), 10);
        includeMinY = parseInt($("#include-slider-range-height").slider("values", 0), 10);
        includeMaxY = parseInt($("#include-slider-range-height").slider("values", 1), 10);
        includeMinZ = parseInt($("#include-slider-range-width").slider("values", 0), 10);
        includeMaxZ = parseInt($("#include-slider-range-width").slider("values", 1), 10);
        includeGender = $('#include-gender-select').val();
        includeCre = $('#include-cre-select').val();

        // get exclude filters
        excludeIds = $('#exclude-id').val().split(";");

        excludeNames = $('#exclude-name').val().split(";");
        excludeContainsNameFilter = false;
        for (i = 0; i < excludeNames.length; i++)
        {
            if (excludeNames[i].trim() != "")
            {
                excludeContainsNameFilter = true;
                break;
            }
        }

        excludeAcronyms = $('#exclude-acron').val().split(";");
        excludeContainsAcronFilter = false;
        for (i = 0; i < excludeAcronyms.length; i++)
        {
            if (excludeAcronyms[i].trim() != "")
            {
                excludeContainsAcronFilter = true;
                break;
            }
        }

        excludeProducts = $('#exclude-prod-id').val().split(";");
        excludeContainsProdFilter = false;
        for (i = 0; i < excludeProducts.length; i++)
        {
            if (excludeProducts[i].trim() != "")
            {
                excludeContainsProdFilter = true;
                break;
            }
        }

        excludeLines = $('#exclude-line').val().split(";");
        excludeContainsLineFilter = false;
        for (i = 0; i < excludeLines.length; i++)
        {
            if (excludeLines[i].trim() != "")
            {
                excludeContainsLineFilter = true;
                break;
            }
        }

        excludeAcronyms = $('#exclude-acron').val().split(";");
        excludeMinVol = parseFloat($('#exclude-min-vol').val(), 10);
        excludeMaxVol = parseFloat($('#exclude-max-vol').val(), 10);
        excludeMinX = parseInt($("#exclude-slider-range-depth").slider("values", 0), 10);
        excludeMaxX = parseInt($("#exclude-slider-range-depth").slider("values", 1), 10);
        excludeMinY = parseInt($("#exclude-slider-range-height").slider("values", 0), 10);
        excludeMaxY = parseInt($("#exclude-slider-range-height").slider("values", 1), 10);
        excludeMinZ = parseInt($("#exclude-slider-range-width").slider("values", 0), 10);
        excludeMaxZ = parseInt($("#exclude-slider-range-width").slider("values", 1), 10);

        // redraw table
        table.draw();
    });

    //
    // generating URL to make save search and share them. Offer copy to clipboard
    //
    $('#generate-url').click(function()
    {
        var searchUrl = pageUrl[0] + "//" + pageUrl[2] + "/" + pageUrl[3] + "/filter/"

        var filtersId = ["include-id", "exclude-id",
                         "include-name", "exclude-name",
                         "include-acron", "exclude-acron",
                         "include-prod-id", "exclude-prod-id",
                         "include-line", "exclude-line",
                         "include-min-vol", "exclude-min-vol",
                         "include-max-vol", "exclude-max-vol",
                         "include-gender-select",
                         "include-cre-select"];

        filtersId.forEach(function(item, index)
        {
            var value = $('#' + item).val().trim();

            // if filter was set (not empty), it will be saved in URL
            if (value)
            {
                searchUrl += '?' + item + ':"' + value + '"';
            }
        });

        function addSliderToUrl(sliderId, minId, maxId)
        {
            return '?' + maxId + ':"' + $('#' + sliderId).slider("values", 1) + '"' +
                   '?' + minId + ':"' + $('#' + sliderId).slider("values", 0) + '"';
        }

        // sliders filters
        searchUrl += addSliderToUrl("include-slider-range-depth", "include-anterior", "include-posterior") +
                     addSliderToUrl("exclude-slider-range-depth", "exclude-anterior", "exclude-posterior") +
                     addSliderToUrl("include-slider-range-height", "include-higher", "include-lower") +
                     addSliderToUrl("exclude-slider-range-height", "exclude-higher", "exclude-lower") +
                     addSliderToUrl("include-slider-range-width", "include-left", "include-right") +
                     addSliderToUrl("exclude-slider-range-width", "exclude-left", "exclude-right");

        console.log("Generated url: " + searchUrl);
        $("#filter-url").val(searchUrl);

        $(".filter-url-group").css("display", "inline"); // show input field
    });

    // https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Interact_with_the_clipboard
    function copyLink() {
        var elemToCopy = document.querySelector("#filter-url");

        elemToCopy.select(); // Select the text field
        elemToCopy.setSelectionRange(0, 99999); // For mobile devices
        if (document.execCommand("copy"))
        {
            document.getElementById("label-copy-url").innerHTML = "link copied";
        }
        else
        {
            document.getElementById("label-copy-url").innerHTML = "couldn't copy";
        }
    }

    document.querySelector("#filter-url").addEventListener("click", copyLink);

    //
    // columns visibilty in datatable
    //
    $('.toggle-vis').on('click', function(e)
    {
        // Get the column API object
        var column = table.column($(this).attr('data-column'));

        // Toggle the visibility
        column.visible(! column.visible());
    });

    //
    // Configure autocomplete
    //
    var structures = getUniqueStructures(table.column(1).data());
    var structuresAcronyms = getUniqueAcronyms(table.column(1).data());
    var specimenLines = table.column(7).data().unique();
    var specimenNames = table.column(8).data().unique();

    autocomplete(document.getElementById("include-name"), structures);
    autocomplete(document.getElementById("include-acron"), structuresAcronyms);
    autocomplete(document.getElementById("include-line"), specimenLines);
    autocomplete(document.getElementById("exclude-name"), structures);
    autocomplete(document.getElementById("exclude-acron"), structuresAcronyms);
    autocomplete(document.getElementById("exclude-line"), specimenLines);

    //
    // Get all ids and copy them
    //
    $('#copy-id-btn').click(function()
    {
        var arrayColumn = getColumn(table, 0);
        var strColumn = "";
        var i = 0
        while(i < arrayColumn.length - 1)
        {
            strColumn += arrayColumn[i] + ';';
            i++;
        }
        strColumn += arrayColumn[i];

        $("#copy-ids-input").val(strColumn);

        $(".copy-ids-group").css("display", "inline"); // show input field
    });

    // https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Interact_with_the_clipboard
    function copyAllIds() {
        var elemToCopy = document.querySelector("#copy-ids-input");

        elemToCopy.select(); // Select the text field
        elemToCopy.setSelectionRange(0, 99999); // For mobile devices
        if (document.execCommand("copy"))
        {
            document.getElementById("label-copy-ids").innerHTML = "link copied";
        }
        else
        {
            document.getElementById("label-copy-ids").innerHTML = "couldn't copy";
        }
    }

    document.querySelector("#copy-ids-input").addEventListener("click", copyAllIds);

    //
    // Apply filters based on url
    //
    if (pageUrl.length > 4 && pageUrl[4].localeCompare("filter") == 0)
    {
        var filter = pageUrl[5].replace(/%22/g, "\"").replace(/%20/g, " ");
        var index = 0;
        while (index < filter.length)
        {
            index++; // go over question mark char

            var filterField = "";
            while (filter[index] != ':' && index < filter.length)
            {
                filterField += filter[index];
                index++;
            }
            index++; // go over double dot char
            index++; // go over quote char

            var value = "";
            while (filter[index] != '"' && index < filter.length)
            {
                value += filter[index];
                index++;
            }
            index++; // go over quote char

            // set value in element id
            if (filterField.includes("select"))
            {
                $("#" + filterField + " option[value=" + value + "]").attr('selected','selected');
            }
            else
            {
                $("#" + filterField).val(value);
                $("#" + filterField).keyup(); // update a slider via text input
            }

            // go to the next filter field
            while (filter[index] != '?' && index < filter.length)
            {
                index++;
            }
        }

        // Apply filters
        document.getElementById('apply').click();
    }
});