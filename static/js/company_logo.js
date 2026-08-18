document.addEventListener("DOMContentLoaded", function() {
    const logoBtn = document.getElementById("companyLogoBtn");
    const logoInput = document.getElementById("companyLogoInput");
    const logoImg = document.getElementById("companyLogoImg");

    if (logoBtn && logoInput) {
        logoBtn.addEventListener("click", function() {
            logoInput.click();
        });

        logoInput.addEventListener("change", function() {
            if (logoInput.files && logoInput.files[0]) {
                const formData = new FormData();
                formData.append("logo", logoInput.files[0]);

                fetch("/api/upload-logo", {
                    method: "POST",
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.logo_url) {
                        if (logoImg) {
                            logoImg.src = data.logo_url;
                            logoImg.style.display = "inline-block";
                        }
                    } else {
                        alert("Error al cargar la imagen: " + (data.error || "Desconocido"));
                    }
                })
                .catch(err => {
                    console.error("Error al subir logo:", err);
                });
            }
        });
    }
});
