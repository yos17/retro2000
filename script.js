// Indonesian Preloved Marketplace with Supabase Integration

// ============================================
// CONFIGURATION & INITIALIZATION
// ============================================

// Sample product data (fallback for demo mode)
let productsDatabase = [
    {
        id: 1,
        name: "iPhone 12 Pro 128GB",
        category_slug: "elektronik",
        category_name: "Elektronik",
        price: 7500000,
        condition: "Seperti Baru",
        location: "Jakarta Selatan",
        description: "iPhone 12 Pro warna Pacific Blue, kondisi mulus 95%, fullset box + charger original. Garansi iBox sudah habis tapi fungsi normal semua.",
        contact: "081234567890",
        image_url: "https://images.unsplash.com/photo-1603891637773-a6fc64f06ab4?w=400"
    },
    {
        id: 2,
        name: "Sepatu Nike Air Jordan 1",
        category_slug: "fashion",
        category_name: "Fashion",
        price: 2500000,
        condition: "Baik",
        location: "Bandung",
        description: "Nike Air Jordan 1 Retro High OG, size 42, kondisi 8/10. Sudah dipakai beberapa kali tapi masih sangat layak. Box hilang.",
        contact: "082345678901",
        image_url: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"
    }
];

// State management
let currentFilter = {
    category: 'semua',
    sort: 'terbaru',
    searchQuery: ''
};

let visitorCount = 1;
let categories = [];
let uploadedImageFile = null; // Store selected file

// ============================================
// SUPABASE FUNCTIONS
// ============================================

// Fetch all products from Supabase
async function fetchProductsFromSupabase() {
    try {
        const { data, error } = await supabase
            .from('products_with_categories')
            .select('*')
            .order('created_at', { ascending: false });

        if (error) throw error;
        return data || [];
    } catch (error) {
        console.error('Error fetching products:', error);
        return [];
    }
}

// Fetch categories from Supabase
async function fetchCategoriesFromSupabase() {
    try {
        const { data, error } = await supabase
            .from('categories')
            .select('*')
            .order('name');

        if (error) throw error;
        return data || [];
    } catch (error) {
        console.error('Error fetching categories:', error);
        return [];
    }
}

// Insert new product to Supabase
async function insertProductToSupabase(productData) {
    try {
        // Get category ID
        const { data: categoryData, error: catError } = await supabase
            .from('categories')
            .select('id')
            .eq('slug', productData.category)
            .single();

        if (catError) throw catError;

        // Insert product
        const { data, error } = await supabase
            .from('products')
            .insert([{
                name: productData.name,
                description: productData.description,
                price: productData.price,
                condition: productData.condition,
                location: productData.location,
                contact: productData.contact,
                image_url: productData.image_url,
                category_id: categoryData.id
            }])
            .select()
            .single();

        if (error) throw error;
        return data;
    } catch (error) {
        console.error('Error inserting product:', error);
        throw error;
    }
}

// Upload image to Supabase Storage
async function uploadImageToSupabase(file) {
    try {
        // Generate unique filename
        const fileExt = file.name.split('.').pop();
        const fileName = `${Date.now()}-${Math.random().toString(36).substring(7)}.${fileExt}`;
        const filePath = `products/${fileName}`;

        // Upload file
        const { data, error } = await supabase.storage
            .from('product-images')
            .upload(filePath, file, {
                cacheControl: '3600',
                upsert: false
            });

        if (error) throw error;

        // Get public URL
        const { data: urlData } = supabase.storage
            .from('product-images')
            .getPublicUrl(filePath);

        return urlData.publicUrl;
    } catch (error) {
        console.error('Error uploading image:', error);
        throw error;
    }
}

// Search products with full-text search
async function searchProductsInSupabase(query) {
    try {
        const { data, error } = await supabase
            .from('products_with_categories')
            .select('*')
            .or(`name.ilike.%${query}%,description.ilike.%${query}%`)
            .order('created_at', { ascending: false });

        if (error) throw error;
        return data || [];
    } catch (error) {
        console.error('Error searching products:', error);
        return [];
    }
}

