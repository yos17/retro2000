# ⚡ QUICK DEPLOY GUIDE - 15 Menit ke Production!

Ikuti langkah ini untuk deploy marketplace Anda ke production.

---

## 🗄️ STEP 1: Setup Supabase (5 menit)

### 1.1 Create Project

1. Buka: **https://app.supabase.com/sign-in**
2. Login atau Sign Up (100% gratis, no credit card)
3. Click **"New Project"**
4. Isi form:
   - **Name**: `barang-bekas-kita`
   - **Database Password**: [Buat password kuat - SIMPAN!]
   - **Region**: `Singapore` (terdekat Indonesia)
   - **Pricing Plan**: Free (sudah otomatis terpilih)
5. Click **"Create new project"**
6. ☕ Tunggu 1-2 menit sampai project ready

### 1.2 Run Database Schema

1. Di Supabase Dashboard, click **"SQL Editor"** (icon </> di sidebar kiri)
2. Click **"New query"**
3. Buka file `supabase-schema.sql` di repo ini (214 lines)
4. **Copy SEMUA isinya** (Ctrl+A, Ctrl+C)
5. **Paste** ke SQL Editor (Ctrl+V)
6. Click **"Run"** (tombol play atau Ctrl+Enter)
7. Tunggu ~10 detik
8. ✅ Harusnya muncul: "Success. No rows returned"

**Apa yang baru dibuat:**
- ✅ 6 categories (Elektronik, Fashion, Kendaraan, dll)
- ✅ 12 sample products
- ✅ Database tables dengan indexes
- ✅ Full-text search capability
- ✅ Row Level Security policies

### 1.3 Create Storage Bucket

1. Click **"Storage"** di sidebar kiri
2. Click **"Create a new bucket"**
3. Isi:
   - **Name**: `product-images`
   - **Public bucket**: ✅ **WAJIB CENTANG INI!**
   - **File size limit**: Biarkan default (50MB)
4. Click **"Create bucket"**

### 1.4 Copy API Keys

1. Click **"Settings"** (icon gear di kiri bawah)
2. Click **"API"** di sidebar
3. Scroll ke bawah, copy 2 values ini:

```
Project URL:
https://xxxxxxxxxxxxx.supabase.co

anon public key:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFz...
```

📋 **SIMPAN kedua values ini di notepad!** Akan dipakai di Step 2.

---

## 🌐 STEP 2: Deploy ke Vercel (8 menit)

### 2.1 Push ke GitHub (jika belum)

Code sudah di GitHub, tapi pastikan latest commit:

```bash
cd /home/user/retro2000
git status
git push
```

### 2.2 Import ke Vercel

1. Buka: **https://vercel.com/new**
2. Login dengan GitHub
3. Click **"Import Git Repository"**
4. Pilih repository **"retro2000"** (atau nama repo Anda)
5. Click **"Import"**

### 2.3 Configure Project

Di halaman "Configure Project":

**Framework Preset**:
- Pilih: **"Other"**

**Build & Development Settings**:
- **Build Command**: Kosongkan atau isi `echo "Static site"`
- **Output Directory**: Isi dengan `.` (satu titik)
- **Install Command**: Kosongkan

### 2.4 Add Environment Variables

Scroll ke **"Environment Variables"**:

1. Click **"Add"** untuk expand section

2. Tambahkan Variable #1:
   - **NAME**: `VITE_SUPABASE_URL`
   - **VALUE**: Paste Project URL dari Step 1.4
   - **Environments**: ✅ Centang SEMUA (Production, Preview, Development)
   - Click "Add"

3. Tambahkan Variable #2:
   - **NAME**: `VITE_SUPABASE_ANON_KEY`
   - **VALUE**: Paste anon public key dari Step 1.4
   - **Environments**: ✅ Centang SEMUA
   - Click "Add"

### 2.5 Deploy!

1. Click **"Deploy"** button (besar, biru, di bawah)
2. Vercel akan:
   - Clone repository
   - Build project
   - Deploy ke global CDN
3. Tunggu ~1-2 menit
4. 🎉 **DONE!**

Vercel akan kasih URL seperti:
```
https://retro2000-xxxxxx.vercel.app
```

---

## ✅ STEP 3: Test Deployment

### 3.1 Open Your Site

1. Click URL yang diberikan Vercel
2. Atau buka: `https://retro2000.vercel.app` (sesuaikan nama)

### 3.2 Verify Supabase Connection

1. Buka site Anda
2. Tekan **F12** (Developer Tools)
3. Click tab **"Console"**
4. Refresh halaman (F5)
5. Cek console log:

✅ **Success:**
```
✅ Supabase initialized successfully!
📊 Mode: Supabase
```

