# Personal Finance Dashboard
Personal Finance Dashboard

## Prerequisites
- Python 3.8+
- pip (Python package installer)
- Virtualenv (optional but recommended)
- Sqllite (or your preferred relational database)

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/mayankWIZ/personal-finance-dashboard.git
    cd personal-finance-dashboard
    ```

2. **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python -m virtualenv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the requirements:**
    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

1. **Configure your database:**
    Update the `DATABASE_URL` in your environment variables or configuration file to point to your Sqllite database.

2. **Run Alembic migrations:**
    ```bash
    alembic upgrade head
    ```

## Running the Backend

1. **Start the backend server:**
    ```bash
    uvicorn khazana.core.apis.main:app --host 0.0.0.0 --port 8080
    ```

## Additional Information

- **Running Tests:**
    ```bash
    pytest tests # or the command you use for running tests
    ```

- **Linting and Formatting:**
    ```bash
    flake8 khazana  # for linting
    black -l 79 khazana  # for code formatting
    ```

## Troubleshooting

If you encounter any issues, please check the following:
- Ensure your virtual environment is activated.
- Verify your database is running and accessible.
- Check the configuration files for any missing or incorrect settings.

For further assistance, feel free to open an issue in the repository.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
