# AI Document Q&A System - Frontend

A modern, responsive web interface for the AI Document Q&A System built with HTML, CSS, and JavaScript.

## 🚀 Features

- **Modern UI/UX**: Beautiful, responsive design with Bootstrap 5
- **User Authentication**: Login and registration with JWT tokens
- **File Upload**: Drag & drop file upload interface
- **Real-time Feedback**: Toast notifications and loading states
- **Mobile Responsive**: Works perfectly on all devices

## 🛠️ Technologies Used

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with animations and gradients
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Beautiful icons
- **Fetch API**: Modern HTTP requests

## 📁 File Structure

```
frontend/
├── index.html          # Main HTML file
├── styles.css          # Custom CSS styles
├── script.js           # JavaScript functionality
└── README.md           # This file
```

## 🚀 Quick Start

1. **Ensure the backend is running**:
   ```bash
   # In the main project directory
   uvicorn app.main_minimal:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend server**:
   ```bash
   # In the frontend directory
   python -m http.server 3000
   ```

3. **Open your browser**:
   ```
   http://localhost:3000
   ```

## 🎯 How to Use

### 1. **Homepage**
- Beautiful hero section with call-to-action buttons
- Features overview with animated cards
- Responsive navigation

### 2. **Authentication**
- Click "Login" or "Register" in the navigation
- Fill in the form and submit
- JWT tokens are automatically stored in localStorage

### 3. **File Upload**
- Click "Upload Document" button
- Drag & drop files or click to browse
- Progress bar shows upload status
- Authentication required for upload

### 4. **Features**
- Click "Learn More" to see system features
- Animated feature cards with icons
- Smooth scrolling navigation

## 🔧 Configuration

### API Endpoint
The frontend connects to the FastAPI backend at `http://localhost:8000`. To change this:

1. Open `script.js`
2. Modify the `API_BASE_URL` constant:
   ```javascript
   const API_BASE_URL = 'http://your-api-url:port';
   ```

### Styling
Customize the appearance by editing `styles.css`:

- **Colors**: Modify CSS variables in `:root`
- **Animations**: Adjust keyframes and transitions
- **Layout**: Modify Bootstrap classes and custom CSS

## 🎨 Design Features

- **Gradient Backgrounds**: Beautiful color gradients
- **Smooth Animations**: Hover effects and transitions
- **Modern Typography**: Clean, readable fonts
- **Responsive Design**: Works on all screen sizes
- **Loading States**: Visual feedback for user actions
- **Toast Notifications**: Non-intrusive status messages

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Local Storage**: Persistent login sessions
- **Input Validation**: Client-side form validation
- **CORS Handling**: Proper cross-origin requests

## 📱 Mobile Responsive

The frontend is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🚀 Deployment

### Static Hosting
The frontend can be deployed to any static hosting service:

1. **Netlify**: Drag and drop the `frontend` folder
2. **Vercel**: Connect your GitHub repository
3. **GitHub Pages**: Push to a GitHub repository
4. **AWS S3**: Upload files to S3 bucket

### Production Build
For production, consider:
- Minifying CSS and JavaScript
- Optimizing images
- Using a CDN for external libraries
- Setting up proper CORS headers

## 🔗 API Integration

The frontend integrates with these backend endpoints:

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /health` - API health check
- `GET /api/v1/features` - System features
- `GET /api/v1/config` - Configuration info

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the backend has CORS enabled
2. **API Connection**: Check if the backend is running on port 8000
3. **File Upload**: Ensure authentication is working
4. **Styling Issues**: Check if all CSS files are loading

### Browser Console
Open browser developer tools (F12) to see:
- API request/response logs
- JavaScript errors
- Network connectivity issues

## 📈 Future Enhancements

- [ ] Real-time chat interface
- [ ] Document preview functionality
- [ ] Advanced search features
- [ ] User profile management
- [ ] Dark mode toggle
- [ ] Offline support
- [ ] Progressive Web App (PWA)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the AI Document Q&A System and follows the same license terms. 