❌ **Failed (kalau ada masalah):**
```
⚠️ Supabase not configured! Using demo mode
```

Jika failed, berarti env vars belum di-set dengan benar.

### 3.3 Test Functionality

**Test #1: Browse Products**
- ✅ Halaman muncul dengan 12 sample products
- ✅ Click salah satu product → detail muncul

**Test #2: Search**
- ✅ Ketik "laptop" di search box
- ✅ Click "Cari" → hasil muncul

**Test #3: Add Product**
- ✅ Click tab "Jual Barang"
- ✅ Isi form lengkap
- ✅ Upload foto (atau pakai URL)
- ✅ Click "Posting Iklan"
- ✅ Check di "Jelajah" → product baru muncul!

**Test #4: Image Upload**
- ✅ Upload foto dari komputer
- ✅ Preview muncul sebelum submit
- ✅ After submit, foto ter-upload ke Supabase Storage

---

## 🔧 Troubleshooting

### ❌ "Supabase not configured"

**Problem**: Environment variables belum di-set atau salah.

**Solution**:
1. Vercel Dashboard → Your Project
2. Click **"Settings"** → **"Environment Variables"**
3. Verify 2 vars ada:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
4. Pastikan values benar (copy dari Supabase Settings → API)
5. Jika salah, edit vars lalu:
   - Click **"Deployments"** tab
   - Click **"..."** di latest deployment
   - Click **"Redeploy"**

### ❌ "Failed to insert product"

**Problem**: Database schema belum di-run atau RLS policies blocking.

**Solution**:
1. Supabase Dashboard → SQL Editor
2. Run query untuk test:
   ```sql
   SELECT * FROM categories;
   ```
3. Jika error atau empty:
   - Re-run file `supabase-schema.sql` (214 lines)
4. Jika masih error, check RLS policies:
   ```sql
   ALTER TABLE products ENABLE ROW LEVEL SECURITY;
   ```

### ❌ "Failed to upload image"

**Problem**: Storage bucket tidak public atau belum dibuat.

**Solution**:
1. Supabase → **Storage**
2. Check bucket `product-images` ada
3. Click bucket → **Settings**
4. ✅ Centang **"Public bucket"**
5. Click **"Save"**

### ❌ Products tidak muncul

**Problem**: Database kosong.

**Solution**:
1. Supabase → **Table Editor**
2. Check table `products` → harusnya ada 12 rows
3. Jika kosong, re-run `supabase-schema.sql`

---

## 🎯 Next Steps (Optional)

### Custom Domain

Jika punya domain (contoh: barangbekas.com):

1. Vercel Dashboard → Settings → **Domains**
2. Click **"Add"**
3. Masukkan domain Anda
4. Update DNS di registrar (Namecheap/GoDaddy/Niagahoster):
   - Add A record: `76.76.21.21`
   - Add CNAME: `cname.vercel-dns.com`
5. Tunggu ~10 menit DNS propagation

### Analytics

Add Google Analytics:

1. Buat GA4 property di analytics.google.com
2. Copy tracking ID
3. Add ke `index.html` sebelum `</head>`:
   ```html
   <!-- Google Analytics -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX');
   </script>
   ```

### SEO Optimization

Add meta tags ke `<head>`:

```html
<meta name="description" content="Marketplace barang preloved terpercaya di Indonesia. Jual beli barang bekas berkualitas dengan harga terjangkau.">
<meta property="og:title" content="Barang Bekas Kita - Marketplace Preloved Indonesia">
<meta property="og:description" content="Jual beli barang bekas berkualitas dengan mudah dan aman">
<meta property="og:image" content="https://your-domain.com/og-image.jpg">
```

---

## 📊 Monitor Usage

### Supabase Free Tier Limits:
- Database: 500MB
- Storage: 1GB
- Bandwidth: 2GB/month
- 50,000 monthly active users

Check: Supabase → Settings → **Usage**

### Vercel Free Tier Limits:
- Bandwidth: 100GB/month
- Deployments: Unlimited
- Serverless function executions: 100GB-hours

Check: Vercel → **Analytics**

---

## 🎉 Congratulations!

Your marketplace is now LIVE on the internet! 🚀

**Share your URL:**
- Social media
- WhatsApp groups
- Indonesian forums
- Facebook marketplace groups

**Start collecting real users and listings!**

---

## 📞 Need Help?

Check:
- Full guide: `DEPLOYMENT_GUIDE.md` (350+ lines)
- Supabase docs: https://supabase.com/docs
- Vercel docs: https://vercel.com/docs

---

Made with ❤️ for Indonesia 🇮🇩
