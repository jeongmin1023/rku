import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LabFit",
  description: "공개 연구 근거와 관심 주제의 연결성을 탐색하는 연구실 탐색 도구"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