// Filter products by category
async function filterProductsByCategory(categorySlug, sortBy = 'terbaru') {
    try {
        let query = supabase
            .from('products_with_categories')
            .select('*');

        if (categorySlug !== 'semua') {
            query = query.eq('category_slug', categorySlug);
        }

        // Apply sorting
        if (sortBy === 'termurah') {
            query = query.order('price', { ascending: true });
        } else if (sortBy === 'termahal') {
            query = query.order('price', { ascending: false });
        } else {
            query = query.order('created_at', { ascending: false });
        }

        const { data, error } = await query;

        if (error) throw error;
        return data || [];
    } catch (error) {
        console.error('Error filtering products:', error);
        return [];
    }
}

// ============================================
// FALLBACK FUNCTIONS (LocalStorage)
// ============================================

function getProductsFromLocalStorage() {
    const stored = localStorage.getItem('userListings');
    const userProducts = stored ? JSON.parse(stored) : [];
    return [...productsDatabase, ...userProducts];
}

function saveProductToLocalStorage(product) {
    const stored = localStorage.getItem('userListings');
    const userProducts = stored ? JSON.parse(stored) : [];
    userProducts.push(product);
    localStorage.setItem('userListings', JSON.stringify(userProducts));
}

// ============================================
// UNIFIED DATA FUNCTIONS
// ============================================

async function getAllProducts() {
    if (isSupabaseEnabled()) {
        return await fetchProductsFromSupabase();
    } else {
        return getProductsFromLocalStorage();
    }
}

async function getAllCategories() {
    if (isSupabaseEnabled()) {
        return await fetchCategoriesFromSupabase();
    } else {
        return [
            { slug: 'elektronik', name: 'Elektronik', emoji: '📱' },
            { slug: 'fashion', name: 'Fashion', emoji: '👕' },
            { slug: 'kendaraan', name: 'Kendaraan', emoji: '🚗' },
            { slug: 'rumah-tangga', name: 'Rumah Tangga', emoji: '🏠' },
            { slug: 'hobi', name: 'Hobi & Olahraga', emoji: '🎮' },
            { slug: 'lainnya', name: 'Lainnya', emoji: '📦' }
        ];
    }
}

// ============================================
// PAGE INITIALIZATION
// ============================================

window.onload = async function() {
    console.log('🚀 Initializing Barang Bekas Kita...');

    // Show loading indicator
    showLoadingState();

    // Load categories
    categories = await getAllCategories();

    // Load products
    await loadItems('items-container');
    await loadItems('browse-items-container');

    // Load visitor count
    if (localStorage.getItem('visitorCount')) {
        visitorCount = parseInt(localStorage.getItem('visitorCount'));
    }
    updateCounterDisplay();

    // Hide loading
    hideLoadingState();

    console.log('✅ App initialized successfully!');
    console.log(`📊 Mode: ${isSupabaseEnabled() ? 'Supabase' : 'Demo (LocalStorage)'}`);
};

function showLoadingState() {
    const containers = ['items-container', 'browse-items-container'];
    containers.forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            container.innerHTML = '<div class="no-items">⏳ Memuat barang...</div>';
        }
    });
}

function hideLoadingState() {
    // Loading is hidden when items are loaded
}

// ============================================
// NAVIGATION
// ============================================

function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));

    // Show selected section
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update active nav link
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => link.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    }

    // Reload items if switching to browse section
    if (sectionName === 'browse') {
        applyFilters();
    }
}

// ============================================
// DISPLAY FUNCTIONS
// ============================================

async function loadItems(containerId, items = null) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
        const itemsToDisplay = items !== null ? items : await getAllProducts();

        if (itemsToDisplay.length === 0) {
            container.innerHTML = '<div class="no-items">Tidak ada barang yang ditemukan.</div>';
            return;
        }

        container.innerHTML = itemsToDisplay.map(item => createItemCard(item)).join('');
    } catch (error) {
        console.error('Error loading items:', error);
        container.innerHTML = '<div class="no-items">❌ Gagal memuat barang. Silakan refresh halaman.</div>';
    }
}

