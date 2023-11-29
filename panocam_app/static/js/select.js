const rectangle = document.createElement("div");
rectangle.style.position = "absolute";
rectangle.style.backgroundColor = "rgba(204,230,255, 0.7)";
rectangle.style.border = "1px dashed black";
document.body.appendChild(rectangle);

const contentContainer = document.getElementById("content")
const selectAreaBtn = document.getElementById("selectAreaBtn");
const separateBtn = document.getElementById("submitArea");
const deleteBtn = document.getElementById("deleteArea");

let areaUrl = '';
let isDrawingEnabled = false;
let isDragged = false;
let rectangleCoords = [];


selectAreaBtn.addEventListener("click", function () {
  toggleRectangleDrawing();
});


const clearRectangleCoords = () => {
  rectangleCoords = [];
};


const addFirstRectangleCoords = coords => {
  rectangleCoords[0] = coords;
};


const addSecondRectangleCoords = coords => {
  rectangleCoords[1] = coords;
};


function relativeSize(e) {
  const containerRect = contentContainer.getBoundingClientRect();
  const relativeX = e.pageX - containerRect.left;
  const relativeY = e.pageY - containerRect.top;
  return { x: relativeX, y: relativeY };
}


const redrawRectangle = () => {
  const containerRect = contentContainer.getBoundingClientRect();
  const relativeX = containerRect.left;

  const top = Math.min(rectangleCoords[0].y, rectangleCoords[1].y);
  const height = Math.max(rectangleCoords[0].y, rectangleCoords[1].y) - top;
  const left = Math.min(rectangleCoords[0].x, rectangleCoords[1].x);
  const width = Math.max(rectangleCoords[0].x, rectangleCoords[1].x) - left;

  rectangle.style.top = top + "px";
  rectangle.style.height = height + "px";
  rectangle.style.left = left + "px";
  rectangle.style.width = width + "px";

  const image = document.getElementById("stream");
  const originalWidth = image.width - relativeX;
  const originalHeight = image.height;

  // относительные координаты
  const percentTop = ((top - relativeX) / originalHeight) * 100;
  const percentLeft = ((left + relativeX) / originalWidth) * 100;
  const percentWidth = ((width + relativeX) / originalWidth) * 100;
  const percentHeight = ((height - relativeX) / originalHeight) * 100;

  const attrs = `${percentTop}, ${percentLeft}, ${percentWidth}, ${percentHeight}`
  areaUrl = 'http://127.0.0.1:8000/camera_stream/1/?attrs=' + attrs


  separateBtn.style.top = top + height + "px";
  separateBtn.style.left = left + width - (relativeX / 3) + "px";
  deleteBtn.style.top = top + height + "px";
  deleteBtn.style.left = left + width - relativeX + "px";
};

function toggleRectangleDrawing () {
  if (isDrawingEnabled) {
    isDrawingEnabled = false;
  } else {
    isDrawingEnabled = true;
  }
};

function handleMouseDown(e) {
  if (isDrawingEnabled) {
    rectangle.style.display = "block";
    isDragged = true;
    clearRectangleCoords();
    addFirstRectangleCoords({ x: e.pageX, y: e.pageY });
    addSecondRectangleCoords({ x: e.pageX, y: e.pageY });
    redrawRectangle();
  }
}

function handleMouseMove(e) {
  if (isDrawingEnabled && isDragged) {
    addSecondRectangleCoords({ x: e.pageX, y: e.pageY });
    redrawRectangle();
  }
}

function openAreaUrl() {
  window.open(areaUrl, '_blank');
  separateBtn.style.display = 'none';
}

function handleMouseUp(e) {
  if (isDrawingEnabled && isDragged) {
    addSecondRectangleCoords({ x: e.pageX, y: e.pageY });
    redrawRectangle();
    isDragged = false;
    isDrawingEnabled = false;
    separateBtn.style.display = 'block';
    deleteBtn.style.display = 'block'
  }
}

function afterDrawing () {
  rectangle.style.display = 'none';
  separateBtn.style.display = 'none';
  deleteBtn.style.display = 'none';
}

contentContainer.addEventListener("mousedown", handleMouseDown);
contentContainer.addEventListener("mousemove", handleMouseMove);
contentContainer.addEventListener("mouseup", handleMouseUp);

function removeEventListeners() {
  contentContainer.removeEventListener("mousedown", handleMouseDown);
  contentContainer.removeEventListener("mousemove", handleMouseMove);
  contentContainer.removeEventListener("mouseup", handleMouseUp);
}