document.addEventListener('DOMContentLoaded', function () {
  loadSchedule();
});

async function loadSchedule() {
  try {
    const res = await fetch('/get_schedule');
    const data = await res.json();
    console.log(data);
    if (Array.isArray(data)) {
      // Проверка, что data - массив
      createScheduleTable(data);
    } else {
      console.error('Полученные данные не являются массивом');
    }
  } catch (error) {
    console.error('Ошибка при загрузке расписания:', error);
  }
}

function createScheduleTable(data) {
  const scheduleContainer = document.querySelector('.scheduleContainer');
  scheduleContainer.innerHTML = '';

  const daysOfWeek = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'];

  daysOfWeek.forEach((day) => {
    const dayData = data.filter((entry) => entry.day === day);

    if (dayData.length > 0) {
      const table = document.createElement('table');
      table.classList.add('schedule-table');

      const caption = document.createElement('caption');
      caption.textContent = day;
      table.appendChild(caption);

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

      scheduleContainer.appendChild(table);
    }
  });
}
