# 🤖 AI StudyBuddy

An intelligent Flask-based web application that provides AI-powered study assistance using Google's Gemini AI model.

## ✨ Features

- **AI-Powered Learning**: Get help with homework, explanations, and study tips
- **User Authentication**: Secure signup/login system with password hashing
- **Modern UI**: Beautiful, responsive design with glassmorphism effects
- **Quick Study Topics**: Pre-defined buttons for common study subjects
- **Real-time Chat**: Interactive Q&A with AI responses

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd AI-StudyBuddy
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_actual_gemini_api_key_here
   SECRET_KEY=your_secure_secret_key_here
   ```
   
   **Important**: Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🔐 Security Features

- **Password Hashing**: Passwords are hashed using SHA-256 with salt
- **Input Sanitization**: User inputs are validated and sanitized
- **Secure Sessions**: Flask sessions with secure secret keys
- **Environment Variables**: Sensitive data stored in environment variables
- **SQL Injection Protection**: Parameterized queries prevent SQL injection

## 🏗️ Project Structure

```
AI-StudyBuddy/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   └── style.css        # Modern CSS styling
├── templates/
│   ├── index.html       # Landing page
│   ├── login.html       # Login form
│   ├── signup.html      # Signup form
│   └── dashboard.html   # Main dashboard
└── users.db             # SQLite database (auto-created)
```

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Glassmorphism**: Modern glass-like UI elements
- **Gradient Backgrounds**: Beautiful color schemes
- **Smooth Animations**: Hover effects and transitions
- **Accessibility**: Proper labels and semantic HTML

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Your Gemini API key | Yes | None |
| `SECRET_KEY` | Flask secret key | No | Auto-generated |

### Database

The application uses SQLite with automatic table creation. The database file (`users.db`) will be created automatically on first run.

## 🚨 Security Notes

1. **Never commit your `.env` file** - it contains sensitive information
2. **Use strong passwords** - minimum 6 characters required
3. **Keep your API key secure** - don't share it publicly
4. **Regular updates** - keep dependencies updated for security patches

## 🐛 Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY environment variable is required"**
   - Make sure you have a `.env` file with your API key
   - Verify the API key is valid and has proper permissions

2. **"Module not found" errors**
   - Ensure your virtual environment is activated
   - Run `pip install -r requirements.txt`

3. **Database errors**
   - Delete `users.db` and restart the application
   - Check file permissions in the project directory

### Getting Help

- Check the console output for error messages
- Verify your API key is working
- Ensure all dependencies are installed correctly

## 📱 Usage

1. **Sign Up**: Create a new account with username and password
2. **Login**: Access your personalized dashboard
3. **Ask Questions**: Type any study-related question
4. **Quick Topics**: Use pre-defined buttons for common subjects
5. **Logout**: Secure logout when finished

## 🔮 Future Enhancements

- [ ] User profiles and study history
- [ ] Multiple AI models support
- [ ] File upload for document analysis
- [ ] Study group features
- [ ] Progress tracking
- [ ] Export chat history

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This application is for educational purposes. Always verify AI-generated information and use it as a supplement to your studies, not a replacement for proper learning.

---

**Made with ❤️ for students everywhere**
