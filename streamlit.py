import streamlit as st
import serial
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# Set up the serial connection to the Arduino
arduinoport = "COM13"  # Adjust as needed
baudrate = 9600
ser = serial.Serial(arduinoport, baudrate, timeout=0.1)


# Buffer to store partial data
buffer = ""


def read_arduino_data():
    """Read and return a complete message from the serial buffer."""
    global buffer
    while ser.in_waiting > 0:
        char = ser.read().decode('utf-8')  # Read one character
        buffer += char  # Append to the buffer


        # Check if we have a complete message
        if '<' in buffer and '>' in buffer:
            start = buffer.find('<')  # Start of the message
            end = buffer.find('>')   # End of the message


            if start < end:  # Ensure the message is valid
                message = buffer[start + 1:end]  # Extract the content
                buffer = buffer[end + 1:]  # Clear the processed part
                return message
            else:
                buffer = buffer[end + 1:]  # Clear invalid start


    return None  # No complete message yet


def parse_sensor_data(data):
    """Parse the temperature and pressure data from the sensor string."""
    try:
        parts = data.split(", ")
        temp = float(parts[0].split("=")[1])  # Extract temperature
        pressure = int(parts[1].split("=")[1])  # Extract pressure
        return temp, pressure
    except (IndexError, ValueError):
        return None, None  # Handle invalid or incomplete data


def display_hydrate_detection():
    # Custom styling with Capris font
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Capris&display=swap');
        
        body {
            background-color: #f4f4f9;
            font-family: 'Capris', sans-serif;
        }
        .title {
            font-size: 40px;
            font-weight: bold;
            text-align: center;
            font-family: 'Capris', cursive;
            color: #4A90E2;
            margin-top: 20px;
        }
        .temp-pressure {
            font-size: 20px;
            font-family: 'Capris', cursive;
            text-align: center;
            margin-top: 10px;
        }
        .subtitle {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            font-family: 'Capris', cursive;
            color: #4A90E2;
            margin-top: 30px;
        }
        </style>
        <div class="title">Hydrate Detection System</div>
        """,
        unsafe_allow_html=True,
    )

    display_outliers()
    # Initialize session state for sensor data
    if "sensor_data" not in st.session_state:
        st.session_state["sensor_data"] = pd.DataFrame(columns=["Temperature (°C)", "Pressure Detected", "Time"])


    # Create placeholders
    temp_placeholder = st.empty()
    chart_placeholder = st.empty()
    table_placeholder = st.empty()


    # Display the table once
    with table_placeholder.container():
        st.markdown("<div class='temp-pressure'>Sensor Data Table:</div>", unsafe_allow_html=True)


    # Real-time data display and plotting
    while True:
        data = read_arduino_data()
        if data:
            temp, pressure = parse_sensor_data(data)
            if temp is not None and pressure is not None:
                # Convert pressure to "High" or "Low"
                pressure_label = "High" if pressure == 1 else "Low"


                # Update temperature and pressure display
                temp_placeholder.markdown(
                    f"""
                    <div class="temp-pressure">
                        Current Temperature: {temp:.2f}°C<br>
                        Pressure: <b style="color: {'red' if pressure_label == 'High' else 'green'};">{pressure_label}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


                # Add new data to the session state DataFrame (prepend row)
                time_stamp = pd.Timestamp.now()
                new_row = pd.DataFrame([[temp, pressure_label, time_stamp]], columns=["Temperature (°C)", "Pressure Detected", "Time"])
                st.session_state["sensor_data"] = pd.concat([new_row, st.session_state["sensor_data"]], ignore_index=True)


                # Update the displayed table (drop the "Time" column)
                table_placeholder.dataframe(
                    st.session_state["sensor_data"].drop(columns=["Time"]),
                    use_container_width=True,
                )


                # Update the line chart (reverse order for real-time display)
                chart_placeholder.line_chart(
                    st.session_state["sensor_data"].set_index("Time").iloc[::-1]["Temperature (°C)"],
                    use_container_width=True,
                )

