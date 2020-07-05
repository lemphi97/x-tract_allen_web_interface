/**
 * Global variables
 */
// For filters:
var names = [""];
var acronyms = [""];
var primNames = [""];
var primAcronyms = [""];
var products = [""];
var lines = [""];
var minVol = "NaN";
var maxVol = "NaN";
var minX = "NaN";
var maxX = "NaN";
var minY = "NaN";
var maxY = "NaN";
var minZ = "NaN";
var maxZ = "NaN";
var gender = "ANY";
var cre = "ANY";
var containsNameFilter = false;
var containsAcronFilter = false;
var containsPrimNameFilter = false;
var containsPrimAcronFilter = false;
var containsProdFilter = false;
var containsLineFilter = false;
// table
var table;

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
        if (array[i].trim().toUpperCase().localeCompare(str.toUpperCase()) == 0)
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

function validateProducts(products, product)
{
    var valid = true;
    if (! caseInsensitiveArrayInclude(products, product))
    {
        valid = false;
    }
    return valid;
}

/*
 * return true if value is between min and max
 */
function validateMinMax(value, min, max)
{
    return (isNaN(min) && isNaN(max)) ||
           (isNaN(min) && value <= max) ||
           (min <= value && isNaN(max)) ||
           (min <= value && value <= max);
}

/*
 * return true if value match allowedValue
 */