function createItemCard(item) {
    const formattedPrice = new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(item.price);

    const categoryEmoji = {
        'elektronik': '📱',
        'fashion': '👕',
        'kendaraan': '🚗',
        'rumah-tangga': '🏠',
        'hobi': '🎮',
        'lainnya': '📦'
    };

    const categorySlug = item.category_slug || item.category;
    const categoryName = item.category_name || item.category;
    const emoji = categoryEmoji[categorySlug] || '📦';

    return `
        <div class="item-card" onclick="showItemDetail('${item.id}')">
            <img src="${item.image_url}" alt="${item.name}" class="item-image"
                 onerror="this.src='https://via.placeholder.com/400x300?text=No+Image'">
            <div>
                <div class="item-name">${item.name}</div>
                <div class="item-price">${formattedPrice}</div>
                <div class="item-location">📍 ${item.location}</div>
                <span class="item-condition">${item.condition}</span>
                <span class="item-category-badge">${emoji} ${categoryName}</span>
            </div>
        </div>
    `;
}

async function showItemDetail(itemId) {
    try {
        const allProducts = await getAllProducts();
        const item = allProducts.find(i => i.id == itemId);
        if (!item) return;

        const formattedPrice = new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(item.price);

        const categoryName = item.category_name || item.category;

        const message = `
📦 ${item.name}

💰 Harga: ${formattedPrice}
📱 Kondisi: ${item.condition}
📍 Lokasi: ${item.location}
📂 Kategori: ${categoryName}

📝 Deskripsi:
${item.description}

📞 Kontak Penjual:
${item.contact}

Hubungi penjual untuk informasi lebih lanjut!
        `;

        alert(message);
    } catch (error) {
        console.error('Error showing item detail:', error);
        alert('❌ Gagal memuat detail barang.');
    }
}

// ============================================
// SEARCH & FILTER
// ============================================

async function searchItems() {
    const searchInput = document.getElementById('search-input');
    const query = searchInput.value.toLowerCase().trim();

    if (!query) {
        alert('Silakan masukkan kata kunci pencarian!');
        return;
    }

    currentFilter.searchQuery = query;

    try {
        let results;
        if (isSupabaseEnabled()) {
            results = await searchProductsInSupabase(query);
        } else {
            const allProducts = await getAllProducts();
            results = allProducts.filter(item =>
                item.name.toLowerCase().includes(query) ||
                item.description.toLowerCase().includes(query) ||
                (item.category_name || item.category).toLowerCase().includes(query)
            );
        }

        // Switch to browse section and show results
        showSection('browse');
        await loadItems('browse-items-container', results);

        if (results.length > 0) {
            alert(`Ditemukan ${results.length} barang untuk "${query}"`);
        } else {
            alert(`Tidak ada barang yang cocok dengan "${query}"`);
        }
    } catch (error) {
        console.error('Error searching:', error);
        alert('❌ Gagal mencari barang. Silakan coba lagi.');
    }
}

function filterByCategory(category) {
    currentFilter.category = category;
    document.getElementById('category-filter').value = category;
    showSection('browse');
    applyFilters();
}

async function applyFilters() {
    const categoryFilter = document.getElementById('category-filter').value;
    const sortFilter = document.getElementById('sort-filter').value;

    currentFilter.category = categoryFilter;
    currentFilter.sort = sortFilter;

    try {
        let filtered;
        if (isSupabaseEnabled()) {
            filtered = await filterProductsByCategory(categoryFilter, sortFilter);
        } else {
            filtered = await getAllProducts();

            // Apply category filter
            if (categoryFilter !== 'semua') {
                filtered = filtered.filter(item =>
                    (item.category_slug || item.category) === categoryFilter
                );
            }

            // Apply sorting
            if (sortFilter === 'termurah') {
                filtered.sort((a, b) => a.price - b.price);
            } else if (sortFilter === 'termahal') {
                filtered.sort((a, b) => b.price - a.price);
            } else {
                filtered.reverse();
            }
        }

        await loadItems('browse-items-container', filtered);
    } catch (error) {
        console.error('Error applying filters:', error);
        alert('❌ Gagal memfilter barang. Silakan coba lagi.');
    }
}

