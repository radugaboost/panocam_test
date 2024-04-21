class ContourArea {
  constructor() {
    this.canvas = null;
    this.areaClosed = false;
    this.points = [];
    this.relativeX = null;
    this.optionsArea = null;
    this.content = null;
    this.image = null;
  }

  updateCanvasSize() {
    this.canvas.width = this.image.width;
    this.canvas.height = this.image.height;
  }

  startDrawing() {
    this.canvas = document.createElement("canvas");
    this.canvas.style.position = 'absolute';
    this.canvas.style.zIndex = 1;
    this.image = document.getElementById("stream");
    this.canvas.width = this.image.width;
    this.canvas.height = this.image.height;
    this.content = document.getElementById("content");
    this.optionsArea = document.getElementById("selectChoice");
    this.relativeX = this.content.getBoundingClientRect().left
    document.body.style.cursor = 'crosshair';
    this.changeArrowsDisplay('none');

    this.drawDarkenedRectangle(this.canvas.getContext('2d'));

    this.content.appendChild(this.canvas);
    this.setupCanvasListeners();
  }

  changeArrowsDisplay(arg) {
    const arrows = Array.from(document.querySelectorAll('.arrow-6')).slice(0, 2);
    for (i in arrows) {
      arrows[i].style.display = arg;
    }
  }

  setupCanvasListeners() {
    this.canvas.addEventListener("mousedown", this.handleMouseDown.bind(this));
    this.canvas.addEventListener("mousemove", this.handleMouseMove.bind(this));
    this.canvas.addEventListener("mouseup", this.handleMouseUp.bind(this));
  }

  findClickedPoint(x, y) {
    for (let i = 0; i < this.points.length; i++) {
      if (Math.abs(x - this.points[i].x) < 10 && Math.abs(y - this.points[i].y) < 10) {
        return i;
      }
    }
    return -1;
  }

  drawConnectingLines(ctx) {
    ctx.strokeStyle = 'red';
    ctx.moveTo(this.points[0].x, this.points[0].y);

    for (let i = 1; i < this.points.length; i++) {
      ctx.lineTo(this.points[i].x, this.points[i].y);
    }
    ctx.stroke();
  }

  drawPoints(ctx) {
    ctx.fillStyle = 'red';

    for (let i = 0; i < this.points.length; i++) {
      ctx.beginPath();
      ctx.arc(this.points[i].x, this.points[i].y, 5, 0, 2 * Math.PI);
      ctx.fill();
    }
  }

  drawSelectedArea(ctx) {
    ctx.beginPath();
    ctx.moveTo(this.points[0].x, this.points[0].y);

    for (let i = 1; i < this.points.length; i++) {
      ctx.lineTo(this.points[i].x, this.points[i].y);
    }

    ctx.fillStyle = 'white';
    ctx.globalAlpha = 0.5;
    ctx.fill();
    ctx.stroke();

    const firstPoint = this.points[0];
    const optionsAreaLeft = Math.max(firstPoint.x - this.relativeX, this.relativeX);
    const optionsAreaTop = firstPoint.y;

    const maxXPage = this.image.width - this.optionsAreaWidth;
    const maxYPage = this.image.height - this.optionsAreaHeight;
    this.optionsArea.style.zIndex = 2;
    this.optionsArea.style.left = Math.min(optionsAreaLeft, maxXPage) + 'px';
    this.optionsArea.style.top = Math.min(optionsAreaTop, maxYPage) + 'px';
  }

  drawDarkenedRectangle(ctx) {
    ctx.globalAlpha = 0.5;
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.globalAlpha = 1;
  }

  handleMouseDown(e) {
    const clickedPointIndex = this.findClickedPoint(e.clientX - this.relativeX, e.clientY);

    if (clickedPointIndex !== -1 || this.areaClosed) {
      this.selectedPointIndex = clickedPointIndex;
      this.isDrawing = true;
    }

    if (clickedPointIndex === 0 && !this.areaClosed) {
      document.body.style.cursor = 'default';
      this.isDrawing = true;
      this.areaClosed = true;
      this.drawSelectedArea(this.canvas.getContext('2d'));
    }

    if (!this.areaClosed && clickedPointIndex === -1) {
      this.points.push({ x: e.clientX - this.relativeX, y: e.clientY });
      const ctx = this.canvas.getContext('2d');
      ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.drawDarkenedRectangle(ctx);
      this.drawConnectingLines(ctx);
      this.drawPoints(ctx);
    }
  }

  handleMouseMove(e) {
    if (this.selectedPointIndex !== -1 & this.isDrawing) {
      this.optionsArea.style.display = 'none';
      this.points[this.selectedPointIndex] = { x: e.clientX - this.relativeX, y: e.clientY };

      const ctx = this.canvas.getContext('2d');
      ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.drawDarkenedRectangle(ctx);
      if (this.areaClosed) {
        this.drawSelectedArea(ctx);
      } else {
        this.drawConnectingLines(ctx);
      }
      this.drawPoints(ctx);
    }
  }

  handleMouseUp() {
    if (this.selectedPointIndex !== -1 & this.isDrawing) {
      this.optionsArea.style.display = 'block';
      this.optionsAreaWidth = this.optionsArea.offsetWidth;
      this.optionsAreaHeight = this.optionsArea.offsetHeight;
    }
    this.isDrawing = false;
    this.selectedPointIndex = -1;
  }

  updateContour() {
    const csrfTokenInput = document.getElementsByName('csrfmiddlewaretoken')[0];
    const csrfToken = csrfTokenInput.value;

    fetch("/add_area/1/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 'points': this.points, 'shape': [this.image.height, this.image.width] })
    })
    .then(response => response.json())
    .then(data => {
      window.open(`${this.image.src}${data.area_id}`, '_blank');
    })
    .catch(error => {
        console.error('Error:', error);
    });
  }

  clear() {
    this.optionsArea.style.display = 'none';
    if (this.canvas.parentNode) {
      this.canvas.parentNode.removeChild(this.canvas);
    };
    this.canvas.removeEventListener("mousedown", this.handleMouseDown);
    this.canvas.removeEventListener("mousemove", this.handleMouseMove);
    this.canvas.removeEventListener("mouseup", this.handleMouseUp);
    this.changeArrowsDisplay('block');
    this.areaClosed = false;
    this.points = [];
  }
}

const contourArea = new ContourArea();
const selectAreaBtn = document.getElementById("selectArea");

function draw() {
  selectAreaBtn.style.display = 'none';
  contourArea.startDrawing();
}

function openAreaUrl() {
  contourArea.updateContour();
}

function afterDrawing() {
  selectAreaBtn.style.display = 'block';
  contourArea.clear();
}