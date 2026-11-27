IoT-Based Patient Health Monitoring and Alert Portal

📌 Project Overview

The IoT-Based Patient Health Monitoring and Alert Portal is a smart healthcare system designed to monitor patients' health conditions in real time using Internet of Things (IoT) technology.

The system collects vital health parameters such as heart rate, blood oxygen saturation (SpO₂), and body temperature using sensors connected to an ESP32 microcontroller.

The collected data is transmitted to a web-based portal where doctors and caregivers can monitor patient health remotely. If abnormal readings are detected, the system generates alerts to notify the responsible healthcare professionals.

🎯 Objectives

To monitor patient health parameters continuously.

To collect real-time health data using IoT sensors.

To display patient readings through a web dashboard.

To detect abnormal health conditions.

To generate automatic alerts for doctors and caregivers.

To maintain patient health history and reports.

To support remote patient monitoring.

⚙️ Technologies Used

Hardware

ESP32 Microcontroller

MAX30102 Heart Rate and SpO₂ Sensor

DS18B20 Temperature Sensor

AD8232 ECG Sensor (Optional)

Buzzer

Connecting Wires

Breadboard

Software

Arduino IDE

Python

Flask Framework

HTML

CSS

JavaScript

MySQL Database

MQTT / HTTP Protocol

🏗️ System Architecture

Sensors collect patient health parameters.

ESP32 reads the sensor values.

Data is transmitted through Wi-Fi.

The backend server receives the sensor data.

Patient readings are stored in the database.

The web portal displays real-time health information.

The alert system checks readings against configured thresholds.

Doctors and caregivers receive notifications when abnormal readings are detected.

✨ Key Features

Patient Registration and Login

Doctor Login and Dashboard

Real-Time Health Monitoring

Heart Rate Monitoring

SpO₂ Monitoring

Body Temperature Monitoring

ECG Monitoring (Optional)

Automatic Abnormality Detection

Emergency Alert Notifications

Patient Health History

Health Report Generation

Remote Patient Monitoring

📊 Health Parameters

Parameter

Sensor

Purpose

Heart Rate

MAX30102

Measures pulse rate

SpO₂

MAX30102

Estimates blood oxygen saturation

Temperature

DS18B20

Measures temperature

ECG

AD8232

Records electrical heart activity


