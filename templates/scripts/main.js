window.onload = function() {
  //console.log(github_colors);
  plot_module.init_module(languages_matches, github_colors, total_posts.total_posts);
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