function validateSelect(allowedValue, value)
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
            validateMinMax(columnVolume, minVol, maxVol) &&
            validateMinMax(x, minX, maxX) &&
            validateMinMax(y, minY, maxY) &&
            validateMinMax(z, minZ, maxZ) &&
            validateSelect(gender, columnGender) &&
            validateSelect(cre, columnCre) &&
            (
                (! containsNameFilter && ! containsAcronFilter) ||
                validateText(names, getStructure(columnStruct)) ||
                validateText(acronyms, getAcronym(columnStruct))
            )
            &&
            (
                (! containsPrimNameFilter && ! containsPrimAcronFilter) ||
                validateText(primNames, getStructure(columnPrimStruct)) ||
                validateText(primAcronyms, getAcronym(columnPrimStruct))
            )
            &&
            (
                ! containsProdFilter ||
                validateProducts(products, columnProduct)
            )
            &&
            (
                ! containsLineFilter ||
                validateText(lines, columnline)
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

    // activate datatable
    table = $('#experiments').DataTable(
    {
        "scrollX": true
    });

    $("#slider-range-depth").slider(
    {
        range: true,
        min: 0,
        max: depth_max,
        values: [0, depth_max],
        slide: function(event, ui)
        {
            $("#anterior").val(ui.values[0])
            $("#posterior").val(ui.values[1]);
        }
    });

    $("#slider-range-height").slider(
    {
        range: true,
        min: 0,
        max: height_max,
        values: [0, height_max],
        slide: function(event, ui)
        {
            $("#lower").val(ui.values[0])
            $("#higher").val(ui.values[1]);
        }
    });

    $("#slider-range-width").slider(
    {
        range: true,
        min: 0,
        max: width_max,
        values: [0, width_max],
        slide: function(event, ui)
        {
            $("#left").val(ui.values[0])
            $("#right").val(ui.values[1]);
        }
    });

    $("#anterior").val($("#slider-range-depth").slider("values", 0));
    $("#posterior").val($("#slider-range-depth").slider("values", 1));
    $("#lower").val($("#slider-range-height").slider("values", 0));
    $("#higher").val($("#slider-range-height").slider("values", 1));
    $("#left").val($("#slider-range-width").slider("values", 0));
    $("#right").val($("#slider-range-width").slider("values", 1));

    $("#anterior").keyup(function()
    {
        var val = parseInt($("#anterior").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#slider-range-depth").slider("values", 1))
        {
            $("#slider-range-depth").slider("values", 0, val);
        }
    });

    $("#posterior").keyup(function()
    {
        var val = parseInt($("#posterior").val(), 10);
        if (!isNaN(val) &&
            val <= depth_max &&
            val >= $("#slider-range-depth").slider("values", 0))
        {
            $("#slider-range-depth").slider("values", 1, val);
        }
    });

    $("#lower").keyup(function()
    {
        var val = parseInt($("#lower").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#slider-range-height").slider("values", 1))
        {
            $("#slider-range-height").slider("values", 0, val);
        }
    });

    $("#higher").keyup(function()
    {
        var val = parseInt($("#higher").val(), 10);
        if (!isNaN(val) &&
            val <= height_max &&
            val >= $("#slider-range-height").slider("values", 0))
        {
            $("#slider-range-height").slider("values", 1, val);
        }
    });

    $("#left").keyup(function()
    {
        var val = parseInt($("#left").val(), 10);
        if (!isNaN(val) &&
            val >= 0 &&
            val <= $("#slider-range-width").slider("values", 1))
        {
            $("#slider-range-width").slider("values", 0, val);
        }
    });

    $("#right").keyup(function()
    {
        var val = parseInt($("#right").val(), 10);
        if (!isNaN(val) &&
            val <= width_max &&
            val >= $("#slider-range-width").slider("values", 0))
        {
            $("#slider-range-width").slider("values", 1, val);
        }
    });

    /*
     * Event listener on input to filter table and re-draw it
     */

    $('#apply').click(function()
    {
        names = $('#name').val().split(";");
        containsNameFilter = false;
        for (i = 0; i < names.length; i++)
        {
            if (names[i].trim() != "")
            {
                containsNameFilter = true;
                break;
            }
        }

        acronyms = $('#acron').val().split(";");
        containsAcronFilter = false;
        for (i = 0; i < acronyms.length; i++)
        {
            if (acronyms[i].trim() != "")
            {
                containsAcronFilter = true;
                break;
            }
        }

        primNames = $('#prim-name').val().split(";");
        containsPrimNameFilter = false;
        for (i = 0; i < primNames.length; i++)
        {
            if (primNames[i].trim() != "")
            {
                containsPrimNameFilter = true;
                break;
            }
        }

        primAcronyms = $('#prim-acron').val().split(";");
        containsPrimAcronFilter = false;
        for (i = 0; i < primAcronyms.length; i++)
        {
            if (primAcronyms[i].trim() != "")
            {
                containsPrimAcronFilter = true;
                break;
            }
        }

        products = $('#prod-id').val().split(";");
        containsProdFilter = false;
        for (i = 0; i < products.length; i++)
        {
            if (products[i].trim() != "")
            {
                containsProdFilter = true;
                break;
            }
        }

        lines = $('#line').val().split(";");
        containsLineFilter = false;
        for (i = 0; i < lines.length; i++)
        {
            if (lines[i].trim() != "")
            {
                containsLineFilter = true;
                break;
            }
        }

        minVol = parseFloat($('#min-vol').val(), 10);
        maxVol = parseFloat($('#max-vol').val(), 10);
        minX = parseInt($("#slider-range-depth").slider("values", 0), 10);
        maxX = parseInt($("#slider-range-depth").slider("values", 1), 10);
        minY = parseInt($("#slider-range-height").slider("values", 0), 10);
        maxY = parseInt($("#slider-range-height").slider("values", 1), 10);
        minZ = parseInt($("#slider-range-width").slider("values", 0), 10);
        maxZ = parseInt($("#slider-range-width").slider("values", 1), 10);

        gender = $('#gender-select').val();
        cre = $('#cre-select').val();

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

    autocomplete(document.getElementById("name"), structures);
    autocomplete(document.getElementById("acron"), structuresAcronyms);
    autocomplete(document.getElementById("prim-name"), primStructures);
    autocomplete(document.getElementById("prim-acron"), primStructuresAcronyms);
    autocomplete(document.getElementById("line"), specimenLines);
});