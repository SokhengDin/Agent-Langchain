import { Geist, Geist_Mono } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Khmer font 
const notoSansKhmer = localFont({
  src: [
    {
      path: "../assets/fonts/Noto_Sans_Khmer/static/NotoSansKhmer-Light.ttf",
      weight: "300",
      style: "normal",
    },
    {
      path: "../assets/fonts/Noto_Sans_Khmer/static/NotoSansKhmer-Regular.ttf",
      weight: "400",
      style: "normal",
    },
    {
      path: "../assets/fonts/Noto_Sans_Khmer/static/NotoSansKhmer-Medium.ttf",
      weight: "500",
      style: "normal",
    },
    {
      path: "../assets/fonts/Noto_Sans_Khmer/static/NotoSansKhmer-SemiBold.ttf",
      weight: "600",
      style: "normal",
    },
    {
      path: "../assets/fonts/Noto_Sans_Khmer/static/NotoSansKhmer-Bold.ttf",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-noto-sans-khmer",
  display: "swap",
});

export const metadata = {
  title: {
    default: "AMS AI Assistant",
    template: "%s | AMS AI Assistant"
  },
  description: "AI-powered chat assistant developed by research students at the Department of Applied Mathematics and Statistics (AMS) at ITC. Get instant help with academic inquiries in English and Khmer.",
  keywords: [
    "AMS",
    "AI Assistant", 
    "Applied Mathematics",
    "Statistics",
    "ITC",
    "Chat Bot",
    "Academic Help",
    "Research",
    "Cambodia",
    "Khmer",
    "English"
  ],
  authors: [
    {
      name: "AMS Research Students",
      url: "https://itc.edu.kh"
    }
  ],
  creator: "Department of Applied Mathematics and Statistics",
  publisher: "Institute of Technology of Cambodia (ITC)",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    alternateLocale: "km_KH",
    siteName: "AMS AI Assistant",
    title: "AMS AI Assistant - Academic Chat Support",
    description: "AI-powered chat assistant for academic inquiries. Developed by AMS research students at ITC.",
    images: [
      {
        url: "/logo/logo.jpg",
        width: 1200,
        height: 630,
        alt: "AMS Department Logo",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "AMS AI Assistant",
    description: "AI-powered academic chat assistant by AMS students at ITC",
    images: ["/logo/logo.jpg"],
  },
  icons: {
    icon: [
      {
        url: "/logo/logo.jpg",
        sizes: "32x32",
        type: "image/jpeg",
      },
      {
        url: "/logo/logo.jpg", 
        sizes: "16x16",
        type: "image/jpeg",
      }
    ],
    apple: [
      {
        url: "/logo/logo.jpg",
        sizes: "180x180",
        type: "image/jpeg",
      }
    ],
    other: [
      {
        rel: "apple-touch-icon-precomposed",
        url: "/logo/logo.jpg",
      }
    ]
  },
  manifest: "/manifest.json",
  category: "education",
  classification: "Academic AI Assistant",
  referrer: "origin-when-cross-origin",
  colorScheme: "light dark",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#000000" }
  ],
  verification: {

  },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="icon" href="/logo/logo.jpg" sizes="any" />
        <link rel="apple-touch-icon" href="/logo/logo.jpg" />
        <meta name="theme-color" content="#ffffff" />
        <meta name="msapplication-TileColor" content="#ffffff" />
        <meta name="msapplication-TileImage" content="/logo/logo.jpg" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${notoSansKhmer.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
