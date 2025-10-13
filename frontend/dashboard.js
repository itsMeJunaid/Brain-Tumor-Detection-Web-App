<script>
const API_URL = 'http://localhost:8000';
let currentScanId = null;
let deleteScanId = null;
let allScansData = [];

// Check authentication
const token = localStorage.getItem('token');
if (!token) window.location.href = 'index.html';

// ===================== VIEW MANAGEMENT =====================
function showView(view) {
    const views = ['uploadView', 'historyView'];
    views.forEach(v => document.getElementById(v).classList.add('hidden'));

    if (view === 'upload') document.getElementById('uploadView').classList.remove('hidden');
    if (view === 'history') {
        document.getElementById('historyView').classList.remove('hidden');
        loadAllScans();
    }
}

// ===================== DOCTOR INFO =====================
async function loadDoctorInfo() {
    try {
        const res = await fetch(`${API_URL}/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return logout();
        const doctor = await res.json();
        document.getElementById('doctorName').textContent = `Dr. ${doctor.full_name}`;
    } catch (err) {
        console.error('Error loading doctor info:', err);
    }
}

// ===================== STATS =====================
async function loadStats() {
    try {
        const res = await fetch(`${API_URL}/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return;
        const stats = await res.json();
        document.getElementById('totalScans').textContent = stats.total_scans;
        document.getElementById('tumorDetected').textContent = stats.tumor_detected;
        document.getElementById('noTumor').textContent = stats.no_tumor;
    } catch (err) {
        console.error('Error loading stats:', err);
    }
}

// ===================== SCAN CARDS =====================
function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric', 
        hour: '2-digit', minute: '2-digit'
    });
}

function getBadgeColor(prediction) {
    return prediction === 'Tumor' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700';
}

function createScanCard(scan, compact = false) {
    const date = formatDate(scan.scan_date);
    const badge = getBadgeColor(scan.prediction);

    return `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition cursor-pointer" onclick="viewScanDetail(${scan.id})">
            <div class="flex justify-between items-start mb-2">
                <div>
                    <p class="font-semibold text-gray-800">${scan.patient_name}</p>
                    <p class="text-xs text-gray-500">${scan.patient_id}</p>
                </div>
                <span class="px-3 py-1 rounded-full text-xs font-semibold ${badge}">${scan.prediction}</span>
            </div>
            <div class="flex justify-between items-center text-xs text-gray-600">
                <span>📅 ${date}</span>
                <span>🎯 ${scan.confidence.toFixed(1)}%</span>
            </div>
        </div>
    `;
}

function createFullScanCard(scan) {
    const date = formatDate(scan.scan_date);
    const badge = getBadgeColor(scan.prediction);
    const borderColor = scan.prediction === 'Tumor' ? 'border-red-200' : 'border-green-200';

    return `
        <div class="bg-white rounded-xl shadow-sm border-2 ${borderColor} overflow-hidden hover:shadow-lg transition">
            <div class="relative">
                <img src="${API_URL}${scan.image_url}" class="w-full h-48 object-cover cursor-pointer" onclick="viewScanDetail(${scan.id})">
                <div class="absolute top-2 right-2">
                    <span class="px-3 py-1 rounded-full text-xs font-bold ${badge} border-2 backdrop-blur-sm">${scan.prediction}</span>
                </div>
            </div>
            <div class="p-4">
                <div class="mb-3">
                    <p class="font-bold text-gray-800 text-lg">${scan.patient_name}</p>
                    <p class="text-sm text-gray-500">ID: ${scan.patient_id}</p>
                </div>
                <div class="flex items-center justify-between text-sm text-gray-600 mb-3 pb-3 border-b">
                    <span>📅 ${date}</span>
                    <span class="font-semibold">🎯 ${scan.confidence.toFixed(1)}%</span>
                </div>
                <div class="flex gap-2">
                    <button onclick="downloadScanReport(${scan.id})" class="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition">📄 PDF</button>
                    <button onclick="viewScanDetail(${scan.id})" class="flex-1 px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white text-sm font-medium rounded-lg transition">👁️ View</button>
                    <button onclick="showDeleteModal(${scan.id})" class="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition">🗑️</button>
                </div>
            </div>
        </div>
    `;
}

// ===================== LOAD SCANS =====================
async function loadRecentScans() {
    try {
        const res = await fetch(`${API_URL}/scans`, { headers: { 'Authorization': `Bearer ${token}` }});
        if (!res.ok) return;
        const scans = await res.json();
        const recentDiv = document.getElementById('recentScans');
        recentDiv.innerHTML = scans.length
            ? scans.slice(0,5).map(scan => createScanCard(scan, true)).join('')
            : '<p class="text-gray-500 text-center py-8">No scans yet</p>';
    } catch (err) {
        console.error('Error loading recent scans:', err);
    }
}

async function loadAllScans() {
    try {
        const res = await fetch(`${API_URL}/scans`, { headers: { 'Authorization': `Bearer ${token}` }});
        if (!res.ok) return;
        allScansData = await res.json();
        displayAllScans(allScansData);
    } catch (err) {
        console.error('Error loading all scans:', err);
    }
}

function displayAllScans(scans) {
    const gridDiv = document.getElementById('allScansGrid');
    gridDiv.innerHTML = scans.length
        ? scans.map(scan => createFullScanCard(scan)).join('')
        : '<div class="col-span-full text-center py-12"><p class="text-gray-500">No scans found</p></div>';
}

