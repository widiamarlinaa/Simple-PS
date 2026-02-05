import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from ttkthemes import ThemedTk

class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class ModernImageProcessor:
    def __init__(self):
        self.window = ThemedTk(theme="arc")
        self.window.title("PIXPOP FUSION")
        self.window.state('zoomed')

        self.current_image = None
        self.previous_image = None
        self.filename = None
        self.zoom_factor = 1.0
        self.image_history = []

        self.setup_ui()

    def setup_ui(self):
        # Main container
        self.container = ttk.Frame(self.window)
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_frame = ttk.Frame(self.container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        title = ttk.Label(header_frame, text="PIXPOP FUSION", font=("Helvetica", 16, "bold"))
        title.pack(side=tk.LEFT)

        # Main content area
        content_frame = ttk.Frame(self.container)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar (left side) with scrolling
        toolbar_frame = ScrollableFrame(content_frame)
        toolbar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        self.toolbar = toolbar_frame.scrollable_frame
        self.setup_file_section()
        self.setup_basic_operations()
        self.setup_advanced_operations()

        # Image area (center)
        self.image_frame = ttk.Frame(content_frame)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.image_frame, bg='#FFFFFF', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Filters section (bottom)
        self.setup_filters_section()

    def setup_file_section(self):
        file_frame = ttk.LabelFrame(self.toolbar, text="File", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(file_frame, text="📂 Open Image", command=self.open_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="💾 Save Image", command=self.save_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="↩️ Undo", command=self.undo).pack(fill=tk.X, pady=2)

    def setup_basic_operations(self):
        basic_frame = ttk.LabelFrame(self.toolbar, text="Image Adjustments", padding=10)
        basic_frame.pack(fill=tk.X, pady=10)

        ttk.Button(basic_frame, text="🔄 Convert to Grayscale", command=self.to_grayscale).pack(fill=tk.X, pady=2)
        ttk.Button(basic_frame, text="⚫⚪ Convert to Binary", command=self.to_binary).pack(fill=tk.X, pady=2)

        ttk.Label(basic_frame, text="✨ Brightness").pack(pady=(10, 0))
        self.brightness_scale = ttk.Scale(basic_frame, from_=-100, to=100, orient=tk.HORIZONTAL)
        self.brightness_scale.pack(fill=tk.X)

        ttk.Button(basic_frame, text="Apply Adjustments", command=self.adjust_brightness).pack(fill=tk.X, pady=5)

        ttk.Label(basic_frame, text="🎭 Contrast").pack(pady=(10, 0))
        self.contrast_scale = ttk.Scale(basic_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL)
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack(fill=tk.X)

        ttk.Button(basic_frame, text="Apply Adjustments", command=self.adjust_contrast).pack(fill=tk.X, pady=5)

    def setup_advanced_operations(self):
        advanced_frame = ttk.LabelFrame(self.toolbar, text="Transform", padding=10)
        advanced_frame.pack(fill=tk.X, pady=10)

        rotation_frame = ttk.Frame(advanced_frame)
        rotation_frame.pack(fill=tk.X, pady=5)
        ttk.Button(rotation_frame, text="Rotate 90°", command=lambda: self.rotate_image(90)).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(rotation_frame, text="Rotate 180°", command=lambda: self.rotate_image(180)).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(rotation_frame, text="Rotate 270°", command=lambda: self.rotate_image(270)).pack(side=tk.LEFT, expand=True, padx=2)

        zoom_frame = ttk.Frame(advanced_frame)
        zoom_frame.pack(fill=tk.X, pady=5)
        ttk.Button(zoom_frame, text="🔍 Zoom In", command=self.zoom_in).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(zoom_frame, text="🔍 Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, expand=True, padx=2)

        flip_frame = ttk.Frame(advanced_frame)
        flip_frame.pack(fill=tk.X, pady=5)
        ttk.Button(flip_frame, text="↔️ Flip H", command=lambda: self.flip_image(1)).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(flip_frame, text="↕️ Flip V", command=lambda: self.flip_image(0)).pack(side=tk.LEFT, expand=True, padx=2)

    def setup_filters_section(self):
        filters_frame = ttk.Frame(self.container, padding=10)
        filters_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        ttk.Button(filters_frame, text="🌫️ Blur Effect", command=self.blur_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(filters_frame, text="✨ Sharpen", command=self.sharpen_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(filters_frame, text="🎨 Sepia", command=self.apply_sepia).pack(side=tk.LEFT, padx=5)
        ttk.Button(filters_frame, text="🌈 Color Pop", command=self.apply_color_pop).pack(side=tk.LEFT, padx=5)


    def open_image(self):
        self.filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")])
        if self.filename:
            self.current_image = cv2.imread(self.filename)
            self.image_history.clear()  
            self.show_image()

            self.canvas.update()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def save_image(self):
        if self.current_image is None:
            messagebox.showerror("Error", "Tidak ada gambar untuk disimpan!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        
        if filename:
            cv2.imwrite(filename, self.current_image)
            messagebox.showinfo("Sukses", "Gambar berhasil disimpan!")

    def show_image(self):
        if self.current_image is None:
            return

        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)

        # Update the window to ensure the canvas size is correct
        self.window.update()  
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_height, image_width = image_rgb.shape[:2]

        # Calculate scale for fitting into canvas
        scale = min(canvas_width / image_width, canvas_height / image_height) * self.zoom_factor
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)

        if new_width > 0 and new_height > 0:  # Ensure dimensions are valid
            image_resized = cv2.resize(image_rgb, (new_width, new_height))

            # Convert to PhotoImage
            image = Image.fromarray(image_resized)
            photo = ImageTk.PhotoImage(image)

            # Update the canvas
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                image=photo, anchor="center"
            )
            self.canvas.image = photo  # Keep a reference!
        
    def backup_image(self):
        if self.current_image is not None:
            self.image_history.append(self.current_image.copy())

        if len(self.image_history) > 100:  # Batas langkah
            self.image_history.pop(0)
    
    def undo(self):
        if self.image_history:
            self.current_image = self.image_history.pop()
            self.show_image()
        else:
            messagebox.showinfo("Undo", "Tidak ada langkah untuk di-undo!")
    
    def to_grayscale(self):
        if self.current_image is None:
            return
        self.backup_image()  # Simpan gambar sebelum perubahan
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_GRAY2BGR)
        self.show_image()
    
    def to_binary(self):
        if self.current_image is None:
            return
        self.backup_image()
        gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        self.current_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        self.show_image()
    
    def adjust_brightness(self):
        if self.current_image is None:
            return
        self.backup_image()

        value = int(self.brightness_scale.get())
        print("Adjusting brightness by:", value)  # Debugging line

        hsv = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        if value > 0:
            lim = 255 - value
            v[v > lim] = 255
            v[v <= lim] += value
        else:
            value = abs(value)
            v[v < value] = 0
            v[v >= value] -= value

        final_hsv = cv2.merge((h, s, v))
        self.current_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        self.show_image()
    
    def adjust_contrast(self):
        if self.current_image is None:
            return
        self.backup_image()
        factor = self.contrast_scale.get()
        self.current_image = cv2.convertScaleAbs(self.current_image, alpha=factor, beta=0)
        self.show_image()

    def rotate_image(self, angle):
        if self.current_image is None:
            return
        self.backup_image()  # Simpan gambar sebelum perubahan

        # Dapatkan dimensi gambar
        (h, w) = self.current_image.shape[:2]
        center = (w // 2, h // 2)

        # Hitung matriks rotasi
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Hitung ukuran bounding box baru
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        # Sesuaikan matriks rotasi untuk menggeser gambar ke tengah
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]

        # Lakukan rotasi dan sesuaikan ukuran kanvas
        rotated_image = cv2.warpAffine(self.current_image, rotation_matrix, (new_w, new_h))
        self.current_image = rotated_image
    
        self.backup_image()
        self.show_image()

    def flip_image(self, axis):
        if self.current_image is None:
            return
        self.backup_image()  # Simpan gambar sebelum perubahan
        
        flipped_image = cv2.flip(self.current_image, axis)
        self.current_image = flipped_image
        
        # Simpan gambar setelah flip ke riwayat
        self.backup_image()
        self.show_image()

    def zoom_in(self):
        self.zoom_factor *= 1.1
        self.show_image()

    def zoom_out(self):
        self.zoom_factor /= 1.1
        self.show_image()

    def blur_image(self):
        if self.current_image is None:
            return
        self.backup_image()
        
        blurred_image = cv2.GaussianBlur(self.current_image, (15, 15), 0)
        self.current_image = blurred_image
        self.show_image()

    def sharpen_image(self):
        if self.current_image is None:
            return
        self.backup_image()
        
        kernel = np.array([[0, -1, 0], 
                       [-1, 5, -1], 
                       [0, -1, 0]])
        sharpened_image = cv2.filter2D(self.current_image, -1, kernel)
        self.current_image = sharpened_image
        self.show_image()

    def apply_sepia(self):
        if self.current_image is None:
            return
        self.backup_image()

        # Pastikan gambar dalam format RGB
        image_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)

        # Terapkan filter sepia
        sepia_filter = np.array([[0.393, 0.769, 0.189],
                                [0.349, 0.686, 0.168],
                                [0.272, 0.534, 0.131]])
        sepia_image = cv2.transform(image_rgb, sepia_filter)

        # Pastikan nilai berada dalam rentang 0-255 dan ubah ke uint8
        sepia_image = np.clip(sepia_image, 0, 255).astype(np.uint8)

        # Kembali ke format BGR untuk OpenCV
        self.current_image = cv2.cvtColor(sepia_image, cv2.COLOR_RGB2BGR)
        self.show_image()

    def apply_color_pop(self):
        if self.current_image is None:
            return
        self.backup_image()

        # Apply color pop (increase saturation)
        hsv_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2HSV)
        hsv_image[..., 1] = hsv_image[..., 1] * 1.5
        color_pop_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        self.current_image = np.clip(color_pop_image, 0, 255)
        
        self.show_image()

if __name__ == "__main__":
    app = ModernImageProcessor()
    app.window.mainloop()
