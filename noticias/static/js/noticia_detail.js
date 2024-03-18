// Función para imprimir la página actual
function printPage() {
    window.print(); // Invoca la función de impresión del navegador
}

// Función para copiar el enlace de la página actual al portapapeles
function copyLink() {
    var url = window.location.href; // Obtener el enlace de la página actual
    navigator.clipboard.writeText(url); // Copiar el enlace al portapapeles del dispositivo
    alert("Enlace copiado: " + url); // Mostrar un mensaje de alerta con el enlace copiado
}

// Función para alternar la visualización del menú desplegable de compartir
function toggleDropdown() {
    var dropdownMenu = document.getElementById("share-dropdown"); // Obtener el menú desplegable de compartir
    var hr = document.querySelector("hr"); // Obtener la línea horizontal
    var spaceBelowDropdown = document.getElementById("space-below-dropdown"); // Obtener el espacio debajo del menú desplegable
    
    // Verificar si el menú desplegable está visible
    if (dropdownMenu.style.display === "block") {
        // Si está visible, ocultarlo
        dropdownMenu.style.display = "none";
        spaceBelowDropdown.style.marginTop = "0"; // Restablecer el margen superior del espacio debajo del menú desplegable
        hr.style.marginTop = "0"; // Ajuste para desplazar la línea horizontal hacia arriba
    } else {
        // Si está oculto, mostrarlo
        dropdownMenu.style.display = "block";
        var dropdownHeight = dropdownMenu.offsetHeight; // Obtener la altura del menú desplegable
        spaceBelowDropdown.style.marginTop = dropdownHeight + "px"; // Establecer el margen superior del espacio debajo del menú desplegable
        hr.style.marginTop = dropdownHeight + "px"; // Ajuste para desplazar la línea horizontal hacia abajo
    }
}

// Escucha eventos de clic en todo el documento
document.addEventListener('click', function(event) {
    var dropdownMenu = document.getElementById('share-dropdown'); // Obtener el menú desplegable de compartir
    var shareIcon = document.querySelector('.share-icon'); // Obtener el icono de compartir
    
    // Verifica si el clic ocurrió dentro del menú desplegable o en el icono de compartir
    var isClickInsideDropdown = dropdownMenu.contains(event.target);
    var isClickOnShareIcon = shareIcon.contains(event.target);
    
    // Si el clic ocurrió fuera del menú desplegable y no en el icono de compartir, cierra el menú
    if (!isClickInsideDropdown && !isClickOnShareIcon) {
        dropdownMenu.style.display = 'none'; // Oculta el menú desplegable
        var hr = document.querySelector("hr"); // Obtener la línea horizontal
        var spaceBelowDropdown = document.getElementById("space-below-dropdown"); // Obtener el espacio debajo del menú desplegable
        spaceBelowDropdown.style.marginTop = "0"; // Restablecer el margen superior del espacio debajo del menú desplegable
        hr.style.marginTop = "0"; // Restablecer la posición de la línea horizontal
    }
});
