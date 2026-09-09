// DOM references are kept together so the rest reads like the user's workflow.
const $ = (selector) => document.querySelector(selector);
const status = $('#status');
const dateInput = $('#date');
let registering = false;
let loadVersion = 0;

function notify(message = '', error = false) {
  status.textContent = message;
  status.classList.toggle('error', error);
}

async function api(path, method = 'GET', body) {
  const response = await fetch(`/api${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: method === 'GET' ? undefined : JSON.stringify(body ?? {}),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => `${item.loc.at(-1)}: ${item.msg}`).join('; ')
      : data.detail;
    if (response.status === 401) showUser(null);
    throw new Error(detail || 'Something went wrong. Please try again.');
  }
  return response.status === 204 ? null : response.json();
}

function showUser(user) {
  loadVersion += 1; // Invalidate any previous user's outstanding journal request.
  $('#auth').hidden = Boolean(user);
  $('#journal').hidden = !user;
  $('#account').hidden = !user;
  $('#username').textContent = user?.username ?? '';
  if (!user) {
    $('#foods').replaceChildren();
    $('#workouts').replaceChildren();
  }
}

function formData(form, numericFields = []) {
  const data = Object.fromEntries(new FormData(form));
  for (const key of numericFields) data[key] = Number(data[key]);
  return data;
}

async function withForm(form, action) {
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  notify();
  try { await action(); }
  catch (error) { notify(error.message, true); }
  finally { button.disabled = false; }
}

// Build user text as textContent; HTML in a food name never becomes executable code.
function renderEntries(kind, entries) {
  const list = $(`#${kind}`);
  list.replaceChildren();
  if (!entries.length) {
    const empty = document.createElement('li');
    empty.className = 'empty';
    empty.textContent = kind === 'foods' ? 'No food logged for this day.' : 'No exercises logged for this day.';
    list.append(empty);
  }
  for (const entry of entries) {
    const row = document.createElement('li');
    const text = document.createElement('div');
    const title = document.createElement('strong');
    const detail = document.createElement('small');
    title.textContent = entry.name ?? entry.exercise;
    detail.textContent = kind === 'foods'
      ? `${entry.calories} kcal · P ${entry.protein} g / C ${entry.carbs} g / F ${entry.fat} g`
      : `${entry.sets} × ${entry.reps} reps · ${entry.weight} lb`;
    const remove = document.createElement('button');
    remove.className = 'remove';
    remove.textContent = 'Remove';
    remove.setAttribute('aria-label', `Remove ${title.textContent}`);
    remove.addEventListener('click', async () => {
      if (!confirm(`Remove ${title.textContent}?`)) return;
      remove.disabled = true;
      try {
        await api(`/${kind}/${entry.id}`, 'DELETE');
        await loadDay();
        notify('Entry removed.');
      } catch (error) { notify(error.message, true); remove.disabled = false; }
    });
    text.append(title, detail);
    row.append(text, remove);
    list.append(row);
  }
}

async function loadDay() {
  const version = ++loadVersion;
  for (const key of ['calories', 'protein', 'carbs', 'fat']) {
    $(`#${key}-total`).textContent = '—';
    $(`#${key}-goal`).textContent = '';
  }
  $('#calories-progress').value = 0;
  $('#foods').replaceChildren();
  $('#workouts').replaceChildren();
  $('#goals-form button').disabled = true;
  if (!dateInput.value) throw new Error('Choose a journal date first.');
  $('#journal').setAttribute('aria-busy', 'true');
  try {
    const day = await api(`/day?date=${encodeURIComponent(dateInput.value)}`);
    if (version !== loadVersion) return; // A slower, older date must not overwrite the current day.
    for (const key of ['calories', 'protein', 'carbs', 'fat']) {
      $(`#${key}-total`).textContent = `${day.totals[key].toLocaleString()}${key === 'calories' ? '' : ' g'}`;
      $(`#${key}-goal`).textContent = `of ${day.goals[key].toLocaleString()}${key === 'calories' ? ' kcal' : ' g'} goal`;
      $('#goals-form').elements[key].value = day.goals[key];
    }
    $('#calories-progress').max = day.goals.calories;
    $('#calories-progress').value = day.totals.calories;
    renderEntries('foods', day.foods);
    renderEntries('workouts', day.workouts);
    $('#goals-form button').disabled = false;
  } finally {
    if (version === loadVersion) $('#journal').setAttribute('aria-busy', 'false');
  }
}

$('#auth-toggle').addEventListener('click', () => {
  registering = !registering;
  $('#username-field').hidden = !registering;
  $('#auth-form').elements.username.disabled = !registering;
  $('#auth-form').elements.username.required = registering;
  $('#auth-form').elements.password.autocomplete = registering ? 'new-password' : 'current-password';
  $('#auth-title').textContent = registering ? 'Start your journal' : 'Welcome back';
  $('#auth-description').textContent = registering ? 'Create an account to save your entries.' : 'Sign in to open your journal.';
  $('#auth-submit').textContent = registering ? 'Create account' : 'Sign in';
  $('#auth-toggle').textContent = registering ? 'Already have an account? Sign in' : 'New here? Create an account';
  notify();
});

$('#auth-form').addEventListener('submit', (event) => {
  event.preventDefault();
  withForm(event.currentTarget, async () => {
    const user = await api(registering ? '/register' : '/login', 'POST', formData($('#auth-form')));
    $('#auth-form').reset();
    showUser(user);
    await loadDay();
    notify('Your journal is ready.');
  });
});

$('#logout').addEventListener('click', async () => {
  try { await api('/logout', 'POST'); showUser(null); notify('Signed out.'); }
  catch (error) { notify(error.message, true); }
});

dateInput.addEventListener('change', async () => {
  try { notify('Loading day…'); await loadDay(); notify(); }
  catch (error) { notify(error.message, true); }
});

for (const [id, path, fields] of [
  ['food-form', '/foods', ['calories', 'protein', 'carbs', 'fat']],
  ['workout-form', '/workouts', ['sets', 'reps', 'weight']],
  ['goals-form', '/goals', ['calories', 'protein', 'carbs', 'fat']],
]) {
  $(`#${id}`).addEventListener('submit', (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    withForm(form, async () => {
      const data = formData(form, fields);
      if (id !== 'goals-form') {
        if (!dateInput.value) throw new Error('Choose a journal date first.');
        data.date = dateInput.value;
      }
      await api(path, id === 'goals-form' ? 'PUT' : 'POST', data);
      if (id !== 'goals-form') form.reset();
      await loadDay();
      notify(id === 'goals-form' ? 'Goals saved.' : 'Entry saved.');
    });
  });
}

async function start() {
  // Local calendar components avoid UTC shifting the journal to yesterday/tomorrow.
  const now = new Date();
  dateInput.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  try {
    const user = await api('/me');
    showUser(user);
    await loadDay();
    notify();
  } catch (error) {
    showUser(null);
    notify(error.message === 'Please sign in to continue.' ? '' : error.message, error.message !== 'Please sign in to continue.');
  }
}
start();
