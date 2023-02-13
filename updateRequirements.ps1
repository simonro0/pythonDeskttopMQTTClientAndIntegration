# Check for outdated libraries
# local environment:
#.\venv\Scripts\pip list --outdated
# global environment:
#pip list --outdated

# Run the following command to install all requirements
# local environment:
#.\venv\Scripts\pip install -r requirements.txt
# global environment:
#pip install -r requirements.txt

# Run the following command to update all existent requirements in requirements.txt
# local environment:
#pip install --upgrade -r requirements.txt
# global environment:
#pip install --upgrade -r requirements.txt

# Run the following command to create the requirements file
# local environment:
#.\venv\Scripts\pip freeze > requirements.txt
# global environment:
pip freeze > requirements.txt