document.addEventListener("DOMContentLoaded", function() {
    // 1. Manejo del menú desplegable con el ícono de engranaje de configuración (⚙️)
    const gearBtn = document.getElementById("settingsGearBtn");
    const dropdownMenu = document.getElementById("settingsDropdownMenu");

    if (gearBtn && dropdownMenu) {
        gearBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            dropdownMenu.classList.toggle("show");
        });

        document.addEventListener("click", function(e) {
            if (!dropdownMenu.contains(e.target) && e.target !== gearBtn) {
                dropdownMenu.classList.remove("show");
            }
        });
    }

    // 2. Manejo de botones de verificación Verde Check / Rojo X
    const checkVerifyContainers = document.querySelectorAll(".check-verify-container");
    checkVerifyContainers.forEach(container => {
        const greenBtn = container.querySelector(".btn-green-check");
        const redBtn = container.querySelector(".btn-red-cross");
        const hiddenInput = container.querySelector(".hidden-check-input");
        const subInputContainer = container.closest(".field-group")?.querySelector(".sub-input-container");

        if (greenBtn && redBtn && hiddenInput) {
            greenBtn.addEventListener("click", function(e) {
                e.preventDefault();
                hiddenInput.value = "yes";
                greenBtn.classList.add("active");
                redBtn.classList.remove("active");
                clearFieldError(container.closest(".field-group"));
                if (subInputContainer) {
                    subInputContainer.style.display = "none";
                }
            });

            redBtn.addEventListener("click", function(e) {
                e.preventDefault();
                hiddenInput.value = "no";
                redBtn.classList.add("active");
                greenBtn.classList.remove("active");
                clearFieldError(container.closest(".field-group"));
                if (subInputContainer) {
                    subInputContainer.style.display = "block";
                }
            });
        }
    });

    // 3. Subida de archivos en la pantalla de Digitalizar
    const selectFileBtn = document.getElementById("selectFileBtn");
    const fileInput = document.getElementById("formFileInput");
    const fileNameDisplay = document.getElementById("fileNameDisplay");

    if (selectFileBtn && fileInput) {
        selectFileBtn.addEventListener("click", function(e) {
            e.preventDefault();
            fileInput.click();
        });

        fileInput.addEventListener("change", function() {
            if (fileInput.files && fileInput.files[0]) {
                const name = fileInput.files[0].name;
                if (fileNameDisplay) {
                    fileNameDisplay.textContent = "Archivo subido: " + name;
                }
            }
        });
    }

    // 4. MEJORA PASO 3: Validación de Campos Incompletos al Presionar "Sí"
    const stepForm = document.getElementById("stepForm");
    const incompleteModal = document.getElementById("incompleteFieldsModal");
    const btnIncompleteOk = document.getElementById("btnIncompleteOk");

    if (btnIncompleteOk && incompleteModal) {
        btnIncompleteOk.addEventListener("click", function(e) {
            e.preventDefault();
            incompleteModal.classList.remove("show");
        });
    }

    function clearFieldError(fieldGroup) {
        if (!fieldGroup) return;
        const icon = fieldGroup.querySelector(".warning-incomplete-icon");
        if (icon) icon.remove();
        const input = fieldGroup.querySelector(".input-pill");
        if (input) input.classList.remove("input-error");
    }

    if (stepForm) {
        stepForm.addEventListener("submit", function(e) {
            // Solo validar si la acción presiona es "next" (Sí)
            const submitter = e.submitter;
            if (submitter && submitter.getAttribute("name") === "action" && submitter.getAttribute("value") === "next") {
                let hasIncomplete = false;
                const fieldGroups = stepForm.querySelectorAll(".field-group");

                fieldGroups.forEach(group => {
                    const label = group.querySelector(".field-label");
                    const input = group.querySelector("input[type='text'].input-pill, select.input-pill");
                    const hiddenCheck = group.querySelector(".hidden-check-input");

                    let isFieldEmpty = false;

                    if (input) {
                        if (!input.value || input.value.trim() === "") {
                            isFieldEmpty = true;
                        }
                    } else if (hiddenCheck) {
                        if (!hiddenCheck.value || hiddenCheck.value.trim() === "") {
                            isFieldEmpty = true;
                        }
                    }

                    if (isFieldEmpty) {
                        hasIncomplete = true;
                        if (input) input.classList.add("input-error");

                        // Agregar ícono de advertencia ⚠️ al lado del título del campo si no existe
                        if (label && !label.querySelector(".warning-incomplete-icon")) {
                            const warnSpan = document.createElement("span");
                            warnSpan.className = "warning-incomplete-icon";
                            warnSpan.textContent = "⚠️";
                            label.appendChild(warnSpan);
                        }
                    } else {
                        clearFieldError(group);
                    }
                });

                // Limpiar advertencia cuando el usuario escriba o seleccione
                stepForm.querySelectorAll("input, select").forEach(inp => {
                    inp.addEventListener("input", function() {
                        if (inp.value.trim() !== "") {
                            clearFieldError(inp.closest(".field-group"));
                        }
                    });
                    inp.addEventListener("change", function() {
                        if (inp.value.trim() !== "") {
                            clearFieldError(inp.closest(".field-group"));
                        }
                    });
                });

                if (hasIncomplete) {
                    e.preventDefault();
                    if (incompleteModal) {
                        incompleteModal.classList.add("show");
                    }
                }
            }
        });
    }

    // 5. MEJORA PASO 3: Lógica del Calendario Interactivo con Selector de Mes y Año en Listas (Roll)
    const monthNames = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ];

    const dateInputs = document.querySelectorAll(".input-date-picker");

    dateInputs.forEach(input => {
        const fieldGroup = input.closest(".field-group") || input.parentElement;
        const popup = fieldGroup.querySelector(".datepicker-popup");

        if (!popup) return;

        let currentDate = new Date(2026, 7, 16);
        let selectedDate = new Date(2026, 7, 16);

        const monthYearLabel = popup.querySelector(".datepicker-month-year");
        const prevBtn = popup.querySelector(".prev-month-btn");
        const nextBtn = popup.querySelector(".next-month-btn");
        const daysGrid = popup.querySelector(".datepicker-grid");
        const todayBtn = popup.querySelector(".btn-datepicker-today");

        // Crear elementos del panel Roll de Mes y Año si no existen
        let rollPanel = popup.querySelector(".datepicker-roll-panel");
        let monthSelect, yearSelect;

        if (!rollPanel) {
            rollPanel = document.createElement("div");
            rollPanel.className = "datepicker-roll-panel";

            monthSelect = document.createElement("select");
            monthSelect.className = "datepicker-roll-select month-roll-select";
            monthNames.forEach((m, idx) => {
                const opt = document.createElement("option");
                opt.value = idx;
                opt.textContent = m;
                monthSelect.appendChild(opt);
            });

            yearSelect = document.createElement("select");
            yearSelect.className = "datepicker-roll-select year-roll-select";
            for (let y = 1940; y <= 2050; y++) {
                const opt = document.createElement("option");
                opt.value = y;
                opt.textContent = y;
                yearSelect.appendChild(opt);
            }

            rollPanel.appendChild(monthSelect);
            rollPanel.appendChild(yearSelect);

            const daysHeader = popup.querySelector(".datepicker-days-header");
            popup.insertBefore(rollPanel, daysHeader);
        } else {
            monthSelect = rollPanel.querySelector(".month-roll-select");
            yearSelect = rollPanel.querySelector(".year-roll-select");
        }

        // Alternar vista Roll al hacer clic en el encabezado del mes y año (ej: "agosto 2026")
        if (monthYearLabel) {
            monthYearLabel.addEventListener("click", function(e) {
                e.stopPropagation();
                rollPanel.classList.toggle("show");
                if (rollPanel.classList.contains("show")) {
                    monthSelect.value = currentDate.getMonth();
                    yearSelect.value = currentDate.getFullYear();
                }
            });
        }

        // Al cambiar mes o año en las listas roll, actualizar el calendario inmediatamente
        monthSelect.addEventListener("change", function(e) {
            e.stopPropagation();
            currentDate.setMonth(parseInt(monthSelect.value));
            renderCalendar(currentDate.getFullYear(), currentDate.getMonth());
        });

        yearSelect.addEventListener("change", function(e) {
            e.stopPropagation();
            currentDate.setFullYear(parseInt(yearSelect.value));
            renderCalendar(currentDate.getFullYear(), currentDate.getMonth());
        });

        function renderCalendar(year, month) {
            if (!monthYearLabel || !daysGrid) return;
            monthYearLabel.textContent = `${monthNames[month]} ${year}`;
            daysGrid.innerHTML = "";

            const firstDayIndex = (new Date(year, month, 1).getDay() + 6) % 7;
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const daysInPrevMonth = new Date(year, month, 0).getDate();

            for (let x = firstDayIndex; x > 0; x--) {
                const dayDiv = document.createElement("div");
                dayDiv.className = "datepicker-day other-month";
                dayDiv.textContent = daysInPrevMonth - x + 1;
                daysGrid.appendChild(dayDiv);
            }

            for (let i = 1; i <= daysInMonth; i++) {
                const dayDiv = document.createElement("div");
                dayDiv.className = "datepicker-day";
                dayDiv.textContent = i;

                if (
                    i === selectedDate.getDate() &&
                    month === selectedDate.getMonth() &&
                    year === selectedDate.getFullYear()
                ) {
                    dayDiv.classList.add("selected");
                }

                dayDiv.addEventListener("click", function(e) {
                    e.stopPropagation();
                    selectedDate = new Date(year, month, i);
                    const formattedDay = String(i).padStart(2, "0");
                    const formattedMonth = String(month + 1).padStart(2, "0");
                    input.value = `${formattedDay}/${formattedMonth}/${year}`;
                    clearFieldError(fieldGroup);
                    popup.classList.remove("show");
                    rollPanel.classList.remove("show");
                });

                daysGrid.appendChild(dayDiv);
            }

            const totalCells = daysGrid.children.length;
            const nextDays = 42 - totalCells;
            for (let j = 1; j <= nextDays; j++) {
                const dayDiv = document.createElement("div");
                dayDiv.className = "datepicker-day other-month";
                dayDiv.textContent = j;
                daysGrid.appendChild(dayDiv);
            }
        }

        input.addEventListener("click", function(e) {
            e.stopPropagation();
            document.querySelectorAll(".datepicker-popup").forEach(p => {
                if (p !== popup) p.classList.remove("show");
            });
            popup.classList.toggle("show");
            renderCalendar(currentDate.getFullYear(), currentDate.getMonth());
        });

        if (prevBtn) {
            prevBtn.addEventListener("click", function(e) {
                e.stopPropagation();
                currentDate.setMonth(currentDate.getMonth() - 1);
                renderCalendar(currentDate.getFullYear(), currentDate.getMonth());
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", function(e) {
                e.stopPropagation();
                currentDate.setMonth(currentDate.getMonth() + 1);
                renderCalendar(currentDate.getFullYear(), currentDate.getMonth());
            });
        }

        if (todayBtn) {
            todayBtn.addEventListener("click", function(e) {
                e.stopPropagation();
                const now = new Date();
                currentDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                selectedDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                const formattedDay = String(now.getDate()).padStart(2, "0");
                const formattedMonth = String(now.getMonth() + 1).padStart(2, "0");
                input.value = `${formattedDay}/${formattedMonth}/${now.getFullYear()}`;
                clearFieldError(fieldGroup);
                popup.classList.remove("show");
                rollPanel.classList.remove("show");
            });
        }

        document.addEventListener("click", function(e) {
            if (!popup.contains(e.target) && e.target !== input) {
                popup.classList.remove("show");
                rollPanel.classList.remove("show");
            }
        });
    });
});
