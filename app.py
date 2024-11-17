from flask import Flask, jsonify
import serial
import time

# Initialize Flask app
app = Flask(__name__)

# Set up the serial connection (replace 'COM3' with your actual Arduino COM port)
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)

print("Connected to Arduino. Reading data...\n")

@app.route('/arduino-data', methods=['GET'])
def get_arduino_data():
    try:
        if arduino.in_waiting > 0:  # Check if data is available from Arduino
            data = arduino.readline().decode('utf-8').strip()  # Read and decode the data
            print(f"Arduino says: {data}")

            # Assuming the data format is something like "Temperature=25.3, Pressure detected"
            if "=" in data:
                temp_value = data.split('=')[-1].strip()  # Extract the numeric value
                pressure_detected = "Pressure detected" in data  # Check if pressure is detected

                return jsonify({
                    "temperature": float(temp_value),
                    "pressure_detected": pressure_detected
                })
            else:
                return jsonify({"error": "Unexpected data format", "raw_data": data}), 400
        else:
            return jsonify({"error": "No data available from Arduino"}), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)  # Runs the Flask app on port 5001
    except KeyboardInterrupt:
        print("\nStopped Flask server.")
    finally:
        arduino.close()
        print("Serial port closed.")
