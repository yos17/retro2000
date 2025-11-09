-- Barang Bekas Kita - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    emoji VARCHAR(10) NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price BIGINT NOT NULL CHECK (price >= 0),
    condition VARCHAR(50) NOT NULL,
    location VARCHAR(255) NOT NULL,
    contact VARCHAR(50) NOT NULL,
    image_url TEXT,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    user_id UUID, -- Will link to auth.users later if you add authentication
    views INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_location ON products(location);

-- Create full-text search index
CREATE INDEX IF NOT EXISTS idx_products_search ON products
USING gin(to_tsvector('indonesian', name || ' ' || description));

-- Insert default categories
INSERT INTO categories (name, emoji, slug) VALUES
    ('Elektronik', '📱', 'elektronik'),
    ('Fashion', '👕', 'fashion'),
    ('Kendaraan', '🚗', 'kendaraan'),
    ('Rumah Tangga', '🏠', 'rumah-tangga'),
    ('Hobi & Olahraga', '🎮', 'hobi'),
    ('Lainnya', '📦', 'lainnya')
ON CONFLICT (slug) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to increment views
CREATE OR REPLACE FUNCTION increment_product_views(product_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE products
    SET views = views + 1
    WHERE id = product_id;
END;
$$ LANGUAGE plpgsql;

-- Row Level Security (RLS) Policies
-- Enable RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Everyone can read categories
CREATE POLICY "Categories are viewable by everyone"
    ON categories FOR SELECT
    USING (true);

-- Everyone can read active products
CREATE POLICY "Active products are viewable by everyone"
    ON products FOR SELECT
    USING (is_active = true);

-- Anyone can insert products (for now - you can restrict this later with auth)
CREATE POLICY "Anyone can create products"
    ON products FOR INSERT
    WITH CHECK (true);

-- Users can update their own products (will work when you add auth)
-- For now, allow all updates
CREATE POLICY "Anyone can update products"
    ON products FOR UPDATE
    USING (true);

-- Create view for products with category info
CREATE OR REPLACE VIEW products_with_categories AS
SELECT
    p.id,
    p.name,
    p.description,
    p.price,
    p.condition,
    p.location,
    p.contact,
    p.image_url,
    p.views,
    p.is_active,
    p.created_at,
    p.updated_at,
    c.name as category_name,
    c.emoji as category_emoji,
    c.slug as category_slug
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.is_active = true;

-- Insert sample data (12 products from your original data)
DO $$
DECLARE
    cat_elektronik UUID;
    cat_fashion UUID;
    cat_kendaraan UUID;
    cat_rumah_tangga UUID;
    cat_hobi UUID;
BEGIN
    -- Get category IDs
    SELECT id INTO cat_elektronik FROM categories WHERE slug = 'elektronik';
    SELECT id INTO cat_fashion FROM categories WHERE slug = 'fashion';
    SELECT id INTO cat_kendaraan FROM categories WHERE slug = 'kendaraan';
    SELECT id INTO cat_rumah_tangga FROM categories WHERE slug = 'rumah-tangga';
    SELECT id INTO cat_hobi FROM categories WHERE slug = 'hobi';

    -- Insert sample products
    INSERT INTO products (name, category_id, price, condition, location, description, contact, image_url) VALUES
    ('iPhone 12 Pro 128GB', cat_elektronik, 7500000, 'Seperti Baru', 'Jakarta Selatan',
     'iPhone 12 Pro warna Pacific Blue, kondisi mulus 95%, fullset box + charger original. Garansi iBox sudah habis tapi fungsi normal semua.',
     '081234567890', 'https://images.unsplash.com/photo-1603891637773-a6fc64f06ab4?w=400'),

    ('Sepatu Nike Air Jordan 1', cat_fashion, 2500000, 'Baik', 'Bandung',
     'Nike Air Jordan 1 Retro High OG, size 42, kondisi 8/10. Sudah dipakai beberapa kali tapi masih sangat layak. Box hilang.',
     '082345678901', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'),

    ('Laptop ASUS ROG Zephyrus G14', cat_elektronik, 15000000, 'Seperti Baru', 'Surabaya',
     'ASUS ROG Zephyrus G14 (2021), Ryzen 9, RTX 3060, 16GB RAM, 1TB SSD. Jarang dipakai, seperti baru. Garansi masih 1 tahun.',
     '083456789012', 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400'),

    ('Sofa Minimalis 3 Seater', cat_rumah_tangga, 3500000, 'Baik', 'Tangerang',
     'Sofa minimalis Scandinavian style, warna abu-abu, sangat nyaman. Dijual karena pindah rumah. Bisa COD atau kirim via ekspedisi.',
     '084567890123', 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400'),

    ('Kamera Canon EOS M50 Mark II', cat_hobi, 8500000, 'Seperti Baru', 'Jakarta Pusat',
     'Canon EOS M50 Mark II + Lensa Kit 15-45mm. Shutter count rendah (5000 shots). Fullset lengkap dengan tas dan memory card 64GB.',
     '085678901234', 'https://images.unsplash.com/photo-1606980707009-7b7a3f87f7af?w=400'),

    ('Honda Beat 2020', cat_kendaraan, 12000000, 'Baik', 'Bekasi',
     'Honda Beat 2020, warna hitam, kilometer 15.000. Pajak hidup, STNK & BPKB lengkap. Service rutin di Honda.',
     '086789012345', 'https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=400'),

    ('Tas Ransel The North Face', cat_fashion, 850000, 'Baik', 'Yogyakarta',
     'Tas ransel The North Face Borealis Classic, warna hitam. Kondisi bagus, tidak ada robek. Cocok untuk kuliah atau traveling.',
     '087890123456', 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'),

    ('PlayStation 5 Digital Edition', cat_hobi, 6500000, 'Seperti Baru', 'Semarang',
     'PS5 Digital Edition, fullset box lengkap + 1 controller. Kondisi 99% seperti baru. Bonus 3 game digital.',
     '088901234567', 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400'),

    ('Kulkas 2 Pintu Samsung', cat_rumah_tangga, 4200000, 'Baik', 'Depok',
     'Kulkas Samsung 2 pintu inverter, kapasitas 500L. Kondisi normal, dingin, tidak berisik. Free ongkir area Jabodetabek.',
     '089012345678', 'https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=400'),

    ('Samsung Galaxy Tab S8', cat_elektronik, 7800000, 'Seperti Baru', 'Malang',
     'Samsung Galaxy Tab S8 WiFi Only, 8GB/128GB. Mulus no lecet, fullset + S-Pen. Bonus keyboard case.',
     '081122334455', 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400'),

    ('Jam Tangan Casio G-Shock', cat_fashion, 1200000, 'Baik', 'Bogor',
     'Casio G-Shock GA-2100 (CasiOak), warna hitam. Original, beli dari Casio Store. Box dan kartu garansi lengkap.',
     '082233445566', 'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=400'),

    ('Sepeda Lipat Brompton', cat_hobi, 18500000, 'Baik', 'Jakarta Utara',
     'Brompton M6L 2019, warna hitam. Kondisi terawat, service rutin. Sudah upgrade beberapa parts. Full original.',
     '083344556677', 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400');
END $$;

-- Grant permissions (adjust based on your needs)
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- Create storage bucket for product images (run this in Supabase Storage settings or SQL)
-- Note: You'll need to create the bucket in Supabase Dashboard > Storage
-- Bucket name: product-images
-- Public: true
-- Then run this policy:

-- Storage policies (run after creating the bucket)
-- CREATE POLICY "Product images are publicly accessible"
--   ON storage.objects FOR SELECT
--   USING (bucket_id = 'product-images');

-- CREATE POLICY "Anyone can upload product images"
--   ON storage.objects FOR INSERT
--   WITH CHECK (bucket_id = 'product-images');
