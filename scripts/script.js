function hidedu(ob) {
  ob.className += " folded";
}


function showdu(ob) {
  ob.className = ob.parentNode.className.replace(new RegExp(" folded\\b"), "");
}


function change_tab(event) {
  event = event || window.event;
  //remove active from all siblings
  var siblings = this.parentNode.childNodes;
  for(var i=0; i<siblings.length; i++) {
    siblings[i].className = siblings[i].className.replace(new RegExp(" active\\b"), "");
  }
  //set this node as active
  this.className += " active";
  //get id of du to unfold
  var duid = "duid" + this.href.split("#")[1];
  console.log(duid);
  //fold as required
  var du = this.parentNode.nextSibling;
  while(du) {
    if(du.id == duid)
      du.className = du.className.replace(new RegExp(" folded\\b"), "");
    else if(du.className.indexOf("folded") == -1) {
      du.className += " folded";
    }
    du = du.nextSibling;
  }
  this.blur();
  return false;
}


function insert_tabs(tabs) {
  var tagdiv = document.createElement("div");
  tagdiv.className = "tags";
  var class_string = "main active";
  var label_length = 80/tabs.length;
  for(var i=0; i<tabs.length; i++) {
    var anchor = document.createElement("a");
    anchor.setAttribute("href", "#" + tabs[i].linkend);
    anchor.className = class_string;
    anchor.onclick = change_tab;
    var label = tabs[i].label.slice(0, label_length);
    if(label.length < tabs[i].label.length) {
      label = label.slice(0, -1) + "\u2026";
    }
    anchor.textContent = label;
    tagdiv.appendChild(anchor);
    class_string = "alternate";
  }
  //find du container
  console.log(tagdiv.innerHTML);
  var du_container = document.getElementById("duid" + tabs[0].linkend).parentNode;
  du_container.insertBefore(tagdiv, du_container.firstChild);
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