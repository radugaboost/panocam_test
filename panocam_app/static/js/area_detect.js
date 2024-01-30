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
    console.log(`${this.image.height}x${this.image.width}`)
    fetch("http://localhost:8000/rest/DetectionArea/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 'points': this.points.map(point => [parseInt(point.x, 10), parseInt(point.y, 10)]), 'shape': `${this.image.height}x${this.image.width}`, 'label': 'car', 'camera': 'http://localhost:8000/rest/Camera/1/' })
    })
    .then(response => response.json())
    .then(data => {
      console.log(data);
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
  afterDrawing();
}

function afterDrawing() {
  selectAreaBtn.style.display = 'block';
  contourArea.clear();
}



document.addEventListener('DOMContentLoaded', function() {
    const arrow = document.querySelector('.updateLabel');
    const popup = document.querySelector('.popup');
    const popupContent = document.querySelector('.popup-content');

    arrow.addEventListener('click', function() {
        fetchData();
        popup.classList.toggle('active');
    });

    const updateButton = document.querySelector('.updateLabel');
    updateButton.addEventListener('click', function() {
        fetchData();
    });

    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-button')) {
            const areaUrl = event.target.dataset.areaUrl;
            const areaId = extractNumberFromUrl(areaUrl);

            fetch(`/rest/DetectionArea/${areaId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            }).then(() => {
                fetchData();
            });
        }
    });

    function fetchData() {
        fetch('/rest/DetectionArea/?camera=http:///rest/Camera/1/&ordering=id', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            popupContent.innerHTML = '';

            const slider = document.createElement('div');
            slider.className = 'slick-slider';

            data.forEach(item => {
                const slide = document.createElement('div');
                slide.className = 'slick-slide';

                const nameLabel = document.createElement('p');
                nameLabel.textContent = 'Id: ' + extractNumberFromUrl(item.url);
                slide.appendChild(nameLabel);

                const labelInput = document.createElement('input');
                labelInput.type = 'text';
                labelInput.value = item.label;
                slide.appendChild(labelInput);

                const deleteButton = document.createElement('button');
                deleteButton.className = 'delete-button';
                deleteButton.innerHTML = '&#10006;';
                deleteButton.dataset.areaUrl = item.url;
                slide.appendChild(deleteButton);

                slider.appendChild(slide);
            });

            popupContent.appendChild(slider);

            $(slider).slick({
                slidesToShow: 5,
                slidesToScroll: 5,
                vertical: true,
                dots: true,
                arrows: false,
                infinite: true,
                adaptiveHeight: true,
            });

            const updateButton = document.createElement('button');
            updateButton.className = 'update-button';
            updateButton.textContent = 'Update Label';
            updateButton.addEventListener('click', function() {
                const labelInputs = document.querySelectorAll('.popup-content input');
                labelInputs.forEach((input, index) => {
                    const areaUrl = data[index].url;
                    const areaId = extractNumberFromUrl(areaUrl);
                    const newLabel = input.value;

                    fetch(`/rest/DetectionArea/${areaId}/`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: JSON.stringify({
                            label: newLabel,
                        }),
                    });
                });
            });

            popupContent.appendChild(updateButton);
        });
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});

function extractNumberFromUrl(url) {
    const match = url.match(/\/(\d+)\/$/);
    return match ? parseInt(match[1], 10) : null;
}