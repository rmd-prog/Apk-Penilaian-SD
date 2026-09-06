# SI-NILAI SD V7 — TA 2026/2027

Fondasi aplikasi penilaian SD berbasis React/Vite, responsive HP, siap dibungkus Android dengan Capacitor.

## Menjalankan
- Node.js LTS
- `npm install`
- `npm run dev`

## Build website
`npm run build`

## Android
Setelah Node.js + Android Studio terpasang:
1. `npm install`
2. `npm run build`
3. `npx cap add android`
4. `npx cap sync`
5. `npx cap open android`

## Produksi
Backend contoh tersedia di `server/index.js`. Untuk multi-guru/online, hubungkan API ke PostgreSQL/Neon dan tambahkan autentikasi.

## Dasar kebijakan
TA 2026/2027 menggunakan Keputusan Kepala BKPDM Nomor 020 Tahun 2026 untuk perubahan CP Pendidikan Agama dan Budi Pekerti; CP mapel lain mengacu Keputusan Kepala BSKAP Nomor 046/H/KR/2025.
