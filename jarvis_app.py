import customtkinter as ctk
import subprocess
import threading
import os
import pyttsx3
import pyautogui
from datetime import datetime
import glob


class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Теперь официально
        self.user_name = "АНДРЕЙ"
        self.title(f"JARVIS System v4.0 - {self.user_name} WORKSTATION")
        self.geometry("1000x950")
        ctk.set_appearance_mode("dark")

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 190)

        self.working_dir = os.getcwd()
        self.is_thinking = False
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_idx = 0

        self.setup_ui()

    def setup_ui(self):
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=10, padx=20, fill="x")

        # Индикатор статуса и спиннер
        self.status_label = ctk.CTkLabel(self.top_frame, text=f"OPERATOR: {self.user_name}", font=("Arial", 14, "bold"))
        self.status_label.pack(side="left", padx=15)

        self.spinner_label = ctk.CTkLabel(self.top_frame, text="", font=("Arial", 20), text_color="#FFD700")
        self.spinner_label.pack(side="left", padx=10)

        # Кнопки
        self.git_btn = ctk.CTkButton(self.top_frame, text="GIT SYNC", command=self.git_sync, fg_color="#2ecc71",
                                     width=100)
        self.git_btn.pack(side="right", padx=5)

        self.vision_btn = ctk.CTkButton(self.top_frame, text="SCAN", command=self.take_screenshot, fg_color="#e67e22",
                                        width=100)
        self.vision_btn.pack(side="right", padx=5)

        # Чат
        self.chat_display = ctk.CTkTextbox(self, width=960, height=700, wrap="word", font=("Consolas", 15))
        self.chat_display.pack(pady=10, padx=20)
        self.chat_display._textbox.tag_config("jarvis_tag", foreground="#FFD700")
        self.chat_display._textbox.tag_config("user_tag", foreground="#3498db")
        self.chat_display.configure(state="disabled")

        # Ввод
        self.user_input = ctk.CTkEntry(self, placeholder_text=f"Слушаю тебя, {self.user_name}...", height=50)
        self.user_input.pack(pady=20, padx=20, fill="x")
        self.user_input.bind("<Return>", lambda e: self.send_message())

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

    def speak(self, text):
        def say():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass

        threading.Thread(target=say, daemon=True).start()

    def git_sync(self):
        self.toggle_thinking(True)

        def run():
            msg = f"Update {datetime.now().strftime('%H:%M:%S')}"
            for cmd in ["git add .", f'git commit -m "{msg}"', "git push origin main"]:
                subprocess.run(cmd, shell=True, cwd=self.working_dir)
            self.after(0, lambda: self.append_chat("SYSTEM", "GitHub синхронизирован."))
            self.after(0, lambda: self.toggle_thinking(False))

        threading.Thread(target=run, daemon=True).start()

    def append_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        tag = "jarvis_tag" if sender == "JARVIS" else "user_tag"
        self.chat_display.insert("end", f"[{sender}]: {message}\n\n", tag)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        if sender == "JARVIS": self.speak(message)

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

            # Проверка на открытие программ (базовая логика)
            if "открой" in user_text.lower() and "хром" in user_text.lower():
                os.system("start chrome")
                self.after(0, lambda: self.append_chat("JARVIS", "Открываю Google Chrome, Андрей."))
                return

            process = subprocess.Popen(
                f'nanobot agent -m "{user_text}"',
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True, cwd=self.working_dir, text=True,
                encoding='utf-8', errors='replace', env=env,
                creationflags=0x08000000
            )
            for line in iter(process.stdout.readline, ''):
                if line.strip() and "INFO" not in line:
                    self.after(0, lambda l=line.strip(): self.append_chat("JARVIS", l))
            process.wait()
        except Exception as e:
            self.after(0, lambda: self.append_chat("ERROR", str(e)))
        finally:
            self.after(0, lambda: self.toggle_thinking(False))

    def take_screenshot(self):
        # Логика скриншота...
        pass


if __name__ == "__main__":
    app = JarvisGUI()
    app.mainloop()