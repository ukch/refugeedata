(function() {
    "use strict";

    var gulp = require('gulp');
    var sass = require('gulp-sass');
    require('gulp-watch');
    var minifycss = require('gulp-minify-css');
    var rename = require('gulp-rename');
    var gzip = require('gulp-gzip');
    var livereload = require('gulp-livereload');
    var watchify = require('gulp-watchify');

    var gzip_options = {
        threshold: '1kb',
        gzipOptions: {
            level: 9
        }
    };

    /* Compile Our Sass */
    gulp.task('sass', function() {
        return gulp.src('scss/*.scss')
            .pipe(sass())
            .pipe(gulp.dest('refugeedata/static/css'))
            .pipe(rename({suffix: '.min'}))
            .pipe(minifycss())
            .pipe(gulp.dest('refugeedata/static/css'))
            .pipe(gzip(gzip_options))
            .pipe(gulp.dest('refugeedata/static/css'))
            .pipe(livereload());
    });

    /* Watch Files For Changes */
    gulp.task('watch', function() {
        livereload.listen();
        gulp.watch('scss/*.scss', ['sass']);

        /* Trigger a live reload on any Django template changes */
        gulp.watch('**/templates/*').on('change', livereload.changed);

    });

    // Hack to enable configurable watchify watching
    var watching = false;
    gulp.task('enable-watch-mode', function() { watching = true; });

    // Browserify and copy js files
    gulp.task('browserify', watchify(function(watchify) {
        var bundlePaths = {
            src: [
                'js/**/*.js',
            ],
            dest: 'refugeedata/static/js/'
        };
        return gulp.src(bundlePaths.src)
            .pipe(watchify({
                watch:watching
            }))
            .pipe(gulp.dest(bundlePaths.dest));
    }));

    gulp.task('watchify', ['enable-watch-mode', 'browserify']);

    gulp.task('default', ['sass', 'watch', 'watchify']);
    gulp.task('build', ['sass', 'browserify']);
}());
