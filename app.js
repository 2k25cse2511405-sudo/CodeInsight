const codeEl = document.getElementById('code');
const lineNumbers = document.getElementById('lineNumbers');
const lineCount = document.getElementById('lineCount');
const sample = `def find_pairs(nums):
    pairs = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == 10:
                pairs.append((nums[i], nums[j]))
    return pairs

values = [1, 2, 3, 4, 5, 6]
print(find_pairs(values))`;

function updateLines() {
  const count = Math.max(1, codeEl.value.split('\\n').length);
  lineNumbers.textContent = Array.from({length: count}, (_, i) => i + 1).join('\\n');
  lineCount.textContent = `${codeEl.value.split('\\n').length} lines`;
}
codeEl.addEventListener('input', updateLines);
codeEl.addEventListener('scroll', () => { lineNumbers.scrollTop = codeEl.scrollTop; });
document.getElementById('sampleBtn').addEventListener('click', () => {
  codeEl.value = sample;
  updateLines();
});
document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const btn = document.getElementById('analyzeBtn');
  btn.disabled = true;
  btn.innerHTML = '<span>◌</span> Analyzing...';
  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code: codeEl.value, language: document.getElementById('language').value})
    });
    const data = await response.json();
    if (!response.ok || !data.valid) {
      showError(data.error || 'Unable to analyze this code.');
    } else {
      showReport(data);
    }
  } catch (err) {
    showError('Could not connect to the analyzer. Make sure the Flask server is running.');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>✦</span> Analyze code <span class="arrow">→</span>';
  }
});

function showError(message) {
  document.getElementById('emptyState').classList.remove('hidden');
  document.getElementById('report').classList.add('hidden');
  document.getElementById('emptyState').innerHTML = `<div class="empty-icon">!</div><h3>Analysis could not complete</h3><p>${escapeHtml(message)}</p>`;
  document.getElementById('reportStatus').textContent = 'ERROR';
}
function showReport(data) {
  document.getElementById('emptyState').classList.add('hidden');
  document.getElementById('report').classList.remove('hidden');
  document.getElementById('reportStatus').textContent = 'COMPLETE';
  document.getElementById('complexity').textContent = data.complexity;
  document.getElementById('complexitySummary').textContent = data.summary;
  document.getElementById('loopCount').textContent = data.loops ?? 0;
  document.getElementById('depthCount').textContent = data.max_loop_depth ?? 0;
  document.getElementById('findingCount').textContent = data.findings.length;
  document.getElementById('findingLabel').textContent = `${data.findings.length} items`;
  const container = document.getElementById('findings');
  container.innerHTML = '';
  data.findings.forEach(item => {
    const icon = item.severity === 'warning' ? '!' : item.severity === 'success' ? '✓' : 'i';
    const line = item.line ? `<span class="line">Line ${item.line}</span>` : '';
    const div = document.createElement('div');
    div.className = `finding ${item.severity}`;
    div.innerHTML = `<div class="finding-icon">${icon}</div><div><b>${escapeHtml(item.title)}${line}</b><p>${escapeHtml(item.detail)}</p></div>`;
    container.appendChild(div);
  });
  const tip = data.max_loop_depth >= 2
    ? 'If possible, replace repeated searching inside nested loops with a set or dictionary lookup to reduce the work.'
    : data.complexity.includes('n log n')
    ? 'Avoid sorting more than once when the data has not changed, and check whether the sorted order is actually needed.'
    : 'Choose data structures that match the operation, and avoid repeating expensive work inside loops.';
  document.getElementById('tip').textContent = tip;
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
codeEl.value = sample;
updateLines();
