
      const dropzone = document.getElementById("dropzone");
      const fileInput = document.getElementById("fileInput");
      const processBtn = document.getElementById("processBtn");
      const statusEl = document.getElementById("status");
      const fileInfo = document.getElementById("fileInfo");
      const fileNameEl = document.getElementById("fileName");
      const fileSizeEl = document.getElementById("fileSize");
      const filePreviewEl = document.getElementById("filePreview"); // New element
      const removeFileBtn = document.getElementById("removeFile");
      const resultImage = document.getElementById("resultImage");
      const resultContainer = document.getElementById("resultContainer");
      const downloadBtn = document.getElementById("downloadBtn");

      let selectedFile = null;
      let currentImageBlob = null;

      const resetStatus = () => {
        statusEl.textContent = "";
        statusEl.className = "status";
      };

      const setStatus = (message, kind = "") => {
        statusEl.textContent = message;
        statusEl.className = kind ? `status active ${kind}` : "status";
      };

      const humanFileSize = (bytes) => {
        if (!bytes) return "0 B";
        const thresh = 1024;
        if (Math.abs(bytes) < thresh) {
          return `${bytes} B`;
        }
        const units = ["KB", "MB", "GB", "TB"];
        let u = -1;
        do {
          bytes /= thresh;
          ++u;
        } while (Math.abs(bytes) >= thresh && u < units.length - 1);
        return `${bytes.toFixed(1)} ${units[u]}`;
      };

      const updateUI = () => {
        if (selectedFile) {
          fileNameEl.textContent = selectedFile.name;
          fileSizeEl.textContent = humanFileSize(selectedFile.size);
          fileInfo.classList.add("active");
          processBtn.disabled = false;

          // Display image preview
          const reader = new FileReader();
          reader.onload = (e) => {
            filePreviewEl.src = e.target.result;
            filePreviewEl.style.display = "block";
          };
          reader.readAsDataURL(selectedFile);
        } else {
          fileInfo.classList.remove("active");
          processBtn.disabled = true;
          filePreviewEl.style.display = "none";
          filePreviewEl.src = "";
          resultContainer.style.display = "none"; // Hide result when no file
          resultImage.src = ""; // Clear result image
          currentImageBlob = null; // Clear the download blob
        }
      };

      const acceptFile = (file) => {
        if (!file) {
          selectedFile = null;
          updateUI();
          return;
        }

        if (!file.type.startsWith("image/")) {
          setStatus("Please choose an image file.", "error");
          selectedFile = null;
          updateUI();
          return;
        }

        resetStatus();
        selectedFile = file;
        updateUI();
      };

      dropzone.addEventListener("dragover", (event) => {
        event.preventDefault();
        dropzone.classList.add("dragover");
      });

      dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
      });

      dropzone.addEventListener("drop", (event) => {
        event.preventDefault();
        dropzone.classList.remove("dragover");
        const file = event.dataTransfer.files?.[0];
        acceptFile(file);
      });

      fileInput.addEventListener("change", (event) => {
        const file = event.target.files?.[0];
        acceptFile(file);
      });

      removeFileBtn.addEventListener("click", () => {
        selectedFile = null;
        fileInput.value = "";
        updateUI();
        resetStatus();
      });

      processBtn.addEventListener("click", async () => {
        if (!selectedFile) {
          return;
        }

        resetStatus();
        setStatus("Processing your image with AI...", "processing");
        processBtn.classList.add("loading");
        processBtn.disabled = true;

        const formData = new FormData();
        formData.append("image", selectedFile, selectedFile.name);

        try {
          const response = await fetch("/process", {
            method: "POST",
            body: formData,
          });

          if (!response.ok) {
            let errorMessage = "Failed to process image.";
            try {
              const data = await response.json();
              if (data?.error) {
                errorMessage = data.error;
              }
            } catch (_) {
              // ignore JSON parsing error
            }
            throw new Error(errorMessage);
          }

          const blob = await response.blob();
          currentImageBlob = blob;
          const imageUrl = URL.createObjectURL(blob);
          resultImage.src = imageUrl;
          resultContainer.style.display = "block";

          // Clean up the old object URL when the image loads
          resultImage.onload = () => {
            URL.revokeObjectURL(imageUrl);
          };

          setStatus("Success! Your upscaled image is ready.", "success");
        } catch (error) {
          console.error(error);
          setStatus(error.message, "error");
        } finally {
          processBtn.classList.remove("loading");
          processBtn.disabled = !selectedFile;
        }
      });

      downloadBtn.addEventListener("click", () => {
        if (!currentImageBlob || !selectedFile) {
          return;
        }

        const downloadUrl = URL.createObjectURL(currentImageBlob);
        const link = document.createElement("a");
        const baseName = selectedFile.name.replace(/\.[^/.]+$/, "");
        link.href = downloadUrl;
        link.download = `upscaled_${baseName}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(downloadUrl);
      });

      // Initial UI update
      updateUI();