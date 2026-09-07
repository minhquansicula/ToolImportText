document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const previewContainer = document.getElementById("previewContainer");
    const imagePreview = document.getElementById("imagePreview");
    const submitBtn = document.getElementById("submitBtn");
    const uploadForm = document.getElementById("uploadForm");
    const statusMessage = document.getElementById("statusMessage");

    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                previewContainer.classList.remove("hidden");
                submitBtn.classList.remove("hidden");
                submitBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        } else {
            previewContainer.classList.add("hidden");
            submitBtn.classList.add("hidden");
            submitBtn.disabled = true;
        }
    });

    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        submitBtn.disabled = true;
        submitBtn.textContent = "Đang gửi...";
        statusMessage.textContent = "";
        statusMessage.className = "";

        try {
            const response = await fetch(`/upload/${token}`, {
                method: "POST",
                body: formData
            });

            const data = await response.json().catch(() => null);

            if (response.ok) {
                statusMessage.textContent = "Thành công: " + (data ? data.message : "Ảnh đã được tải lên.");
                statusMessage.className = "success";
                // Reset form
                fileInput.value = "";
                previewContainer.classList.add("hidden");
                submitBtn.classList.add("hidden");
            } else {
                throw new Error((data && data.detail) ? data.detail : "Có lỗi xảy ra khi tải ảnh lên.");
            }
        } catch (error) {
            statusMessage.textContent = error.message;
            statusMessage.className = "error";
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Gửi lên máy tính";
        }
    });
});
