var exportIndicatorsModal = document.getElementById('exportIndicatorsModal');
var exportIndicatorsButton = document.getElementById('exportIndicatorsButton');
var closeIndicators = document.getElementsByClassName('closeIndicators')[0];

exportIndicatorsButton.onclick = function() {
    exportIndicatorsModal.style.display = 'block';
}

closeIndicators.onclick = function() {
    exportIndicatorsModal.style.display = 'none';
}

window.onclick = function(event) {
        if (event.target === exportIndicatorsModal) {
        exportIndicatorsModal.style.display = 'none';
    }
}

var addIndicatorsButton = document.getElementById('addIndicatorsToDashboard');
var popup = document.getElementById('popupAddIndicatorsToDashboard');

addIndicatorsButton.onclick = function() {
    popup.style.display = 'block';
    setTimeout(function() {
        popup.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};

var generateIndicatorsButton = document.getElementById('generateIndicatorsButton');
var generateButtonPopup = document.getElementById('popupGenerateIndicators');

generateIndicatorsButton.onclick = function() {
    generateButtonPopup.style.display = 'block';
    setTimeout(function() {
        generateButtonPopup.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};


