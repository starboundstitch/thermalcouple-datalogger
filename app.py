import pyqtgraph as pg
from PyQt6 import QtCore, QtWidgets, uic
import atexit
import nidaqmx
import threading
from pandas import DataFrame
from nidaqmx.constants import AcquisitionType, ThermocoupleType, TemperatureUnits

NUM_COLLECTPOINTS = 20
NUM_DATAPOINTS = 60
TIMING_INTERVAL = 4.0


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        atexit.register(self.cleanup)

        uic.loadUi('mainwindow.ui', self)
        self.setWindowTitle("Thermalcouple Logger")

        # Dac logic setup
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_thrmcpl_chan(
            "cDAQ4Mod1/ai0",
            units=TemperatureUnits.DEG_C,
            thermocouple_type=ThermocoupleType.T
        )
        self.task.ai_channels.add_ai_thrmcpl_chan(
            "cDAQ4Mod1/ai1",
            units=TemperatureUnits.DEG_C,
            thermocouple_type=ThermocoupleType.T
        )
        self.task.ai_channels.add_ai_thrmcpl_chan(
            "cDAQ4Mod1/ai2",
            units=TemperatureUnits.DEG_C,
            thermocouple_type=ThermocoupleType.T
        )

        self.task.timing.cfg_samp_clk_timing(TIMING_INTERVAL, sample_mode=AcquisitionType.CONTINUOUS)

        # Logic for the pushbotton test stuff
        self.pushButton.clicked.connect(self.export_button)
        self.pushButton_2.clicked.connect(self.clear_data)
        self.pushButton_3.clicked.connect(self.collect_data_point)
        self.pushButton_4.clicked.connect(self.collect_data)
        self.LED1.setCurrentIndex(0)

        # Temperature vs time dynamic plot
        pen1 = pg.mkPen(color=(255, 0, 255))
        pen2 = pg.mkPen(color=(0, 255, 255))
        pen3 = pg.mkPen(color=(255, 255, 0))
        self.temp_graph.setTitle("Temperature vs Time", size="20pt")
        self.temp_graph.setLabel("left", "Temperature (°C)")
        self.temp_graph.setLabel("bottom", "Time (s)")
        self.temp_graph.addLegend()
        self.temp_graph.showGrid(x=True, y=True)

        # Set Up Data for the Plot
        # self.time = list(range(NUM_DATAPOINTS))
        self.time = [0] * NUM_DATAPOINTS
        cur_temp = self.task.read()
        self.temperature = []
        self.temperature.append([cur_temp[0] for _ in range(NUM_DATAPOINTS)])
        self.temperature.append([cur_temp[1] for _ in range(NUM_DATAPOINTS)])
        self.temperature.append([cur_temp[2] for _ in range(NUM_DATAPOINTS)])

        # Add thermalcouple lines to graph
        self.line = []
        self.line.append(self.temp_graph.plot(
            self.time,
            self.temperature[0],
            name="Temperature Sensor 1",
            pen=pen1,
            symbolSize=0,
        ))
        self.line.append(self.temp_graph.plot(
            self.time,
            self.temperature[1],
            name="Temperature Sensor 2",
            pen=pen2,
            symbolSize=0,
        ))
        self.line.append(self.temp_graph.plot(
            self.time,
            self.temperature[2],
            name="Temperature Sensor 3",
            pen=pen3,
            symbolSize=0,
        ))

        # Data Collection Setup
        self.data = [[], [], [], []]
        self.collect_time = 0

        # Table Setup
        self.tableWidget.setHorizontalHeaderLabels([
            "Time(s)",
            "Thermalcouple 1",
            "Thermalcouple 2",
            "Thermalcouple 3"
        ])

        # Add a timer to simulate new temperature measurements
        self.timer = QtCore.QTimer()
        self.timer.setInterval(int(1000 / TIMING_INTERVAL))
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    # Test Push Button Logic
    def button3_clicked(self):
        self.LED1.setCurrentIndex(int(self.pushButton_3.isChecked()))

    # Function that Updates every Tick
    def update_plot(self):

        # Update Time
        self.time = self.time[1:]
        self.time.append(self.time[-1] + 1 / TIMING_INTERVAL)
        self.temperature[0] = self.temperature[0][1:]
        self.temperature[1] = self.temperature[1][1:]
        self.temperature[2] = self.temperature[2][1:]

        # Update Data
        data = self.task.read()
        self.temperature[0].append(data[0])
        self.temperature[1].append(data[1])
        self.temperature[2].append(data[2])
        self.line[0].setData(self.time, self.temperature[0])
        self.line[1].setData(self.time, self.temperature[1])
        self.line[2].setData(self.time, self.temperature[2])

        # Only Collect Data Once per Second
        if (self.collect_time != 0 and
                self.collect_time % TIMING_INTERVAL == 0):

            self.collect_data_point()

        if (self.collect_time > 0):

            self.collect_time -= 1

    def collect_data_point(self):

        self.data[0].append(self.time[-1])
        self.data[1].append(self.temperature[0][-1])
        self.data[2].append(self.temperature[1][-1])
        self.data[3].append(self.temperature[2][-1])

        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
        row = self.tableWidget.rowCount()
        self.tableWidget.setItem(row - 1, 0, QtWidgets.QTableWidgetItem(str(self.data[0][-1])))
        self.tableWidget.setItem(row - 1, 1, QtWidgets.QTableWidgetItem(str(self.data[1][-1])))
        self.tableWidget.setItem(row - 1, 2, QtWidgets.QTableWidgetItem(str(self.data[2][-1])))
        self.tableWidget.setItem(row - 1, 3, QtWidgets.QTableWidgetItem(str(self.data[3][-1])))

    def collect_data(self):

        self.collect_time = NUM_COLLECTPOINTS * TIMING_INTERVAL

    def export_button(self):

        x = threading.Thread(target=self.export_data)
        x.start()

    def export_data(self):

        df = DataFrame({
            'Collection Time': self.data[0],
            'Thermalcouple 1': self.data[1],
            'Thermalcouple 2': self.data[2],
            'Thermalcouple 3': self.data[3],
        })
        df.to_excel('test.xlsx', sheet_name='sheet1', index=False)

    def clear_data(self):

        self.data.clear()
        self.data = [[], [], [], []]
        self.tableWidget.setRowCount(0)

    def cleanup(self):
        print("cleaning up the function now")

        # Must have cleanup
        self.task.stop()


# Main application
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    main = MainWindow()
    main.show()
    app.exec()
