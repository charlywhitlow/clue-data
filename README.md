# Notes

Dependencies are saved in `environment.yaml`

To run in virtual environment:

    # install virtual environment
    python3 -m venv env

    # activate virtual environment
    source ./env/bin/activate

    # install dependencies in env
    pip3 install -r environment.yaml

    # run program
    python3 clue-import.py

    # to update environment.yaml file from active environment
    pip3 freeze > environment.yaml

    # deactivate virtual environment
    deactivate
