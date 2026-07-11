'use strict';

const state = {
  token: localStorage.getItem('ht_token') || null,
  username: null,
  habits: [],
  selectedHabitId: null,
  records: [],
};

let recordsByDate = {};
let editingRecordId = null;
let currentDayKey = null;
let habitModalMode = 'create';
let habitModalEditingId = null;

// ---------- API helper ----------

async function api(path, { method = 'GET', json = null, form = null } = {}) {
  const headers = {};
  let body;
  if (json !== null) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(json);
  } else if (form !== null) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams(form).toString();
  }
  if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

  const res = await fetch(path, { method, headers, body });

  if (res.status === 401) {
    clearSession();
    showAuthView();
    throw new Error('Session expired. Please log in again.');
  }

  if (!res.ok) {
    let detail = res.statusText || `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (data && data.detail) {
        detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch (e) { /* ignore */ }
    throw new Error(detail);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

// ---------- session ----------

function clearSession() {
  state.token = null;
  state.username = null;
  localStorage.removeItem('ht_token');
}

function showAuthView() {
  document.getElementById('authView').classList.remove('hidden');
  document.getElementById('appView').classList.add('hidden');
  document.getElementById('userBox').classList.add('hidden');
}

function showAppView() {
  document.getElementById('authView').classList.add('hidden');
  document.getElementById('appView').classList.remove('hidden');
  document.getElementById('userBox').classList.remove('hidden');
  document.getElementById('usernameLabel').textContent = state.username;
}

async function boot() {
  if (!state.token) {
    showAuthView();
    return;
  }
  try {
    const me = await api('/users/user/me/');
    state.username = me.username;
    showAppView();
    await loadHabits();
  } catch (e) {
    clearSession();
    showAuthView();
  }
}

// ---------- toast ----------

let toastTimer = null;
function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add('hidden'), 3000);
}

// ---------- auth forms ----------

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const target = tab.dataset.tab;
    document.getElementById('loginForm').classList.toggle('hidden', target !== 'login');
    document.getElementById('registerForm').classList.toggle('hidden', target !== 'register');
  });
});

document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('loginError');
  errEl.textContent = '';
  const fd = new FormData(e.target);
  try {
    const tokenRes = await api('/users/token', {
      method: 'POST',
      form: { username: fd.get('username'), password: fd.get('password') },
    });
    state.token = tokenRes.access_token;
    localStorage.setItem('ht_token', state.token);
    await boot();
  } catch (err) {
    errEl.textContent = err.message;
  }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('registerError');
  errEl.textContent = '';
  const fd = new FormData(e.target);
  const username = fd.get('username');
  const password = fd.get('password');
  try {
    await api('/users/create_user', { method: 'POST', json: { username, password } });
    const tokenRes = await api('/users/token', { method: 'POST', form: { username, password } });
    state.token = tokenRes.access_token;
    localStorage.setItem('ht_token', state.token);
    await boot();
  } catch (err) {
    errEl.textContent = err.message;
  }
});

document.getElementById('logoutBtn').addEventListener('click', () => {
  clearSession();
  state.habits = [];
  state.selectedHabitId = null;
  state.records = [];
  showAuthView();
});

// ---------- habits ----------

async function loadHabits() {
  state.habits = await api('/habits/get_all');
  renderHabitsList();
  if (state.selectedHabitId && state.habits.some(h => h.id === state.selectedHabitId)) {
    await selectHabit(state.selectedHabitId);
  } else if (state.habits.length > 0) {
    await selectHabit(state.habits[0].id);
  } else {
    state.selectedHabitId = null;
    document.getElementById('emptyState').classList.remove('hidden');
    document.getElementById('habitDetail').classList.add('hidden');
  }
}

function renderHabitsList() {
  const list = document.getElementById('habitsList');
  list.innerHTML = '';
  for (const habit of state.habits) {
    const card = document.createElement('div');
    card.className = 'habit-card' + (habit.id === state.selectedHabitId ? ' selected' : '');
    const name = document.createElement('div');
    name.className = 'h-name';
    name.textContent = habit.name;
    const desc = document.createElement('div');
    desc.className = 'h-desc';
    desc.textContent = habit.description;
    card.appendChild(name);
    card.appendChild(desc);
    card.addEventListener('click', () => selectHabit(habit.id));
    list.appendChild(card);
  }
}

async function selectHabit(habitId) {
  state.selectedHabitId = habitId;
  renderHabitsList();
  const habit = state.habits.find(h => h.id === habitId);
  if (!habit) return;

  document.getElementById('emptyState').classList.add('hidden');
  document.getElementById('habitDetail').classList.remove('hidden');
  document.getElementById('habitName').textContent = habit.name;
  document.getElementById('habitDescription').textContent = habit.description;
  document.getElementById('habitCreated').textContent =
    'Created ' + new Date(habit.create_at).toLocaleDateString();

  await loadRecords(habitId);
}

function openHabitModal(mode, habit) {
  habitModalMode = mode;
  habitModalEditingId = habit ? habit.id : null;
  document.getElementById('habitModalTitle').textContent = mode === 'create' ? 'New habit' : 'Edit habit';
  document.getElementById('habitFormName').value = habit ? habit.name : '';
  document.getElementById('habitFormDescription').value = habit ? habit.description : '';
  document.getElementById('habitModalError').textContent = '';
  document.getElementById('habitModalBackdrop').classList.remove('hidden');
}

function closeHabitModal() {
  document.getElementById('habitModalBackdrop').classList.add('hidden');
}

document.getElementById('newHabitBtn').addEventListener('click', () => openHabitModal('create', null));
document.getElementById('editHabitBtn').addEventListener('click', () => {
  const habit = state.habits.find(h => h.id === state.selectedHabitId);
  if (habit) openHabitModal('edit', habit);
});
document.getElementById('habitModalCancel').addEventListener('click', closeHabitModal);

document.getElementById('habitModalForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('habitModalError');
  errEl.textContent = '';
  const name = document.getElementById('habitFormName').value.trim();
  const description = document.getElementById('habitFormDescription').value.trim();
  try {
    if (habitModalMode === 'create') {
      const created = await api('/habits/create_habit', { method: 'POST', json: { name, description } });
      closeHabitModal();
      await loadHabits();
      if (created && created.id) await selectHabit(created.id);
      toast('Habit created');
    } else {
      await api(`/habits/${habitModalEditingId}`, { method: 'PUT', json: { name, description } });
      closeHabitModal();
      await loadHabits();
      toast('Habit updated');
    }
  } catch (err) {
    errEl.textContent = err.message;
  }
});

document.getElementById('deleteHabitBtn').addEventListener('click', async () => {
  const habit = state.habits.find(h => h.id === state.selectedHabitId);
  if (!habit) return;
  if (!confirm(`Delete habit "${habit.name}"? This also deletes all of its records.`)) return;
  try {
    await api(`/habits/${habit.id}`, { method: 'DELETE' });
    state.selectedHabitId = null;
    toast('Habit deleted');
    await loadHabits();
  } catch (err) {
    toast('Failed to delete: ' + err.message);
  }
});

// ---------- records ----------

async function loadRecords(habitId) {
  state.records = await api(`/habit_records/${habitId}`);
  buildRecordsByDate();
  renderCalendar();
  renderRecordsTable();
}

function dateKeyUTC(d) {
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, '0');
  const day = String(d.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

// The API returns naive datetime strings with no timezone suffix (SQLite drops
// tzinfo on storage), so `new Date(r.date)` would get parsed as local time and
// re-reading it through getUTC* would shift the day. Read the calendar day as
// plain text instead - it's exactly what we sent (YYYY-MM-DDT00:00:00...).
function dateKeyFromRecord(r) {
  return r.date.slice(0, 10);
}

function buildRecordsByDate() {
  recordsByDate = {};
  for (const r of state.records) {
    const key = dateKeyFromRecord(r);
    if (!recordsByDate[key]) recordsByDate[key] = { total: 0, items: [] };
    recordsByDate[key].total += r.value;
    recordsByDate[key].items.push(r);
  }
}

function computeThresholds() {
  const positives = Object.values(recordsByDate)
    .map(v => v.total)
    .filter(v => v > 0)
    .sort((a, b) => a - b);
  if (positives.length === 0) return [1, 2, 3];
  const q = (p) => positives[Math.min(positives.length - 1, Math.floor(p * (positives.length - 1)))];
  const t1 = q(0.25), t2 = q(0.5), t3 = q(0.75);
  return [t1, Math.max(t2, t1), Math.max(t3, t2, t1)];
}

function levelFor(total, th) {
  if (!total || total <= 0) return 0;
  if (total <= th[0]) return 1;
  if (total <= th[1]) return 2;
  if (total <= th[2]) return 3;
  return 4;
}

function renderCalendar() {
  const calendar = document.getElementById('calendar');
  calendar.innerHTML = '';

  const now = new Date();
  const today = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  const WEEKS = 53;
  const start = new Date(today);
  start.setUTCDate(start.getUTCDate() - (WEEKS * 7 - 1));
  start.setUTCDate(start.getUTCDate() - start.getUTCDay());

  const days = [];
  const cursor = new Date(start);
  while (cursor <= today) {
    days.push(new Date(cursor));
    cursor.setUTCDate(cursor.getUTCDate() + 1);
  }
  while (days.length % 7 !== 0) days.push(null);

  const weeks = [];
  for (let i = 0; i < days.length; i += 7) weeks.push(days.slice(i, i + 7));

  const thresholds = computeThresholds();

  for (const week of weeks) {
    const firstOfMonthDay = week.find(d => d && d.getUTCDate() === 1);
    const label = document.createElement('div');
    label.className = 'month-label';
    if (firstOfMonthDay) {
      label.textContent = firstOfMonthDay.toLocaleString(undefined, { month: 'short', timeZone: 'UTC' });
    }
    calendar.appendChild(label);

    for (const day of week) {
      const cell = document.createElement('div');
      if (!day || day > today) {
        cell.className = 'day-cell future';
      } else {
        const key = dateKeyUTC(day);
        const entry = recordsByDate[key];
        const total = entry ? entry.total : 0;
        const lvl = levelFor(total, thresholds);
        cell.className = `day-cell lvl-${lvl}`;
        cell.title = `${key}: ${total || 'no record'}`;
        cell.addEventListener('click', () => openDayModal(key));
      }
      calendar.appendChild(cell);
    }
  }

  const totalAll = state.records.reduce((sum, r) => sum + r.value, 0);
  document.getElementById('totalSummary').textContent =
    `${state.records.length} record(s) - total ${round2(totalAll)}`;
}

function round2(n) {
  return Math.round(n * 100) / 100;
}

// ---------- quick add form ----------

const recordDateInput = document.getElementById('recordDate');
recordDateInput.value = dateKeyUTC(new Date());

document.getElementById('recordForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('recordError');
  errEl.textContent = '';
  const dateStr = document.getElementById('recordDate').value;
  const value = parseFloat(document.getElementById('recordValue').value);
  try {
    await createRecord(dateStr, value);
    toast('Record added');
  } catch (err) {
    errEl.textContent = err.message;
  }
});

async function createRecord(dateStr, value) {
  const isoDate = `${dateStr}T00:00:00.000Z`;
  await api('/habit_records/create', {
    method: 'POST',
    json: { habit_id: state.selectedHabitId, date: isoDate, value },
  });
  await loadRecords(state.selectedHabitId);
}

async function updateRecord(recordId, value) {
  const record = state.records.find(r => r.id === recordId);
  if (!record) return;
  await api(`/habit_records/${recordId}`, {
    method: 'PUT',
    json: { habit_id: state.selectedHabitId, date: record.date, value },
  });
  await loadRecords(state.selectedHabitId);
}

async function deleteRecord(recordId) {
  await api(`/habit_records/${recordId}`, { method: 'DELETE' });
  await loadRecords(state.selectedHabitId);
}

// ---------- records table ----------

function renderRecordsTable() {
  const body = document.getElementById('recordsTableBody');
  const noRecordsEl = document.getElementById('noRecords');
  body.innerHTML = '';

  const sorted = [...state.records].sort((a, b) => new Date(b.date) - new Date(a.date));
  noRecordsEl.classList.toggle('hidden', sorted.length !== 0);

  for (const r of sorted) {
    const tr = document.createElement('tr');
    const dateTd = document.createElement('td');
    dateTd.textContent = dateKeyFromRecord(r);
    tr.appendChild(dateTd);

    const valueTd = document.createElement('td');
    const actionsTd = document.createElement('td');
    actionsTd.className = 'actions';

    if (editingRecordId === r.id) {
      const input = document.createElement('input');
      input.type = 'number';
      input.step = 'any';
      input.value = r.value;
      valueTd.appendChild(input);

      const saveBtn = document.createElement('button');
      saveBtn.className = 'btn-icon';
      saveBtn.textContent = 'Save';
      saveBtn.addEventListener('click', async () => {
        const val = parseFloat(input.value);
        if (Number.isNaN(val)) return;
        editingRecordId = null;
        try {
          await updateRecord(r.id, val);
          toast('Record updated');
        } catch (err) {
          toast('Failed to update: ' + err.message);
        }
      });
      const cancelBtn = document.createElement('button');
      cancelBtn.className = 'btn-icon';
      cancelBtn.textContent = 'Cancel';
      cancelBtn.addEventListener('click', () => {
        editingRecordId = null;
        renderRecordsTable();
      });
      actionsTd.appendChild(saveBtn);
      actionsTd.appendChild(cancelBtn);
    } else {
      valueTd.textContent = r.value;
      const editBtn = document.createElement('button');
      editBtn.className = 'btn-icon';
      editBtn.textContent = 'Edit';
      editBtn.addEventListener('click', () => {
        editingRecordId = r.id;
        renderRecordsTable();
      });
      const deleteBtn = document.createElement('button');
      deleteBtn.className = 'btn-icon';
      deleteBtn.textContent = 'Delete';
      deleteBtn.addEventListener('click', async () => {
        if (!confirm('Delete this record?')) return;
        try {
          await deleteRecord(r.id);
          toast('Record deleted');
        } catch (err) {
          toast('Failed to delete: ' + err.message);
        }
      });
      actionsTd.appendChild(editBtn);
      actionsTd.appendChild(deleteBtn);
    }

    tr.appendChild(valueTd);
    tr.appendChild(actionsTd);
    body.appendChild(tr);
  }
}

// ---------- day modal ----------

function openDayModal(dateKey) {
  currentDayKey = dateKey;
  const entry = recordsByDate[dateKey];
  const items = entry ? entry.items : [];

  document.getElementById('dayModalTitle').textContent = dateKey;
  const itemsEl = document.getElementById('dayModalItems');
  itemsEl.innerHTML = '';

  if (items.length === 0) {
    const p = document.createElement('p');
    p.className = 'muted small';
    p.textContent = 'No records for this day yet.';
    itemsEl.appendChild(p);
  }

  for (const r of items) {
    const row = document.createElement('div');
    row.className = 'day-modal-item';

    const input = document.createElement('input');
    input.type = 'number';
    input.step = 'any';
    input.value = r.value;

    const rowActions = document.createElement('div');
    rowActions.className = 'row-actions';

    const saveBtn = document.createElement('button');
    saveBtn.type = 'button';
    saveBtn.className = 'btn-icon';
    saveBtn.textContent = 'Save';
    saveBtn.addEventListener('click', async () => {
      const val = parseFloat(input.value);
      if (Number.isNaN(val)) return;
      try {
        await updateRecord(r.id, val);
        toast('Record updated');
        openDayModal(dateKey);
      } catch (err) {
        document.getElementById('dayModalError').textContent = err.message;
      }
    });

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'btn-icon';
    deleteBtn.textContent = 'Delete';
    deleteBtn.addEventListener('click', async () => {
      try {
        await deleteRecord(r.id);
        toast('Record deleted');
        openDayModal(dateKey);
      } catch (err) {
        document.getElementById('dayModalError').textContent = err.message;
      }
    });

    rowActions.appendChild(saveBtn);
    rowActions.appendChild(deleteBtn);
    row.appendChild(input);
    row.appendChild(rowActions);
    itemsEl.appendChild(row);
  }

  document.getElementById('dayModalValue').value = 1;
  document.getElementById('dayModalError').textContent = '';
  document.getElementById('dayModalBackdrop').classList.remove('hidden');
}

document.getElementById('dayModalCancel').addEventListener('click', () => {
  document.getElementById('dayModalBackdrop').classList.add('hidden');
});

document.getElementById('dayModalForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('dayModalError');
  errEl.textContent = '';
  const value = parseFloat(document.getElementById('dayModalValue').value);
  try {
    await createRecord(currentDayKey, value);
    toast('Record added');
    openDayModal(currentDayKey);
  } catch (err) {
    errEl.textContent = err.message;
  }
});

// ---------- init ----------

boot();
