var plot_module = function() {

  var get_pl_line_chart = function(language_matches, langs) {
    var date_list = ['x'];
    var lang_counts = {};
    var columns = [];

    var index1, index2;
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
    console.log(columns);
    return c3.generate({
      data: {
        x: 'x',
        columns: columns
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

  return {
    get_pl_line_chart: get_pl_line_chart,
    get_pl_venn_diagram: get_venn_diagram
  };
}();
