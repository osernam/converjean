const overlay = document.getElementById('overlay');
    const modalFinalizado = document.getElementById('modalFinalizado');

    function cambiarContenidoModal(modalId) {
      const modal = document.getElementById(modalId);
      modal.innerHTML = 'Nuevo contenido para ' + modalId;
    }

    function mostrarModalFinalizado() {
      overlay.style.display = 'flex'; // Muestra la overlay
      modalFinalizado.style.display = 'block'; // Muestra el modal de "Finalizado"
      // Simular un retraso antes de ocultar la ventana flotante
      setTimeout(function() {
        overlay.style.display = 'none'; // Oculta la overlay
        modalFinalizado.style.display = 'none'; // Oculta el modal de "Finalizado"
      }, 2000); // Cambia el 2000 a la cantidad de milisegundos que deseas esperar antes de ocultar la ventana flotante
    }