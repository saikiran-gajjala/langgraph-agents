# Movie AI Bot Application
## Project Description:
 Movie AI Bot Generative AI application is designed to help to explore and analyze movie-related information effortlessly. It answers questions in natural language by retrieving data from the MongoDB Atlas Mflix database and dynamically generates visualizations or charts based on the data. The application combines a React-based front end with a Python-powered backend built using Langchain and LangGraph. By leveraging LangGraph and an Agentic RAG (Retrieval-Augmented Generation) approach, it efficiently fetches and processes data from the MongoDB database to deliver insightful responses and interactive visualizations.

![thumbnail](https://github.com/user-attachments/assets/94985252-89d6-4d14-aedb-17beb8e76a75)


## Running the Frontend and Backend Projects

### Prerequisites
- Node.js (v20 or higher)
- Python (v3.10.11 or higher)
- pip
- MongoDB Atlas Account with sample **mflix** dataset included. Refer to the link (https://www.mongodb.com/docs/atlas/sample-data/)

### Backend Setup
1. Navigate to the backend directory:
    ```sh
    cd backend
    ```
2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```
3. Activate the virtual environment:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
4. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
5. You may need to configure environment variables as specified in the `.env.example` file
6. Run the backend server:
    ```sh
    python app.py
    ```

### Frontend Setup
1. Navigate to the frontend directory:
    ```sh
    cd frontend
    ```
2. Install the required dependencies:
    ```sh
    npm install
    ```
3. You may need to configure environment variables as specified in the `.env.example` file
4. Start the frontend development server:
    ```sh
    npm start
    ```

### Accessing the Application
- Open your browser and navigate to `http://localhost:5173` to access the frontend.
- The backend server will be running on `http://localhost:8001`.

### Additional Notes
- Ensure both the frontend and backend servers are running simultaneously for the application to function correctly.
- You may need to configure environment variables as specified in the `.env.example` files in both the frontend and backend directories.
