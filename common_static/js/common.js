$(document).ready(function(){
      $('#sum').click(function(){
          var a = $("#a").val();
          var b = $("#b").val();
          var c = $("#c").val();
          var tbody ="";
          tbody +="<tr><th>" + "IP" + "</th> <th>" + "unreachable" + "</th><th>"+ "skipped" +"</th><th>"+ "ok" +"</th><th>"+"changed"+"</th><th>"+"failures"+"</th></tr>";
          $.getJSON('/playbook/',{'a':a,'b':b,'c':c},function(ret){
               $.each(ret,function(index,values){
                           var trs = "";
                           trs += "<tr><td>" + index + "</td> <td>" + values['unreachable'] + "</td><td>"+ values['skipped'] +"</td><td>"+values['ok'] +"</td><td>"+values['changed']+"</td><td>"+values['failures']+"</td></tr>";
                           tbody += trs;
                });
                           $('#customers').html('')
                           $('#customers').append(tbody);

          });
     });
});