// ============================================
// IMAGE HANDLING
// ============================================

function handleImagePreview(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('❌ Ukuran file terlalu besar! Maksimal 5MB.');
        event.target.value = '';
        return;
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
        alert('❌ File harus berupa gambar!');
        event.target.value = '';
        return;
    }

    // Store file for upload
    uploadedImageFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('image-preview');
        const previewImg = document.getElementById('preview-img');
        previewImg.src = e.target.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// ============================================
// SUBMIT LISTING
// ============================================

async function submitListing(event) {
    event.preventDefault();

    // Show loading state
    const submitBtn = event.target.querySelector('.submit-btn');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '⏳ Memproses...';
    submitBtn.disabled = true;

    try {
        // Get form values
        const name = document.getElementById('item-name').value;
        const category = document.getElementById('item-category').value;
        const price = parseInt(document.getElementById('item-price').value);
        const condition = document.getElementById('item-condition').value;
        const location = document.getElementById('item-location').value;
        const description = document.getElementById('item-description').value;
        const contact = document.getElementById('item-contact').value;
        const imageUrl = document.getElementById('item-image-url').value;

        let finalImageUrl = imageUrl;

        // Upload image if file is selected
        if (uploadedImageFile && isSupabaseEnabled()) {
            submitBtn.textContent = '📤 Mengupload foto...';
            finalImageUrl = await uploadImageToSupabase(uploadedImageFile);
        } else if (!finalImageUrl) {
            finalImageUrl = 'https://via.placeholder.com/400x300?text=No+Image';
        }

        // Prepare product data
        const productData = {
            name,
            category,
            price,
            condition,
            location,
            description,
            contact,
            image_url: finalImageUrl
        };

        // Insert product
        if (isSupabaseEnabled()) {
            submitBtn.textContent = '💾 Menyimpan data...';
            await insertProductToSupabase(productData);
        } else {
            // LocalStorage mode
            const newItem = {
                id: Date.now(),
                ...productData,
                category_slug: category,
                category_name: category,
                created_at: new Date().toISOString()
            };
            saveProductToLocalStorage(newItem);
        }

        // Success!
        alert('🎉 Iklan berhasil diposting!\n\nBarang Anda sekarang sudah tampil di marketplace. Semoga cepat laku!');

        // Reset form
        document.getElementById('sell-form').reset();
        uploadedImageFile = null;
        document.getElementById('image-preview').style.display = 'none';

        // Reload items
        await loadItems('items-container');
        await loadItems('browse-items-container');

        // Switch to browse section
        showSection('browse');

    } catch (error) {
        console.error('Error submitting listing:', error);
        alert('❌ Gagal memposting iklan. Error: ' + error.message);
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// ============================================
// VISITOR COUNTER
// ============================================

function incrementCounter() {
    visitorCount++;
    localStorage.setItem('visitorCount', visitorCount);
    updateCounterDisplay();

    const counterElement = document.querySelector('.visitor-count');
    counterElement.style.transform = 'scale(1.2)';

    setTimeout(() => {
        counterElement.style.transform = 'scale(1)';
    }, 300);
}

function updateCounterDisplay() {
    const counterElement = document.getElementById('counter');
    if (counterElement) {
        const formattedCount = visitorCount.toString().padStart(5, '0');
        counterElement.textContent = formattedCount;
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function changeColor(element) {
    const colors = ['#667eea', '#764ba2', '#48bb78', '#f5576c', '#f093fb'];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    element.style.color = randomColor;
}
