# thermocouple-datalogger

A python program which uses NI DAQ cards to log thermocouple data.


## Installing

Clone the repository:

```
git clone https://github.com/starboundstitch/thermocouple-datalogger.git
cd thermocouple-datalogger
```

The recommended way for installing dependencies is to use a [python virtual environment](https://docs.python.org/3/library/venv.html) ( or the provided shell.nix file).

```
python -m venv .venv
```

On Windows Powershell:

```
.\venv\Scripts\Activate.bat
pip install -r requirements.txt
```

That should install the dependencies and the program should be able to be ran.

## Running

If you are not currently in a virtual environment, you can get into it again by executing the following command.

```
.\venv\Scripts\Activate.bat
```

And then you can run the app.

```
python app.py
```

> [!WARNING]
Ensure that the NI DAQ is plugged in before starting the program.
