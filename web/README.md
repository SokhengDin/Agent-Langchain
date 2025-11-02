# AMS AI Assistant - Chat Application

A modern, bilingual AI-powered chat assistant developed by research students at the Department of Applied Mathematics and Statistics (AMS) at the Institute of Technology of Cambodia (ITC). This application provides academic support in both English and Khmer languages.

## 🌟 Features

- **Bilingual Support**: Switch between English and Khmer languages
- **Modern UI**: Clean, responsive design with dark/light theme support
- **Real-time Chat**: Interactive chat interface with typing indicators
- **Academic Focus**: Specialized for academic inquiries and research support
- **Khmer Font Support**: Beautiful Noto Sans Khmer font integration
- **Mobile Responsive**: Works seamlessly on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

Make sure you have the following installed on your computer:
- **Node.js** (version 18 or higher) - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/LLM-research-and-application-AMS/Chat-App.git
   cd chat-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```
   or if you prefer yarn:
   ```bash
   yarn install
   ```

3. **Set up environment variables**
   
   Create a `.env.local` file in the root directory:
   ```bash
   touch .env.local
   ```
   
   Add the following content to `.env.local`:
   ```env
   NEXT_PUBLIC_LLM_API_BASE_URL=your_api_base_url_here
   ```
   
   > **Note**: Replace `your_api_base_url_here` with your actual API endpoint URL

4. **Run the development server**
   ```bash
   npm run dev
   ```
   or with yarn:
   ```bash
   yarn dev
   ```

5. **Open your browser**
   
   Navigate to [http://localhost:3000](http://localhost:3000) to see the application running.

## 📁 Project Structure

```
chat-app/
├── app/                    # Next.js App Router
│   ├── layout.js          # Root layout with metadata and fonts
│   ├── page.js            # Home page component
│   ├── globals.css        # Global styles
│   └── not-found.js       # 404 page
├── components/            # React components
│   ├── ChatContainer.jsx  # Main chat interface
│   ├── ChatHeader.jsx     # Chat header with title
│   ├── ChatInput.jsx      # Message input component
│   ├── ChatMessages.jsx   # Messages display
│   ├── LanguageToggle.jsx # Language switcher
│   ├── WelcomeModal.jsx   # Welcome popup
│   ├── Footer.jsx         # Footer component
│   └── ui/               # Reusable UI components
├── contexts/             # React contexts
│   └── LanguageContext.js # Language state management
├── locales/              # Translation files
│   ├── en.json           # English translations
│   └── km.json           # Khmer translations
├── services/             # API services
│   └── chatService.js    # Chat API integration
├── config/               # Configuration files
│   └── config.js         # App configuration
├── assets/               # Static assets
│   └── fonts/            # Custom fonts (Khmer)
├── hooks/                # Custom React hooks
├── lib/                  # Utility libraries
└── public/               # Public static files
```

## 🛠️ Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build the application for production
- `npm run start` - Start the production server
- `npm run lint` - Run ESLint to check code quality

## 🌐 Language Support

The application supports two languages:

- **English (en)**: Default language
- **Khmer (km)**: Cambodian language with proper font support

Users can switch between languages using the language toggle button in the chat interface.

## 🎨 Styling & UI

- **Framework**: Tailwind CSS for styling
- **Components**: Radix UI for accessible components
- **Icons**: Lucide React for modern icons
- **Fonts**: 
  - Geist Sans & Geist Mono for English text
  - Noto Sans Khmer for Khmer text
- **Animations**: Tailwind CSS animations

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_LLM_API_BASE_URL` | Base URL for the AI chat API | Yes |

### API Integration

The chat service connects to a backend API endpoint:
- Endpoint: `/api/v1/hotel-agent/chat`
- Method: POST
- Payload: `{ message: string, thread_id: string }`

## 🚀 Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Deploy to Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to [Vercel](https://vercel.com)
3. Add environment variables in Vercel dashboard
4. Deploy automatically

## 🤝 Contributing

This project is developed by research students at AMS, ITC. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Learning Resources

If you're new to the technologies used in this project:

- **Next.js**: [Official Documentation](https://nextjs.org/docs)
- **React**: [React Documentation](https://react.dev/)
- **Tailwind CSS**: [Tailwind Docs](https://tailwindcss.com/docs)
- **JavaScript**: [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript)


## 📄 License

This project is developed for educational purposes by AMS research students at ITC.

---

**Happy Coding! 🎓✨**