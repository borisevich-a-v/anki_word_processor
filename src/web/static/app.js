// Which cards are ticked, editing them, and saving the export. The server renders the table and
// makes the file; this only ticks, counts, edits in place and hands the file to the browser.
const $ = id => document.getElementById(id);
const list = $('list');
const rows = () => [...list.querySelectorAll('tbody tr')];
const box = tr => tr.querySelector('input');
const plugin = () => list.querySelector('[name=plugin]').value;
let lastClicked = null;

// ---- messages: shown at once near the action, and gone by themselves
const timers = {};
function say(id, text, kind = '', ms = 0) {
  const el = $(id), target = el.querySelector('.t') || el;
  const shown = (t, k) => {
    target.textContent = t; el.className = id === 'cardmsg' && t ? `show ${k}` : k;
    if (id === 'cardmsg' && !t) list.querySelectorAll('td.fix').forEach(td => td.classList.remove('fix'));
  };
  if (!ms && kind === 'err' && id === 'cardmsg') ms = 8000;  // a reason is read in time, then it is gone
  clearTimeout(timers[id]);
  shown(text, kind);
  if (ms) timers[id] = setTimeout(() => shown('', ''), ms);
}
$('cardmsg').onclick = () => say('cardmsg', '');
document.addEventListener('keydown', e => {  // Escape closes a message, unless it belongs to a field or the question
  if (e.key === 'Escape' && !dialog.open && !e.target.closest('textarea')) say('cardmsg', '');
});

// ---- the lists of files follow the data folder, in place so an open choice is not lost
async function refreshFiles() {
  try {
    const res = await fetch('/files');
    if (!res.ok) return;
    const fresh = new DOMParser().parseFromString(await res.text(), 'text/html');
    const names = el => [...el.options].map(o => o.value).join('\n');
    let changed = false;
    for (const id of ['terms', 'source']) {
      const sel = $(id), next = fresh.getElementById(id);
      if (!next || names(sel) === names(next)) continue;
      const was = sel.value;
      sel.innerHTML = next.innerHTML;
      sel.value = was;  // a file that is gone leaves the choice empty
      changed = true;
    }
    $('filehint').innerHTML = fresh.getElementById('filehint').innerHTML;
    if (changed) { remember(); checkSame(); markStale(); }
  } catch {}
}
for (const id of ['terms', 'source']) {
  $(id).addEventListener('pointerdown', refreshFiles);
  $(id).addEventListener('focus', refreshFiles);
}
window.addEventListener('focus', refreshFiles);
document.addEventListener('visibilitychange', () => { if (!document.hidden) refreshFiles(); });

// ---- choices are remembered in this browser
const CHOICES = 'process_anki.choices';
const picks = ['plugin', 'terms', 'source'];
function remembered() { try { return JSON.parse(localStorage.getItem(CHOICES)) || {}; } catch { return {}; } }
function remember() {
  try { localStorage.setItem(CHOICES, JSON.stringify(Object.fromEntries(picks.map(k => [k, $(k).value])))); } catch {}
}
function restore(which = picks) {
  const saved = remembered();
  let changed = false;
  for (const k of which) {
    const sel = $(k);
    if (saved[k] === undefined || sel.value === saved[k]) continue;
    if ([...sel.options].some(o => o.value === saved[k])) { sel.value = saved[k]; changed ||= k === 'plugin'; }
  }
  checkSame();
  return changed;
}
// The report and summary on the page belong to the choices the run was started with.
function markStale() {
  const st = $('status'), d = st.dataset;
  if (d.plugin === undefined) return;
  // only a choice that was made counts; a run in progress is never shown as old
  const chosen = $('terms').value !== '';
  const other = $('plugin').value !== d.plugin || (chosen && ($('terms').value !== d.terms || $('source').value !== d.source));
  st.classList.toggle('stale', other && !st.classList.contains('running'));
}
function checkSame() {
  const same = $('terms').value && $('terms').value === $('source').value;
  $('samewarn').textContent = same ? 'The terms file and the source text must be different files.' : '';
  $('run').disabled = !!same;
}
function showPair() { $('pair').textContent = $('plugin').selectedOptions[0].textContent; }

document.addEventListener('change', e => {
  if (!picks.includes(e.target.id)) return;
  remember(); checkSame(); markStale();
  if (e.target.id === 'plugin') showPair();
});
$('runform').addEventListener('keydown', e => {  // Enter in a choice only picks it; it never starts a paid run
  if (e.key === 'Enter' && e.target.matches('select')) e.preventDefault();
});
document.addEventListener('DOMContentLoaded', () => {
  const idle = $('status').dataset.idle !== undefined;
  restore(idle ? picks : ['terms', 'source']);  // a running or finished run keeps its own pair
  if (idle && $('plugin').value !== String(list.querySelector('[name=plugin]').value)) {
    showPair(); htmx.trigger($('plugin'), 'change');
  }
  showPair();
  markStale();
});

