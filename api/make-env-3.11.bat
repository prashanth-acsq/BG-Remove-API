start /MAX cmd /c "cls && title Prepare Environment && py -3.11 -m venv venv311 && cd venv311/Scripts && activate && cd .. && cd .. && py -3.8 -m pip install --upgrade pip && pip install -r requirements.txt && deactivate && timeout /t 5 /nobreak"