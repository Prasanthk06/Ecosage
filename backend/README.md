# EcoSage Backend API

A complete Flask backend API for the EcoSage environmental intelligence platform.

## Features

- **RESTful API** for events, carbon calculation, and image classification
- **Real-time leaderboard** using Socket.IO and Redis
- **Image classification gateway** to TorchServe
- **MySQL database** with SQLAlchemy ORM
- **CORS support** for frontend integration
- **Environment-based configuration**

## API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/events` - Get all events
- `POST /api/events` - Create new event
- `POST /api/calculate_carbon` - Calculate carbon footprint
- `POST /api/classify` - Classify uploaded images
- `GET /api/leaderboard` - Get current leaderboard

### Socket.IO Events
- `connect` - Client connection
- `disconnect` - Client disconnection
- `complete_challenge` - User completes a challenge
- `join_leaderboard` - Join leaderboard updates
- `leaderboard_update` - Broadcast leaderboard changes

## Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Install and start MySQL:**
   - Install MySQL Server
   - Create database: `CREATE DATABASE ecosage;`
   - Update DATABASE_URL in .env

5. **Install and start Redis:**
   - Install Redis Server
   - Start Redis service
   - Update REDIS_HOST/REDIS_PORT in .env

6. **Initialize database:**
   ```bash
   python init_db.py
   ```

## Running the Application

### Development
```bash
python app.py
```

### Production
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

The API will be available at `http://localhost:5000`

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `ecosage-secret-key-2024` | Flask secret key |
| `FLASK_DEBUG` | `False` | Enable debug mode |
| `FLASK_PORT` | `5000` | Port to run the server |
| `DATABASE_URL` | `mysql+pymysql://root:password@localhost:3306/ecosage` | Database connection URL |
| `REDIS_HOST` | `localhost` | Redis server host |
| `REDIS_PORT` | `6379` | Redis server port |
| `TORCHSERVE_URL` | `http://127.0.0.1:8080/predictions/waste_classifier` | TorchServe endpoint |

### Database Schema

#### Events Table
- `id` - Primary key
- `title` - Event title
- `date` - Event date
- `time` - Event time
- `location` - Event location
- `description` - Event description
- `category` - Event category
- `attendees` - Number of attendees

#### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - User email
- `score` - User score for leaderboard
- `challenges_completed` - Number of completed challenges

## API Usage Examples

### Get Events
```bash
curl -X GET http://localhost:5000/api/events
```

### Calculate Carbon Footprint
```bash
curl -X POST http://localhost:5000/api/calculate_carbon \
  -H "Content-Type: application/json" \
  -d '{"electricity": 350, "transportation": 1200}'
```

### Upload Image for Classification
```bash
curl -X POST http://localhost:5000/api/classify \
  -F "image=@path/to/image.jpg"
```

### Get Leaderboard
```bash
curl -X GET http://localhost:5000/api/leaderboard
```

## Integration with TorchServe

The image classification endpoint acts as a gateway to TorchServe. If TorchServe is not available, the API returns mock classification results to ensure frontend functionality.

To set up TorchServe:
1. Install TorchServe
2. Deploy your waste classification model
3. Ensure it's running at the configured URL

## Socket.IO Integration

The backend supports real-time features through Socket.IO:

```javascript
// Frontend JavaScript example
const socket = io('http://localhost:5000');

// Join leaderboard updates
socket.emit('join_leaderboard');

// Complete a challenge
socket.emit('complete_challenge', {
  username: 'eco_warrior',
  points: 50,
  challenge_name: 'Recycle 10 items'
});

// Listen for leaderboard updates
socket.on('leaderboard_update', (data) => {
  console.log('Updated leaderboard:', data.leaderboard);
});
```

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "error": "Error type",
  "message": "Detailed error message"
}
```

## Testing

Use tools like Postman, curl, or the included test scripts to test the API endpoints.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.