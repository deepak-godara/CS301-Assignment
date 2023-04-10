import csv
import zmq
import json
from cryptography.fernet import Fernet
import matplotlib.pyplot as plt


class SolarPlant:
    def __init__(self, panel_efficiency):
        self.panel_efficiency = panel_efficiency

    def calculate_energy(self, temperature, sunlight_intensity):
        energy = self.panel_efficiency * sunlight_intensity * (temperature - 20)
        return energy


def read_solar_data(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)
    return data


def write_output_data(filename, output_data):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Time', 'Temperature', 'Sunlight Intensity', 'Energy']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_data:
            writer.writerow(row)


def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(json.dumps(data).encode())
    return encrypted_data


def send_data(encrypted_data, host, port):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{host}:{port}")
    socket.send(encrypted_data)
    response = socket.recv()
    socket.close()
    return response

def plot_solar_data(solar_data):
    """Plots the solar data using matplotlib."""
    temperature_data = [data['temperature'] for data in solar_data]
    sunlight_intensity_data = [data['sunlight_intensity'] for data in solar_data]
    humidity_data = [data['humidity'] for data in solar_data]
    pressure_data = [data['pressure'] for data in solar_data]
    plt.subplot(2, 2, 1)
    plt.plot(temperature_data)
    plt.title('Temperature')
    plt.subplot(2, 2, 2)
    plt.plot(sunlight_intensity_data)
    plt.title('Sunlight Intensity')
    plt.subplot(2, 2, 3)
    plt.plot(humidity_data)
    plt.title('Humidity')
    plt.subplot(2, 2, 4)
    plt.plot(pressure_data)
    plt.title('Pressure')
    plt.tight_layout()
    plt.show()


def main():
    # Reading data from file
    solar_data = read_solar_data('solar_data.csv')


    # Initializing the SolarPlant object
    plant = SolarPlant(0.2)

    # Initializing output data list
    output_data = []

    # Calculating energy for each row and adding it to output data
    for row in solar_data:
        temperature = float(row['temperature'])
        sunlight_intensity = float(row['sunlight_intensity'])
        energy = plant.calculate_energy(temperature, sunlight_intensity)
        output_row = {'Date': row['date'], 'Time': row['time'], 'Temperature': temperature,
                      'Sunlight Intensity': sunlight_intensity, 'Energy': energy}
        output_data.append(output_row)

    # Writing output data to file
    write_output_data('output_data.csv', output_data)
    
    plot_solar_data(solar_data)

    # Encrypting data and sending it to server
    key = b'_6CfS_RuIgFGNrqyTctTbT3q4V2M4drKjZVeg-hf62c='
    encrypted_data = encrypt_data(output_data, key)
    response = send_data(encrypted_data, 'localhost', '5555')
    print(response)


if __name__ == '__main__':
    main()