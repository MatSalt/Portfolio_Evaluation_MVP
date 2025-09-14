import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "포트폴리오 스코어 - AI 기반 포트폴리오 분석 서비스",
  description: "증권사 앱의 포트폴리오 스크린샷을 업로드하면 AI가 전문가 수준의 투자 분석을 제공합니다. 펀더멘탈, 기술적 분석, 거시경제 등 다각도로 포트폴리오를 평가해드립니다.",
  keywords: ["포트폴리오", "투자분석", "AI", "주식", "펀드", "투자전략", "포트폴리오분석"],
  authors: [{ name: "포트폴리오 스코어 팀" }],
  creator: "포트폴리오 스코어",
  publisher: "포트폴리오 스코어",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "ko_KR",
    url: "https://portfolio-score.vercel.app",
    title: "포트폴리오 스코어 - AI 기반 포트폴리오 분석 서비스",
    description: "증권사 앱의 포트폴리오 스크린샷을 업로드하면 AI가 전문가 수준의 투자 분석을 제공합니다.",
    siteName: "포트폴리오 스코어",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "포트폴리오 스코어 - AI 기반 포트폴리오 분석 서비스",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "포트폴리오 스코어 - AI 기반 포트폴리오 분석 서비스",
    description: "증권사 앱의 포트폴리오 스크린샷을 업로드하면 AI가 전문가 수준의 투자 분석을 제공합니다.",
    images: ["/og-image.png"],
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 1,
  },
  themeColor: "#3B82F6",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
