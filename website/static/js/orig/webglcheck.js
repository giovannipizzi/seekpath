/*
  Note: this code has been adapted from get.webgl.org
*/
    /**/
var startWebGLCheck = function() {
    function $$(x) {
        return document.getElementById(x);
    }

    // Add indexOf to IE.
    if(!Array.indexOf){
        Array.prototype.indexOf = function(obj){
            for(var i=0; i<this.length; i++){
                if(this[i]==obj){
                    return i;
                }
            }
            return -1;
        }
    }

    var canvas, gl;

    function removeClass(element, clas) {
        // Does not work in IE var classes = element.getAttribute("class");
        var classes = element.className;
        if (classes) {
            var cs = classes.split(/\s+/);
            if (cs.indexOf(clas) != -1) {
                cs.splice(cs.indexOf(clas), 1);
            }
            // Does not work in IE element.setAttribute("class", cs.join(" "));
            element.className = cs.join(" ");
        }
    }

    function addClass(element, clas) {
        element.className = element.className + " " + clas;
    }

    function pageLoaded() {
        removeClass($$("have-javascript"), "webgl-hidden");

        // I moved an equivalent call in the <body> to have the div disappear
        // ASAP
        
        // addClass($$("no-javascript"), "webgl-hidden");
        canvas = document.getElementById("webgl-logo");
        var ratio = (window.devicePixelRatio ? window.devicePixelRatio : 1);
        canvas.width = 1 * ratio; // replace 1 with the width you want as specified in the HTML
        canvas.height = 1 * ratio; // replace 1 with the height you want as specified in the HTML
        var experimental = false;
        try { gl = canvas.getContext("webgl"); }
        catch (x) { gl = null; }

        if (gl == null) {
            try { gl = canvas.getContext("experimental-webgl"); experimental = true; }
            catch (x) { gl = null; }
        }

        if (gl) {
            // hide/show phrase for webgl-experimental
            $$("webgl-experimental").style.display = experimental ? "auto" : "none";

            // show webgl supported div, and launch webgl demo
            removeClass($$("webgl-yes"), "webgl-hidden");
        } else if ("WebGLRenderingContext" in window) {
            // not a foolproof way to check if the browser
            // might actually support WebGL, but better than nothing
            removeClass($$("webgl-disabled"), "webgl-hidden");
        } else {
            // Show the no webgl message.
            removeClass($$("webgl-no"), "webgl-hidden");
        }
        // In any case, hide the canvas since I don't want to show a logo
        addClass($$("webgl-logo"), "webgl-hidden");
    }

    // addEventListener does not work on IE7/8.
    window.onload = pageLoaded;
}