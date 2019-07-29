function toggleStrVisInteraction(enableStrInteraction){
    if (enableStrInteraction){
        // enable interaction here
        $("#str-overlay").css("display", "none")
        .css("-webkit-touch-callout", "auto")
        .css("-webkit-user-select", "auto")
        .css("-khtml-user-select", "auto")
        .css("-moz-user-select", "auto")
        .css("-ms-user-select", "auto")
        .css("user-select", "auto");
    }
    else{
        // disable interaction here
        $("#str-overlay").css("display", "table")
        .css("-webkit-touch-callout", "none")
        .css("-webkit-user-select", "none")
        .css("-khtml-user-select", "none")
        .css("-moz-user-select", "none")
        .css("-ms-user-select", "none")
        .css("user-select", "none");
    }
};

function jsmolCrystal(data, parentHtmlId, appletName, supercellOptions) {
    var parentDiv = document.getElementById(parentHtmlId);
    var the_width = parentDiv.offsetWidth - 5;
    var the_height = parentDiv.offsetHeight - 5;

    var Info = {
        width: the_width,
        height: the_height,
        debug: false,
        color: "#FFFFFF",
        use: "HTML5",
        j2sPath: "../static/js/jsmol/j2s",
        serverURL: "../static/js/jsmol/php/jsmol.php",
        console: "jmolApplet_infodiv"
    };

    var jsmolStructureviewer = Jmol.getApplet(appletName, Info);

    if (supercellOptions === undefined){
        var loadingScript = 'color cpk; load INLINE "' + data + '"; wireframe 0.15; spacefill 23%';
    } else {
        var loadingScript = 'color cpk; load INLINE "' + data + '" {' + supercellOptions[0] + ' ' + supercellOptions[1] + ' ' + supercellOptions[2] + '}; wireframe 0.15; spacefill 23%';
    }

    //draw x,y,z axes instead of a,b,c vectors as default
    loadingScript+= '; axes off; draw xaxis ">X" vector {0 0 0} {2 0 0} color red width 0.15; draw yaxis ">Y" vector {0 0 0} {0 2 0} color green width 0.15; draw zaxis ">Z" vector {0 0 0} {0 0 2} color blue width 0.15';

    //do not show info on top left
    loadingScript+= '; unitcell primitive';

    //Sets the unit cell line diameter in Angstroms
    loadingScript+= '; unitcell 2';

    // antialiasDisplay ON
    loadingScript+= '; set antialiasDisplay on';

    //Zooms to the setting that fills the screen with the currently displayed atoms
    loadingScript+= "; set zoomLarge false";

    //remove JSmol logo
    loadingScript+= '; set frank off';

    Jmol.script(jsmolStructureviewer, loadingScript);

    //parentDiv.innerHTML = Jmol.getAppletHtml(jsmolStructureviewer);
    //$("#" + parentHtmlId).html(Jmol.getAppletHtml(jsmolStructureviewer));

    return jsmolStructureviewer;
}

var cellLine = "; unitcell 2";

function toggleRotation(viewer) {
    if ($("#spin-input").is(":checked")){
        var jmolscript = "spin on";
    } else {
        var jmolscript = "spin off";
    }
    Jmol.script(eval(viewer), jmolscript);
    return jmolscript;
};

function showBonds(viewer) {
    if ($("#bonds-input").is(":checked")){
        var jmolscript = "wireframe 0.15";
    } else {
        var jmolscript = "wireframe off";
    }
    Jmol.script(eval(viewer), jmolscript);
    return jmolscript;
};

function showPacked(viewer) {
    var nx = $('#nx').val();
    var ny = $('#ny').val();
    var nz = $('#nz').val();

    if ($("#packed-input").is(":checked")){
        var jmolscript = "save orientation 0; load '' {" + nx + " " + ny + " " + nz + "} packed; unitcell primitive; restore orientation 0" + jsmolDrawAxes(viewer) + cellLine + "; " + showLabels(viewer) + "; " + showBonds(viewer);
    } else {
        var jmolscript = "save orientation 0; load '' {" + nx + " " + ny + " " + nz + "}; unitcell primitive; restore orientation 0" + jsmolDrawAxes(viewer) + cellLine + "; " + showLabels(viewer) + "; " + showBonds(viewer);
    }
    $("#spin-input").prop("checked", false);
    $("#spheres-input").prop("checked", false);
    Jmol.script(eval(viewer), jmolscript);
    return jmolscript;
};

function showLabels(viewer) {
    if ($("#labels-input").is(":checked")){
        var jmolscript = "label %a";
    } else {
        var jmolscript = "label off";
    }
    Jmol.script(eval(viewer), jmolscript);
    return jmolscript;
};

function showSpheres(viewer) {
    if ($("#spheres-input").is(":checked")){
        var jmolscript = "spacefill on";
    } else {
        var jmolscript = "spacefill 23%";
    }
    Jmol.script(eval(viewer), jmolscript);
    return jmolscript;
};

