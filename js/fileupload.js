(function(){
    "use strict";

    var Dropzone = require("dropzone");
    var cookie = require("cookie");
    var fixOrientation = require('fix-orientation');
    var toBlob = require("canvas-to-blob");
    toBlob.init()

    function uploadFile(blob) {
        var oldFile = imageDropzone.files[0];
        blob.accepted = oldFile.accepted;
        blob.lastModified = Date.now();
        blob.lastModifiedDate = new Date();
        blob.name = oldFile.name;
        blob.previewElement = oldFile.previewElement;
        blob.previewTemplate = oldFile.previewTemplate;
        blob.status = oldFile.status;
        blob.upload = {
            bytesSent: 0,
            progress: 0,
            total: blob.size
        };
        blob.webkitRelativePath = oldFile.webkitRelativePath;
        imageDropzone.files[0] = blob;
        imageDropzone.processQueue();
    }

    function scaleImageToCanvas(image, dwidth, dheight) {
        var scaleRatio = 1;
        var sourceWidth = image.naturalWidth;
        var sourceHeight = image.naturalHeight;
        if (sourceWidth > dwidth || sourceHeight > dheight) {
            var widthRatio = dwidth / sourceWidth;
            var heightRatio = dheight / sourceHeight;
            scaleRatio = Math.min(widthRatio, heightRatio);
        }
        var canvas = document.createElement("canvas");
        canvas.width = sourceWidth * scaleRatio;
        canvas.height = sourceHeight * scaleRatio;
        var ctx = canvas.getContext("2d");
        ctx.scale(scaleRatio, scaleRatio);
        ctx.drawImage(image, 0, 0);
        canvas.toBlob(uploadFile, "image/jpeg", 1);
    }

    function rotateAndScaleFile(file, dwidth, dheight) {
        var reader = new FileReader();
        reader.onload = (function(readerFile) {
            return function(e) {
                fixOrientation(e.target.result, { image: true }, function (fixed, image) {
                    var waitForImg = setInterval(function() {
                        if (image.naturalWidth && image.naturalHeight) {
                            clearInterval(waitForImg);
                            scaleImageToCanvas(image, dwidth, dheight);
                        }
                    }, 30);
                });
            };
        })(file);
        reader.readAsDataURL(file);
    }

    // Dropzone options
    Dropzone.options.regImageUploader = {
        headers: {'X-CSRFToken': cookie.parse(document.cookie).csrftoken},
        acceptedFiles: "image/*",
        autoProcessQueue: false,
        maxFiles: 1,

        init: function() {
            window.imageDropzone = this;
            this.on("success", function(file, response) {
                var form = document.forms.mainForm;
                form.photo.value = response.filename;
            });
            this.on("addedfile", function(file){
                rotateAndScaleFile(file, 600, 800);
            });
        }
    };
}());
