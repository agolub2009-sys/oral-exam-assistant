import os
import sys
import re
import cv2
import speech_recognition as sr
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

from pathlib import Path

# ======================
# Внутренние компоненты
# ======================

class TopicManager:
    def init(self, subject: str, topic: str):
        self.subject = subject
        self.topic = topic
        self.topic_dir = os.path.join("data", subject, topic)

    def ensure_topic_folder(self):
        Path(self.topic_dir).mkdir(parents=True, exist_ok=True)

    def save_user_answer(self, text: str):
        with open(os.path.join(self.topic_dir, "last_answer.txt"), "w", encoding="utf-8") as f:
            f.write(text)

    def load_reference_answer(self) -> str:
        ref_path = os.path.join(self.topic_dir, "reference.txt")
        if os.path.isfile(ref_path):
            with open(ref_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""

    def generate_suggestions(self, user: str, reference: str):
        words = set(re.findall(r'\b\w{4,}\b', reference.lower()))
        user_lower = user.lower()
        missing = [w for w in list(words)[:10] if w not in user_lower]
        return [f"Consider mentioning: '{w}'" for w in missing[:5]]

    def generate_questions(self):
        return [
            "Can you explain this in your own words?",
            "What are the key components?",
            "How does this connect to other topics?",
            "Give a real-world example.",
            "What if one part fails? What happens?"
        ]

def load_and_save_image(input_path: str, output_dir: str):
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError("Unable to load image")
    output_path = os.path.join(output_dir, "material.jpg")
    cv2.imwrite(output_path, img)

def record_speech() -> str:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            print("🎤 Listening... (speak now)")
            audio = r.listen(source, timeout=8, phrase_time_limit=30)
            return r.recognize_google(audio, language="en-US")
        except Exception as e:
            print(f"🎤 Speech error: {type(e).name}")
            return ""

def speak_text(text: str):
    if pyttsx3 is None:
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.say(text)
        engine.runAndWait()
    except:
        pass

# ======================
# Главная программа
# ======================

def main():
    print("🎓 Oral Exam Assistant (Single-File Version)")
    print("=" * 50)

    subject = input("Enter subject (e.g., Biology): ").strip()
    topic = input("Enter topic name: ").strip()

    if not subject or not topic:
        print("❌ Subject and topic are required.")
        sys.exit(1)

    tm = TopicManager(subject, topic)
    tm.ensure_topic_folder()

    img_path = input("\nEnter image path (or skip): ").strip().strip('"')
    if img_path and os.path.isfile(img_path):
        try:
            load_and_save_image(img_path, tm.topic_dir)
            print("✅ Image saved.")
        except Exception as e:
            print(f"⚠️ Failed to save image: {e}")

    print("\n🎤 Recording your oral answer...")
    answer = record_speech()
    if not answer:
        print("❌ No speech detected.")
        return

    print(f"\n📝 You said:\n{answer}\n")
    tm.save_user_answer(answer)

    reference = tm.load_reference_answer()
    if not reference:
        print("ℹ️ No 'reference.txt' found.")
        print(f"👉 Create it in: {tm.topic_dir}")
        return

    suggestions = tm.generate_suggestions(answer, reference)
    if suggestions:
        print("🔍 Suggestions:")
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s}")
    else:
        print("✅ Great answer!")

    questions = tm.generate_questions()
    print("\n❓ Practice questions:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
if questions and pyttsx3:
        speak_text(f"Question: {questions[0]}")

    print(f"\n💾 Saved in: {tm.topic_dir}")

if name == "main":
    # Проверка зависимостей
    missing = []
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    try:
        import speech_recognition
    except ImportError:
        missing.append("SpeechRecognition")
    if missing:
        print("❌ Missing packages:", ", ".join(missing))
        print("👉 Run: pip install opencv-python SpeechRecognition pyttsx3")
        sys.exit(1)
    main()
