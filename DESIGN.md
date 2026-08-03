# RealFifty (PropTech Dashboard) DESIGN.md

## 1. Brand Identity & Vibe
- **Name**: RealFifty
- **Core Concept**: Seoul's Top 50 Real Estate (Apartments) MDD & Liquidity Tracking Terminal.
- **Vibe / Keywords**: Premium, Professional, Financial Terminal (e.g., Bloomberg Terminal), Data-Driven, Sleek, Trustworthy, Modern.
- **Target Audience**: High-net-worth real estate investors, data analysts, who want quick, intuitive insights into market crashes (MDD) and liquidity.

## 2. Color Palette
- **Primary Brand Color**: Deep Navy / Charcoal (`#131B2E` or `#0F172A`) for sidebars and headers to give a solid, premium feel.
- **Secondary Accent**: Subtle Gold or Coral Pink (`#FFB4AB` or `#D4AF37`) for the "Fifty" logo text or premium highlights.
- **Background**: Soft light gray (`#F7F9FC`) for the main content area (if light mode) or sleek dark mode (`#0B0F19`) if designing a full dark terminal.
- **Data Semantic Colors**:
  - **Bull (Rise/Expensive)**: Red (`#BA1A1A` or `#ef4444`) - Matches Korean stock market convention.
  - **Bear (Drop/Cheap)**: Blue (`#3B82F6` or `#2563eb`) - Korean convention for price drops.
  - **Neutral/Text**: `#191C1E` (Dark text), `#76777D` (Subtext).

## 3. Typography
- **Primary Font**: `Pretendard`, `Inter`, or `Spoqa Han Sans Neo`.
- **Numbers Font**: `Roboto Mono`, `Inter`, or `SF Pro Display`. Numbers must be highly legible, monospace-like, and clearly distinct because this is a financial dashboard.
- **Hierarchy**:
  - App Title: Extrabold, 2.2rem.
  - Page Headers / Complex Names: 800 weight, large size.
  - Ticker & Small Data: 600 weight, tight letter spacing.

## 4. UI/UX Components & Layout
- **Layout**: Sidebar Navigation (left) + Main Dashboard Content (right).
- **Top Ticker**: A continuously scrolling marquee ticker showing the biggest dropping apartments.
- **Cards**: Glassmorphism or solid white cards with subtle shadows (`box-shadow: 0 4px 20px rgba(0,0,0,0.05)`). Rounded corners (12px or 16px).
- **Data Visualizations**: Recharts-based or similar aesthetic. Clean grid lines, no clutter.
- **Tags/Pills**: Used for area types (e.g., '84A', '110B'). Should look like crisp, clickable tags indicating active vs inactive states.

## 5. Interaction & Animations
- Hover effects on property cards and area tags (slight lift or border color change).
- Smooth fade-in for charts.
- Micro-interactions for switching tab periods (1년, 5년, 10년).

## 6. Constraints
- The site is built with Next.js and React.
- Must be fully responsive (Desktop first, but mobile-friendly grid stacking).
- Keep CSS clean. Avoid overly distracting gradients; focus on typography and data clarity.