// ===================== FILTER SCANS =====================
function filterScans() {
    const term = document.getElementById('searchInput').value.toLowerCase();
    const filtered = allScansData.filter(scan =>
        scan.patient_name.toLowerCase().includes(term) ||
        scan.patient_id.toLowerCase().includes(term)
    );
    displayAllScans(filtered);
}

// ===================== VIEW SCAN DETAILS =====================
async function viewScanDetail(scanId) {
    try {
        const res = await fetch(`${API_URL}/scan/${scanId}`, { headers: { 'Authorization': `Bearer ${token}` }});
        if (!res.ok) return;
        const scan = await res.json();
        showView('upload');
        displayResult(scan);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
        console.error('Error viewing scan:', err);
    }
}

// ===================== DELETE SCAN =====================
function showDeleteModal(scanId) {
    deleteScanId = scanId;
    document.getElementById('deleteModal').classList.add('active');
}

function closeDeleteModal() {
    deleteScanId = null;
    document.getElementById('deleteModal').classList.remove('active');
}

async function confirmDelete() {
    if (!deleteScanId) return;
    try {
        const res = await fetch(`${API_URL}/scan/${deleteScanId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            closeDeleteModal();
            loadStats();
            loadAllScans();
            loadRecentScans();
            alert('✅ Scan deleted successfully!');
        } else {
            alert('❌ Failed to delete scan');
        }
    } catch (err) {
        console.error('Error deleting scan:', err);
        alert('❌ Network error');
    }
}

// ===================== DOWNLOAD REPORT =====================
async function downloadScanReport(scanId) {
    try {
        const res = await fetch(`${API_URL}/download-report/${scanId}`, { headers: { 'Authorization': `Bearer ${token}` }});
        if (!res.ok) return alert('Failed to download report');
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Brain_Tumor_Report_${scanId}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (err) {
        console.error('Error downloading report:', err);
        alert('Failed to download report');
    }
}

async function downloadReport() {
    if (currentScanId) await downloadScanReport(currentScanId);
}

// ===================== FILE UPLOAD =====================
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('mriImage');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const fileName = document.getElementById('fileName');

function previewFile(file) {
    const reader = new FileReader();
    reader.onload = e => {
        previewImg.src = e.target.result;
        imagePreview.classList.remove('hidden');
        fileName.textContent = file.name;
    };
    reader.readAsDataURL(file);
}

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', e => {
    if (e.target.files[0]) previewFile(e.target.files[0]);
});

dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('border-blue-500', 'bg-blue-50');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-blue-500', 'bg-blue-50');
});

dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('border-blue-500', 'bg-blue-50');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        fileInput.files = e.dataTransfer.files;
        previewFile(file);
    }
});

// ===================== UPLOAD FORM =====================
document.getElementById('uploadForm').addEventListener('submit', async e => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('patient_name', document.getElementById('patientName').value);
    formData.append('patient_id', document.getElementById('patientId').value);
    formData.append('notes', document.getElementById('notes').value);

    document.getElementById('loadingCard').classList.remove('hidden');
    document.getElementById('resultCard').classList.add('hidden');

    try {
        const res = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        if (!res.ok) return alert('Prediction failed. Please try again.');
        const result = await res.json();
        displayResult(result);
        loadStats();
        loadRecentScans();
    } catch (err) {
        console.error('Error:', err);
        alert('Network error. Please check your connection.');
    } finally {
        document.getElementById('loadingCard').classList.add('hidden');
    }
});

// ===================== DISPLAY RESULT =====================
function displayResult(result) {
    currentScanId = result.scan_id || result.id;

    const predictionBox = document.getElementById('predictionBox');
    const isTumor = result.prediction === 'Tumor';
    predictionBox.className = `rounded-xl p-6 mb-4 border-2 ${isTumor ? 'border-red-300' : 'border-green-300'}`;
    
    document.getElementById('resultCard').classList.remove('hidden');
    document.getElementById('scanId').textContent = currentScanId;
    document.getElementById('originalImage').src = `${API_URL}${result.image_url}`;
    document.getElementById('gradcamImage').src = `${API_URL}${result.gradcam_url}`;
    document.getElementById('predictionText').textContent = result.prediction;
    document.getElementById('confidenceText').textContent = `${result.confidence.toFixed(1)}%`;
    document.getElementById('resultPatientName').textContent = result.patient_name;
    document.getElementById('resultPatientId').textContent = result.patient_id;

    document.getElementById('predictionText').className = `text-3xl font-bold ${isTumor ? 'text-red-700' : 'text-green-700'}`;
    document.getElementById('confidenceText').className = `text-3xl font-bold ${isTumor ? 'text-red-700' : 'text-green-700'}`;

    document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ===================== NEW SCAN =====================
function newScan() {
    document.getElementById('uploadForm').reset();
    document.getElementById('imagePreview').classList.add('hidden');
    document.getElementById('resultCard').classList.add('hidden');
    currentScanId = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===================== LOGOUT =====================
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('doctor');
    window.location.href = 'index.html';
}

// ===================== INITIALIZE =====================
loadDoctorInfo();
loadStats();
loadRecentScans();
showView('upload');
</script>
