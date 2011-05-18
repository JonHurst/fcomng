function hidedu(ob)
{
    ob.parentNode.className += " folded"
}

function showdu(ob)
{
    ob.parentNode.className = ob.parentNode.className.replace(new RegExp(" folded\\b"), "");
}
