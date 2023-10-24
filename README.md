# Todo FastAPI App

A simple Todo application built with FastAPI.

## Features

- JWT Authentication: Implements JWT (JSON Web Tokens) authentication for secure user authentication and authorization.

- Task Management with Categories: Allows users to create tasks organized by categories for better organization and management.

- CRUD Operations: Enables users to perform Create, Read, Update, and Delete operations on tasks and categories.


## Requirements

- Python 3.10+
- Poetry

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/witelokk/todo.git
   ```

2. Navigate to the project directory:

    ```bash
    cd todo
    ```

3. Set up the environment variables: `POSTGRES_USERNAME`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `SECRET_KEY`

4. Run the app:

    ```bash
    poetry run todo
    ```

## API Endpoints

- `POST /auth/`: Create User
- `POST /auth/token`: Get Token
- `GET /tasks/`: Get Tasks
- `POST /tasks/`: Add Task
- `GET /tasks/{task_id}`: Get Task
- `PATCH /tasks/{task_id}`: Edit Task
- `DELETE /tasks/{task_id}`: Delete Task
- `GET /tasks/category/{category_id}`: Get Tasks By Category
- `GET /categories`: Get Categories
- `POST /categories`: Add Category
- `GET /categories/{category_id}`: Get Category
- `PATCH /categories/{category_id}`: Edit Category
- `DELETE /categories/{category_id}`: Delete Category

You can get more information about these endpoints using docs at /docs.
