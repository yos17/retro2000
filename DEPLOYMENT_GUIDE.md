# 🚀 Deployment Guide - Barang Bekas Kita

Panduan lengkap untuk deploy marketplace preloved Indonesia ke Supabase + Vercel.

---

## 📋 Prerequisites

Sebelum mulai, pastikan Anda punya:
- ✅ Akun GitHub (gratis)
- ✅ Akun Supabase (gratis): https://supabase.com
- ✅ Akun Vercel (gratis): https://vercel.com
- ✅ Repository ini sudah di push ke GitHub

---

## 🗄️ STEP 1: Setup Supabase Database

### 1.1 Create Supabase Project

1. Buka https://app.supabase.com
2. Click **"New Project"**
3. Isi detail project:
   - **Name**: `barang-bekas-kita` (atau nama lain)
   - **Database Password**: Buat password yang kuat (SIMPAN ini!)
   - **Region**: Pilih Singapore (terdekat dengan Indonesia)
4. Click **"Create new project"**
5. Tunggu ~2 menit sampai project selesai dibuat

### 1.2 Run SQL Schema

1. Di Supabase Dashboard, klik **"SQL Editor"** di sidebar kiri
2. Klik **"New query"**
3. Buka file `supabase-schema.sql` di repository ini
4. **Copy semua isi file** tersebut
5. **Paste** ke SQL Editor
6. Klik **"Run"** (atau tekan Ctrl+Enter)
7. Tunggu sampai muncul "Success. No rows returned"

✅ Database siap! Sekarang Anda sudah punya:
- 6 kategori barang
- 12 sample products
- Full-text search capability
- Views dan functions

### 1.3 Create Storage Bucket

1. Di Supabase Dashboard, klik **"Storage"** di sidebar
2. Klik **"Create a new bucket"**
3. Isi:
   - **Name**: `product-images`
   - **Public bucket**: ✅ **CENTANG INI** (penting!)
4. Klik **"Create bucket"**

### 1.4 Get API Keys

1. Di Supabase Dashboard, klik **"Settings"** (icon gear di bawah)
2. Klik **"API"** di sidebar
3. Copy 2 values ini:
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (key yang panjang)

📝 **SIMPAN kedua values ini!** Akan digunakan di Vercel nanti.

---

## 🌐 STEP 2: Deploy to Vercel

### 2.1 Import Repository

1. Buka https://vercel.com/new
2. Login dengan GitHub
3. Click **"Import Git Repository"**
4. Pilih repository **retro2000** (atau nama repo Anda)
5. Click **"Import"**

### 2.2 Configure Project

Di halaman configuration:

1. **Framework Preset**: Pilih **"Other"** (ini static site)
2. **Root Directory**: Biarkan `.` (root)
3. **Build Command**: Biarkan kosong atau isi `echo "Static site"`
4. **Output Directory**: Isi dengan `.` (titik)
5. **Install Command**: Biarkan kosong

### 2.3 Add Environment Variables

Scroll ke bagian **"Environment Variables"**:

1. Click **"Add"** atau expand section
2. Tambahkan 2 environment variables:

**Variable 1:**
- **Name**: `VITE_SUPABASE_URL`
- **Value**: Paste Project URL dari Supabase (langkah 1.4)
- **Environment**: Centang semua (Production, Preview, Development)

**Variable 2:**
- **Name**: `VITE_SUPABASE_ANON_KEY`
- **Value**: Paste anon public key dari Supabase (langkah 1.4)
- **Environment**: Centang semua (Production, Preview, Development)

### 2.4 Deploy!

1. Click **"Deploy"** button
2. Tunggu ~1-2 menit
3. 🎉 **SELESAI!** App Anda sudah online!

Vercel akan memberikan URL seperti:
- `https://retro2000.vercel.app`
- atau custom domain jika Anda punya

---

## ✅ STEP 3: Verify Deployment

1. Buka URL Vercel Anda
2. Buka browser console (F12 → Console tab)
3. Refresh halaman
4. Cek console log:
   - ✅ **"✅ Supabase initialized successfully!"** = Berhasil!
   - ❌ **"⚠️ Supabase not configured!"** = Ada masalah di env vars

### Jika ada masalah:

1. Cek Vercel **Settings** → **Environment Variables**
2. Pastikan kedua vars sudah ada
3. Klik **"Redeploy"** di Deployments tab

---

## 🧪 STEP 4: Test Functionality

Coba fitur-fitur ini:

