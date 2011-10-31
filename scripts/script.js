function hidedu(ob) {
  ob.className += " folded";
}


function showdu(ob) {
  ob.className = ob.parentNode.className.replace(new RegExp(" folded\\b"), "");
}


function insert_tabs(tabs) {
  console.log(tabs);
}


function initial_fold() {
  var msn = '2412';
  for(var i=0; i<folding.length; i++) {
    var du_container = folding[i];
    var tabs = [];
    for(var j=0; j<du_container.length; j++) {
      var du = du_container[j];
      var msn_found = du[1].indexOf(msn);
      if(msn_found == -1) {
        var ob = document.getElementById("duid" + du[0]);
        ob.className = "alternate";
        hidedu(ob);
        tabs.push({linkend:du[0], label:du[2]});
      }
      else {
        tabs.unshift({linkend:du[0], label:du[2]});
      }
    }
    insert_tabs(tabs);
  }
}