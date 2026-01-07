from nmap_manager import NmapManager

def run_tests():
    manager = NmapManager()
    
    test_cases = [
        {
            "name": "Easy Intent Test",
            "intent": "hhhhhhhhhhhhhhhhhh",
            "target": "hhhhhhhh"
        },
        {
            "name": "Medium Intent Test",
            "intent": "Scan ports for HTTP, FTP, SMTP and version detection Run malware scripts with faster timing and traceroute",
            "target": "192.168.3.1"
        },
        {
            "name": "Hard Intent Test",
            "intent": "run a complex vulnerability scan with aggressive timing",
            "target": "192.168.1.10"
        }
    ]
    
    print("=== NMAP-AI Multi-Tier Pipeline Test ===")
    
    for case in test_cases:
        print(f"\nRunning: {case['name']}")
        result = manager.execute_pipeline(case['intent'], case['target'])
        
        print(f"  Category: {result['category']}")
        print(f"  Command:  {result['command']}")
        print(f"  Valid:    {result['is_valid']}")
        
    print("\n=== Test Suite Complete ===")

if __name__ == "__main__":
    run_tests()
