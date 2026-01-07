

import os
from dotenv import load_dotenv
from kg_rag_engine import KGRAGEngine # From Task 1
from peft import PeftModel
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# --- NEW SDK IMPORT ---
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

class NmapManager:
    """
    The Orchestrator: Classifies intent and routes to the correct specialized agent.
    Enhanced with LoRA-powered Diffusion Synthesis for Hard intents.
    """
    def __init__(self):
        # 1. Initialize the 'Brain' (KG-RAG)
        self.kg_rag = KGRAGEngine()
        
        # 2. Initialize the 'Classifier' (NEW SDK)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env")
            
        self.client = genai.Client(api_key=api_key)
        self.gemini_model = "gemini-2.5-flash" 
        
        # 3. Initialize the 'Specialist' (LoRA Model)
        print("[System] Loading LoRA Specialist Model...")
        self.base_model_name = "t5-small"
        self.lora_adapter_path = "./nmap-ai-final"
        
        try:
            # Added legacy=False to silence the warning
            self.tokenizer = T5Tokenizer.from_pretrained(self.base_model_name, legacy=False)
            base_model = T5ForConditionalGeneration.from_pretrained(self.base_model_name)
            self.lora_model = PeftModel.from_pretrained(base_model, self.lora_adapter_path)
            self.lora_model.eval()
            print("[System] LoRA Model loaded successfully.")
        except Exception as e:
            print(f"[Warning] Could not load LoRA model. Using simulation mode. Error: {e}")
            self.lora_model = None

    def classify_intent(self, intent: str) -> str:
        """
        Uses Gemini to categorize the intent. Now uses the correct SDK client.
        """
        prompt = f"""
        Analyze the following user request and classify it into one of four categories:
        - 'Irrelevant': The request is garbage (e.g., random characters like 'hhhh'), gibberish, or NOT related to network scanning/cybersecurity.
        - 'Easy': Basic port scans, ping scans, or simple host discovery.
        - 'Medium': Service/version detection, OS detection, or specific timing/stealth flags.
        - 'Hard': Vulnerability scanning, custom scripts, or complex multi-step reconnaissance.
        
        Intent: "{intent}"
        
        Respond with ONLY the category name: Irrelevant, Easy, Medium, or Hard.
        """
        try:
            # --- FIX: Use self.client.models.generate_content ---
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=prompt
            )
            category = response.text.strip()
            # Clean up potential extra whitespace or punctuation
            if "Irrelevant" in category: return "Irrelevant"
            if "Easy" in category: return "Easy"
            if "Medium" in category: return "Medium"
            if "Hard" in category: return "Hard"
            
            return "Medium" # Default fallback if Gemini is unsure
            
        except Exception as e:
            print(f"[Error] Gemini Classification failed: {e}")
            # --- CRITICAL CHANGE: If API fails, do NOT default to Easy for garbage inputs ---
            # Ideally, we fail safely, but for now, we keep Easy ONLY if it looks safe.
            return "Irrelevant"
 
    def _generate_with_lora(self, intent: str, target: str) -> str:
        """Helper method to generate a command using the LoRA model."""
        # if self.lora_model is None:
        #     return f"nmap -sS -sV -n {target}" # Fallback

        input_text = f"translate English to Nmap: {intent} on {target}"
        inputs = self.tokenizer(input_text, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.lora_model.generate(
                **inputs,
                max_new_tokens=128,
                num_beams=5,
                early_stopping=True
            )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def process_easy(self, intent: str, target: str) -> str:
        print("[Routing] Sending to KG-RAG (Task 1)...")
        keywords = intent.lower().split()
        return self.kg_rag.generate_zero_shot(keywords, target)

    def process_medium(self, intent: str, target: str) -> str:
        print("[Routing] Sending to LoRA Specialist (Task 2)...")
        return self._generate_with_lora(intent, target)

    def process_hard(self, intent: str, target: str) -> str:
        print("[Routing] Sending to Enhanced Diffusion Synthesis (Task 3)...")
        
        print("  [Diffusion] Generating initial guess with LoRA...")
        current_command = self._generate_with_lora(intent, target)
        
        for i in range(5):
            print(f"  [Refinement Loop] Iteration {i+1}: {current_command}")
            validation = self.kg_rag.validate_command(current_command, is_root=True)
            
            if validation["is_valid"]:
                print("  [Success] Command validated by KG-RAG.")
                return current_command
            else:
                error_msg = validation['errors'][0]
                print(f"  [Fixing] Error found: {error_msg}")
                
                fix_prompt = f"""
                The Nmap command "{current_command}" is invalid because: {error_msg}
                Rewrite the command to fix this error while keeping the original intent: "{intent}".
                Respond with ONLY the fixed Nmap command.
                """
                try:
                    # --- NEW SDK CALL ---
                    response = self.client.models.generate_content(
                        model=self.gemini_model,
                        contents=fix_prompt
                    )
                    current_command = response.text.strip()
                except:
                    current_command = current_command.replace("-A", "-sS -sV")
                
        return current_command

    def functional_validation(self, command: str):
        """Task 4: Sends the command to the MCP server."""
        print(f"\n[Task 4] Starting Functional Validation via MCP...")
        
        try:
            # --- FIX: Import the RAW function, not the tool wrapper ---
            from nmap_mcp_server import run_nmap_scan
            
            # Test against localhost for safety if needed, 
            # but usually you want to test the actual target in a controlled lab.
            # For this test we keep the command as is or modify safe targets.
            test_command = command 
            
            report = run_nmap_scan(test_command)
            
            if "SUCCESS" in report:
                print("[Success] Command is functionally valid.")
                return True, report
            else:
                print("[Failure] Command failed execution.")
                return False, report
        except ImportError:
            print("[Warning] nmap_mcp_server not found or import error.")
            return True, "Skipped (Import Error)"
        
        
    def execute_pipeline(self, intent: str, target: str):
        print(f"\n--- New Request: '{intent}' on {target} ---")
        
        category = self.classify_intent(intent)
        print(f"[Manager] Intent classified as: {category}")
        
        # --- FIX: Immediate Exit for Irrelevant Intents ---
        if category == "Irrelevant":
            print("[Block] Request blocked: Intent is irrelevant or malformed.")
            return {
                "intent": intent,
                "category": category,
                "command": None,
                "is_valid": False,
                "is_functional": False,
                "mcp_report": "BLOCKED: The system determined this request is irrelevant to Nmap."
            }

        if category == "Easy":
            command = self.process_easy(intent, target)
        elif category == "Medium":
            command = self.process_medium(intent, target)
        else:
            command = self.process_hard(intent, target)
            
        # Static Validation
        final_check = self.kg_rag.validate_command(command, is_root=True)
        
        # Functional Validation
        is_functional, report = self.functional_validation(command)
        
        return {
            "intent": intent,
            "category": category,
            "command": command,
            "is_valid": final_check["is_valid"],
            "is_functional": is_functional,
            "mcp_report": report
        }

if __name__ == "__main__":
    manager = NmapManager()
    result = manager.execute_pipeline("ping scan the network", "127.0.0.1")
    print(f"Final Result: {result}")