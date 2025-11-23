import json
import logging
import os
import re
import sys
import time
from typing import List, Optional, Dict

from PyQt6.QtCore import (
    QUrl, QObject, pyqtSignal, pyqtSlot, QThread, pyqtProperty,
    QStandardPaths, QDir
)
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from openai import OpenAI, OpenAIError

# --- Configuration ---
class Config:
    MODEL_URL = "https://huggingface.co/lmstudio-ai/gemma-2b-it-GGUF/resolve/main/gemma-2b-it-q8_0.gguf"
    MODEL_PATH = "model.gguf"
    LLM_BASE_URL = "http://127.0.0.1:8080/v1"
    LLM_API_KEY = "no-api-key-needed"
    LLM_MODEL_ID = MODEL_PATH
    CHAT_SAVE_SUBDIR = "chats"
    
    # Generation settings
    GEN_ATTEMPTS = 5
    DEFAULT_CHAT_TOKENS = 800
    DEFAULT_TEMP = 0.7
    STOP_TOKENS = ["<|im_end|>"]

class LLMRunner(QObject):
    finished = pyqtSignal(str, str, str)  # raw_response, formatted_response, mode

    def __init__(self, data, mode, max_tokens, base_url, api_key, model_id, parent=None):
        super().__init__(parent)
        self.data = data
        self.mode = mode
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.api_key = api_key
        self.model_id = model_id
        self.client: Optional[OpenAI] = None

    def _ensure_client(self) -> bool:
        if self.client:
            return True
        try:
            self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
            return True
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI client: {e}")
            return False

    def _generate_candidates(self, prompt_text: str) -> List[str]:
        """Generates N variants of the answer."""
        candidates = []
        logging.info(f"[GEN] Generating {Config.GEN_ATTEMPTS} candidates...")
        
        for i in range(Config.GEN_ATTEMPTS):
            try:
                response = self.client.completions.create(
                    model=self.model_id,
                    prompt=prompt_text,
                    max_tokens=self.max_tokens,
                    temperature=0.75
                )
                text = response.choices[0].text.strip()
                if text:
                    candidates.append(text)
            except OpenAIError as e:
                logging.warning(f"[GEN] Generation attempt {i+1} failed: {e}")
        
        return candidates

    def _evaluate_candidates(self, prompt_text: str, candidates: List[str]) -> str:
        """Asks the LLM to pick the best candidate from the list."""
        if not candidates:
            return "❌ Error: No responses generated."
        
        if len(candidates) == 1:
            logging.info("[GEN] Only one candidate generated, skipping evaluation.")
            return candidates[0]

        logging.info(f"[GEN] Evaluating {len(candidates)} candidates...")

        eval_prompt = (
            "You are an unbiased AI evaluator. Select the response that best answers the prompt.\n\n"
            f"Original Prompt:\n\"{prompt_text}\"\n\n"
            "Candidates:\n\n"
        )
        
        for i, cand in enumerate(candidates, 1):
            eval_prompt += f"[CANDIDATE {i}]\n{cand}\n[END CANDIDATE {i}]\n\n"

        eval_prompt += (
            "Instruction: Reply with ONLY the number of the best candidate (e.g., '1', '2')."
        )

        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": eval_prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=10,
                temperature=0.0
            )
            choice_text = response.choices[0].message.content.strip()
            return self._parse_evaluation(choice_text, candidates)
        except Exception as e:
            logging.error(f"[GEN] Evaluation failed: {e}. Returning first candidate.")
            return candidates[0]

    def _parse_evaluation(self, choice_text: str, candidates: List[str]) -> str:
        logging.info(f"[GEN] Evaluator choice: '{choice_text}'")
        match = re.search(r'\d+', choice_text)
        if match:
            idx = int(match.group(0)) - 1
            if 0 <= idx < len(candidates):
                return candidates[idx]
        
        logging.warning("[GEN] Could not parse evaluator choice. Defaulting to first.")
        return candidates[0]

    def generate(self, prompt_text: str) -> str:
        if not self._ensure_client():
            return "❌ Error: LLM Client not initialized."
        
        candidates = self._generate_candidates(prompt_text)
        return self._evaluate_candidates(prompt_text, candidates)

    def chat(self, history_list: List[Dict[str, str]]) -> str:
        if not self._ensure_client():
            return "❌ Error: LLM Client not initialized."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=history_list,
                max_tokens=self.max_tokens,
                temperature=Config.DEFAULT_TEMP,
                stop=Config.STOP_TOKENS
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Chat error: {e}")
            return f"❌ LLM Error: {e}"

    @pyqtSlot()
    def run(self):
        try:
            response_text = ""
            if self.mode == "chat":
                logging.info(f"[CHAT] Processing history with {len(self.data)} messages.")
                response_text = self.chat(self.data)
            elif self.mode == "gen":
                logging.info(f"[GEN] Processing prompt: {self.data[:50]}...")
                response_text = self.generate(self.data)
            else:
                response_text = f"❌ Unknown mode: {self.mode}"

            final_response = response_text if response_text.startswith("❌") else f"🤖 PupuAI:\n\n{response_text}"
            self.finished.emit(response_text, final_response, self.mode)

        except Exception as e:
            logging.critical(f"Critical Worker Error: {e}", exc_info=True)
            self.finished.emit(str(e), str(e), "error")


