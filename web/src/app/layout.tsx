import type { Metadata } from "next";
import "./globals.css";
import "./member.css";
import "./usability.css";
import MemberProvider from "./MemberProvider";

export const metadata: Metadata = {
  title: "RealFifty | 대한민국 주택시장 AI 분석 터미널",
  description: "국토부 실거래가와 매물 최저호가를 기반으로 대한민국 대표 50개 아파트의 시장 상황을 분석합니다.",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ko"
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col"><MemberProvider>{children}</MemberProvider></body>
    </html>
  );
}
