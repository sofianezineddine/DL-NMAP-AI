import re
from typing import List, Dict, Any, Optional

class KGRAGEngine:
    """
    KG-RAG Engine for Nmap: Handles semantic validation and zero-shot command generation
    using a simulated Knowledge Graph rule set.
    """
    
    def __init__(self):
        # Simulated Knowledge Graph Data (In a real scenario, this would be Neo4j queries)
        self.ontology = {
            "options": {
                "-sS": {"privilege": "root", "conflicts": ["-sT", "-sU"]},
                "-sT": {"privilege": "user", "conflicts": ["-sS", "-sU"]},
                "-sU": {"privilege": "root", "conflicts": ["-sS", "-sT"]},
                "-O": {"privilege": "root", "conflicts": []},
                "-sV": {"privilege": "user", "conflicts": []},
                "-A": {"privilege": "root", "conflicts": []},
                "-p": {"privilege": "user", "conflicts": []},
                "-n": {"privilege": "user", "conflicts": []},
                "-F": {"privilege": "user", "conflicts": []}
            },
            "intents": {
                "stealth": ["-sS"],
                "version": ["-sV"],
                "os": ["-O"],
                "aggressive": ["-A"],
                "fast": ["-F"],
                "no_dns": ["-n"]
            }
        }

    def validate_command(self, command: str, is_root: bool = False) -> Dict[str, Any]:
        """
        Validates an Nmap command against the Knowledge Graph rules.
        """
        parts = command.split()
        options_found = [p for p in parts if p.startswith("-")]
        
        errors = []
        warnings = []
        
        # 1. Check for unknown options
        for opt in options_found:
            if opt not in self.ontology["options"] and not opt.startswith("-p"):
                warnings.append(f"Unknown or unvalidated option: {opt}")
                continue
            
            # 2. Check Privilege Requirements
            if opt in self.ontology["options"]:
                required_priv = self.ontology["options"][opt]["privilege"]
                if required_priv == "root" and not is_root:
                    errors.append(f"Option '{opt}' requires root privileges.")
            
            # 3. Check for Conflicts
            if opt in self.ontology["options"]:
                conflicts = self.ontology["options"][opt]["conflicts"]
                for other_opt in options_found:
                    if other_opt in conflicts:
                        errors.append(f"Conflict detected: '{opt}' cannot be used with '{other_opt}'.")

        return {
            "is_valid": len(errors) == 0,
            "errors": list(set(errors)),
            "warnings": list(set(warnings)),
            "command": command
        }

    def generate_zero_shot(self, intent_keywords: List[str], target: str, ports: Optional[str] = None) -> str:
        """
        Generates an Nmap command based on intent mapping in the Knowledge Graph.
        """
        flags = []
        
        # Map intents to flags
        for keyword in intent_keywords:
            keyword = keyword.lower()
            if keyword in self.ontology["intents"]:
                flags.extend(self.ontology["intents"][keyword])
        
        # Add ports if specified
        if ports:
            flags.append(f"-p {ports}")
            
        # Deduplicate flags
        unique_flags = []
        for f in flags:
            if f not in unique_flags:
                unique_flags.append(f)
                
        # Construct final command
        command = f"nmap {' '.join(unique_flags)} {target}".strip()
        return command

# --- Example Usage ---
if __name__ == "__main__":
    engine = KGRAGEngine()
    
    # Example 1: Validation of a conflicting command
    cmd1 = "nmap -sS -sT 192.168.1.1"
    print(f"Validating: {cmd1}")
    print(engine.validate_command(cmd1))
    
    # Example 2: Validation of a root-only command as a normal user
    cmd2 = "nmap -sU 192.168.1.1"
    print(f"\nValidating: {cmd2} (as user)")
    print(engine.validate_command(cmd2, is_root=False))
    
    # Example 3: Zero-shot generation from intents
    intents = ["stealth", "version", "no_dns"]
    target = "example.com"
    print(f"\nGenerating command for intents: {intents}")
    generated_cmd = engine.generate_zero_shot(intents, target)
    print(f"Generated: {generated_cmd}")
    print(f"Validation: {engine.validate_command(generated_cmd, is_root=True)}")
