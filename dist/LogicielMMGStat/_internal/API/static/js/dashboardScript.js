var exportDashboardModal = document.getElementById('exportDashboardModal');
var exportDashboardButton = document.getElementById('exportDashboardButton');
var closeDashboardExport = document.getElementsByClassName('closeDashboardExport')[0];

exportDashboardButton.onclick = function() {
    exportDashboardModal.style.display = 'block';
}

closeDashboardExport.onclick = function() {
    exportDashboardModal.style.display = 'none';
}

window.onclick = function(event) {
        if (event.target === exportDashboardModal) {
        exportDashboardModal.style.display = 'none';
    }
}

var reinitialiseButton = document.getElementById('reinitialiseButton');
var popupReinitializeDashboard = document.getElementById('popupReinitializeDashboard');

reinitialiseButton.onclick = function() {
    popupReinitializeDashboard.style.display = 'block';
    setTimeout(function() {
        popupReinitializeDashboard.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};

var exportPopUpDashboardButton = document.getElementById('exportPopUpDashboardButton');
var popupExportDashboard = document.getElementById('popupExportDashboard');

exportPopUpDashboardButton.onclick = function() {
    popupExportDashboard.style.display = 'block';
    setTimeout(function() {
        popupExportDashboard.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};


