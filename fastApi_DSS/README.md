# Installation and Running the Backend

## Prerequisites

Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).

## Step 1: Create a Virtual Environment

It is recommended to create a virtual environment to manage your project dependencies.

```sh
python -m venv venv
```

Activate the virtual environment:

- On Windows:
  ```sh
  .\venv\Scripts\activate
  ```
- On macOS/Linux:
  ```sh
  source venv/bin/activate
  ```

## Step 2: Install Dependencies

Install the required dependencies using `pip`: 
> I may miss some of the dependencies, please install them if you encounter any error

```sh
pip install fastapi duckdb watchfiles uvicorn
```

## Step 3: Run the Backend

Use `watchfiles` to run the backend with automatic reloading:

```sh
watchfiles "uvicorn main:app"
```

This command will start the FastAPI application and automatically reload it whenever changes are detected in the source files.