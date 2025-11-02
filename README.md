# The Elevator

A pretty good elevator if you ask me! This is an elevator simulation system with a RESTful API built using FastAPI. It simulates an intelligent elevator that efficiently handles floor requests using priority queues.

## Features

- **Smart Elevator Logic**: Uses optimized algorithms with priority queues to handle multiple floor requests
- **RESTful API**: FastAPI-based server with automatic documentation
- **Interactive CLI Tester**: User-friendly command-line interface to test the elevator system
- **Realistic Simulation**: Supports external requests (up/down buttons) and internal passenger requests

## Prerequisites

- **Python 3.7+**: Make sure you have Python installed
- **Git**: To clone the repository (or download as ZIP)

## Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/OBress/The-Elevator.git
cd The-Elevators
```

Or download and extract the ZIP file.

### 2. Install Dependencies

It's recommended to use a virtual environment:

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

## Running the Application

### Step 1: Start the Server

Run the following command to start the FastAPI server:

```bash
python main.py
```

You should see output indicating the server is running:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

The API server will be available at:

- **Local**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc`

### Step 2: Test the Service

In a **new terminal window** (keep the server running in the first terminal), run the API tester:

```bash
python apitester.py
```

This will launch an interactive CLI tool where you can:

1. **View elevator status** - See current floor, direction, and queues
2. **Request floors** - Add floor requests with direction (up/down/internal)
3. **Step elevator** - Move the elevator forward by N steps
4. **Reset elevator** - Reset to ground floor
5. **Get help** - View detailed instructions

### Example Usage

1. Start with viewing the elevator status (Option 1)
2. Request a floor (Option 2):
   - Floor: 5
   - Direction: 1 (someone on floor 5 wants to go up)
3. Step the elevator (Option 3) to move it toward the target
4. Watch the elevator move and service requests!

## API Endpoints

If you prefer to use the API directly (e.g., with cURL, Postman, or your own code):

### GET `/`

Check if service is running

### GET `/api/elevator`

Get current elevator status

### POST `/api/elevator/request`

Request a floor

```json
{
  "floor": 5,
  "direction": 1
}
```

- `direction`: 1 = up, -1 = down, 0 = internal (passenger inside)

### POST `/api/elevator/step`

Step the elevator forward

```json
{
  "steps": 1
}
```

### POST `/api/elevator/reset`

Reset elevator to default state (ground floor, empty queues)

## Project Structure

```
The-Elevator/
├── Elevator.py       # Core elevator logic and algorithms
├── main.py           # FastAPI server
├── apitester.py      # Interactive CLI testing tool
├── tester.py         # Additional testing utilities
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, edit `main.py` and change the port number:

```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

### Cannot Connect to API

Make sure the server is running before starting the API tester. You should see the server running in another terminal window.

### Module Not Found

Make sure you've installed all dependencies:

```bash
pip install -r requirements.txt
```

## Contributing

Feel free to submit issues or pull requests!

## License

This project is open source and available for educational purposes.
