import sys
from env.environment import CyberIncidentEnv
from env.models import Observation, Action, EnvironmentState

def validate_environment():
    print("Starting local validation of Cyber Incident Response OpenEnv...")
    
    try:
        # 1. Test reset()
        env = CyberIncidentEnv(task_id="easy")
        obs = env.reset()
        if not isinstance(obs, Observation):
            print("Error: reset() did not return an Observation object.")
            return False
        print("[PASS] reset() returns Observation object.")
        
        # 2. Test step()
        action = {"investigate_host": "workstation_1"}
        obs, reward, done, info = env.step(action)
        
        if not isinstance(obs, Observation):
            print("Error: step() did not return an Observation object.")
            return False
        if not isinstance(reward, (int, float)):
            print("Error: step() did not return a numeric reward.")
            return False
        if not isinstance(done, bool):
            print("Error: step() did not return a boolean done flag.")
            return False
        if not isinstance(info, dict):
            print("Error: step() did not return an info dictionary.")
            return False
        print("[PASS] step() returns (obs, reward, done, info) with correct types.")
        
        # 3. Test state()
        state = env.state()
        if not isinstance(state, EnvironmentState):
            print("Error: state() did not return an EnvironmentState object.")
            return False
        print("[PASS] state() returns EnvironmentState object.")
        
        # 4. Test reward and score ranges
        if not (-1.0 <= reward <= 1.0):
            print(f"Error: reward {reward} is out of range [-1.0, 1.0].")
            return False
        
        # Run until done to check final score
        while not done:
            obs, reward, done, info = env.step({"investigate_host": "workstation_1"})
            
        final_score = info.get("final_score", -1.0)
        if not (0.0 <= final_score <= 1.0):
            print(f"Error: final score {final_score} is out of range [0.0, 1.0].")
            return False
        print(f"[PASS] final score {final_score} is within range [0.0, 1.0].")
        
        print("\nAll local validation checks passed!")
        return True
        
    except Exception as e:
        print(f"Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_environment()
    sys.exit(0 if success else 1)