def display_outliers():
    # Custom CSS to apply the Capris font to the title
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Capris&display=swap');
        
        .subtitle {
            font-family: 'Capris', cursive;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            color: #4A90E2;
            margin-top: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Subtitle for linear regression
    st.markdown('<div class="subtitle">Linear Regression and Outlier Detection</div>', unsafe_allow_html=True)

    # Specify the path of the CSV file on your local machine
    file_path = "updated_file_numeric_time.csv"  # Update this with your local CSV file path
    file_path_2 = "new_temp_file.csv"
    file_path_3 = "new_pressure_file.csv"
    # Read the CSV file using pandas
    col3, col4 = st.columns(2)
    try:
        df = pd.read_csv(file_path)
        df_2 = pd.read_csv(file_path_2)
        df_3 = pd.read_csv(file_path_3)
        # Display the data in Streamlit
        #st.write("Data from the CSV file:")
        #st.write(df.head())
        
        with col3:
            # Create a scatter plot of the 'time' vs 'volume'
            fig, ax = plt.subplots()
            ax.scatter(df_2['numeric_time'], df_2['Temperature (C)'], c='blue', label='Data points')

            ax.set_xlabel('Time')  # Set the x-axis label
            ax.set_ylabel('Temp')  # Set the y-axis label
            ax.set_title('Scatter Plot of Time vs Temp')  # Set the title

            # Display the plot in Streamlit
            st.pyplot(fig)
        with col4:
            # Create a scatter plot of the 'time' vs 'volume'
            fig, ax = plt.subplots()
            ax.scatter(df_3['numeric_time'], df_3['Pressure (MPa)'], c='blue', label='Data points')

            ax.set_xlabel('Time')  # Set the x-axis label
            ax.set_ylabel('Pressure')  # Set the y-axis label
            ax.set_title('Scatter Plot of Time vs Pressure')  # Set the title

            # Display the plot in Streamlit
            st.pyplot(fig)
        # Check if the DataFrame has the expected columns (adjust these to your CSV file's columns)
        if 'numeric_time' in df.columns and 'total_volume' in df.columns:
            col1, col2 = st.columns(2)
            # Create a scatter plot of the 'time' vs 'volume'
            fig, ax = plt.subplots()
            ax.scatter(df['numeric_time'], df['total_volume'], c='blue', label='Data points')

            ax.set_xlabel('Time')  # Set the x-axis label
            ax.set_ylabel('Volume')  # Set the y-axis label
            ax.set_title('Scatter Plot of Time vs Volume')  # Set the title

            # Display the plot in Streamlit
            #st.pyplot(fig)

            # Extract 'time' as independent variable (X) and 'volume' as dependent variable (y)
            X = df[['numeric_time']].values  # Independent variable (reshape for single feature)
            y = df['total_volume'].values  # Dependent variable
            
            # Initialize and fit the linear regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict the volume based on the model
            y_pred = model.predict(X)
            
            # Calculate residuals (differences between actual and predicted values)
            residuals = y - y_pred
            
            # Calculate outliers based on residuals (2 standard deviations rule)
            residual_std = np.std(residuals)
            residual_mean = np.mean(residuals)
            
            # Find outliers (residuals that are more than 2 standard deviations from the mean)
            outliers = df[np.abs(residuals - residual_mean) > 2 * residual_std]
            
            # Print outliers
            #st.write("Outliers:")
            #st.write(outliers)
            
            # Plotting
            fig, ax = plt.subplots()
            
            # Scatter plot of the actual data points
            ax.scatter(df['numeric_time'], df['total_volume'], color='blue', label='Data points')
            
            # Plot the best fit line
            ax.plot(df['numeric_time'], y_pred, color='red', label='Best fit line')
            
            ax.set_xlabel('Time')  # Set the x-axis label
            ax.set_ylabel('Volume')  # Set the y-axis label
            ax.set_title('Linear Regression: Time vs Volume')  # Set the title
            ax.legend()

            # Display the plot in Streamlit
            #st.pyplot(fig)

            # Print outliers in a table format
            
            outliers_table = pd.DataFrame({
                'Time': outliers['Time'],
                'Actual Value (Volume)': outliers['total_volume'],
                'Predicted Value (Volume)': model.predict(outliers[['numeric_time']])
            })
            
            with col1:
                # Display outliers table in Streamlit
                st.write("Hydrates Detected (Time, Actual Volume, Predicted Volume):")
                st.write(outliers_table)

            # Plotting
            fig, ax = plt.subplots(figsize=(6, 4))

            # Scatter plot of the actual data points
            ax.scatter(df['numeric_time'], df['total_volume'], color='blue', label='Data points')

            # Plot the best fit line
            ax.plot(df['numeric_time'], y_pred, color='red', label='Best fit line')

            ax.set_xlabel('Time')  # Set the x-axis label
            ax.set_ylabel('Volume')  # Set the y-axis label
            ax.set_title('Linear Regression: Time vs Volume')  # Set the title
            ax.legend()

            with col2:
                # Display the plot in Streamlit
                st.pyplot(fig)

        else:
            st.write("CSV does not have the required columns 'numeric_time' and 'total_volume'.")
    except Exception as e:
        st.write(f"Error reading or processing the CSV file: {e}")


if __name__ == "__main__":
    display_hydrate_detection()
