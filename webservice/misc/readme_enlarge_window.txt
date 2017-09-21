To enlarge the BZ window, you can put this in HTML (or copy-paste the code in 
a terminal).

It's a dirty trick, but it does the job.

	<script>
	  var enlarge_window = function () {
	    // Some magic to enlarge the window. Will work only once.
	    bzblock = $('#canvas3dcontainer')[0]

  	    container = $('#aboveleft')[0]
	    container.removeChild(bzblock)

	    newdest = $('#above')[0];
	    newdest.appendChild(bzblock);

	    canvas = $('#canvas3d')[0].getElementsByTagName('canvas')[0];
	    bzblock.style.height = "1024px";
	    bzblock.style.width = "1024px";
	    resize_canvases();
          }
	</script>
        <a onclick="enlarge_window()" href="#">Enlarge BZ window</a>


