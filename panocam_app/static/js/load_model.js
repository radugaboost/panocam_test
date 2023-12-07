document.addEventListener("DOMContentLoaded", function() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
        var model_id = checkbox.id.split('-')[1];
        var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        var previousState = checkbox.checked;

        checkbox.addEventListener("change", function() {
            var active = this.checked;

            if (active !== previousState) {
                $.ajax({
                    type: "POST",
                    url: "/change_model_status/" + model_id + "/",
                    data: {
                        csrfmiddlewaretoken: csrftoken,
                        active: active,
                    },
                    success: function() {
                        // Обработчик успешной отправки
                    },
                });
                previousState = active;
            }
        });

        var deleteButton = document.querySelector('.delete-button[data-model-id="' + model_id + '"]');

        if (deleteButton) {
            deleteButton.addEventListener("click", function() {
                $.ajax({
                    type: "POST",
                    url: "/delete_model/" + model_id + "/",
                    data: {
                        csrfmiddlewaretoken: csrftoken,
                    },
                    success: function() {
                        location.reload();
                    },
                });
            });
        }
    });
});
