# Grateful - A Modern Gratitude Network

A beautiful, modern social platform for sharing gratitude and building positive communities.

## 🚀 Features

- **Modern Authentication** - NextAuth.js with multiple providers
- **Real-time Feed** - Live updates with WebSocket support
- **Rich Content** - Photo uploads, location tagging, and beautiful posts
- **Social Features** - Hearts, comments, follows, and mentions
- **Mobile-First** - Responsive design that works on all devices
- **Performance** - Optimized for speed with modern caching

## 🛠 Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **NextAuth.js** - Authentication
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and sessions
- **Alembic** - Database migrations
- **Cloudinary** - Image uploads

### Infrastructure
- **Docker** - Containerization
- **Vercel** - Frontend deployment
- **Railway** - Backend deployment

## 🏗 Project Structure

```
grateful/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── api/                 # FastAPI backend
├── packages/
│   ├── database/            # Database schema & migrations
│   ├── shared/              # Shared types & utilities
│   └── ui/                  # Reusable UI components
├── infrastructure/          # Docker, deployment configs
└── docs/                   # Documentation
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL
- Redis

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/grateful.git
   cd grateful
   ```

2. **Start the infrastructure**
   ```bash
   docker-compose up -d
   ```

3. **Setup the frontend**
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

4. **Setup the backend**
   ```bash
   cd apps/api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

5. **Run database migrations**
   ```bash
   cd apps/api
   alembic upgrade head
   ```

Visit [http://localhost:3000](http://localhost:3000) to see the app!

## 📝 Development

### Frontend Development
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript checks

### Backend Development
- `uvicorn main:app --reload` - Start development server
- `alembic revision --autogenerate -m "description"` - Create migration
- `alembic upgrade head` - Apply migrations
- `pytest` - Run tests

## 🧪 Testing

```bash
# Frontend tests
cd apps/web
npm run test

# Backend tests
cd apps/api
pytest
```

## 🚀 Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set environment variables
3. Deploy automatically on push to main

### Backend (Railway)
1. Connect your GitHub repository to Railway
2. Set environment variables
3. Deploy automatically on push to main

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with love for the gratitude community
- Inspired by the need for positive social media
- Powered by modern web technologies 