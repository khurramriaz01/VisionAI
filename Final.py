import speech_recognition as sr
import google.generativeai as genai
import pyttsx3
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, Frame, Canvas
import threading
from dotenv import load_dotenv
import cv2
from PIL import Image, ImageTk
import queue
import logging
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 0.8)

class SmartGlassesUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Smart Glasses")
        self.root.geometry("1200x600")
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        self.current_frame = None
        self.camera_running = True
        if not self.cap.isOpened():
            logging.error("Webcam not found. Some features may be unavailable.")
        
        # Threading and processing control
        self.processing_queue = queue.Queue()
        self.is_processing = False
        
        # Conversation memory
        self.conversation_history = []
        
        # Create UI panels
        self.create_camera_panel()
        self.create_chat_panel()
        self.start_processing_thread()
        self.start_camera_stream()
        
        # Initial system readiness
        self.speak("System ready")

    def create_camera_panel(self):
        """Create left panel for camera feed"""
        self.left_panel = Frame(self.root, width=640, height=480)
        self.left_panel.pack_propagate(0)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.camera_label = tk.Label(self.left_panel)
        self.camera_label.pack(fill="both", expand=True)

    def create_chat_panel(self):
        """Create right panel for chat history with scroll"""
        self.right_panel = Frame(self.root)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        self.canvas = Canvas(self.right_panel)
        self.scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Create control buttons
        self.btn_frame = Frame(self.right_panel)
        self.btn_frame.pack(pady=5)
        
        self.ask_btn = tk.Button(
            self.btn_frame, 
            text="Speak/Ask", 
            command=self.queue_voice_input,
            width=15
        )
        self.ask_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(self.right_panel, text="Status: Idle", fg="green")
        self.status_label.pack(pady=5)
        
        self.append_to_display("=== AI Smart Glasses ===\nSystem ready.\n\n")

    def start_camera_stream(self):
        """Start updating camera feed"""
        def update_frame():
            if self.camera_running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    img.thumbnail((640, 480))
                    self.current_frame = img  # Store current frame for capture
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.camera_label.imgtk = imgtk
                    self.camera_label.configure(image=imgtk)
            self.root.after(50, update_frame)
        
        update_frame()

    def append_to_display(self, text, image=None):
        """Add message to chat history with optional image"""
        message_frame = Frame(self.scrollable_frame, relief=tk.GROOVE, bd=1)
        message_frame.pack(fill="x", pady=2, padx=5)
        
        text_label = tk.Label(message_frame, text=text, wraplength=400, justify=tk.LEFT, anchor="w")
        text_label.pack(side=tk.TOP, fill="x")
        
        if image is not None:
            img_label = tk.Label(message_frame)
            img_label.image = image  # Keep reference
            img_label.configure(image=image)
            img_label.pack(side=tk.TOP, pady=5)
        
        # Auto-scroll to bottom
        self.canvas.yview_moveto(1.0)

    def start_processing_thread(self):
        """Start background processing thread"""
        def process_queue():
            while True:
                try:
                    task = self.processing_queue.get(block=True)
                    task()
                    self.processing_queue.task_done()
                except Exception as e:
                    logging.error(f"Processing error: {e}")
                
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()

    def queue_voice_input(self):
        """Queue voice input task"""
        if not self.is_processing:
            self.is_processing = True
            self.ask_btn.config(state=tk.DISABLED)
            self.update_status("Processing...")
            self.processing_queue.put(self.process_voice_input)
        else:
            self.append_to_display("Processing previous request. Please wait...\n\n")

    def process_voice_input(self):
        """Handle voice input processing"""
        try:
            user_input = self.get_voice_input()
            
            if user_input.startswith("Error:"):
                self.append_to_display(f"{user_input}")
                return
                
            self.conversation_history.append(f"You: {user_input}")
            self.append_to_display(f"You: {user_input}")
            
            if user_input.lower() in ['exit', 'quit', 'stop']:
                self.append_to_display("AI: Goodbye! Shutting down system.")
                self.speak("Goodbye! Shutting down system")
                self.root.after(2000, self.root.destroy)
                return
            
            # Capture screenshot
            screenshot = self.capture_screenshot()
            display_image = None
            
            # Generate response
            full_context = "\n".join(self.conversation_history)
            if screenshot:
                # Create thumbnail for display
                screenshot.thumbnail((300, 300))
                display_image = ImageTk.PhotoImage(screenshot)
                self.append_to_display("(Image captured)", image=display_image)
                
                response = model.generate_content([
                    f"""{full_context}
                    Context of question: {user_input}. Analyze the current scene.
                    - Answer normally if unrelated to visual context
                    - Keep answer concise (under 4 sentences)
                    - Focus on objects/text when relevant""",
                    screenshot
                ])
            else:
                response = model.generate_content(full_context)
            
            result_text = response.text
            self.conversation_history.append(f"AI: {result_text}")
            self.append_to_display(f"AI: {result_text}")
            self.speak(result_text)
        
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.append_to_display(error_msg)
            self.speak("Sorry, I encountered an error")
        
        finally:
            self.root.after(0, self.reset_processing_state)

    def reset_processing_state(self):
        """Reset processing state and button"""
        self.is_processing = False
        self.ask_btn.config(state=tk.NORMAL)
        self.update_status("Idle")

    def capture_screenshot(self):
        """Capture current frame from webcam"""
        try:
            return self.current_frame.copy() if self.current_frame else None
        except Exception as e:
            logging.error(f"Error capturing screenshot: {e}")
            return None

    def get_voice_input(self):
        """Capture voice input from microphone with retries"""
        recognizer = sr.Recognizer()
        retries = 3
        for attempt in range(retries):
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
                return recognizer.recognize_google(audio)
            except Exception as e:
                logging.warning(f"Speech recognition failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    return "Error: Could not recognize speech after multiple attempts."

    def speak(self, text):
        """Convert text to speech in a background thread"""
        def _speak():
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                logging.error(f"Speech error: {e}")
                self.append_to_display(f"Speech error: {str(e)}\n\n")
        threading.Thread(target=_speak, daemon=True).start()

    def update_status(self, status):
        """Update the status label"""
        color = "green" if status == "Idle" else "orange"
        self.status_label.config(text=f"Status: {status}", fg=color)

    def on_closing(self):
        """Cleanup resources when closing window"""
        self.camera_running = False
        try:
            if self.cap and self.cap.isOpened():
                self.cap.release()
            engine.stop()
        finally:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartGlassesUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()