(function() {
    "use strict";

    var _assign = require("lodash.assign");
    var gulp = require('gulp');
    var sass = require('gulp-sass');
    require('gulp-watch');
    var minifycss = require('gulp-clean-css');
    var rename = require('gulp-rename');
    var glob = require('glob');
    var gzip = require('gulp-gzip');
    var livereload = require('gulp-livereload');
    var watchify = require('watchify');
    var browserify = require('browserify');
    var source = require('vinyl-source-stream');
    var buffer = require('vinyl-buffer');
    var log = require('gulplog');
    var sourcemaps = require('gulp-sourcemaps');

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
            .pipe(livereload({ start: livereload.server ? true : false }));
    });

    /* Watch Files For Changes */
    gulp.task('watch', function() {
        livereload.listen();
        gulp.watch('scss/*.scss', gulp.task('sass'));

        /* Trigger a live reload on any Django template changes */
        gulp.watch('**/templates/*').on('change', livereload.changed);

    });

    var jsFiles = glob.sync('./js/**/*.js');
    var b = watchify(browserify(_assign(watchify.args, {
        entries: jsFiles,
    })));

    // Hack to enable configurable watchify watching
    gulp.task('enable-watch-mode', function(done) {
        b.on('update', bundle); // on any dep update, runs the bundler
        b.on('log', log.info); // output build logs to terminal
        done()
    });

    function bundle() {
        return b.bundle()
        // log errors if they happen
            .on('error', log.error.bind(log, 'Browserify Error'))
            .pipe(source('bundle.js'))
        // optional, remove if you don't need to buffer file contents
            .pipe(buffer())
        // optional, remove if you dont want sourcemaps
            .pipe(sourcemaps.init({loadMaps: true})) // loads map from browserify file
        // Add transformation tasks to the pipeline here.
            .pipe(sourcemaps.write('./')) // writes .map file
            .pipe(gulp.dest('refugeedata/static/js/'));
    }
    gulp.task('browserify', bundle);

    gulp.task('watchify', gulp.series('enable-watch-mode', 'browserify'));

    gulp.task('default', gulp.series('sass', 'watch', 'watchify'));
    gulp.task('build', gulp.series('sass', 'browserify'));
}());
