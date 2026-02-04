import customtkinter as ctk
import subprocess
import threading
import os
import tkinter as tk
from datetime import datetime
import psutil
import time
import pyautogui


class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.user_name = "АНДРЕЙ"
        self.title(f"JARVIS v4.2 | {self.user_name} WORKSTATION")
        self.geometry("1000x950")
        ctk.set_appearance_mode("dark")

        self.working_dir = os.getcwd()
        self.is_thinking = False
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_idx = 0

        self.setup_ui()

        # Системный монитор в фоне
        threading.Thread(target=self.update_system_stats, daemon=True).start()

    def update_system_stats(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.after(0, lambda c=cpu, r=ram: self.title(
                    f"JARVIS v4.2 | CPU: {c}% | RAM: {r}% | {self.user_name}"
                ))
            except:
                pass
            time.sleep(2)

    def setup_ui(self):
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=10, padx=20, fill="x")

        self.status_label = ctk.CTkLabel(self.top_frame, text="• ONLINE", text_color="#2ecc71",
                                         font=("Arial", 12, "bold"))
        self.status_label.pack(side="left", padx=15)

        self.spinner_label = ctk.CTkLabel(self.top_frame, text="", font=("Arial", 20), text_color="#FFD700")
        self.spinner_label.pack(side="left", padx=10)

        # Кнопки управления
        ctk.CTkButton(self.top_frame, text="SYNC", command=self.git_sync, fg_color="#2ecc71", width=80).pack(
            side="right", padx=5)
        ctk.CTkButton(self.top_frame, text="SCAN", command=self.take_screenshot, fg_color="#e67e22", width=80).pack(
            side="right", padx=5)

        # ЧАТ с восстановленным копированием
        self.chat_display = ctk.CTkTextbox(self, width=960, height=700, wrap="word", font=("Consolas", 15))
        self.chat_display.pack(pady=10, padx=20)
        self.chat_display._textbox.tag_config("jarvis_tag", foreground="#FFD700")
        self.chat_display._textbox.tag_config("user_tag", foreground="#3498db")

        # Привязываем контекстное меню (правая кнопка мыши)
        self.chat_display.bind("<Button-3>", self.show_context_menu)
        self.chat_display.configure(state="disabled")

        # ВВОД
        self.user_input = ctk.CTkEntry(self, placeholder_text=f"Слушаю, Андрей...", height=50)
        self.user_input.pack(pady=20, padx=20, fill="x")
        self.user_input.bind("<Return>", lambda e: self.send_message())

    def show_context_menu(self, event):
        """Меню копирования"""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Копировать всё", command=self.copy_all)
        menu.post(event.x_root, event.y_root)

    def copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self.chat_display.get("1.0", "end"))

    def toggle_thinking(self, state):
        self.is_thinking = state
        if state:
            self.animate()
        else:
            self.spinner_label.configure(text="")

    def animate(self):
        if self.is_thinking:
            self.spinner_label.configure(text=self.spinner_chars[self.spinner_idx % len(self.spinner_chars)])
            self.spinner_idx += 1
            self.after(80, self.animate)

    def git_sync(self):
        self.toggle_thinking(True)

        def run():
            msg = f"Update {datetime.now().strftime('%H:%M:%S')}"
            subprocess.run("git add .", shell=True, cwd=self.working_dir)
            subprocess.run(f'git commit -m "{msg}"', shell=True, cwd=self.working_dir)
            subprocess.run("git push origin main", shell=True, cwd=self.working_dir)
            self.after(0, lambda: (self.append_chat("SYSTEM", "GitHub Sync Complete."), self.toggle_thinking(False)))

        threading.Thread(target=run, daemon=True).start()

    def append_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        tag = "jarvis_tag" if sender == "JARVIS" else "user_tag"
        self.chat_display.insert("end", f"[{sender}]: {message}\n\n", tag)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        msg = self.user_input.get()
        if not msg.strip(): return
        self.append_chat(self.user_name, msg)
        self.user_input.delete(0, "end")
        threading.Thread(target=self.get_bot_response, args=(msg,), daemon=True).start()

    def get_bot_response(self, user_text):
        self.after(0, lambda: self.toggle_thinking(True))
        try:
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            process = subprocess.Popen(
                f'nanobot agent -m "{user_text}"',
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True, cwd=self.working_dir, text=True,
                encoding='utf-8', errors='replace', env=env,
                creationflags=0x08000000
            )
            for line in iter(process.stdout.readline, ''):
                line_clean = line.strip()
                # ФИЛЬТР: Пропускаем технические логи nanobot
                if not line_clean: continue
                if any(x in line_clean for x in ["DEBUG", "INFO", "Executing tool", "[32m"]):
                    continue

                self.after(0, lambda l=line_clean: self.append_chat("JARVIS", l))
            process.wait()
        finally:
            self.after(0, lambda: self.toggle_thinking(False))

    def take_screenshot(self):
        shot_dir = os.path.join(self.working_dir, "screenshots")
        if not os.path.exists(shot_dir): os.makedirs(shot_dir)
        path = os.path.join(shot_dir, f"shot_{datetime.now().strftime('%H%M%S')}.png")
        self.iconify()
        self.after(500, lambda: (pyautogui.screenshot(path), self.deiconify(),
                                 self.append_chat("SYSTEM", "Скриншот в базе.")))


if __name__ == "__main__":
    app = JarvisGUI()
    app.mainloop()