const form = document.getElementById('analysisForm');
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('cvFile');
const fileName = document.getElementById('fileName');
const statusBox = document.getElementById('status');
const overlay = document.getElementById('loadingOverlay');

function setStatus(msg, kind = '') {
  statusBox.textContent = msg;
  statusBox.className = `status ${kind}`.trim();
}

function updateName() {
  const file = fileInput.files && fileInput.files[0];
  fileName.textContent = file ? `Selected: ${file.name}` : 'No file selected';
}

['dragenter', 'dragover'].forEach((name) => {
  dropzone.addEventListener(name, (event) => {
    event.preventDefault();
    dropzone.classList.add('dragover');
  });
});
['dragleave', 'drop'].forEach((name) => {
  dropzone.addEventListener(name, () => dropzone.classList.remove('dragover'));
});
dropzone.addEventListener('drop', (event) => {
  event.preventDefault();
  if (event.dataTransfer?.files?.length) {
    fileInput.files = event.dataTransfer.files;
    updateName();
  }
});
fileInput.addEventListener('change', updateName);

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const file = fileInput.files && fileInput.files[0];
  const jobDescription = document.getElementById('jobDescription').value.trim();
  const jobTitle = document.getElementById('jobTitle').value.trim();
  const company = document.getElementById('company').value.trim();

  if (!file) return setStatus('Please upload a PDF file.', 'error');
  if (!jobDescription) return setStatus('Please paste a job description.', 'error');

  overlay.classList.add('show');
  setStatus('Analyzing...', 'ok');

  const formData = new FormData();
  formData.append('cv_file', file);
  formData.append('job_description', jobDescription);
  if (jobTitle) formData.append('job_title', jobTitle);
  if (company) formData.append('company', company);

  try {
    const response = await fetch('/analyze', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analysis failed');
    window.location.href = `/dashboard/${data.analysis_id}`;
  } catch (err) {
    setStatus(err.message || 'Unexpected error.', 'error');
  } finally {
    overlay.classList.remove('show');
  }
});