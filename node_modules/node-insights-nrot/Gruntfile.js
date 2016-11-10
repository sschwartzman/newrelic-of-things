'use strict';

var path = require('path');

module.exports = function (grunt) {

  require('load-grunt-tasks')(grunt);
  require('time-grunt')(grunt);

  grunt.initConfig({

    settings: {
    },

    clean: {
      node: ['./node_modules'],
      docs: ['./docs'],
      coverage: {
        src: ['./coverage']
      }
    },

    env : {
      options : {
      },
      test : {
        NODE_ENV : 'test'
      }
    },

    exec: {
      istanbul: {
        cmd: function () {
          var files = [
            grunt.file.expand('database/tests/*.js').join(' '),
            grunt.file.expand('database/models/tests/*.js').join(' '),
            grunt.file.expand('tests/*.js').join(' ')
          ];
          var cover = 'istanbul cover --x "" node_modules/mocha/bin/_mocha -- --timeout 60000 --reporter spec' + files.join(' ');
          var report = 'istanbul' + ' report ' + 'cobertura';
          return cover + ' && ' + report;
        }
      },
      mocha: {
        cmd: function runMocha(xarg) {
          var src = [];
          var arg = xarg ? xarg.toLowerCase() : '';
          if (arg === 'some-subtask'){
            src = [ ];
          } else {
            src = [
              'tests/*.js',
              '!node_modules/**/*.js'
            ];
          }
          var files = grunt.file.expand(src);
          var bin = path.resolve(__dirname, './node_modules/.bin/mocha');
          var options = ' --colors --harmony --reporter spec --timeout 20000 ';
          var cmd = bin + options + files.join(' ');
          console.log(cmd);
          return cmd;
        }
      }
    },

    jsdoc : {
      dist : {
        src: ['*.js', '!Gruntfile.js'],
        options: {
          destination: 'docs'
        }
      }
    }

  });

  grunt.registerTask('coverage', ['clean:coverage', 'env:test', 'exec:istanbul']);
  grunt.registerTask('docs', [ 'clean:docs', 'jsdoc' ]);

  grunt.registerTask('test', 'Run Tests', function () {
    grunt.task.run(['env:test', 'exec:mocha:all']);
  });

  grunt.registerTask('default', ['test']);

};