function jsmolDrawAxes(viewer) {
    var e = document.getElementById("axesMenu");
    var selectedAxes = e.options[e.selectedIndex].value;
    switch (selectedAxes){
        case "xyz":
            var jmolscript = "; axes off; draw xaxis '>X' vector {0 0 0} {2 0 0} color red width 0.15; draw yaxis '>Y' vector {0 0 0} {0 2 0} color green width 0.15; draw zaxis '>Z' vector {0 0 0} {0 0 2} color blue width 0.15";
            break;
        case "abc":
            var jmolscript = "; draw xaxis delete; draw yaxis delete; draw zaxis delete; set axesMode 2; axes 5";
            break;
        case "noaxes":
            var jmolscript = "; draw xaxis delete; draw yaxis delete; draw zaxis delete; axes off";
    }
    Jmol.script(eval(viewer), jmolscript);
    return jmolscript;
};

function jsmolSupercell(viewer) {
    var nx = $('#nx').val();
    var ny = $('#ny').val();
    var nz = $('#nz').val();
    $("#spin-input").prop("checked", false);
    $("#spheres-input").prop("checked", false);
    $("#packed-input").prop("checked", false);
    var jmolscript = "save orientation 0; load '' {" + nx + " " + ny + " " + nz + "}; unitcell primitive; restore orientation 0" + jsmolDrawAxes(viewer) + cellLine + "; " + showLabels(viewer) + "; " + showBonds(viewer);
    Jmol.script(eval(viewer), jmolscript);
};

function jsmol222cell(viewer) {
    $("#spin-input").prop("checked", false);
    $("#spheres-input").prop("checked", false);
    $("#packed-input").prop("checked", false);
    // reset nx, ny, nz to 2,2,2
    $('#nx').val(2);
    $('#ny').val(2);
    $('#nz').val(2);
    Jmol.script(eval(viewer), "save orientation 0; load '' {2 2 2}; unitcell primitive; restore orientation 0" + jsmolDrawAxes(viewer) + cellLine + "; " + showLabels(viewer) + "; " + showBonds(viewer));
};

function centerXaxis(viewer){
    Jmol.script(eval(viewer), "moveto 1 axis x");
};

function centerYaxis(viewer){
    Jmol.script(eval(viewer), "moveto 1 axis y");
};

function centerZaxis(viewer){
    Jmol.script(eval(viewer), "moveto 1 axis z");
};

$.fn.bindFirst = function(name, fn) {
    var elem, handlers, i, _len;
    this.bind(name, fn);
    for (i = 0, _len = this.length; i < _len; i++) {
      elem = this[i];
      handlers = jQuery._data(elem).events[name.split('.')[0]];
      handlers.unshift(handlers.pop());
    }
  };

function enableDoubleTap(element, callback, ignoreOnMove) {
    /* Enable double-tap event for phones */
    element.dbltapTimeout = undefined;
    element.shortTap = false;

    var preventOnMove = false;
    if (typeof ignoreOnMove !== 'undefined') {
        preventOnMove = ignoreOnMove;
    }

    // Manual detect of double tap
    //element.addEventListener('touchend', function(event) {
    $(element).bindFirst('touchend', function(event) {
      if (typeof element.dbltapTimeout !== 'undefined') {
          // start disabling any timeout that would reset shortTap to false
          clearTimeout(element.dbltapTimeout);
      }
      if (element.shortTap) {
          // if here, there's been another tap a few ms before
          // reset the variable and do the custom action
          element.shortTap = false;
          event.preventDefault();
          event.stopImmediatePropagation();
          callback();
      }
      else {
          if (event.targetTouches.length != 0) {
              // activate this only when there is only a finger
              // if more than one finger is detected, cancel detection
              // of double tap
              if (typeof element.dbltapTimeout !== 'undefined') {
                  // disable the timeout
                  clearTimeout(element.dbltapTimeout);
                  element.shortTap = false;
              }
            return;
          }
          // If we are here, no tap was recently detected
          // mark that a tap just happened, and start a timeout
          // to reset this
          element.shortTap = true;

          element.dbltapTimeout = setTimeout(function() {
              // after 500ms, reset shortTap to false
              element.shortTap = false;
          }, 500);
      }
  });
  element.addEventListener('touchcancel', function(event) {
      if (typeof element.dbltapTimeout !== 'undefined') {
          // disable the timeout if the touch was canceled
          clearTimeout(element.dbltapTimeout);
          element.shortTap = false;
      }
  });
  if (!preventOnMove) {
        element.addEventListener('touchmove', function(event) {
        if (typeof element.dbltapTimeout !== 'undefined') {
            // disable the timeout if the finger is being moved
            clearTimeout(element.dbltapTimeout);
            element.shortTap = false;
        }
    });  
  }
}
