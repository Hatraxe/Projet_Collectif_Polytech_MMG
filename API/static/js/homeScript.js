// Pour la modale d'importation
var importModal = document.getElementById('myModal');
var importBtn = document.getElementById('importButton');
var closeImport = document.getElementsByClassName('close')[0];

importBtn.onclick = function() {
    importModal.style.display = 'block';
}

closeImport.onclick = function() {
    importModal.style.display = 'none';
}

// Pour la modale d'exportation
var exportModal = document.getElementById('exportModal');
var exportBtn = document.getElementById('exportButton');
var closeExport = document.getElementsByClassName('closeExport')[0];

exportBtn.onclick = function() {
    exportModal.style.display = 'block';
}

closeExport.onclick = function() {
    exportModal.style.display = 'none';
}




// Pour la modale d'exportation des graphiques

// Gérer le clic en dehors des modales
window.onclick = function(event) {
    if (event.target === importModal) {
        importModal.style.display = 'none';
    }
    if (event.target === exportModal) {
        exportModal.style.display = 'none';
    }

}

var deleteDataButton = document.getElementById('deleteDataButton');
var popupDeleteData = document.getElementById('popupDeleteData');

deleteDataButton.onclick = function() {
    popupDeleteData.style.display = 'block';
    setTimeout(function() {
        popupDeleteData.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};

var importDataButton = document.getElementById('importDataButton');
var popupImportData = document.getElementById('popupImportData');

importDataButton.onclick = function() {
    popupImportData.style.display = 'block';
    setTimeout(function() {
        popupImportData.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};



var exportDataButton = document.getElementById('exportDataButton');
var popupDeleteData = document.getElementById('popupDeleteData');

exportDataButton.onclick = function() {
    popupDeleteData.style.display = 'block';
    setTimeout(function() {
        popupDeleteData.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};

