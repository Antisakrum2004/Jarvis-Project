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
        self.title(f"JARVIS v4.3 | {self.user_name} WORKSTATION")
        self.geometry("1000x950")
        ctk.set_appearance_mode("dark")

        self.working_dir = os.getcwd()
        self.is_thinking = False
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_idx = 0

        self.setup_ui()
        threading.Thread(target=self.update_system_stats, daemon=True).start()

    def update_system_stats(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.after(0, lambda c=cpu, r=ram: self.title(
                    f"JARVIS v4.3 | CPU: {c}% | RAM: {r}% | {self.user_name}"
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

        ctk.CTkButton(self.top_frame, text="SYNC", command=self.git_sync, fg_color="#2ecc71", width=80).pack(
            side="right", padx=5)
        ctk.CTkButton(self.top_frame, text="SCAN", command=self.take_screenshot, fg_color="#e67e22", width=80).pack(
            side="right", padx=5)

        # ЧАТ
        self.chat_display = ctk.CTkTextbox(self, width=960, height=700, wrap="word", font=("Consolas", 15))
        self.chat_display.pack(pady=10, padx=20)
        self.chat_display._textbox.tag_config("jarvis_tag", foreground="#FFD700")
        self.chat_display._textbox.tag_config("user_tag", foreground="#3498db")

        self.chat_display.bind("<Button-3>", self.show_context_menu)
        self.chat_display.configure(state="disabled")

        # ВВОД (Исправлена вставка текста)
        self.user_input = ctk.CTkEntry(self, placeholder_text=f"Командуй, Андрей...", height=50)
        self.user_input.pack(pady=20, padx=20, fill="x")

        # Явное разрешение стандартных горячих клавиш (Ctrl+V и т.д.)
        self.user_input.bind("<Control-v>", lambda e: self.user_input.event_generate("<<Paste>>"))
        self.user_input.bind("<Control-c>", lambda e: self.user_input.event_generate("<<Copy>>"))
        self.user_input.bind("<Return>", lambda e: self.send_message())

    def show_context_menu(self, event):
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
            for cmd in ["git add .", f'git commit -m "{msg}"', "git push origin main"]:
                subprocess.run(cmd, shell=True, cwd=self.working_dir)
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

        # --- ФИЧА №9: ЛОКАЛЬНЫЙ ПОИСК ---
        if "найди файл" in user_text.lower() or "поиск файла" in user_text.lower():
            filename = user_text.lower().replace("найди файл", "").replace("поиск файла", "").strip()
            self.append_chat("JARVIS", f"Запускаю поиск файла: {filename}...")

            def search():
                results = []
                # Ищем в основных папках пользователя, чтобы не сканировать весь диск С полгода
                search_paths = [
                    os.path.join(os.path.expanduser("~"), "Downloads"),
                    os.path.join(os.path.expanduser("~"), "Documents"),
                    os.path.join(os.path.expanduser("~"), "Desktop")
                ]
                for path in search_paths:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if filename in file.lower():
                                results.append(os.path.join(root, file))

                if results:
                    res_str = "\n".join(results[:5])  # Показываем первые 5 находок
                    self.after(0, lambda: self.append_chat("JARVIS", f"Вот что я нашел:\n{res_str}"))
                else:
                    self.after(0, lambda: self.append_chat("JARVIS", "Файл не найден, Андрей."))
                self.after(0, lambda: self.toggle_thinking(False))

            threading.Thread(target=search, daemon=True).start()
            return
        # --- КОНЕЦ ФИЧИ №9 ---

        # Дальше идет обычный вызов nanobot...
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
                l_clean = line.strip()
                if not l_clean or any(x in l_clean for x in
                                      ["DEBUG", "INFO", "Executing tool", "[3", "Traceback", "File \"", "ValueError"]):
                    continue
                self.after(0, lambda l=l_clean: self.append_chat("JARVIS", l))
            process.wait()
        finally:
            self.after(0, lambda: self.toggle_thinking(False))

    def take_screenshot(self):
        shot_dir = os.path.join(self.working_dir, "screenshots")
        if not os.path.exists(shot_dir): os.makedirs(shot_dir)
        path = os.path.join(shot_dir, f"shot_{datetime.now().strftime('%H%M%S')}.png")
        self.iconify()
        self.after(500, lambda: (pyautogui.screenshot(path), self.deiconify(),
                                 self.append_chat("SYSTEM", "Скриншот готов.")))


if __name__ == "__main__":
    app = JarvisGUI()
    app.mainloop()