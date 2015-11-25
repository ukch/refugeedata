(function(){
    "use strict";

    var Dropzone = require("dropzone");
    var cookie = require("cookie");

    // Dropzone options
    Dropzone.options.regImageUploader = {
        headers: {'X-CSRFToken': cookie.parse(document.cookie).csrftoken},
        acceptedFiles: "image/*",
        maxFiles: 1,
        init: function() {
            this.on("success", function(file, response) {
                var form = document.forms.mainForm;
                form.photo.value = response.filename;
            });
        }
    };
}());
