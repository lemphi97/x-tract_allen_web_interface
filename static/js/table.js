// based on: https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_autocomplete
function autocomplete(inp, arr)
{
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e)
    {
        var a, b, i, val = this.value;
        var lastVal = val.substring(this.value.lastIndexOf(";") + 1, this.value.length).trim();
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!lastVal)
        {
            return false;
        }
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/
        for (i = 0; i < arr.length; i++)
        {
            /*check if the item starts with the same letters as the text field value:*/
            if (arr[i].substr(0, lastVal.length).toUpperCase() == lastVal.toUpperCase())
            {
                /*create a DIV element for each matching element:*/
                b = document.createElement("DIV");
                /*make the matching letters bold:*/
                b.innerHTML = "<strong>" + arr[i].substr(0, lastVal.length) + "</strong>";
                b.innerHTML += arr[i].substr(lastVal.length, arr[i].length);
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function(e)
                {
                    /*insert the value for the autocomplete text field:*/
                    var addedVal = this.getElementsByTagName("input")[0].value;
                    var lastSeparation = val.lastIndexOf(";");
                    if (lastSeparation < 0)
                    {
                        inp.value = addedVal;
                    }
                    else
                    {
                        var prevVal = val.substring(0, lastSeparation);
                        inp.value = prevVal + "; " + addedVal;
                    }

                    $('#' + inp.id).keyup();

                    /*close the list of autocompleted values,
                    (or any other open lists of autocompleted values:*/
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });

    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e)
    {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40)
        {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        }
        else if (e.keyCode == 38)
        { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        }
        else if (e.keyCode == 13)
        {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1)
            {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });

    function addActive(x)
    {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(x)
    {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++)
        {
            x[i].classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(elmnt)
    {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++)
        {
            if (elmnt != x[i] && elmnt != inp)
            {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }

    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e)
    {
        closeAllLists(e.target);
    });
}

/*
 * Gets hemisphere without the acronym from a line in the datatable
 */
function getHemisphere(str)
{
    var indexBeforeAcron = str.lastIndexOf("(");
    if (indexBeforeAcron < 0)
    {
        return "";
    }
    return str.substring(0, indexBeforeAcron).trim();
}

/*
 * Gets all the unique hemisphere without the acronym from the column of the datatable
 */
function getHemispheres(column)
{
    var array = new Array(column.length);
    for (i = 0; i < column.length; i++)
    {
        array[i] = getHemisphere(column[i]);
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

/*
 * Check if the name str is part of the allowed names
 */
function validateNames(names, name)
{
    var valid = true;
    if (! caseInsensitiveArrayInclude(names, name))
    {
        valid = false;
    }
    return valid;
}

/*
 * Check if the acronym str is part of the allowed acronyms
 */
function validateAcronyms(acronyms, acronym)
{
    var valid = true;
    if (! caseInsensitiveArrayInclude(acronyms, acronym))
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


$(document).ready(function ()
{
    // activate datatable
    var table = $('#experiments').DataTable({
        "scrollX": true
    });

    var hemispheres = getHemispheres(table.column(1).data().unique());
    var hemispheresAcronyms = getAcronyms(table.column(1).data().unique());

    // columns visibilty in datatable
    $('.toggle-vis').on('click', function(e)
    {
        // Get the column API object
        var column = table.column($(this).attr('data-column'));

        // Toggle the visibility
        column.visible(! column.visible());
    });

    // Event listener to the two range filtering inputs to redraw on input
    $('#name, #acron,' +
      '#prod-id,' +
      '#min-vol, #max-vol,' +
      '#min-x, #max-x,' +
      '#min-y, #max-y,' +
      '#min-z, #max-z').keyup(function()
    {
        /* Custom filtering function which will validate each lines */
        $.fn.dataTable.ext.search.push
        (
            function(settings, data, dataIndex)
            {
                // hemisphere section
                var names = $('#name').val().split(";");
                var acronyms = $('#acron').val().split(";");
                var hemi = data[1];

                // product id
                var products = $('#prod-id').val().split(";");
                var prod = data[2];

                // injection volume
                var minVol = parseFloat($('#min-vol').val(), 10);
                var maxVol = parseFloat($('#max-vol').val(), 10);
                var volume = parseFloat(data[3]) || 0;

                // injection location
                var minX = parseInt($('#min-x').val(), 10);
                var maxX = parseInt($('#max-x').val(), 10);
                var minY = parseInt($('#min-y').val(), 10);
                var maxY = parseInt($('#max-y').val(), 10);
                var minZ = parseInt($('#min-z').val(), 10);
                var maxZ = parseInt($('#max-z').val(), 10);
                var location = parseParenthesesToArray(data[4]);
                var x = parseInt(location[0]);
                var y = parseInt(location[1]);
                var z = parseInt(location[2]);

                if
                (
                    validateMinMax(volume, minVol, maxVol) &&
                    validateMinMax(x, minX, maxX) &&
                    validateMinMax(y, minY, maxY) &&
                    validateMinMax(z, minZ, maxZ)
                )
                {
                    // THIS PART IS EXECUTED FOR EVERYLINE WHILE WE ONLY NEED IT ONCE, to investigate...
                    var containsNameFilter = false;
                    var containsAcronFilter = false;
                    var containsProdFilter = false;
                    for (i = 0; i < names.length; i++)
                    {
                        if (names[i].trim() != "")
                        {
                            containsNameFilter = true;
                            break;
                        }
                    }
                    for (i = 0; i < acronyms.length; i++)
                    {
                        if (acronyms[i].trim() != "")
                        {
                            containsAcronFilter = true;
                            break;
                        }
                    }
                    for (i = 0; i < products.length; i++)
                    {
                        if (products[i].trim() != "")
                        {
                            containsProdFilter = true;
                            break;
                        }
                    }
                    if
                    (
                        (
                            (! containsNameFilter && ! containsAcronFilter) ||
                            validateNames(names, getHemisphere(hemi)) ||
                            validateAcronyms(acronyms, getAcronym(hemi))
                        )
                        &&
                        (
                            ! containsProdFilter ||
                            validateProducts(products, prod)
                        )
                    )
                    return true;
                }
                return false;
            }
        );

        table.draw();
    });

    autocomplete(document.getElementById("name"), hemispheres);
    autocomplete(document.getElementById("acron"), hemispheresAcronyms);
});