// shared with other scripts
var numberCrunchTimerID = 0;

function numberCrunchStop() {
  var numberCrunch = document.getElementById("animNumberCrunching");
  if (numberCrunch) {
    if (typeof numberCrunchTimerID !== 'undefined') {
      logFunc('numberCrunch cancel after response start', numberCrunchTimerID);
      window.clearTimeout(numberCrunchTimerID);
      numberCrunch.style.display = "none";
    }
  }
}

function numberCrunchStart() {
  var numberCrunch = document.getElementById("animNumberCrunching");
  if (numberCrunch) {
    if (typeof numberCrunchTimerID !== 'undefined') {
      numberCrunchTimerID = window.setTimeout(function () { numberCrunch.style.display = "block"; }, 40);
      logFunc('numberCrunch timeOut ID:', numberCrunchTimerID);
    }
  }
}

function updateWebsite(responseMap) {

}

// Based on www.petercollingridge.co.uk/tutorials/svg/interactive/dragging/
// Contains closures for isolation.
// SVG main canvas is stored into variable 'svg' via onload event.
// Added vertical/horizontal constrains.
// Added dynamic constraint limits as argument.
// https://obfuscator.io/
function activateDrag(evt, graphID, constrainerID, planName, postUpdateURL, gridDivisions=10) {
 
  if (typeof planName === "undefined") {
    planName = "default-plan-1"
  }

  if (typeof postUpdateURL === "undefined") {
    postUpdateURL = "/rentomat/plan-update";
  }

  if (typeof gridDivisions === "undefined") {
    gridDivisions = 10;
    // gridDivisions = gridDivisions || 0;  // for ES5 - stackoverflow.com/questions/12797118/
  }



  logFunc = function () {
    var line = "";
    for (var i = 0; i < arguments.length; i++) {
      line += String(arguments[i]) + ", ";
    }
    line += "\n"
    console.log(line);
    var out = document.getElementById("console-log"); // some visible div - to watch errors
    if (out !== null) {
      out.innerHTML += line;
      out.scrollTop = out.scrollHeight;
    }
  };

  // ajax request without jQuery
  // postParams can be javascript map/dictionary or object
  // https://stackoverflow.com/questions/18541940/map-vs-object-in-javascript
  function asyncPostUpdateReadResponse(mapOfParams) {
    var xhr = new XMLHttpRequest();
    xhr.timeout = 15*1000; // millisecs

    xhr.onreadystatechange = function () {
      if (xhr.readyState == XMLHttpRequest.DONE) {   // XMLHttpRequest.DONE == 4
        if (xhr.status == 200) {
          logFunc('XMLHttpRequest: Response', xhr.responseText);
          try {
            var responseMap = JSON.parse(xhr.responseText);
            updateWebsite(responseMap);
          } catch (error) {
            logFunc("response json parse error", error);
            numberCrunchStop()
          }
        } else {
          logFunc('XMLHttpRequest: status != 200 returned', xhr.status, xhr.statusText);
          numberCrunchStop()
        }
      }
    };

    var getParams = 'key1=val1&key2=val2'; // some URL GET params - just for demonstration
    // header Content-Length is treated as unsafe
    // xhr.setRequestHeader('Content-Length', (JSON.stringify(mapOfParams)).length );
    // instead
    getParams += "&content-length=" + (JSON.stringify(mapOfParams)).length

    xhr.open('POST', postUpdateURL + "?" + getParams, true);

    // CORS:  www.w3.org/TR/cors/: simple request header must be:  application/x-www-form-urlencoded, multipart/form-data, or text/plain
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    // xhr.setRequestHeader('Content-type', 'application/json');

    
    // xhr.send(encodeURI(getParams));
    // xhr.send(JSON.stringify({
    //     name: 'John Smith',
    //     age: 34
    // }));
    logFunc('XMLHttpRequest: Sending ', JSON.stringify(mapOfParams));
    xhr.send(JSON.stringify(mapOfParams));
  }

  var svg = evt.target; // main svg document or container

  // the dragged element; el may be set to the *parent* of the originall clicked event
  var el;
  // elOrig always contains the element clicked on
  var elOrig;

  var start;
  var transform;
  var bbox;
  var minX, maxX, minY, maxY;

  var constrain;
  var constrainVert;
  var constrainHori;
  var any3;

  // default coords for the inner plot area - acting as dragging constraints - should always get overridden below
  var boundaryX1 = 0;
  var boundaryX2 = 320;
  var boundaryY1 = 0;
  var boundaryY2 = 240;
  var gridWidth  = 10;
  var gridHeight = 10;

  var bboxC = svg.getBBox();  // default - without constrainer - viewBox="0 0 40 30" must be equal to pixel width and height
  if (typeof constrainerID !== "undefined") {
    var constrainer = document.getElementById(constrainerID);
    if (constrainer) {
      bboxC = constrainer.getBBox();
    }
  }

  // boundaryX1 = parseFloat(constrainer.getAttributeNS(null, "x"));
  // boundaryX2 = parseFloat(constrainer.getAttributeNS(null, "width")) + boundaryX1;
  // ...
  boundaryX1 = bboxC.x;
  boundaryX2 = bboxC.x + bboxC.width;
  boundaryY1 = bboxC.y;
  boundaryY2 = bboxC.y + bboxC.height;
  gridWidth  = (boundaryX2 - boundaryX1) / gridDivisions;
  gridHeight = (boundaryY2 - boundaryY1) / gridDivisions;
  logFunc("constraining to ", constrainerID, bboxC.x, bboxC.x + bboxC.width, bboxC.y, bboxC.y + bboxC.height);


  // upload user changes
  var postChanges = {
    name: planName,
    points: {}
  };

  var postChangesExample = {
    name: planName,
    points: {
      111: { x: 2, y: 3 },
    }
  };


  // Mapping SVG container units to screen coordinates.
  // Current Transformation Matrix for the screen
  // is an object with six keys: a, b, c, d, e, f.
  function mouseAsLocal(evt) {
    var CTM = svg.getScreenCTM();
    if (evt.touches) { evt = evt.touches[0]; } // only the first touch
    return {
      x: (evt.clientX - CTM.e) / CTM.a,
      y: (evt.clientY - CTM.f) / CTM.d
    };
  }

  /*
    Transformation matrix
    a   b   e
    c   d   f
    0   0   1

    Only six values are used in the above 3x3 matrix.
    A transformation matrix is also expressed as a vector: [a b c d e f].

    a and d responsible for scaling in x and y respectively,
    e and f gives you the translated axis in the x and y respectively.

  */
  function getTransform(domEl) {

    // Make sure the first transform on the element is a translate transform
    var base = domEl.transform.baseVal;

    var validBase = false;
    if (typeof (base) != 'undefined' && base != null) {
      var validBase = true;
      // logFunc("baseTf defined && not null / type / length ", base, typeof base, base.length);
    }

    // stackoverflow.com/questions/35120590
    var numberOfTransformations = -1;
    if (typeof (base) != 'undefined' && base != null) {
      if (typeof base.length !== 'undefined') {
        numberOfTransformations = base.length;
      } else if (typeof base.numberOfItems !== 'undefined') {
        numberOfTransformations = base.numberOfItems;
      }
    }

    var cond2 = numberOfTransformations < 1;

    var cond3 = false;
    if (!cond2) {
      var tf = base.getItem(0);
      if (tf) {
        cond3 = tf.type !== SVGTransform.SVG_TRANSFORM_TRANSLATE;
      }
    }

    if (cond2 || cond3) {
      // Create a dummy translation by (0, 0)
      var translateDummy = svg.createSVGTransform();
      translateDummy.setTranslate(0, 0);
      domEl.transform.baseVal.insertItemBefore(translateDummy, 0);
      // logFunc("base tf added; base: ", base, "base.length:", numberOfTransformations );
    }
    // logFunc("base.length:", numberOfTransformations );

    var tf;
    try {
      tf = base.getItem(0);
    } catch (error) {
      logFunc("getTransform error", error);
      var translateDummy = svg.createSVGTransform();
      translateDummy.setTranslate(0, 0);
      tf = translateDummy;
    }

    return tf;
  }


  function startDrag(evt) {

    if (evt.target.classList.contains('draggable')) {

      el = evt.target;
      elOrig = el;
      // SVG groups themselves to do not capture mouse events,
      // so we need to get the group element from the child element.
      if (evt.target.parentNode.tagName == "g") {
        el = evt.target.parentNode;

        // firefox-repeat-problem-with-groups
        elOrig.classList.add("noevents");

        // firefox-repeat-problem-with-groups
        window.setTimeout(function () {
          // we re-activate event handling at the end of dragging
          // elOrig.classList.remove("noevents");
          // logFunc("removed again");
        }, 1500);


      }

      start = mouseAsLocal(evt);

      // failed trials to achieve z-axis change of dragged element
      if (false) {
        // el.style.zIndex = 100; // useless in SVG 1.1
        // el.setAttributeNS(null, "z", "100"); // useless in SVG 1.1
        var paragraph = document.createElement("P");
        var txt = document.createTextNode("a par - dragged " + el.id);
        paragraph.appendChild(txt);
        document.body.appendChild(paragraph);
        // <use xlink:href='#" + el.id + "'  />
        var use = document.createElement("USE");
        use.setAttributeNS("xlink", "xlink:href", "#" + el.id)
        svg.appendChild(use);
      }

      // Add existing translation
      transform = getTransform(el);
      start.x -= transform.matrix.e;
      start.y -= transform.matrix.f;


      gridify       = evt.target.classList.contains('draggable');
      gridify       = gridWidth > 1 && gridHeight > 1

      constrain     = evt.target.classList.contains('constrain');
      constrainVert = evt.target.classList.contains('constrain-vert');
      constrainHori = evt.target.classList.contains('constrain-hori');
      any3 = gridify ||  constrain || constrainVert || constrainHori
      if (any3) {
        bbox = el.getBBox();
        minX = boundaryX1 - bbox.x - bbox.width  / 2;
        maxX = boundaryX2 - bbox.x - bbox.width  / 2;
        minY = boundaryY1 - bbox.y - bbox.height / 2;
        maxY = boundaryY2 - bbox.y - bbox.height / 2;
        // logFunc("constr both", minX, maxX, minY, maxY);
      }


      if (constrainVert) {
        minX = 0.000;
        maxX = 0.000;
        // minX = -0.02;
        // maxX = +0.02;
        minX += transform.matrix.e;
        maxX += transform.matrix.e;
        // logFunc("constr verti", minX, maxX, minY, maxY);
      } else if (constrainHori) {
        minY = 0.000;
        maxY = 0.000;
        // minY = -0.02;
        // maxY = +0.02;
        minY += transform.matrix.f;
        maxY += transform.matrix.f;
        // logFunc("constr horiz", minX, maxX, minY, maxY);
      }




    }
  }


  function drag(evt) {

    if (typeof el === "undefined") {
      el = false;
      return
    }

    if (!el) {
      el = false;
      return;
    }

    evt.preventDefault();
    // evt.stopPropagation(); // did not stop the firefox-repeat-problem
    var coord = mouseAsLocal(evt);
    var dx = coord.x - start.x;
    var dy = coord.y - start.y;
    if (any3) {
      if (dx < minX) { dx = minX; }
      else if (dx > maxX) { dx = maxX; }
      if (dy < minY) { dy = minY; }
      else if (dy > maxY) { dy = maxY; }
    }
    transform.setTranslate(dx, dy);
    // logFunc("dragged", dx, dy);

  }


  function endDrag(evt) {

    try {

      if (typeof el === "undefined") {
        el = false;
        return
      }

      if (!el) {
        el = false;
        return;
      }

      if (typeof el.id === "undefined") {
        el = false;
        return;
      }

      if (typeof el.id === "") {
        el = false;
        return;
      }

      

      // snap dragged object to grid
      if (gridWidth > 1 && gridHeight > 1) {

        var graW = gridWidth; // shortcut to granularity; for example 25
        var graH = gridHeight; 

        var gridX = transform.matrix.e
        gridX = Math.round((gridX - minX) / graW) * graW   + minX
        if      (gridX < minX + graW) { gridX = minX; } // off limit...
        else if (gridX > maxX - graW) { gridX = maxX; }

        var gridY = transform.matrix.f
        gridY = Math.round((gridY - minY) / graH) * graH   + minY
        if      (gridY < minY + graH) { gridY = minY; } // off limit...
        else if (gridY > maxY - graH) { gridY = maxY; }

        transform.setTranslate(gridX, gridY);
      }


      // 
      // get new polygon point position - and post it to server
      var isDirty = false;
      // logFunc("polygon drag 01", el.id, el.id.substring(2), parseInt(el.id.substring(2)) );
      var xId = parseInt(el.id.substring(2));
      var numAreas = 3;
      for (var i1 = 0; i1 < numAreas; i1++) {
        // var poly = document.getElementById(graphID + " area" + String(i));
        var cssClass = graphID + " area" + String(i1);
        var elements = document.getElementsByClassName(cssClass);
        for (i2 = 0; i2 < elements.length; i2++) {
          var poly = elements[i2];
          if (poly) {
            var newY = el.getBBox().y + el.getBBox().height / 2
            newY += transform.matrix.f;
            if (poly.points) {
              var pointIdx = Math.floor(xId / 10); // float to integer
              // logFunc("polygon and polygon.points exist; pointIdx - length", pointIdx, poly.points.length, typeof (poly.points), poly.points[pointIdx] );
              // poly.points[pointIdx].y = newY  // this fails on safari-mobile - instead see code below
              // var point1 = svg.createSVGPoint();
              // point1.y = 170;
              // poly.points.appendItem(point1);
              var pointOfChange = null;
              try {
                pointOfChange = poly.points.getItem(pointIdx);
              } catch (error) {
                // document.getElementById("console-log").style.display = "block";
                // logFunc("polygon.points index problem", error);
                logFunc("polygon.points index problem: area-, css-idx, len: ", i1, i2, poly.points.length);
                continue;
              }
              pointOfChange.y = newY;

              // only for first area: post changes
              if (i1 === 0) {
                var tfY = (newY - boundaryY1) / (boundaryY2 - boundaryY1);
                var newX = el.getBBox().x + el.getBBox().width / 2
                var tfX = (newX - boundaryX1) / (boundaryX2 - boundaryX1);
                postChanges.points[pointIdx] = { x: tfX, y: tfY };
                isDirty = true;
              }

            } else {
              logFunc("polygon.points does not exist; area-, css-idx: ", i1, i2);
            }
          } // if poly
        }  // for elements
      } // for areas

   
      // 
      // get new speed control element position - and post it to server
      // values range from -0.5 to +0.5  -  0.0 is neutral
      if (el.id === "ctrl1" || el.id === "ctrl2" || el.id === "ctrl3" ) {

        isDirty = true;

        postChanges.Control = el.id;

        postChanges.X =  el.getBBox().x + el.getBBox().width  / 2;
        postChanges.X += transform.matrix.e;
        postChanges.X -= boundaryX1
        postChanges.X /= boundaryX2 - boundaryX1  // 0...1
        postChanges.X *= 2   //  0...+2
        postChanges.X -= 1   // -1...+1
        // postChanges.X = dcMotorTransform(postChanges.X) // left-right changes are only offsets for forward movements - thus anyway kick in at lower voltages
        postChanges.X =  postChanges.X.toFixed(3);

        // y is increasing downwards
        postChanges.Y =  el.getBBox().y + el.getBBox().height / 2;
        postChanges.Y += transform.matrix.f;
        postChanges.Y -= boundaryY1
        postChanges.Y /= boundaryY2 - boundaryY1 // 0...1 - but in wrong way
        postChanges.Y += -1  // -1...0
        postChanges.Y *= -1  // +1...0
        postChanges.Y *= 2   //  0...+2
        postChanges.Y -= 1   // -1...+1
        postChanges.Y = dcMotorTransform(postChanges.Y) 
        postChanges.Y =  postChanges.Y.toFixed(3);


      }

      /*
      // dump changes
      var val;
      Object.keys(postChanges.y).forEach(function (key) {
        val = postChanges.y[key];
        logFunc("postChanges.y", key, val);
      });
      */

      if (isDirty) {
        numberCrunchStart();
        asyncPostUpdateReadResponse(postChanges);
      }


    } catch (error) {
      logFunc("end drag error", error);
      numberCrunchStop();
    }

    // firefox-repeat-problem-with-groups
    // reactivate event handling
    elOrig.classList.remove("noevents");
    elOrig = false;
    el = false;


    logFunc("end drag");

  }

  svg.addEventListener('mousedown', startDrag);
  svg.addEventListener('mousemove', drag);
  svg.addEventListener('mouseup', endDrag);
  svg.addEventListener('mouseleave', endDrag);

  svg.addEventListener('touchstart', startDrag);
  svg.addEventListener('touchmove', drag);
  svg.addEventListener('touchend', endDrag);
  svg.addEventListener('touchleave', endDrag);
  svg.addEventListener('touchcancel', endDrag);



  logFunc("dragging activated")

}


function vidstageToggle() {
  var vidstage = document.getElementById("vidstage");
  if (vidstage) {
    if (vidstage.innerHTML != "") {
      vidstage.innerHTML = "";
    } else {
      vidstage.innerHTML = "<img src='/video/' width='100%' />";
    }
  }
}



// transforming 0...0,15...1  to  0...0,575...1 
// 'dead zone' of 0.15
function dcMotorTransform(val) {

  // remember sign
  var sign = 1;
  if (val < 0) {
    sign = -1;
    val = -val
  }

  // dead zone before any action
  if (val < 0.15) {
    return 0;
  }

  // jump into action with 0.575 volt
  // the min voltage to effect straight movement
  var th = 0.5 // threshold
  val = val * (1 - th) + th


  // restore sign
  return sign * val;

}

