var exportGraphModal = document.getElementById('exportGraphModal');
var exportGraphBtn = document.getElementById('exportGraphButton');
var closeGraphExport = document.getElementsByClassName('closeGraphExport')[0];

exportGraphBtn.onclick = function() {
    exportGraphModal.style.display = 'block';
}

closeGraphExport.onclick = function() {
    exportGraphModal.style.display = 'none';
}

window.onclick = function(event) {
        if (event.target === exportGraphModal) {
        exportGraphModal.style.display = 'none';
    }
}

var addGraphButton = document.getElementById('addGraphToDashboard');
var popupAddGraphDashboard = document.getElementById('popupAddGraphToDashboard');

addGraphButton.onclick = function() {
    popupAddGraphDashboard.style.display = 'block';
    setTimeout(function() {
        popupAddGraphDashboard.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};

var generateGraphButton = document.getElementById('generateGraphButton');
var popupGenerateGraph = document.getElementById('popupGenerateGraph');

generateGraphButton.onclick = function() {
    popupGenerateGraph.style.display = 'block';
    setTimeout(function() {
        popupGenerateGraph.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};