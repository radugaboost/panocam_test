let cameras = [];
let currentIndex = 0;

const imgElem = document.querySelector('#stream');

class Camera {
    constructor(options) {
        this.src = `/camera_stream/${options.cameraId}/`
        this.ip = options.ip;
        this.name = options.name;
        this.mask = options.mask;
        this.url = options.url
        this.configUrl = options.image_config;
        this.imageConfig = null;
        this.setImageConfig();
    }

    async setImageConfig() {
        try {
            const response = await fetch(
                this.configUrl,
                {
                    method: 'GET'
                }
            )
            const result = await response.json();
            this.imageConfig = {
                brightness: result.brightness,
                contrast: result.contrast,
                frame_rate: result.frame_rate,
                hue: result.hue,
                name: result.name,
                resolution: result.resolution,
                saturation: result.saturation,
                sharpness: result.sharpness,
                smoothing: result.smoothing
            };
        } catch (error) {
            console.log("Error", error);
        }
    };
}

async function get_cameras() {
    try {
        const response = await fetch(
            'http://localhost:8000/rest/Camera/',
            {
                method: 'GET'
            }
        )
        const result = await response.json();
        for (item in result) {
            const { ip, mask, name, url, image_config } = result[item];
            const cameraId = Number(item) + 1;
            cap = new Camera({ ip, mask, name, url, image_config, cameraId });
            cameras.push(cap);
        };
    } catch (error) {
        console.log("Error:", error);
    }

};

function nextStream () {
    if (currentIndex < cameras.length - 1) {
        currentIndex++;
    }
    imgElem.src = cameras[currentIndex].src;
}

function prevStream () {
    if (currentIndex > 0) {
        currentIndex--;
    }
    imgElem.src = cameras[currentIndex].src;
}

function begin_stream () {
    if (cameras.length > 0) {
        imgElem.src = cameras[currentIndex].src;
    } else {
        imgElem.src = '/static/images/placeholder.png';
    }
}

async function init() {
    try {
        await get_cameras();
        document.querySelector('.spinner-border').style.display = "none";
        begin_stream();
        const arrows = Array.from(document.querySelectorAll('.arrow-6')).slice(0, 2);
        imgElem.style.display = 'block';
        for (i in arrows) {
            arrows[i].style.display = 'block';
        }
    } catch (error) {
        console.error(error);
    }
}
  
init();
