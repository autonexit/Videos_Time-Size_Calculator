import os
import cv2
import threading
import customtkinter as ctk
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------------- Helpers ----------------
def format_bytes(num_bytes: int) -> str:
    # نمایش خوانا
    step = 1024.0
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < step:
            return f"{size:.2f} {unit}"
        size /= step
    return f"{size:.2f} PB"

def safe_video_duration_seconds(path: str) -> float:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        cap.release()
        return 0.0

    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    cap.release()

    if fps and fps > 0:
        return float(frames / fps)
    return 0.0

# ---------------- UI (no class) ----------------
app = ctk.CTk()
app.title("MP4 Duration Calculator")
app.geometry("600x450")
app.resizable(False, False)

selected_path = {"value": ""}  # ساده‌ترین روش برای دسترسی داخل توابع

title_label = ctk.CTkLabel(app, text="🎬 MP4 Duration & Size Calculator", font=("Arial", 26, "bold"))
title_label.pack(pady=20)

path_label = ctk.CTkLabel(app, text="No folder selected", wraplength=500)
path_label.pack(pady=5)

progress = ctk.CTkProgressBar(app, width=400)
progress.set(0)
progress.pack(pady=10)

result_label = ctk.CTkLabel(app, text="", font=("Arial", 16))
result_label.pack(pady=20)

def select_folder():
    p = filedialog.askdirectory()
    if p:
        selected_path["value"] = p
        path_label.configure(text=p)
        result_label.configure(text="")
        progress.set(0)

def set_ui_progress(value: float):
    # آپدیت امن UI از داخل ترد
    app.after(0, lambda: progress.set(value))

def set_ui_text(text: str):
    app.after(0, lambda: result_label.configure(text=text))

def calculate():
    folder = selected_path["value"]
    if not folder:
        set_ui_text("⚠ Please select a folder first!")
        return

    mp4_files = []
    total_size_bytes = 0

    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".mp4"):
                full = os.path.join(root, f)
                mp4_files.append(full)
                # حجم فایل
                try:
                    total_size_bytes += os.path.getsize(full)
                except OSError:
                    pass

    total_files = len(mp4_files)
    if total_files == 0:
        set_ui_text("No MP4 files found in this folder.")
        set_ui_progress(0)
        return

    set_ui_text(f"Found {total_files} videos... calculating")

    total_seconds = 0.0

    for idx, file_path in enumerate(mp4_files):
        total_seconds += safe_video_duration_seconds(file_path)

        prog = (idx + 1) / total_files
        set_ui_progress(prog)

    total_hours = total_seconds / 3600.0
    size_text = format_bytes(total_size_bytes)

    # ... همان کد قبلی ...

    set_ui_text(
        f"🎉 Total Time: {total_hours:.2f} hours\n"
        f"📦 Total Size: {size_text}\n"
        f"🎞 Files: {total_files}\n"
        f"POWEREN.IR"
    )



def start_thread():
    threading.Thread(target=calculate, daemon=True).start()

select_button = ctk.CTkButton(app, text="Select Folder", width=200, height=40, command=select_folder)
select_button.pack(pady=10)

start_button = ctk.CTkButton(
    app,
    text="Start Calculation",
    width=200,
    height=40,
    fg_color="green",
    hover_color="#1f6f43",
    command=start_thread
)
start_button.pack(pady=15)

app.mainloop()