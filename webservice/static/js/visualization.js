function toggleStrVisInteraction(enableStrInteraction){
    if (enableStrInteraction){
        // enable interaction here
        $("#str-overlay").css("display", "none");
        $("#crystal").css('pointer-events', 'auto');
        enableStrInteraction = false;
    }
    else{
        // disable interaction here
        $("#str-overlay").css("display", "table");
        $("#crystal").css('pointer-events', 'none');
        enableStrInteraction = true;
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