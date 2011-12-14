"use strict";

//default msn for folding
var default_msn = '2412';


//add indexOf function to IE
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (searchElement /*, fromIndex */ ) {
        if (this === void 0 || this === null) {
            throw new TypeError();
        }
        var t = Object(this);
        var len = t.length >>> 0;
        if (len === 0) {
            return -1;
        }
        var n = 0;
        if (arguments.length > 0) {
            n = Number(arguments[1]);
            if (n !== n) { // shortcut for verifying if it's NaN
                n = 0;
            } else if (n !== 0 && n !== Infinity && n !== -Infinity) {
                n = (n > 0 || -1) * Math.floor(Math.abs(n));
            }
        }
        if (n >= len) {
            return -1;
        }
        var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);
        for (; k < len; k++) {
            if (k in t && t[k] === searchElement) {
                return k;
            }
        }
        return -1;
    };
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
  var duid = this.href.split("#")[1];
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


function initial_fold() {
  var msn = get_active_msn();
  for(var i=0; i<folding.length; i++) {
    var du_container = folding[i];
    var tagdiv = document.getElementById("duid" + du_container[0][0]).parentNode.firstChild;
    var tags = tagdiv.children;
    for(var k=0;k<tags.length;k++) {
      tags[k].onclick = change_tab;
    }
    for(var j=0; j<du_container.length; j++) {
      var du = du_container[j];
      var msn_found = du[1].indexOf(msn);
      if(msn_found == -1) {
        var ob = document.getElementById("duid" + du[0]);
        ob.className = ob.className.replace(new RegExp("main"), "alternate folded");
      }
      else {
        for(k=0; k<tags.length; k++) {
          if(tags[k].href.split("#duid")[1] == du[0]) {
            tags[k].className = "main active";
            break;
          }
        }
        if(k != 0) {
          var main_tag = tagdiv.removeChild(tags[k]);
          tagdiv.insertBefore(main_tag, tagdiv.firstChild);
        }
      }
    }
  }
  add_eventlisteners();
  //With long pages the ...#duid... url was jumping to the wrong place - force
  //it into view after processing is complete
  var linkjump = window.location.hash.slice(1);
  if (linkjump) {
    var targetElement = document.getElementById(linkjump);
    targetElement.scrollIntoView();
  }


}


function toggle_applies(ob) {
  if(!ob.parentNode.style.whiteSpace || ob.parentNode.style.whiteSpace == "nowrap") {
    ob.parentNode.style.whiteSpace = "normal";
    ob.childNodes[0].src = "../images/minus.gif";
  }
  else {
    ob.parentNode.style.whiteSpace = "nowrap";
    ob.childNodes[0].src = "../images/plus.gif";
  }

  return false;
}


function toggle_folded(ob)
{
  //this is the folding for index pages
  //the click is received in the anchors context, so change img src below and next section
  var img_ob = ob.childNodes[0];
  var section = ob.parentNode.nextSibling;
  if(section.className.indexOf("folded") != -1) {
    img_ob.src = "../images/minus.gif";
    section.className = section.className.replace(new RegExp(" folded\\b"), "");
  }
  else {
    img_ob.src = "../images/plus.gif";
    section.className += " folded";
  }
  return false;
}


function get_active_msn() {
  var msn = default_msn;
  try {
    if(window.localStorage["active_msn"])
      msn = window.localStorage["active_msn"];
  }
  catch(e) {
    if(window.console)
      console.log("Failed to find active_msn in localStorage; using default of " + msn);
  }
  return msn;
}


function set_folding_reg() {
  var reg_ob = document.getElementById("folding_reg");
  var label = fleet[get_active_msn()];
  if(reg_ob.textContent != undefined)
      reg_ob.textContent = label;
    else //fix for IE
      reg_ob.innerText = label;

}


function set_active_msn(msn) {
  try {
    window.localStorage["active_msn"] = msn;
    alert("Pre-folding MSN now set to " + msn);
    return true;
  }
  catch(e) {
    var message = "Unfortunately it appears that local storage is not available.\n\n";
    if(window.location.protocol.slice(0,4) == "file") {
      message += "Many browsers do not support local storage with the file:// " +
      "protocol for security reasons.";
    }
    else {
      message += "Please try a more modern browser.";
    }
    alert(message);
    return false;
  }
}


function change_reg(ob) {
  var new_reg = document.getElementById("new_reg").value.toUpperCase();
  var msn = "";
  for(var p in fleet) {
    if(fleet[p] == new_reg) {
      msn = p;
      break;
    }
  }
  if (!msn) {
    alert("Could not find " + new_reg);
  }
  else {
    set_active_msn(msn);
  }
  return false;
}


function add_eventlisteners() {
  //adds an click handler to all ducontainer and infocontainer divs - apparently
  //this triggers correct hover behaviour on iDevices
  var divs = document.getElementsByTagName("div");
  for(var c=0; c<divs.length; c++) {
    if(divs[c].className == "infocontainer" || divs[c].className == "du_container") {
      divs[c].onclick = on_div_click;
    }
  }
}


function on_div_click(mouse_event) {
  if(this.className == "du_container" && mouse_event.ctrlKey && this.firstChild.className == "tags") {
    var tags = this.firstChild.childNodes;
    var active_tag = 0;
    for(var i=0; i<tags.length; i++) {
      if(tags[i].className.indexOf("active") != -1) {
        active_tag = i;
      }
      tags[i].className = tags[i].className.replace(new RegExp(" active\\b"), "");
    }
    if(mouse_event.shiftKey){
      active_tag -= 1;
      if(active_tag == -1) {
        active_tag += tags.length;
      }
    }
    else {
      active_tag += 1;
      if(active_tag == tags.length) {
        active_tag = 0;
      }
    }
    tags[active_tag].className += " active";
    //get id of du to unfold
    var duid = tags[active_tag].href.split("#")[1];
    //fold as required
    var du = this.childNodes[1];
    while(du) {
      if(du.id == duid)
        du.className = du.className.replace(new RegExp(" folded\\b"), "");
      else if(du.className.indexOf("folded") == -1) {
        du.className += " folded";
      }
      du = du.nextSibling;
    }
  }
  return true;
}