// ---- the table follows a run: refreshed whenever a term is done, with selection, focus and
// place kept; never over a field being edited (it waits until the editor is closed)
let kept = null, lastDone, pendingRefresh = false;
const editing = () => !!list.querySelector('textarea');
const isRefresh = e => (e.detail.pathInfo?.requestPath || '').includes('after_run');
function refreshCards() {
  if (editing()) pendingRefresh = true;
  else htmx.trigger(document.body, 'run-progress');
}
document.body.addEventListener('htmx:beforeSwap', e => {
  if (e.detail.target !== list || !isRefresh(e)) return;
  if (editing()) {
    e.detail.shouldSwap = false; pendingRefresh = true;
    const n = (String(e.detail.serverResponse).match(/<tr data-id=/g) || []).length - rows().length;
    if (n > 0) {
      $('paused').hidden = false;
      $('paused').textContent = `List paused while editing: ${n} new ${n === 1 ? 'card' : 'cards'} will show when you finish (Enter saves, Esc cancels).`;
    }
    return;
  }
  const focused = list.contains(document.activeElement) ? document.activeElement.closest('tbody tr') : null;
  kept = {
    checked: new Set(rows().filter(tr => box(tr).checked).map(tr => tr.dataset.id)),
    focus: focused && focused.dataset.id,
    last: lastClicked && lastClicked.dataset.id,
    top: list.scrollTop, left: list.scrollLeft,
  };
});
document.body.addEventListener('htmx:afterSwap', e => {
  if (e.target.id === 'pickers') restore(['terms', 'source']);
  if (e.target !== list) return;
  $('paused').hidden = true;
  lastClicked = null;
  if (kept) {
    const was = kept; kept = null;
    rows().forEach(tr => { box(tr).checked = was.checked.has(tr.dataset.id); });
    lastClicked = rows().find(tr => tr.dataset.id === was.last) || null;
    list.scrollTop = was.top; list.scrollLeft = was.left;
    const back = rows().find(tr => tr.dataset.id === was.focus);
    if (back) { rows().forEach(r => { r.tabIndex = -1; }); back.tabIndex = 0; back.focus({ preventScroll: true }); }
    sync(true);
  } else {
    sync(true);
    if (list.querySelector('#clearmsgs')) { say('exmsg', ''); say('cardmsg', ''); }
  }
});
document.body.addEventListener('htmx:afterSettle', () => {
  markStale();
  const st = $('status').dataset;
  $('cardprogress').textContent = st.done !== undefined && st.total ? `making ${st.done}/${st.total}` : '';
  const done = st.done;  // present while a run goes on
  if (done !== lastDone) { lastDone = done; if (done !== undefined) refreshCards(); }
});

// ---- failed terms
document.addEventListener('click', async e => {
  const b = e.target.closest('#copyfailed');
  if (!b) return;
  try { await navigator.clipboard.writeText(b.dataset.terms); say('cardmsg', 'Failed terms copied', '', 4000); }
  catch { say('cardmsg', 'Could not copy; select the terms and copy them by hand', 'err'); }
});

// ---- selecting
function sync(quiet = false) {
  if (!quiet) say('exmsg', '');  // an export result is about the selection it was made with
  const all = rows(), n = all.filter(tr => box(tr).checked).length;
  all.forEach(tr => tr.classList.toggle('sel', box(tr).checked));
  $('sel').textContent = `${n} selected of ${all.length}`;
  $('exn').textContent = $('deln').textContent = n;
  if (all.length && !all.some(tr => tr.tabIndex === 0)) all[0].tabIndex = 0;
}
function select(pick) {
  rows().forEach(tr => { box(tr).checked = pick(tr); });
  sync();
}
function toggle(tr) { box(tr).checked = !box(tr).checked; lastClicked = tr; sync(); }

list.addEventListener('click', e => {
  const tr = e.target.closest('tbody tr');
  if (!tr || e.target.closest('textarea')) return;
  const all = rows(), from = all.indexOf(lastClicked), to = all.indexOf(tr);
  if (e.shiftKey && from >= 0) {
    all.slice(Math.min(from, to), Math.max(from, to) + 1).forEach(r => { box(r).checked = true; });
  } else if (e.target !== box(tr)) {
    box(tr).checked = !box(tr).checked;
  }
  lastClicked = tr;
  sync();
});

