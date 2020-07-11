/**
 * Global variables
 */
// table
var table;

// include filters:
var includeNames = [""];
var includeAcronyms = [""];
var includePrimNames = [""];
var includePrimAcronyms = [""];
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
var includeContainsPrimNameFilter = false;
var includeContainsPrimAcronFilter = false;
var includeContainsProdFilter = false;
var includeContainsLineFilter = false;

// exclude filters:
var excludeNames = [""];
var excludeAcronyms = [""];
var excludePrimNames = [""];
var excludePrimAcronyms = [""];
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
var excludeContainsPrimNameFilter = false;
var excludeContainsPrimAcronFilter = false;
var excludeContainsProdFilter = false;
var excludeContainsLineFilter = false;

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

// TODO Seems to kinda break if there is too many columns. fix?
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
 * Gets structure without the acronym from a line in the datatable
 */
function getStructure(str)
{
    var indexBeforeAcron = str.lastIndexOf("(");
    if (indexBeforeAcron < 0)
    {
        return "";
    }
    return str.substring(0, indexBeforeAcron).trim();
}

/*
 * Gets all the unique structures without the acronym from the column of the datatable
 */
function getStructures(column)
{
    var array = new Array(column.length);
    for (i = 0; i < column.length; i++)
    {
        array[i] = getStructure(column[i]);
    }
    return array;
}

/*
 * Get the acronym from a line in the datatable
 */
function getAcronym(str)
{
    var indexAcronStarts = str.lastIndexOf("(") + 1;
    var indexAcronEnds = str.lastIndexOf(")");
    if (indexAcronStarts <= indexAcronEnds)
    {
        return str.substring(indexAcronStarts, indexAcronEnds).trim();
    }
    return "";
}

/*
 * Gets all the unique acronym from the column of the datatable
 */
function getAcronyms(column)
{
    var array = new Array(column.length);
    for (i = 0; i < column.length; i++)
    {
        array[i] = getAcronym(column[i]);
    }
    return array;
}

/*
 * Takes the values separated by ',' between parentheses and return it as an array
 */