class AIWorker(QObject):
    aiResponseReady = pyqtSignal(str)
    clearChatDisplay = pyqtSignal()
    isWorkingChanged = pyqtSignal(bool)
    historyListChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_working = False
        self.llm_thread: Optional[QThread] = None
        self.llm_runner: Optional[LLMRunner] = None
        self.chat_history: List[Dict[str, str]] = []
        self.current_mode = "chat"

        self.chat_save_dir = self._setup_chat_directory()
        self.refreshChatList()

    def _setup_chat_directory(self) -> str:
        data_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation) or "."
        
        QGuiApplication.setOrganizationName("PupuAI_Dev")
        QGuiApplication.setApplicationName("PupuAI_App")
        
        chat_dir = os.path.join(data_path, Config.CHAT_SAVE_SUBDIR)
        os.makedirs(chat_dir, exist_ok=True)
        logging.info(f"✅ Chat directory: {chat_dir}")
        return chat_dir

    def _set_working(self, working: bool):
        if self._is_working != working:
            self._is_working = working
            self.isWorkingChanged.emit(working)

    @pyqtProperty(bool, notify=isWorkingChanged)
    def isWorking(self):
        return self._is_working

    @pyqtSlot()
    def clearChatHistory(self):
        self.chat_history.clear()
        # Initial system prompt
        system_prompt = {
            "role": "system",
            "content": "I'm a poet, I don't produce anything except poetry. I write only in Russian."
        }
        self.chat_history.append(system_prompt)
        logging.info("✅ Chat history cleared.")
        self.clearChatDisplay.emit()
        self.aiResponseReady.emit("--- New Chat ---")

    @pyqtSlot()
    def saveCurrentChat(self):
        if self._is_working or not self.chat_history:
            logging.warning("❌ Cannot save: Worker busy or history empty.")
            return

        try:
            filename = f"chat_{int(time.time())}.json"
            filepath = os.path.join(self.chat_save_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            logging.info(f"✅ Saved chat to {filename}")
            self.refreshChatList()
        except OSError as e:
            logging.error(f"❌ Save failed: {e}")

    @pyqtSlot(str)
    def loadChat(self, filename):
        if self._is_working:
            logging.warning("❌ Worker busy, cannot load chat.")
            return
            
        filepath = os.path.join(self.chat_save_dir, filename)
        if not os.path.exists(filepath):
            logging.error(f"❌ File not found: {filename}")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.chat_history = json.load(f)
            
            logging.info(f"✅ Loaded chat '{filename}'. restoring UI...")
            self.clearChatDisplay.emit()
            
            for message in self.chat_history:
                role = message.get("role")
                content = message.get("content")
                if role == "user":
                    self.aiResponseReady.emit(f"👤 You:\n\n{content}")
                elif role == "assistant":
                    self.aiResponseReady.emit(f"🤖 PupuAI:\n\n{content}")
            
            self.current_mode = "chat"
        except (OSError, json.JSONDecodeError) as e:
            logging.error(f"❌ Load failed for '{filename}': {e}")
            self.clearChatHistory()

    @pyqtSlot()
    def refreshChatList(self):
        try:
            files = [f for f in os.listdir(self.chat_save_dir) if f.endswith('.json')]
            files.sort(reverse=True)
            self.historyListChanged.emit(files)
        except OSError as e:
            logging.error(f"❌ Failed to list chats: {e}")

    @pyqtSlot(str)
    def deleteChat(self, filename):
        if self._is_working:
            return

        filepath = os.path.join(self.chat_save_dir, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logging.info(f"✅ Deleted '{filename}'.")
                self.refreshChatList()
            else:
                logging.warning(f"⚠️ File '{filename}' not found.")
        except OSError as e:
            logging.error(f"❌ Delete failed: {e}")

    @pyqtSlot(str, str, int)
    def startGeneration(self, prompt, mode="chat", max_tokens=Config.DEFAULT_CHAT_TOKENS):
        if self._is_working:
            logging.warning("Worker is already busy.")
            return

        # Handle mode switching
        if mode != self.current_mode:
            logging.info(f"Switching mode: {self.current_mode} -> {mode}")
            self.current_mode = mode
            self.clearChatHistory()

        self._set_working(True)
        self.aiResponseReady.emit(f"👤 You:\n\n{prompt}")

        # Prepare payload
        payload = self.chat_history.copy() if mode == "chat" else prompt
        if mode == "chat":
            self.chat_history.append({"role": "user", "content": prompt})
            # Update payload with new message
            payload = self.chat_history.copy() 

        # Thread setup
        self.llm_thread = QThread()
        self.llm_runner = LLMRunner(
            data=payload,
            mode=mode,
            max_tokens=max_tokens,
            base_url=Config.LLM_BASE_URL,
            api_key=Config.LLM_API_KEY,
            model_id=Config.LLM_MODEL_ID
        )
        
        self.llm_runner.moveToThread(self.llm_thread)
        self.llm_thread.started.connect(self.llm_runner.run)
        self.llm_runner.finished.connect(self.handle_result)
        self.llm_runner.finished.connect(self.llm_thread.quit)
        self.llm_runner.finished.connect(self.llm_runner.deleteLater)
        self.llm_thread.finished.connect(self.llm_thread.deleteLater)
        self.llm_thread.finished.connect(self._clear_thread_refs)
        
        self.llm_thread.start()
        logging.info("Worker thread started.")

    @pyqtSlot()
    def _clear_thread_refs(self):
        self.llm_runner = None
        self.llm_thread = None

    @pyqtSlot(str, str, str)
    def handle_result(self, raw_result, formatted_result, mode):
        logging.info(f"Result received. Mode: {mode}")
        self.aiResponseReady.emit(formatted_result)
        self._set_working(False)

        if mode == 'chat' and not raw_result.startswith("❌"):
            self.chat_history.append({"role": "assistant", "content": raw_result})

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"
    
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    ai_worker = AIWorker()
    engine.rootContext().setContextProperty("aiWorker", ai_worker)

    qml_file_path = os.path.join("design", "Group_5.qml")
    if not os.path.exists(qml_file_path):
        logging.critical(f"QML file not found: {qml_file_path}")
        sys.exit(-1)

    engine.load(QUrl.fromLocalFile(qml_file_path))

    if not engine.rootObjects():
        logging.critical("Failed to load QML.")
        sys.exit(-1)

    engine.quit.connect(app.quit)
    sys.exit(app.exec())