$('range').onclick = () => {
  const lo = +$('from').value || -Infinity, hi = +$('to').value || Infinity;
  select(tr => +tr.dataset.id >= lo && +tr.dataset.id <= hi);
};
$('all').onclick = () => select(() => true);
$('none').onclick = () => select(() => false);
$('lastrun').onclick = () => {
  select(tr => tr.classList.contains('new'));
  if (rows().some(tr => tr.classList.contains('new'))) return;
  const made = $('status').dataset.made;
  say('exmsg', made === '0' ? 'The last run made no cards' : 'No cards of the last run in this list', 'cancel', 6000);
};

// ---- keyboard on the cards: one stop for Tab, arrows move, Space selects, Enter edits
function focusRow(tr) {
  rows().forEach(r => { r.tabIndex = -1; });
  tr.tabIndex = 0;
  tr.focus();
  tr.scrollIntoView({ block: 'nearest' });
}
list.addEventListener('focusin', e => {
  const tr = e.target.closest('tbody tr');
  if (tr && !e.target.closest('textarea')) rows().forEach(r => { r.tabIndex = r === tr ? 0 : -1; });
});
list.addEventListener('keydown', e => {
  const tr = e.target.closest('tbody tr');
  if (!tr || e.target.closest('textarea') || e.target !== tr) return;
  const all = rows(), i = all.indexOf(tr);
  if (e.key === ' ') { e.preventDefault(); toggle(tr); }
  else if (e.key === 'Enter') { e.preventDefault(); startEdit(tr.querySelector('td[data-field="0"]')); }
  else if (e.key === 'ArrowDown' && all[i + 1]) { e.preventDefault(); focusRow(all[i + 1]); }
  else if (e.key === 'ArrowUp' && all[i - 1]) { e.preventDefault(); focusRow(all[i - 1]); }
  else if (e.key === 'Home') { e.preventDefault(); focusRow(all[0]); }
  else if (e.key === 'End') { e.preventDefault(); focusRow(all[all.length - 1]); }
  else if (e.key === 'Delete') { e.preventDefault(); askDelete(); }
});

// ---- deleting: a question in front of the page that must be answered
const dialog = $('confirm');
async function askDelete() {
  await saving;  // an edit that is being left is settled first
  const n = rows().filter(tr => box(tr).checked).length;
  if (!n) { say('cardmsg', 'Nothing selected, nothing deleted', '', 5000); return; }
  if (!$('cardmsg').classList.contains('err')) say('cardmsg', '');
  const names = rows().filter(tr => box(tr).checked).map(tr => tr.querySelector('td[data-field="0"]').textContent.trim());
  $('n').textContent = n;
  $('ncards').textContent = n === 1 ? 'card' : 'cards';
  $('names').textContent = names.length > 3 ? `${names.slice(0, 3).join(', ')} and ${names.length - 3} more` : names.join(', ');
  $('allwarn').hidden = n !== rows().length;
  dialog.showModal();
}
$('delete').onclick = askDelete;
$('keep').onclick = () => dialog.close();
$('yes').onclick = async e => {
  e.preventDefault();
  dialog.close();
  const body = new URLSearchParams({ plugin: plugin() });
  const gone = rows().filter(tr => box(tr).checked);
  gone.forEach(tr => body.append('ids', tr.dataset.id));
  const place = rows().indexOf(gone[0]);
  try {
    const res = await fetch('/cards/delete', { method: 'POST', body });
    if (!res.ok) throw new Error(`the server answered ${res.status}`);
    const { count } = await res.json();
    gone.forEach(tr => tr.remove());
    sync();
    const left = rows();  // keep the focus in the list, near where the cards were
    if (left.length) focusRow(left[Math.min(place, left.length - 1)]); else $('delete').focus();
    say('cardmsg', `Deleted cards: ${count}`, 'ok', 5000);
  } catch (err) {
    say('cardmsg', `Not deleted: ${err.message}`, 'err');
  }
};

// ---- editing a field in place
let saving = Promise.resolve();  // the edit that is being left, until it is saved or dropped
function setCell(td, value) {
  td.textContent = '';
  td.classList.remove('editing');
  if (td.dataset.field === '0') td.append(Object.assign(document.createElement('b'), { textContent: value }));
  else td.textContent = value;
  if (pendingRefresh && !editing()) { pendingRefresh = false; htmx.trigger(document.body, 'run-progress'); }
}

