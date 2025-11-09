# 🛒 Barang Bekas Kita

**Marketplace Barang Preloved #1 di Indonesia**

Modern marketplace untuk jual-beli barang bekas (preloved) dengan UI yang clean dan user-friendly. Built dengan Supabase + Vercel untuk performa dan skalabilitas maksimal.

![Status](https://img.shields.io/badge/status-ready-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## ✨ Features

### 🔥 Core Features
- ✅ **Browse Products** - Lihat semua barang yang dijual
- ✅ **Search** - Cari barang dengan keyword
- ✅ **Filter & Sort** - Filter by kategori, sort by harga
- ✅ **Sell Items** - Post iklan jual barang dengan mudah
- ✅ **Image Upload** - Upload foto langsung atau pakai URL
- ✅ **Categories** - 6 kategori: Elektronik, Fashion, Kendaraan, Rumah Tangga, Hobi, Lainnya
- ✅ **Responsive Design** - Works di desktop & mobile

### 🚀 Tech Stack
- **Frontend**: HTML5, CSS3 (Modern gradients), Vanilla JavaScript
- **Backend**: Supabase (PostgreSQL + Auth + Storage)
- **Hosting**: Vercel (CDN global, auto-scaling)
- **Database**: PostgreSQL with Full-Text Search
- **Storage**: Supabase Storage for images

### 🎨 Design
- Modern, clean UI dengan gradient yang eye-catching
- Card-based layout untuk products
- Smooth animations & transitions
- Mobile-responsive

---

## 🚀 Quick Start

### Option 1: Demo Mode (No Setup Required)

Buka `index.html` langsung di browser. App akan jalan dengan localStorage (demo mode).

### Option 2: Full Stack dengan Supabase

Ikuti **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** untuk setup lengkap dengan:
- Supabase database
- Image upload
- Production deployment

**Quick Summary:**
1. Create Supabase project
2. Run `supabase-schema.sql`
3. Create storage bucket "product-images"
4. Deploy to Vercel
5. Add environment variables
6. Done! 🎉

---

## 📁 Project Structure

```
retro2000/
├── index.html              # Main HTML file
├── style.css               # Modern styles with gradients
├── script.js               # Main app logic with Supabase integration
├── config.js               # Supabase configuration
├── supabase-schema.sql     # Database schema
├── vercel.json             # Vercel deployment config
├── .env.example            # Environment variables template
├── DEPLOYMENT_GUIDE.md     # Complete deployment guide
└── README.md               # This file
```

---

## 🗄️ Database Schema

### Tables:
- **categories** - Product categories (Elektronik, Fashion, dll)
- **products** - Main products table
- **products_with_categories** - View with joined data

### Features:
- Full-text search in Indonesian
- Auto-updated timestamps
- Row Level Security (RLS)
- Indexes for performance

---

## 🔧 Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```env
VITE_SUPABASE_URL=your-project-url.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

Get these from: Supabase Dashboard → Settings → API

### Local Development

1. Clone repo
2. Create `.env` file
3. Open `index.html` in browser
4. Or use local server: `python -m http.server 8000`

---

## 📊 Sample Data

App includes 12 sample products across all categories:
- iPhone 12 Pro, ASUS ROG Laptop, Samsung Tab S8
- Nike Air Jordan, The North Face Backpack, Casio G-Shock
- Honda Beat, Brompton Bike
- Sofa, Kulkas Samsung
- Canon Camera, PlayStation 5

---

## 🎯 Roadmap

### Phase 1: MVP (✅ DONE)
- [x] Product listing & browsing
- [x] Search & filter
- [x] Sell items form
- [x] Image upload
- [x] Supabase integration
- [x] Vercel deployment

### Phase 2: User Features (Coming Soon)
- [ ] User authentication (Supabase Auth)
- [ ] User profiles
- [ ] My listings management
- [ ] Favorites/wishlist
- [ ] User ratings & reviews

### Phase 3: Advanced Features
- [ ] Real-time chat between buyer & seller
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] Product moderation
- [ ] Payment integration (Midtrans/Xendit)

### Phase 4: Optimization
- [ ] SEO optimization
- [ ] Google Analytics
- [ ] Social media integration
- [ ] PWA (Progressive Web App)
- [ ] Push notifications

---

## 🌐 Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import repo to Vercel
3. Add environment variables
4. Deploy!

URL: `https://your-project.vercel.app`

### Netlify

Also works! Just:
1. Connect GitHub repo
2. Add env vars
3. Deploy

---

## 📱 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork this repo
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes!

---

## 👨‍💻 Author

Built with ❤️ for Indonesian marketplace community

---

## 🙏 Acknowledgments

- **Supabase** - Amazing open-source Firebase alternative
- **Vercel** - Best deployment platform for frontend
- **Unsplash** - Free high-quality images for samples

---

## 📞 Support

Need help? Check out:
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Supabase Docs](https://supabase.com/docs)
- [Vercel Docs](https://vercel.com/docs)

---

## 🔗 Links

- **Live Demo**: (Deploy first then add link here)
- **Supabase**: https://supabase.com
- **Vercel**: https://vercel.com

---

Made with ❤️ for Indonesia 🇮🇩
