function sortTableNum(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("myTable");
  switching = true;
  dir = "asc";
  while (switching) {
    switching = false;
    rows = table.rows;
    for (i = 1; i < (rows.length - 1); i++) {
      shouldSwitch = false;
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      
      x_symbol_last = x.innerHTML
      y_symbol_last = y.innerHTML
            if (x_symbol_last == 'None'){
        x_symbol_last = '-99.9'
      }
      if (y_symbol_last == 'None'){
        y_symbol_last = '-99.9'
      }
      if (dir == "asc") {
        if (Number(x_symbol_last) > Number(y_symbol_last)) {
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (Number(x_symbol_last) < Number(y_symbol_last)) {

          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {

      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
 
      switchcount ++;
    } else {
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}