function startEdit(td) {
  if (!td || td.querySelector('textarea')) return;
  const old = td.textContent, area = document.createElement('textarea');
  area.value = old;
  td.textContent = '';
  td.classList.add('editing');
  td.append(area);
  const fit = () => { area.style.height = 'auto'; area.style.height = area.scrollHeight + 4 + 'px'; };
  fit();
  area.focus();
  area.select();
  let busy = false, closed = false;

  // Saves; true when the cell is done (saved, or nothing to save), false when refused.
  async function commit(leaving = false) {
    if (busy || closed) return false;
    if (area.value === old) { closed = true; setCell(td, old); return true; }
    busy = true;
    try {
      const body = new URLSearchParams({
        plugin: plugin(), card: td.closest('tr').dataset.id, field: td.dataset.field, value: area.value,
      });
      const res = await fetch('/cards/edit', { method: 'POST', body });
      const { ok, error, value, fix } = res.ok ? await res.json() : { ok: false, error: `the server answered ${res.status}` };
      if (!ok) {
        say('cardmsg', `Not changed: ${error}`, 'err');
        const other = fix != null && td.closest('tr').querySelector(`td[data-field="${fix}"]`);
        if (other) other.classList.add('fix');
        if (leaving) { closed = true; setCell(td, old); } else area.classList.add('bad');
        return false;
      }
      closed = true;
      setCell(td, value ?? area.value);
      say('exmsg', '');
      say('cardmsg', 'Card changed', 'ok', 4000);
      return true;
    } catch (err) {
      say('cardmsg', `Not changed: ${err.message}`, 'err');
      if (leaving) { closed = true; setCell(td, old); } else area.classList.add('bad');
      return false;
    } finally { busy = false; }
  }

  area.addEventListener('input', () => {
    if (/[\r\n]/.test(area.value)) area.value = area.value.replace(/\s*[\r\n]+\s*/g, ' ');
    area.classList.remove('bad');
    fit();
  });
  area.addEventListener('keydown', async k => {
    if (k.key === 'Escape') { k.preventDefault(); closed = true; say('cardmsg', ''); setCell(td, old); td.closest('tr').focus(); }
    else if (k.key === 'Enter') { k.preventDefault(); const tr = td.closest('tr'); if (await commit()) tr.focus(); }
    else if (k.key === 'Tab') {
      const next = k.shiftKey ? td.previousElementSibling : td.nextElementSibling;
      const target = next && next.dataset.field !== undefined ? next : null;
      if (!target) { if (!closed && area.value !== old) { k.preventDefault(); if (await commit()) td.closest('tr').focus(); } return; }
      k.preventDefault();
      if (await commit()) startEdit(target);
    }
  });
  area.addEventListener('blur', () => { if (!closed && !busy) saving = commit(true); });
}

list.addEventListener('dblclick', e => startEdit(e.target.closest('td[data-field]')));

// ---- exporting
async function save(blob, name) {
  if (window.showSaveFilePicker) {  // asks where to save and under what name
    const handle = await window.showSaveFilePicker({
      suggestedName: name,
      types: [{ description: 'Anki import file', accept: { 'text/tab-separated-values': ['.tsv'] } }],
    });
    const out = await handle.createWritable();
    await out.write(blob);
    await out.close();
    return { name: handle.name, asked: true };
  }
  const a = document.createElement('a');  // no dialog available: a plain download
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
  return { name, asked: false };
}

$('export').onclick = async () => {
  await saving;
  const body = new URLSearchParams({ plugin: plugin() });
  rows().filter(tr => box(tr).checked).forEach(tr => body.append('ids', tr.dataset.id));
  say('exmsg', '');
  try {
    const res = await fetch('/export', { method: 'POST', body });
    if (!res.ok) throw new Error(`the server answered ${res.status}`);
    const count = +res.headers.get('X-Count');
    if (!count) { say('exmsg', 'Nothing selected, nothing written', '', 6000); return; }
    const { name, asked } = await save(await res.blob(), res.headers.get('X-Suggested-Name'));
    const cards = count === 1 ? 'card' : 'cards', where = asked ? '' : 'to Downloads ';
    say('exmsg', `Saved ${count} ${cards} ${where}as ${name}`, 'ok', 15000);
  } catch (err) {
    if (err.name === 'AbortError') say('exmsg', 'Cancelled, nothing saved', 'cancel', 6000);
    else say('exmsg', `Export failed: ${err.message}`, 'err');
  }
};

// ---- help: a button or F1; the page itself carries no tips
const help = $('help');
function toggleHelp() {
  if (help.open) { help.close(); return; }
  if (editing() || dialog.open) return;
  help.showModal();
  $('help').querySelector('.helpbody').scrollTop = 0;  // read from the start, not from the focused close button
}
$('helpbtn').onclick = toggleHelp;
help.addEventListener('click', e => {  // a click on the backdrop lands on the dialog itself, outside its box
  const r = help.getBoundingClientRect();
  if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) help.close();
});
document.addEventListener('keydown', e => {
  if (e.key === 'F1') { e.preventDefault(); toggleHelp(); }
});

sync();
