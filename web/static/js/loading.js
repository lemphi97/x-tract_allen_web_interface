"use_strict";

var nbAjaxReq = 0;

var loadingGif = document.createElement("IMG");
loadingGif.src = "/static/img/wip.gif";
loadingGif.style.display = "none";
loadingGif.style.position = "fixed";
loadingGif.style.top = "4px";
loadingGif.style.right = "4px";

document.body.appendChild(loadingGif);

function newRequest()
{
    nbAjaxReq++;
    loadingGif.style.display = "inline";
}

function requestOver()
{
    nbAjaxReq--;
    if (nbAjaxReq == 0)
    {
        loadingGif.style.display = "none";
    }
}

