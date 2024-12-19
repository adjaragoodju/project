document.addEventListener('DOMContentLoaded', function () {
  loadSchedule();
});

async function loadSchedule() {
  try {
    const res = await fetch('/get_schedule');
    const data = await res.json();
    console.log(data);
    if (Array.isArray(data)) {
      createScheduleTable(data);
    } else {
      console.error('Полученные данные не являются массивом');
    }
  } catch (error) {
    console.error('Ошибка при загрузке расписания:', error);
  }
}

function createScheduleTable(data) {
  const scheduleContainer = document.querySelector('#scheduleContainer');
  scheduleContainer.innerHTML = '';

  const daysOfWeek = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'];

  daysOfWeek.forEach((day) => {
    const dayData = data.filter((entry) => entry.day === day);

    if (dayData.length > 0) {
      const item = document.createElement('div');
      item.className = 'table-responsive';

      const table = document.createElement('table');
      table.classList.add('table', 'table-bordered', 'table-hover');

      const dayText = document.createElement('h4');
      dayText.textContent = day;
      item.appendChild(dayText);
      item.appendChild(table);

      const thead = document.createElement('thead');
      const headerRow = document.createElement('tr');
      [
        'Пара',
        'Начало',
        'Конец',
        'Дисциплина',
        'Преподаватель',
        'Аудитория',
      ].forEach((text) => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
      });
      thead.appendChild(headerRow);
      table.appendChild(thead);

      const tbody = document.createElement('tbody');
      dayData.forEach((entry) => {
        const row = document.createElement('tr');
        ['pair', 'time', 'end_time', 'subject', 'professor', 'room'].forEach(
          (field) => {
            const td = document.createElement('td');
            td.textContent = entry[field];
            row.appendChild(td);
          }
        );
        tbody.appendChild(row);
      });
      table.appendChild(tbody);

      scheduleContainer.appendChild(item);
    }
  });
}
