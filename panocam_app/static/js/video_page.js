document.addEventListener('DOMContentLoaded', () => {
  const videoId = extractVideoIdFromUrl();

    fetch(`/get_video_data/${videoId}/`)
    .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(videoData => {
        displayVideoInfo(videoData);
    })
    .catch(error => {
        console.error('Ошибка при получении данных о видео:', error);
        if (error instanceof TypeError || (error.response && error.response.status >= 400 && error.response.status < 500)) {
            window.location.href = '/videos';
        }
    });


  function extractVideoIdFromUrl() {
    const url = window.location.href;
    const parts = url.split('/');
    return parts[parts.length - 2];
  }

    function getDate(dateTimeString) {
        const dateTime = new Date(dateTimeString);
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return dateTime.toLocaleDateString('en-US', options);
    }

    function getTime(dateTimeString) {
        const dateTime = new Date(dateTimeString);
        const options = { hour: 'numeric', minute: 'numeric' };
        return dateTime.toLocaleTimeString('en-US', options);
    }
  function displayVideoInfo(videoData) {
    const videoInfoDiv = document.getElementById('videoInfo');
    videoInfoDiv.innerHTML = `
        <div class='ml-4'>
            <h3 class="fw-bold">${videoData.name}</h3>
            <div class="row mt-4">
                <div class="col-md-8">
                    <div class="mb-3">
                        <p class="h5"><strong>Start:</strong></p>
                        <hr class="my-1">
                        <p class="mb-0"><strong>Date:</strong> <span class="h6">${getDate(videoData.start)}</span></p>
                        <p class="mb-0"><strong>Time:</strong> <span class="h6">${getTime(videoData.start)}</span></p>
                    </div>
                </div>
            </div>
            <div class="row mt-4">
                <div class="col-md-8">
                    <div class="mb-4">
                        <p class="h5"><strong>End:</strong></p>
                        <hr class="my-1">
                        <p class="mb-0"><strong>Date:</strong> <span class="h6">${getDate(videoData.end)}</span></p>
                        <p class="mb-0"><strong>Time:</strong> <span class="h6">${getTime(videoData.end)}</span></p>
                    </div>
                </div>
            </div>
        </div>
    `;
  }
  function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) {
        return parts.pop().split(';').shift();
      }
    }

fetch(`/get_video_file/${videoId}/`)
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.blob();
  })
  .then(videoBlob => {
    const videoPlayer = document.getElementById('videoPlayer');
    videoPlayer.src = URL.createObjectURL(videoBlob);
  })
  .catch(error => {
    console.error('Ошибка при получении видеофайла:', error);
    if (error instanceof TypeError || (error.response && error.response.status >= 400 && error.response.status < 500)) {
      window.location.href = '/video';
    }
  });

  const deleteButton = document.getElementById('deleteButton');
    deleteButton.addEventListener('click', () => {
      console.log("test")
      const csrfToken = getCookie('csrftoken');
      fetch(`/drop_video_record/${videoId}/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        }
      })
      .then(response => {
        if (response.status !== 204) {
          throw new Error('Network response was not ok');
        }
        console.log('Видео успешно удалено');
        window.location = '/videos';
      })
      .catch(error => {
        console.error('Ошибка при удалении видео:', error);
        if (error instanceof TypeError || (error.response && error.response.status >= 400 && error.response.status < 500)) {
          window.location.href = '/videos';
        }
      });
    });
});
