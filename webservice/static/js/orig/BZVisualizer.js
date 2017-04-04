/*

Brillouin zone WebGL Visualizer

Author: Giovanni Pizzi (2016)

Lincense: The MIT License (MIT)

Copyright (c), 2016, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE
(Theory and Simulation of Materials (THEOS) and National Centre for 
Computational Design and Discovery of Novel Materials (NCCR MARVEL)),
Switzerland.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

*/
// Global variables
var show_axes = false;
var show_b_vectors = true;
var show_pathpoints = false; // If you want to show the points of the explicit path

// if true, use the SVG renderer rather than the WebGL one
// Note that it supports less functionality, and it requires an additional
// dependency (not in the main three.js code, but in examples/js/renderer
// (both the svg renderer and the projector))
// This is mainly useful if you want to get a vector image of the BZ
// rather than a raster screenshot
var use_svg_renderer = false;

// strings to update
var to_update = [];

var bz_material = new THREE.MeshBasicMaterial(
{
    color: 0xd53e4f,
    opacity: 0.5,
    transparent: true,
    //side: THREE.DoubleSide,
});

var edge_material = new THREE.MeshBasicMaterial(
{
    color: 0x333333,
    opacity: 1.,
    transparent: false,
});

var line_material = new THREE.MeshBasicMaterial(
{
    color: 0x045add,
    opacity: 1.,
    transparent: false,
});

var point_material = new THREE.MeshBasicMaterial(
{
    color: 0x3288bd,
    opacity: 1.,
    transparent: false,
});

var pointpath_material = new THREE.MeshBasicMaterial(
{
    color: 0x883232,
    opacity: 1.,
    transparent: false,
});

// need to be global in the current implementation
var scene = null;
var camera = null;
var renderer = null;
var current_canvas_id = null;

var load_BZ_ajax = function(url, canvasID, infoID) {
    document.getElementById(infoID).innerHTML = "Loading..."
    $.getJSON(newpath_to_load, function(jsondata) {
        load_BZ(canvasID, infoID, jsondata);
    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
        document.getElementById(infoID).innerHTML = "Request Failed: " + err;
    });
}

var prettify_label = function(label) {
        // Underscores
        label = label.replace(/_(.)/gi,function (match, p1, offset, string) {
            return '<sub>'+p1+'</sub>';
        });
        // Gamma
        label = label.replace(/GAMMA/gi,'&Gamma;');
        // Delta
        label = label.replace(/DELTA/gi,'&Delta;');
        // Sigma
        label = label.replace(/SIGMA/gi,'&Sigma;');
        // Lambda
        label = label.replace(/LAMBDA/gi,'&Lambda;');
        label = label.replace(/\-/gi, '&mdash;')
        return label;
}

var resize_renderer = function() {
    if (current_canvas_id) {
        var canvas3d = document.getElementById(current_canvas_id);

        var devicePixelRatio = window.devicePixelRatio || 1;

        // current width (in CSS pixels)
        canvas3d_width = canvas3d.offsetWidth;
        canvas3d_height = canvas3d.offsetHeight;

        if (renderer) {
            camera.aspect = canvas3d_width / canvas3d_height;
            camera.updateProjectionMatrix();

            // propertly scale dom element *and* renderer to take into account 
            // devicePixelRatio (that is e.g. 2 on Retina displays)
        	renderer.setSize( canvas3d_width * devicePixelRatio, canvas3d_height * devicePixelRatio);
            renderer.domElement.style.width = canvas3d_width + "px";
            renderer.domElement.style.height = canvas3d_height + "px";
            renderer.domElement.width = canvas3d_width * devicePixelRatio;
            renderer.domElement.height = canvas3d_height * devicePixelRatio;
        }
        render();        
    }
}

