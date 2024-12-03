document.addEventListener('DOMContentLoaded', function () {
  loadSchedule();

  const form = document.getElementById('edit-schedule-form');
  form.addEventListener('submit', handleSubmit);

  const addRowBtn = document.getElementById('add-row-btn');
  addRowBtn.addEventListener('click', addRow);
});

async function loadSchedule() {
  try {
    const res = await fetch('/get_schedule');
    const data = await res.json();
    if (Array.isArray(data)) {
      // Проверка, что data - массив
      populateTable(data);
    } else {
      console.error('Полученные данные не являются массивом');
    }
  } catch (error) {
    console.error('Ошибка при загрузке расписания:', error);
  }
}

function populateTable(data) {
  const tableBody = document.getElementById('schedule-table-body');
  tableBody.innerHTML = '';

  const daysOrder = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'];

  data.sort((a, b) => {
    return (
      daysOrder.indexOf(a.day) - daysOrder.indexOf(b.day) || a.pair - b.pair
    );
  });

  data.forEach((entry) => {
    const row = document.createElement('tr');
    row.dataset.id = entry.id; // Добавляем id как атрибут data

    const dayCell = document.createElement('td');
    const daySelect = createSelect(
      ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'],
      entry.day
    );
    dayCell.appendChild(daySelect);
    row.appendChild(dayCell);

    ['pair', 'time', 'end_time', 'subject', 'professor', 'room'].forEach(
      (field) => {
        const td = document.createElement('td');
        const input = document.createElement('input');
        input.type = field === 'pair' ? 'number' : 'text';
        if (field === 'time' || field === 'end_time') input.type = 'time';
        input.value = entry[field];
        td.appendChild(input);
        row.appendChild(td);
      }
    );

    const actionCell = document.createElement('td');
    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Удалить';
    deleteButton.addEventListener('click', () => deleteRow(entry.id, row));
    actionCell.appendChild(deleteButton);
    row.appendChild(actionCell);

    tableBody.appendChild(row);
  });
}

function createSelect(options, selectedOption) {
  const select = document.createElement('select');
  options.forEach((option) => {
    const opt = document.createElement('option');
    opt.value = option;
    opt.textContent = option;
    if (option === selectedOption) {
      opt.selected = true;
    }
    select.appendChild(opt);
  });
  return select;
}

function addRow() {
  const tableBody = document.getElementById('schedule-table-body');
  const row = document.createElement('tr');

  const dayCell = document.createElement('td');
  const daySelect = createSelect(
    ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'],
    'Понедельник'
  );
  dayCell.appendChild(daySelect);
  row.appendChild(dayCell);

  ['pair', 'time', 'end_time', 'subject', 'professor', 'room'].forEach(
    (field) => {
      const td = document.createElement('td');
      const input = document.createElement('input');
      input.type = field === 'pair' ? 'number' : 'text';
      if (field === 'time' || field === 'end_time') input.type = 'time';
      td.appendChild(input);
      row.appendChild(td);
    }
  );

  const actionCell = document.createElement('td');
  const deleteButton = document.createElement('button');
  deleteButton.textContent = 'Удалить';
  deleteButton.addEventListener('click', () => deleteRow(null, row));
  actionCell.appendChild(deleteButton);
  row.appendChild(actionCell);

  tableBody.appendChild(row);
}

async function deleteRow(id, row) {
  if (id) {
    try {
      await fetch(`/delete_schedule/${id}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error('Ошибка при удалении пары:', error);
      return;
    }
  }
  row.remove();
}

async function handleSubmit(event) {
  event.preventDefault();

  const rows = document
    .getElementById('schedule-table-body')
    .getElementsByTagName('tr');
  const data = [];

  for (let row of rows) {
    const id = row.dataset.id;
    const select = row.getElementsByTagName('select')[0];
    const inputs = row.getElementsByTagName('input');
    const entry = {
      id: id || null,
      day: select.value,
      pair: inputs[0].value,
      time: inputs[1].value,
      end_time: inputs[2].value,
      subject: inputs[3].value,
      professor: inputs[4].value,
      room: inputs[5].value,
    };
    data.push(entry);
  }

  try {
    const res = await fetch('/update_schedule', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    const result = await res.json();
    alert(result.message);
    loadSchedule(); // Перезагрузить расписание после обновления
  } catch (error) {
    console.error('Ошибка при сохранении расписания:', error);
  }
}
