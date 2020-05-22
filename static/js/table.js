function parseParenthesesToArray(str)
{
    var noParentheses = str.substring(str.indexOf("(") + 1, str.indexOf(")"));
    var trimWhiteSpace = noParentheses.replace(", ", ",");
    return trimWhiteSpace.split(",");
}

function validateMinMax(value, min, max)
{
    return (isNaN(min) && isNaN(max)) ||
           (isNaN(min) && value <= max) ||
           (min <= value && isNaN(max)) ||
           (min <= value && value <= max);
}

function validateNames(str, arrayName)
{
    // TODO
    var valid = true;
    return true;
}

function validateAcronyms(str, arrayAcron)
{
    // TODO
    var valid = true;
    return valid;
}