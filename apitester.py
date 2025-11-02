#!/usr/bin/env python3
import requests
import sys
from typing import Optional

# API Configuration
API_BASE_URL = "http://localhost:8000"


def print_banner():
    """Print the CLI banner"""
    print("\n" + "="*60)
    print("          ELEVATOR API TESTER")
    print("="*60 + "\n")


def print_menu():
    """Print the main menu"""
    print("\nAvailable Commands:")
    print("  1. View elevator status")
    print("  2. Request floor (with direction)")
    print("  3. Step elevator")
    print("  4. Reset elevator")
    print("  5. Help")
    print("  q. Quit")
    print("-" * 60)


def get_status() -> Optional[dict]:
    """Get current elevator status"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/elevator")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API. Is the server running?")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting status: {e}")
        return None


def display_status(status: dict):
    """Display elevator status in a nice format"""
    if not status:
        return
    
    print("\n" + "="*60)
    print("ELEVATOR STATUS")
    print("="*60)
    print(f"  ID:              {status['id']}")
    print(f"  Current Floor:   {status['currentFloor']}")
    
    direction_map = {-1: "DOWN ↓", 0: "IDLE ⏸", 1: "UP ↑"}
    direction_str = direction_map.get(status['direction'], str(status['direction']))
    print(f"  Direction:       {direction_str}")
    
    print(f"  Active Target:   {status['activeTarget'] if status['activeTarget'] is not None else 'None'}")
    print(f"  Queue (Up):      {status['queueUp'] if status['queueUp'] else '[]'}")
    print(f"  Queue (Down):    {status['queueDown'] if status['queueDown'] else '[]'}")
    print("="*60 + "\n")


def request_floor():
    """Request a floor with direction"""
    print("\n--- Request Floor ---")
    
    try:
        floor = int(input("Enter floor number (0-10): "))
        print("\nDirection options:")
        print("  1  = UP (called from outside, going up)")
        print("  -1 = DOWN (called from outside, going down)")
        print("  0  = INTERNAL (passenger inside the elevator)")
        
        direction = int(input("Enter direction (-1, 0, or 1): "))
        
        if direction not in [-1, 0, 1]:
            print("❌ Error: Direction must be -1, 0, or 1")
            return
        
        response = requests.post(
            f"{API_BASE_URL}/api/elevator/request",
            json={"floor": floor, "direction": direction}
        )
        response.raise_for_status()
        
        print("✅ Floor request added successfully!")
        display_status(response.json())
        
    except ValueError:
        print("❌ Error: Please enter valid numbers")
    except requests.exceptions.HTTPError as e:
        # Extract error message from response if available
        try:
            error_detail = e.response.json().get('detail', str(e))
            print(f"❌ API Error: {error_detail}")
        except:
            print(f"❌ API Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")


def step_elevator():
    """Step the elevator forward"""
    print("\n--- Step Elevator ---")
    
    try:
        steps = input("Enter number of steps (default=1): ").strip()
        steps = int(steps) if steps else 1
        
        response = requests.post(
            f"{API_BASE_URL}/api/elevator/step",
            json={"steps": steps}
        )
        response.raise_for_status()
        
        print(f"✅ Elevator stepped forward {steps} step(s)!")
        display_status(response.json())
        
    except ValueError:
        print("❌ Error: Please enter a valid number")
    except requests.exceptions.HTTPError as e:
        # Extract error message from response if available
        try:
            error_detail = e.response.json().get('detail', str(e))
            print(f"❌ API Error: {error_detail}")
        except:
            print(f"❌ API Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")


def reset_elevator():
    """Reset the elevator"""
    print("\n--- Reset Elevator ---")
    confirm = input("Are you sure you want to reset? (y/n): ").lower()
    
    if confirm != 'y':
        print("Reset cancelled.")
        return
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/elevator/reset")
        response.raise_for_status()
        
        print("✅ Elevator reset successfully!")
        display_status(response.json())
        
    except requests.exceptions.HTTPError as e:
        # Extract error message from response if available
        try:
            error_detail = e.response.json().get('detail', str(e))
            print(f"❌ API Error: {error_detail}")
        except:
            print(f"❌ API Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")


def print_help():
    """Print help information"""
    print("\n" + "="*60)
    print("HELP - HOW TO USE THIS TOOL")
    print("="*60)
    print("\n1. VIEW STATUS")
    print("   Shows current elevator state, floor, direction, and queues")
    
    print("\n2. REQUEST FLOOR")
    print("   Add a floor to the elevator's queue:")
    print("   - Floor: 0-10")
    print("   - Direction:")
    print("     * 1 (UP):    Someone outside pressed up button")
    print("     * -1 (DOWN): Someone outside pressed down button")
    print("     * 0 (INTERNAL): Someone inside selected a floor")
    
    print("\n3. STEP ELEVATOR")
    print("   Move the elevator forward by N steps")
    print("   - Each step moves the elevator one floor closer to target")
    
    print("\n4. RESET ELEVATOR")
    print("   Reset elevator to ground floor (0) with empty queues")
    
    print("\n" + "="*60 + "\n")


def check_api_connection():
    """Check if API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.status_code == 200
    except:
        return False


def main():
    """Main CLI loop"""
    print_banner()
    
    # Check API connection
    print("Checking API connection...")
    if not check_api_connection():
        print(f"❌ Cannot connect to API at {API_BASE_URL}")
        print("Please ensure the API server is running (python main.py)")
        sys.exit(1)
    
    print(f"✅ Connected to API at {API_BASE_URL}\n")
    
    # Show initial status
    status = get_status()
    if status:
        display_status(status)
    
    # Main loop
    while True:
        try:
            print_menu()
            choice = input("Enter command: ").strip().lower()
            
            if choice == '1':
                status = get_status()
                if status:
                    display_status(status)
            
            elif choice == '2':
                request_floor()
            
            elif choice == '3':
                step_elevator()
            
            elif choice == '4':
                reset_elevator()
            
            elif choice == '5':
                print_help()
            
            elif choice == 'q' or choice == 'quit':
                print("\n👋 Goodbye!\n")
                sys.exit(0)
            
            else:
                print(f"❌ Unknown command: '{choice}'. Type '5' for help.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("The program will continue running. Type 'q' to quit.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        sys.exit(0)

