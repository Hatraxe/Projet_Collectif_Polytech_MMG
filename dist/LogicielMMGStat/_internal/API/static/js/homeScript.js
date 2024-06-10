// Pour la modale d'importation
var importModal = document.getElementById('myModal');
var importBtn = document.getElementById('importButton');
var closeImport = document.getElementsByClassName('closeImport')[0];

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
var popupExportData = document.getElementById('popupExportData');

exportDataButton.onclick = function() {
    popupExportData.style.display = 'block';
    setTimeout(function() {
        popupExportData.style.display = 'none';
    }, 1500); // Disparaît après 3 secondes
};

var sidenav = document.getElementById("mySidenav");
var openBtn = document.getElementById("openBtn");
var closeBtn = document.getElementById("closeBtn");

openBtn.onclick = openNav;
closeBtn.onclick = closeNav;

/* Set the width of the side navigation to 250px */
function openNav() {
  sidenav.classList.add("active");
}

/* Set the width of the side navigation to 0 */
function closeNav() {
  sidenav.classList.remove("active");
}
