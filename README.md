# SocialVoyage

A social platform for travelers to connect and plan trips together.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- MongoDB Atlas account (for cloud database)

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Dakshmulundkar/SocialVoyage.git
   cd SocialVoyage
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **MongoDB Setup**
   - Create a MongoDB Atlas account if you don't have one
   - Create a new cluster
   - Get your connection string from MongoDB Atlas
   - Create a `.env` file with your MongoDB connection string

5. **Environment Variables**
   Create a `.env` file in the root directory with the following:
   ```
   MONGODB_URI=your_mongodb_connection_string
   SECRET_KEY=your_secret_key
   ```

6. **Initialize Database**
   ```bash
   python init_db.py
   ```

7. **Run the Application**
   ```bash
   python app.py
   ```

8. **Access the Application**
   Open your browser and go to: `http://localhost:5000`

## Project Structure

```
SocialVoyage/
├── app.py
├── database.py
├── requirements.txt
├── .env
├── static/
│   ├── landing/
│   ├── login/
│   ├── profile/
│   ├── interests/
│   └── signup/
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   └── ...
└── README.md
```

## Common Issues and Solutions

1. **ModuleNotFoundError**
   - Solution: Make sure you've activated the virtual environment and installed all requirements

2. **MongoDB Connection Error**
   - Solution: Check your MongoDB connection string in .env
   - Ensure your IP address is whitelisted in MongoDB Atlas
   - Verify your username and password are correct

3. **Static Files Not Loading**
   - Solution: Check if all static files are present in the correct directories
   - Verify file permissions

4. **Port Already in Use**
   - Solution: Change the port in app.py or kill the process using the port

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Running with Docker

The application can be easily deployed using Docker and Docker Compose.

### Prerequisites

- Docker
- Docker Compose

### Quick Start

1. **Build and start the services**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   Open your browser and go to: `http://localhost:5000`

### Production Deployment

For production deployments, make sure to update the environment variables in `docker-compose.yml`:

- Change the `SECRET_KEY` to a strong, unique value
- Update MongoDB credentials
- Consider using external volume mounts for persistent data

### Building the Container

To build just the Flask application container:

```bash
docker build -t socialvoyage-app .
```

### Stopping the Services

```bash
docker-compose down
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