var load_BZ = function(canvasID, infoID, jsondata) {
    // to be used by resize_renderer
    current_canvas_id = canvasID;
    var canvas3d = document.getElementById(canvasID);

    var devicePixelRatio = window.devicePixelRatio || 1;

    document.getElementById(infoID).innerHTML = ""

    // Remove the renderer (and anything else)
    while (canvas3d.firstChild) {
       canvas3d.removeChild(canvas3d.firstChild);
    }
    // I don't need to clear the text divs, I did it in the line above
    // I just need to empty the to_update list
    to_update = [];

    scene = new THREE.Scene();
    canvas3d_width = canvas3d.offsetWidth;
    canvas3d_height = canvas3d.offsetHeight;
    camera = new THREE.PerspectiveCamera( 45, canvas3d_width / canvas3d_height, 0.01, 1000 );
    // If I don't move it, I cannot pan
    camera.position.z = 3;

    //var raycaster = new THREE.Raycaster();

    if (use_svg_renderer) {
        renderer = new THREE.SVGRenderer();
        renderer.setQuality('high');
    }
    else {
        renderer = new THREE.WebGLRenderer({ 
            alpha: true,
            // antialias: true // much slower!
        });        
    }
    // white bg
    renderer.setClearColor( 0xffffff, 0);
    //renderer.setClearColor( 0xcccccc, 0);

    // propertly scale dom element *and* renderer to take into account 
    // devicePixelRatio (that is e.g. 2 on Retina displays)
    renderer.setSize( canvas3d_width * devicePixelRatio, canvas3d_height * devicePixelRatio);
    renderer.domElement.style.width = canvas3d_width + "px";
    renderer.domElement.style.height = canvas3d_height + "px";
    renderer.domElement.width = canvas3d_width * devicePixelRatio;
    renderer.domElement.height = canvas3d_height * devicePixelRatio;

    //document.body.appendChild( renderer.domElement );
    canvas3d.appendChild( renderer.domElement );

    // Now is commented, needs to be called by hand
    // var doc = canvas3d.ownerDocument;
    // var win = doc.defaultView || doc.parentWindow;
    // win.addEventListener("resize", resize_renderer);

    controls = new THREE.OrbitControls( camera, renderer.domElement );
    controls.addEventListener( 'change', render ); // add this only if there is no animation loop (requestAnimationFrame)
    // needed because we want to redraw only on change
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.enableZoom = true;

    special_points = jsondata['kpoints'];
    b1 = jsondata['b1'];
    b2 = jsondata['b2'];
    b3 = jsondata['b3'];

    max_b_length = Math.sqrt(Math.max(
        Math.pow(b1[0],2) + Math.pow(b1[1],2) + Math.pow(b1[2],2),
        Math.pow(b2[0],2) + Math.pow(b2[1],2) + Math.pow(b2[2],2),
        Math.pow(b3[0],2) + Math.pow(b3[1],2) + Math.pow(b3[2],2)));

    var axeslength = max_b_length * 1.5;
    camera.position.z = max_b_length * 3;

    data = jsondata['faces_data'];
    for (var label in special_points) {
        pos = special_points[label];

        radius = 0.02 * max_b_length;

        var sphere_geometry = new THREE.SphereGeometry(
            radius, 16, 16 );
        var sphere = new THREE.Mesh(
            sphere_geometry, point_material );
        sphere.translateX(pos[0]);
        sphere.translateY(pos[1]);
        sphere.translateZ(pos[2]);
        scene.add(sphere);

        // Label
        var textdiv = document.createElement('div');
        textdiv.style.position = 'absolute';
        textdiv.style.fontFamily = "'Helvetica Neue', Helvetica, Arial, sans-serif";
        //textdiv.style.zIndex = 1;    // if you still don't see the label, try uncommenting this
        textdiv.style.width = 100;
        textdiv.style.height = 100;
        textdiv.style.backgroundColor = "transparent";

        // prettify label
        label = prettify_label(label);

        textdiv.innerHTML = label;
        // disallow scrolling etc. so that it goes to the parent div
        textdiv.style.pointerEvents = "none"; 
        // next are to disallow selection
        textdiv.style.userSelect = "none";
        textdiv.style.userSelect = "none";
        textdiv.style.webkitUserSelect = "none";
        textdiv.style.MozUserSelect = "none";
        textdiv.setAttribute("unselectable", "on");

        // out of view at the beginning
        textdiv.style.top = -100 + 'px';
        textdiv.style.left = -100 + 'px';
        canvas3d.appendChild(textdiv);

        to_update.push([
            new THREE.Vector3(pos[0], pos[1], pos[2]), 
            textdiv]);
    }

    if (show_axes) {
        // AXES
        //var dir = new THREE.Vector3( 1, 0, 0 );
        [[new THREE.Vector3( 1, 0, 0 ), '<span style="font-style: italic">x</span>'],
        [new THREE.Vector3( 0, 1, 0 ), '<span style="font-style: italic">y</span>'],
        [new THREE.Vector3( 0, 0, 1 ), '<span style="font-style: italic">z</span>']].forEach(
            function (data) {
                dir = data[0];
                label = data[1];

                // Arrow
                var origin = new THREE.Vector3( 0, 0, 0 );
                var hex = 0x555555;
                var arrow = new THREE.ArrowHelper(
                    dir, 
                    origin,
                    axeslength,
                    hex,
                    headLength=axeslength/10.,
                    headwidth=axeslength/20.);
                //arrowX.line.material.linewidth = 2;
                scene.add( arrow );                

                // Label
                var textdiv = document.createElement('div');
                textdiv.style.position = 'absolute';
                textdiv.style.fontFamily = "'Helvetica Neue', Helvetica, Arial, sans-serif";
                //text2.style.zIndex = 1;    // if you still don't see the label, try uncommenting this
                textdiv.style.color = "#555555";
                textdiv.style.width = 100;
                textdiv.style.height = 100;
                //text2.style.backgroundColor = "blue";
                textdiv.innerHTML = label;
                // out of view at the beginning
                textdiv.style.top = -100 + 'px';
                textdiv.style.left = -100 + 'px';
                textdiv.style.userSelect = "none";
                textdiv.style.userSelect = "none";
                textdiv.style.webkitUserSelect = "none";
                textdiv.style.MozUserSelect = "none";
                textdiv.setAttribute("unselectable", "on");
                textdiv.style.pointerEvents = "none"; 


                canvas3d.appendChild(textdiv);

                pos = dir.clone();
                pos.sub(origin);
                pos.multiplyScalar(axeslength);
                to_update.push([pos, textdiv]);

            });
    }

    // B vectors
    //var dir = new THREE.Vector3( 1, 0, 0 );
    var b_vectors = [[b1, '<span style="font-weight: bold">b</span><sub>1</sub>'],
    [b2, '<span style="font-weight: bold">b</span><sub>2</sub>'],
    [b3, '<span style="font-weight: bold">b</span><sub>3</sub>']
    ];

    if (!show_b_vectors) {
        b_vectors = [];
    }

    b_vectors.forEach(
        function (data) {
            b = data[0];
            label = data[1];

            b_length = Math.sqrt(Math.pow(b[0],2) + Math.pow(b[1],2) + Math.pow(b[2],2));

            dir = new THREE.Vector3(
                b[0]/b_length,
                b[1]/b_length,
                b[2]/b_length);

            // Arrow
            var origin = new THREE.Vector3( 0, 0, 0 );
            var hex = 0x000000;
            var arrow = new THREE.ArrowHelper(
                dir, 
                origin,
                length=b_length,
                hex=hex,
                headLength=b_length/10.,
                headwidth=b_length/20.);
            //arrowX.line.material.linewidth = 2;
            scene.add( arrow );                

            // Label
            var textdiv = document.createElement('div');
            textdiv.style.position = 'absolute';
            textdiv.style.fontFamily = "'Helvetica Neue', Helvetica, Arial, sans-serif";
            //text2.style.zIndex = 1;    // if you still don't see the label, try uncommenting this
            //textdiv.style.color = "#555555";
            textdiv.style.width = 100;
            textdiv.style.height = 100;
            //text2.style.backgroundColor = "blue";
            textdiv.innerHTML = label;
            // out of view at the beginning
            textdiv.style.top = -100 + 'px';
            textdiv.style.left = -100 + 'px';
            textdiv.style.userSelect = "none";
            textdiv.style.userSelect = "none";
            textdiv.style.webkitUserSelect = "none";
            textdiv.style.MozUserSelect = "none";
            textdiv.setAttribute("unselectable", "on");
            textdiv.style.pointerEvents = "none"; 
            canvas3d.appendChild(textdiv);

            pos = dir.clone();
            pos.sub(origin);
            pos.multiplyScalar(b_length);
            to_update.push([pos, textdiv]);

        });

    // Load BZ
    var brillouinzone = new THREE.Geometry();
    data['triangles_vertices'].forEach(function(vertex) {
        brillouinzone.vertices.push(
            new THREE.Vector3(vertex[0], vertex[1], vertex[2]));
    }); 
    data['triangles'].forEach(function(triangle) {
        brillouinzone.faces.push(
            new THREE.Face3(triangle[0], triangle[1], triangle[2]));
    });
    var bz_mesh = new THREE.Mesh(brillouinzone, bz_material);
    // Create BZ edges
    edges = new THREE.EdgesHelper( bz_mesh, 0x00ff00 );
    edges.material = edge_material;
    edges.material.linewidth = 1;
    // Plot BZ and edges
    scene.add(bz_mesh);
    scene.add(edges);


    // draw path
    path = jsondata['path'];
    path.forEach(function (linespec) {
        label1 = linespec[0];
        label2 = linespec[1];
        p1 = special_points[label1];
        p2 = special_points[label2];

        var geometry = new THREE.Geometry();
        geometry.vertices.push(
            new THREE.Vector3(p1[0], p1[1], p1[2]));
        geometry.vertices.push(
            new THREE.Vector3(p2[0], p2[1], p2[2]));
        var line = new THREE.Line(geometry, line_material);
        line.material.linewidth = 4;
        scene.add(line);
    });        


    if (show_pathpoints) {
        kpoints_abs = jsondata['explicit_kpoints_abs'];
        for (var idx in kpoints_abs) {
            pos = kpoints_abs[idx];
            radius = 0.005 * max_b_length;

            var sphere_geometry = new THREE.SphereGeometry(
                radius, 16, 16 );
            var sphere = new THREE.Mesh(
                sphere_geometry, pointpath_material );
            sphere.translateX(pos[0]);
            sphere.translateY(pos[1]);
            sphere.translateZ(pos[2]);
            scene.add(sphere);
        }
    }

    render();

    if (use_svg_renderer) {
        console.log('svg content:');
        console.log(canvas3d.innerHTML.replace('/<path/g','\n<path'));
    }
}

function toScreenPosition(vector3D, camera)
{
	var devicePixelRatio = window.devicePixelRatio || 1;
    var widthHalf = 0.5*renderer.context.canvas.width / devicePixelRatio;
    var heightHalf = 0.5*renderer.context.canvas.height / devicePixelRatio;

    vector2D = vector3D.clone().project(camera);

    vector2D.x = ( vector2D.x * widthHalf ) + widthHalf;
    vector2D.y = - ( vector2D.y * heightHalf ) + heightHalf;

    return { 
        left: vector2D.x,
        top: vector2D.y
    };

};

// render function
function render() { 
    //requestAnimationFrame( render );  // activate only if you want to loop and make an animation
    renderer.render( scene, camera ); 
    
    to_update.forEach(function(data) {
        pos = data[0];
        text = data[1];
        pos2d = toScreenPosition(pos,camera);
        text.style.top = pos2d.top + 'px';
        text.style.left = pos2d.left + 'px';
    });
}