function parseParenthesesToArray(str)
{
    var noParentheses = str.substring(str.indexOf("(") + 1, str.indexOf(")"));
    var trimWhiteSpace = noParentheses.replace(", ", ",");
    return trimWhiteSpace.split(",");
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

function copyColumnToClipboard(columnNumber)
{
    var arrayColumn = getColumn(table, columnNumber);
    var strColumn = "";
    var i = 0
    while(i < arrayColumn.length - 1)
    {
        strColumn += arrayColumn[i] + ';';
        i++;
    }
    strColumn += arrayColumn[i];

    // Create a temporary input field
    let input = document.createElement('input');
    input.value = strColumn;
    document.body.appendChild(input);

    // Select the text field
    input.select();
    input.setSelectionRange(0, 99999); /*For mobile devices*/

    // Copy the text inside the text field
    document.execCommand("copy");

    // Remove the temporary field
    document.body.removeChild(input);

    alert("ids copied to clipboard.");
}

/*
 * Based on https://www.w3schools.com/howto/howto_js_copy_clipboard.asp
 * Copy field value to clipboard
*/
function copy(field_id) {
    /* Get the text field */
    var copyText = document.getElementById(field_id);

    /* Select the text field */
    copyText.select();
    copyText.setSelectionRange(0, 99999); /*For mobile devices*/

    /* Copy the text inside the text field */
    document.execCommand("copy");
}

/* Custom filtering function which will validate each lines */
$.fn.dataTable.ext.search.push
(
    function(settings, data, dataIndex)
    {
        var columnStruct = data[1];
        var columnPrimStruct = data[2];
        var columnProduct = data[3];
        var columnVolume = parseFloat(data[4]) || 0;
        var location = parseParenthesesToArray(data[5]);
        var x = parseInt(location[0]);
        var y = parseInt(location[1]);
        var z = parseInt(location[2]);
        var columnline = data[6];
        var columnSpecName = data[7];
        var columnGender = data[8];
        var columnCre = data[9];

        if
        (
            validateMinMax(columnVolume, includeMinVol, includeMaxVol, excludeMinVol, excludeMaxVol) &&
            validateMinMax(x, includeMinX, includeMaxX, excludeMinX, excludeMaxX) &&
            validateMinMax(y, includeMinY, includeMaxY, excludeMinY, excludeMaxY) &&
            validateMinMax(z, includeMinZ, includeMaxZ, excludeMinZ, excludeMaxZ) &&
            validateSelect(columnGender, includeGender) &&
            validateSelect(columnCre, includeCre) &&
            (
                (! includeContainsNameFilter && ! includeContainsAcronFilter) ||
                validateText(includeNames, getStructure(columnStruct)) ||
                validateText(includeAcronyms, getAcronym(columnStruct))
            )
            &&
            (
                (! excludeContainsNameFilter && ! excludeContainsAcronFilter) ||
                ! (
                    validateText(excludeNames, getStructure(columnStruct)) ||
                    validateText(excludeAcronyms, getAcronym(columnStruct))
                )
            )
            &&
            (
                (! includeContainsPrimNameFilter && ! includeContainsPrimAcronFilter) ||
                validateText(includePrimNames, getStructure(columnPrimStruct)) ||
                validateText(includePrimAcronyms, getAcronym(columnPrimStruct))
            )
            &&
            (
                (! excludeContainsPrimNameFilter && ! excludeContainsPrimAcronFilter) ||
                ! (
                    validateText(excludePrimNames, getStructure(columnPrimStruct)) ||
                    validateText(excludePrimAcronyms, getAcronym(columnPrimStruct))
                )
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
                validateText(includeLines, columnline)
            )
            &&
            (
                ! excludeContainsLineFilter ||
                ! validateText(excludeLines, columnline)
            )
        )
        {
            return true;
        }
        return false;
    }
);

$(document).ready(function ()
{
    var page_url = window.location.href;
    console.log(page_url);

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
        "scrollX": true
    });

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

        // expected starting and ending point for drawing lines in canvas:
        var coronalAxisX = [20, 161];
        var coronalAxisY = [48, 145];
        var sagittalAxisX = [202, 390];
        var sagittalAxisY = [45, 145];
        var horizontalAxisX = [448, 578];
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
            $("#include-lower").val(ui.values[0]);
            $("#include-higher").val(ui.values[1]);
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
    $("#include-lower").val($("#include-slider-range-height").slider("values", 0));
    $("#include-higher").val($("#include-slider-range-height").slider("values", 1));
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

    $("#include-lower").keyup(function()
    {
        var val = parseInt($("#include-lower").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#include-slider-range-height").slider("values", 1))
        {
            $("#include-slider-range-height").slider("values", 0, val);
            drawSliders(true);
        }
    });

    $("#include-higher").keyup(function()
    {
        var val = parseInt($("#include-higher").val(), 10);
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
            $("#exclude-lower").val(ui.values[0]);
            $("#exclude-higher").val(ui.values[1]);
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
    $("#exclude-lower").val($("#exclude-slider-range-height").slider("values", 0));
    $("#exclude-higher").val($("#exclude-slider-range-height").slider("values", 1));
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

    $("#exclude-lower").keyup(function()
    {
        var val = parseInt($("#exclude-lower").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#exclude-slider-range-height").slider("values", 1))
        {
            $("#exclude-slider-range-height").slider("values", 0, val);
            drawSliders(false);
        }
    });

    $("#exclude-higher").keyup(function()
    {
        var val = parseInt($("#exclude-higher").val(), 10);
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

        includePrimNames = $('#include-prim-name').val().split(";");
        includeContainsPrimNameFilter = false;
        for (i = 0; i < includePrimNames.length; i++)
        {
            if (includePrimNames[i].trim() != "")
            {
                includeContainsPrimNameFilter = true;
                break;
            }
        }

        includePrimAcronyms = $('#include-prim-acron').val().split(";");
        includeContainsPrimAcronFilter = false;
        for (i = 0; i < includePrimAcronyms.length; i++)
        {
            if (includePrimAcronyms[i].trim() != "")
            {
                includeContainsPrimAcronFilter = true;
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

        excludePrimNames = $('#exclude-prim-name').val().split(";");
        excludeContainsPrimNameFilter = false;
        for (i = 0; i < excludePrimNames.length; i++)
        {
            if (excludePrimNames[i].trim() != "")
            {
                excludeContainsPrimNameFilter = true;
                break;
            }
        }

        excludePrimAcronyms = $('#exclude-prim-acron').val().split(";");
        excludeContainsPrimAcronFilter = false;
        for (i = 0; i < excludePrimAcronyms.length; i++)
        {
            if (excludePrimAcronyms[i].trim() != "")
            {
                excludeContainsPrimAcronFilter = true;
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

        excludeMinVol = parseFloat($('#exclude-min-vol').val(), 10);
        excludeMaxVol = parseFloat($('#exclude-max-vol').val(), 10);
        excludeMinX = parseInt($("#exclude-slider-range-depth").slider("values", 0), 10);
        excludeMaxX = parseInt($("#exclude-slider-range-depth").slider("values", 1), 10);
        excludeMinY = parseInt($("#exclude-slider-range-height").slider("values", 0), 10);
        excludeMaxY = parseInt($("#exclude-slider-range-height").slider("values", 1), 10);
        excludeMinZ = parseInt($("#exclude-slider-range-width").slider("values", 0), 10);
        excludeMaxZ = parseInt($("#exclude-slider-range-width").slider("values", 1), 10);
        console.log(page_url);
        // redraw table
        table.draw();
    });

    // columns visibilty in datatable
    $('.toggle-vis').on('click', function(e)
    {
        // Get the column API object
        var column = table.column($(this).attr('data-column'));

        // Toggle the visibility
        column.visible(! column.visible());
    });

    var structures = getStructures(table.column(1).data().unique());
    var structuresAcronyms = getAcronyms(table.column(1).data().unique());
    var primStructures = getStructures(table.column(2).data().unique());
    var primStructuresAcronyms = getAcronyms(table.column(2).data().unique());
    var specimenLines = table.column(6).data().unique();
    var specimenNames = table.column(7).data().unique();

    autocomplete(document.getElementById("include-name"), structures);
    autocomplete(document.getElementById("include-acron"), structuresAcronyms);
    autocomplete(document.getElementById("include-prim-name"), primStructures);
    autocomplete(document.getElementById("include-prim-acron"), primStructuresAcronyms);
    autocomplete(document.getElementById("include-line"), specimenLines);
    autocomplete(document.getElementById("exclude-name"), structures);
    autocomplete(document.getElementById("exclude-acron"), structuresAcronyms);
    autocomplete(document.getElementById("exclude-prim-name"), primStructures);
    autocomplete(document.getElementById("exclude-prim-acron"), primStructuresAcronyms);
    autocomplete(document.getElementById("exclude-line"), specimenLines);
});