### Test 1: Browse Products
1. ✅ Buka halaman utama
2. ✅ Lihat 12 sample products muncul
3. ✅ Click salah satu product → detail muncul

### Test 2: Search
1. ✅ Ketik "laptop" di search box
2. ✅ Click "Cari"
3. ✅ Hasil pencarian muncul

### Test 3: Filter
1. ✅ Klik tab "Jelajah"
2. ✅ Pilih kategori "Elektronik"
3. ✅ Pilih sort "Termurah"
4. ✅ Click "Terapkan Filter"

### Test 4: Add Product (PENTING!)
1. ✅ Klik tab "Jual Barang"
2. ✅ Isi form lengkap
3. ✅ Upload foto (atau masukkan URL)
4. ✅ Click "Posting Iklan"
5. ✅ Check di tab "Jelajah" → product baru muncul!

### Test 5: Image Upload
1. ✅ Klik "Jual Barang"
2. ✅ Upload foto dari komputer
3. ✅ Preview muncul
4. ✅ Submit form
5. ✅ Foto ter-upload ke Supabase Storage

---

## 🔧 Troubleshooting

### ❌ "Supabase not configured"

**Penyebab**: Environment variables belum di-set atau salah
**Solusi**:
1. Check Vercel Settings → Environment Variables
2. Pastikan nama vars: `VITE_SUPABASE_URL` dan `VITE_SUPABASE_ANON_KEY`
3. Pastikan values correct (copy dari Supabase Settings → API)
4. Redeploy: Vercel Dashboard → Deployments → ... → Redeploy

### ❌ "Failed to insert product"

**Penyebab**: Database schema belum di-run atau ada error di SQL
**Solusi**:
1. Buka Supabase SQL Editor
2. Run query: `SELECT * FROM categories;`
3. Jika error: Re-run file `supabase-schema.sql`

### ❌ "Failed to upload image"

**Penyebab 1**: Storage bucket belum dibuat
**Solusi**: Create bucket "product-images" di Supabase Storage

**Penyebab 2**: Bucket tidak public
**Solusi**:
1. Supabase → Storage → product-images → Settings
2. Centang "Public bucket"

**Penyebab 3**: File terlalu besar
**Solusi**: Maksimal 5MB per file

### ❌ Products tidak muncul

**Penyebab**: Database kosong atau query error
**Solusi**:
1. Check Supabase → Table Editor → products
2. Pastikan ada data (12 sample products)
3. Jika kosong, re-run SQL schema

---

## 📱 Optional: Custom Domain

Jika ingin custom domain (misal: barangbekas.com):

1. Beli domain di Namecheap/GoDaddy/Niagahoster
2. Vercel Dashboard → Settings → Domains
3. Add domain
4. Update DNS sesuai instruksi Vercel
5. Tunggu ~10 menit untuk propagasi DNS

---

## 🔐 Optional: Add Authentication

Untuk add user login (agar setiap user bisa manage listing mereka sendiri):

1. Supabase → Authentication → Providers
2. Enable Email provider
3. Update RLS policies di database
4. Integrate Supabase Auth di frontend

Tutorial lengkap: https://supabase.com/docs/guides/auth

---

## 📊 Monitoring

### Check Supabase Usage:
- Supabase Dashboard → Settings → Usage
- Free tier limits:
  - Database: 500MB
  - Storage: 1GB
  - Bandwidth: 2GB/month

### Check Vercel Analytics:
- Vercel Dashboard → Analytics
- Free tier: 100GB bandwidth/month

---

## 🎯 Next Steps

Sekarang marketplace Anda sudah online! Beberapa improvement yang bisa dilakukan:

1. **SEO Optimization**:
   - Add meta tags untuk social sharing
   - Create sitemap.xml
   - Add robots.txt

2. **Features**:
   - Add user authentication
   - Add favorites/wishlist
   - Add product ratings & reviews
   - Add messaging between buyer & seller
   - Add admin dashboard

3. **Marketing**:
   - Share di social media
   - Add Google Analytics
   - Create Facebook page
   - Instagram integration

---

## 📞 Support

Jika ada pertanyaan atau butuh bantuan:
- Check console log di browser (F12)
- Check Supabase logs: Dashboard → Logs
- Check Vercel logs: Dashboard → Deployments → [latest] → View Function Logs

---

## 🎉 Congratulations!

Marketplace preloved Indonesia Anda sudah LIVE! 🚀

Share URL Anda dan mulai terima listings dari user!

Made with ❤️ for Indonesia
