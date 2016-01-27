window.onload = function() {
  //console.log(github_colors);
  plot_module.init_module(language_matches, github_colors);
  var pl_line_chart = plot_module.get_pl_line_chart(skills.languages);
  //console.log(language_matches);
  //console.log(pl_line_chart);
  var app_vm = new Vue({
    el: '#main-pane',
    data: {
      title: 'Plot'
    }
  });
}
