function sortTable(n) {
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

      x_symbol_last = x.innerHTML.split(', ')[x.innerHTML.split(',').length - 1]
      y_symbol_last = y.innerHTML.split(', ')[y.innerHTML.split(',').length - 1]
      if (dir == "asc") {
        if (x_symbol_last.toLowerCase() > y_symbol_last.toLowerCase()) {
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x_symbol_last.toLowerCase() < y_symbol_last.toLowerCase()) {

          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {

      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;

      switchcount++;
    } else {
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}



let checkboxes = document.querySelectorAll('.location-checkbox')
let cropName = document.querySelectorAll('.crop-name')

let ids = []
let checkedLocations = []
let rows = document.querySelectorAll('.rows')
let all_checkboxes = document.querySelector(".all")

all_checkboxes.addEventListener('change', function () {

    rows.forEach(item => {
      if (this.checked){
        item.childNodes[1].firstElementChild.checked = true
        let checkbox = item.childNodes[1].firstElementChild
        let id = item.getAttribute('id')
        let dateTime = item.querySelector('.date-time').textContent
        let cropName = item.querySelector('.crop-name').textContent
        let locName = item.querySelector('.location-name').textContent
        if (checkbox.checked ==  true && !checkedLocations.includes(id)) {
          checkedLocations.push(id)
      
          console.log(checkedLocations);
          let template =
            `
            <tr id="location${id}" class="enter-weights-block">
            <td><span id="location${id}">${dateTime}</span></td>
            <td><span id="location${id}">${cropName}</span></td>
            <td><span id="location${id}">${locName}</span></td>
            <td><input id="locationInput${id}" type="text" data-id="${id}" placeholder="Enter index weights"></td>
            </tr>
          `
          document.querySelector('.weighted-results-content').innerHTML += template
      
        } 
      }
      else{
        item.childNodes[1].firstElementChild.checked = false
        let id = item.getAttribute('id')
        let index = checkedLocations.findIndex(x => x === id)
          checkedLocations.splice(index, 1)
          document.getElementById(`location${id}`).remove()
      }
      return checkedLocations
    })
});



rows.forEach(item => {
  item.addEventListener('click', () =>{
    console.log(item);
  })
})

checkboxes.forEach(item => {
  item.addEventListener('click', () => {
    let parent = item.parentNode
    let id = parent.parentNode.getAttribute('id')
    let dateTime = parent.parentNode.querySelector('.date-time').textContent
    let cropName = parent.parentNode.querySelector('.crop-name').textContent

    let locName = parent.parentNode.querySelector('.location-name').textContent

    if (item.checked && !checkedLocations.includes(id)) {
      checkedLocations.push(id)

      console.log(checkedLocations);
      let template =
        `
        <tr id="location${id}" class="enter-weights-block">
        <td><span id="location${id}">${dateTime}</span></td>
        <td><span id="location${id}">${cropName}</span></td>
        <td><span id="location${id}">${locName}</span></td>
        <td><input id="locationInput${id}" type="text" data-id="${id}" placeholder="Enter index weights"></td>
        </tr>
      `
      document.querySelector('.weighted-results-content').innerHTML += template

    } else {
      let index = checkedLocations.findIndex(x => x === id)
      checkedLocations.splice(index, 1)
      document.getElementById(`location${id}`).remove()

    }

    return checkedLocations
  })
})

document.getElementById('live-button').addEventListener('click', (e) => {
  if (checkedLocations.length != 0) {
    let inputHidden = document.getElementById('deleteindex')
    inputHidden.value = checkedLocations
  }
  else {
    e.preventDefault()
    let warning = document.querySelector('.live-warning')
    warning.classList.add('live-error')
    setTimeout(() => {
      warning.classList.remove('live-error')
    }, 3500);
  }
  setTimeout("", 5000);

})

document.getElementById('exportCsv').addEventListener('click', (e) => {
  if (checkedLocations.length != 0) {
    let inputHidden = document.getElementById('csvindex')
    inputHidden.value = checkedLocations

  }
  else {
    e.preventDefault()
    let warning = document.querySelector('.csv-warning')

    warning.classList.add('csv-error')

    setTimeout(() => {
      warning.classList.remove('csv-error')
    }, 3500);
  }
  setTimeout("", 5000);
})

document.getElementById('combine_button').addEventListener('click', (e) => {
  if (checkedLocations.length != 0) {
    let inputHidden = document.getElementById('combine_index')
    inputHidden.value = checkedLocations
  }
  else {
    e.preventDefault()
    let warning = document.querySelector('.combine-warning')

    warning.classList.add('combine-error')

    setTimeout(() => {
      warning.classList.remove('combine-error')
    }, 3500);
  }
  setTimeout("", 5000);
})

document.getElementById('createWeighted').addEventListener('click', (e) => {
  if (checkedLocations.length >= 2) {
    document.querySelector('.pcoded-content-popup').classList.add('open')
    document.querySelector('.popup-wrapper').classList.add('open')
  } else {
    e.preventDefault()
    let warning = document.querySelector('.warning')
    warning.classList.add('error')
    setTimeout(() => {
      warning.classList.remove('error')
    }, 3500);
  }
  setTimeout("", 5000);
})


function getValues() {
  let inputs = document.querySelectorAll('.popup-item input')
  let values = []
  for (let i = 0; i < inputs.length; i++) {
    if (parseInt(inputs[i].value)) {
      values.push(parseInt(inputs[i].value))
    }
  }
  if (values.length == inputs.length) {
    let inputHidden = document.getElementById('weightedResults')
    let inputinds = document.getElementById('inds')
    console.log(values);
    console.log(inputs);
    inputHidden.value = values
    inputinds.value = checkedLocations
  }
  else {
    return false;
  }
}

document.getElementById('createWeightedIndex').addEventListener('click', (e) => {
  let x = getValues();
  if (x === false) {
    e.preventDefault()
    alert('Missed or incorrect value')
  }
})

document.querySelector('.popup-close').addEventListener('click', () => {
  document.querySelector('.pcoded-content-popup').classList.remove('open')
  document.querySelector('.popup-wrapper').classList.remove('open')
})

var loc = document.querySelectorAll('.lngLat')
result = [];
for (var i = 0; i < loc.length; i++) {
  result.push(loc[i].textContent);
  let x = result[i].slice(0, 8);
  let y = result[i].slice(19, 28);
  let r = x + ', ' + y;

  document.getElementsByClassName('lngLat')[i].textContent = r;
}
let loc_names = []
let loc_name = document.querySelectorAll('.loc');
for (var i = 0; i < loc_name.length; i++) {
  loc_names.push(loc_name[i].textContent);
}


var x = document.getElementsByClassName("planting-date");


function dateFromDay(day) {
  var year = new Date().getFullYear();
  var date = new Date(year, 0); // initialize a date in `year-01-01`
  return new Date(date.setDate(day)); // add the number of days
}
for (var i = 0; i < x.length; i++) {
  let convertDate = dateFromDay(x[i].textContent).toDateString();
  x[i].innerHTML = convertDate
}




checkboxes.forEach(item => {
  item.addEventListener('click', () => {

    if (item.checked) {
      console.log(item);
    }

  })
})


