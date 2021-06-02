echo "Performing environment setup..."
ORIGINAL_DIRECTORY="`pwd`"
LOCAL_DIRECTORY="`dirname ${0}`"
cd ${LOCAL_DIRECTORY}
LOG_FILE=./tfgmParkAndRideDetailsScraper.log
if [[ ! -f "$LOG_FILE" ]]; then
    touch ${LOG_FILE}
fi
chmod -R 757 ${LOG_FILE}
VENV_DIR=venv
if [[ ! -d "$VENV_DIR" ]]; then
    echo "$VENV_DIR directory not detected. Creating virtual environment..."
    virtualenv ${VENV_DIR}
fi
source venv/bin/activate
pip install -r requirements.txt

echo "Launching TfGM Park and Ride Details Scraper..."
python main.py

echo "Performing environment teardown..."
deactivate
cd ${ORIGINAL_DIRECTORY}
echo "TfGM Park and Ride Details Scraper terminated."

