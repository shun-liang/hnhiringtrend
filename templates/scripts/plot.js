var plot_module = function() {
  var language_matches;
  var github_colors;

  var init_module = function(matches, colors) { 
    language_matches = matches;
    github_colors = colors;
  }

  var get_pl_line_chart = function(langs) {
    console.log(langs);
    //console.log("Plotting..." + github_colors);
    var date_list = ['x'];
    var lang_counts = {};
    var columns = [];

    var index;
    //console.log(github_colors);
    console.log(_get_pl_color_codes(langs));
    for(index = 0; index < langs.length; index++) {
      lang_counts[langs[index]] = [langs[index]];
    }

    for(var key in language_matches) {
      if(language_matches.hasOwnProperty(key)) {
        post_date = new Date(key * 1000);
        date_list.push(post_date);
        for(index = 0; index < langs.length; index++) {
          var lang = langs[index];
          lang_counts[lang].push(language_matches[key][lang].length);
        }
      }
    }
    columns.push(date_list);
    for(var lang in lang_counts) {
      if(lang_counts.hasOwnProperty(lang)) {
        columns.push(lang_counts[lang]);
      }
    }
    //console.log(columns);
    return c3.generate({
      bindto: '#pl-line-chart',
      data: {
        x: 'x',
        columns: columns,
        colors: _get_pl_color_codes(langs),
        selection: {
          draggable: true
        }
      },
      axis: {
        x: {
          type: 'timeseries',
          tick: {
            format: '%Y-%m'
          }
        }
      },
     tooltip:{
       grouped: false
     }
    })
  }

  var get_venn_diagram = function() {
  };

  var _get_pl_color_codes = function(langs) {
    var index;
    var color_codes = {};
    console.log(langs);
    for(index = 0; index < langs.length; index++) {
      lang = langs[index];
      //console.log(lang);
      //console.log(github_colors[lang]);
      if(lang == 'Assembly Language') {
        color_codes[lang] = github_colors['Assembly'];
      }
      else if(lang == 'Bash'){ 
        color_codes[lang] = github_colors['Shell'];
      }
      else {
        color_codes[lang] = github_colors[lang];
      }

    }
    return color_codes;
  };

  return {
    init_module: init_module,
    get_pl_line_chart: get_pl_line_chart,
    get_pl_venn_diagram: get_venn_diagram
  };
}();
