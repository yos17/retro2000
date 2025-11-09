// Indonesian Preloved Marketplace JavaScript

// Sample product data (in real app, this would come from a database)
let productsDatabase = [
    {
        id: 1,
        name: "iPhone 12 Pro 128GB",
        category: "elektronik",
        price: 7500000,
        condition: "Seperti Baru",
        location: "Jakarta Selatan",
        description: "iPhone 12 Pro warna Pacific Blue, kondisi mulus 95%, fullset box + charger original. Garansi iBox sudah habis tapi fungsi normal semua.",
        contact: "081234567890",
        image: "https://images.unsplash.com/photo-1603891637773-a6fc64f06ab4?w=400"
    },
    {
        id: 2,
        name: "Sepatu Nike Air Jordan 1",
        category: "fashion",
        price: 2500000,
        condition: "Baik",
        location: "Bandung",
        description: "Nike Air Jordan 1 Retro High OG, size 42, kondisi 8/10. Sudah dipakai beberapa kali tapi masih sangat layak. Box hilang.",
        contact: "082345678901",
        image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"
    },
    {
        id: 3,
        name: "Laptop ASUS ROG Zephyrus G14",
        category: "elektronik",
        price: 15000000,
        condition: "Seperti Baru",
        location: "Surabaya",
        description: "ASUS ROG Zephyrus G14 (2021), Ryzen 9, RTX 3060, 16GB RAM, 1TB SSD. Jarang dipakai, seperti baru. Garansi masih 1 tahun.",
        contact: "083456789012",
        image: "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400"
    },
    {
        id: 4,
        name: "Sofa Minimalis 3 Seater",
        category: "rumah-tangga",
        price: 3500000,
        condition: "Baik",
        location: "Tangerang",
        description: "Sofa minimalis Scandinavian style, warna abu-abu, sangat nyaman. Dijual karena pindah rumah. Bisa COD atau kirim via ekspedisi.",
        contact: "084567890123",
        image: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400"
    },
    {
        id: 5,
        name: "Kamera Canon EOS M50 Mark II",
        category: "hobi",
        price: 8500000,
        condition: "Seperti Baru",
        location: "Jakarta Pusat",
        description: "Canon EOS M50 Mark II + Lensa Kit 15-45mm. Shutter count rendah (5000 shots). Fullset lengkap dengan tas dan memory card 64GB.",
        contact: "085678901234",
        image: "https://images.unsplash.com/photo-1606980707009-7b7a3f87f7af?w=400"
    },
    {
        id: 6,
        name: "Honda Beat 2020",
        category: "kendaraan",
        price: 12000000,
        condition: "Baik",
        location: "Bekasi",
        description: "Honda Beat 2020, warna hitam, kilometer 15.000. Pajak hidup, STNK & BPKB lengkap. Service rutin di Honda.",
        contact: "086789012345",
        image: "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=400"
    },
    {
        id: 7,
        name: "Tas Ransel The North Face",
        category: "fashion",
        price: 850000,
        condition: "Baik",
        location: "Yogyakarta",
        description: "Tas ransel The North Face Borealis Classic, warna hitam. Kondisi bagus, tidak ada robek. Cocok untuk kuliah atau traveling.",
        contact: "087890123456",
        image: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400"
    },
    {
        id: 8,
        name: "PlayStation 5 Digital Edition",
        category: "hobi",
        price: 6500000,
        condition: "Seperti Baru",
        location: "Semarang",
        description: "PS5 Digital Edition, fullset box lengkap + 1 controller. Kondisi 99% seperti baru. Bonus 3 game digital.",
        contact: "088901234567",
        image: "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400"
    },
    {
        id: 9,
        name: "Kulkas 2 Pintu Samsung",
        category: "rumah-tangga",
        price: 4200000,
        condition: "Baik",
        location: "Depok",
        description: "Kulkas Samsung 2 pintu inverter, kapasitas 500L. Kondisi normal, dingin, tidak berisik. Free ongkir area Jabodetabek.",
        contact: "089012345678",
        image: "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=400"
    },
    {
        id: 10,
        name: "Samsung Galaxy Tab S8",
        category: "elektronik",
        price: 7800000,
        condition: "Seperti Baru",
        location: "Malang",
        description: "Samsung Galaxy Tab S8 WiFi Only, 8GB/128GB. Mulus no lecet, fullset + S-Pen. Bonus keyboard case.",
        contact: "081122334455",
        image: "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400"
    },
    {
        id: 11,
        name: "Jam Tangan Casio G-Shock",
        category: "fashion",
        price: 1200000,
        condition: "Baik",
        location: "Bogor",
        description: "Casio G-Shock GA-2100 (CasiOak), warna hitam. Original, beli dari Casio Store. Box dan kartu garansi lengkap.",
        contact: "082233445566",
        image: "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=400"
    },
    {
        id: 12,
        name: "Sepeda Lipat Brompton",
        category: "hobi",
        price: 18500000,
        condition: "Baik",
        location: "Jakarta Utara",
        description: "Brompton M6L 2019, warna hitam. Kondisi terawat, service rutin. Sudah upgrade beberapa parts. Full original.",
        contact: "083344556677",
        image: "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400"
    }
];

// Store for user-created listings
let userListings = [];

// Current filters
let currentFilter = {
    category: 'semua',
    sort: 'terbaru',
    searchQuery: ''
};

// Visitor counter
let visitorCount = 1;

// Page load initialization
window.onload = function() {
    // Load items on home page
    loadItems('items-container');
    loadItems('browse-items-container');

    // Load visitor count from localStorage
    if (localStorage.getItem('visitorCount')) {
        visitorCount = parseInt(localStorage.getItem('visitorCount'));
    }
    updateCounterDisplay();

    // Load user listings from localStorage
    if (localStorage.getItem('userListings')) {
        userListings = JSON.parse(localStorage.getItem('userListings'));
        productsDatabase = [...productsDatabase, ...userListings];
    }
};

// Section navigation
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
    event.target.classList.add('active');

    // Reload items if switching to browse section
    if (sectionName === 'browse') {
        applyFilters();
    }
}

// Load and display items
function loadItems(containerId, items = null) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const itemsToDisplay = items || getAllItems();

    if (itemsToDisplay.length === 0) {
        container.innerHTML = '<div class="no-items">Tidak ada barang yang ditemukan.</div>';
        return;
    }

    container.innerHTML = itemsToDisplay.map(item => createItemCard(item)).join('');
}

// Get all items (sample + user created)
function getAllItems() {
    return productsDatabase;
}

// Create item card HTML
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

    return `
        <div class="item-card" onclick="showItemDetail(${item.id})">
            <img src="${item.image}" alt="${item.name}" class="item-image"
                 onerror="this.src='https://via.placeholder.com/400x300?text=No+Image'">
            <div>
                <div class="item-name">${item.name}</div>
                <div class="item-price">${formattedPrice}</div>
                <div class="item-location">📍 ${item.location}</div>
                <span class="item-condition">${item.condition}</span>
                <span class="item-category-badge">${categoryEmoji[item.category] || '📦'} ${item.category}</span>
            </div>
        </div>
    `;
}

// Show item detail (alert with full info)
function showItemDetail(itemId) {
    const item = productsDatabase.find(i => i.id === itemId);
    if (!item) return;

    const formattedPrice = new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(item.price);

    const message = `
📦 ${item.name}

💰 Harga: ${formattedPrice}
📱 Kondisi: ${item.condition}
📍 Lokasi: ${item.location}
📂 Kategori: ${item.category}

📝 Deskripsi:
${item.description}

📞 Kontak Penjual:
${item.contact}

Hubungi penjual untuk informasi lebih lanjut!
    `;

    alert(message);
}

// Search functionality
function searchItems() {
    const searchInput = document.getElementById('search-input');
    const query = searchInput.value.toLowerCase().trim();

    if (!query) {
        alert('Silakan masukkan kata kunci pencarian!');
        return;
    }

    currentFilter.searchQuery = query;

    const results = productsDatabase.filter(item =>
        item.name.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query)
    );

    // Switch to browse section and show results
    showSection('browse');
    loadItems('browse-items-container', results);

    if (results.length > 0) {
        alert(`Ditemukan ${results.length} barang untuk "${query}"`);
    } else {
        alert(`Tidak ada barang yang cocok dengan "${query}"`);
    }
}

// Filter by category (from category buttons)
function filterByCategory(category) {
    currentFilter.category = category;
    document.getElementById('category-filter').value = category;
    showSection('browse');
    applyFilters();
}

// Apply filters
function applyFilters() {
    const categoryFilter = document.getElementById('category-filter').value;
    const sortFilter = document.getElementById('sort-filter').value;

    currentFilter.category = categoryFilter;
    currentFilter.sort = sortFilter;

    let filtered = getAllItems();

    // Apply category filter
    if (categoryFilter !== 'semua') {
        filtered = filtered.filter(item => item.category === categoryFilter);
    }

    // Apply sorting
    if (sortFilter === 'termurah') {
        filtered.sort((a, b) => a.price - b.price);
    } else if (sortFilter === 'termahal') {
        filtered.sort((a, b) => b.price - a.price);
    } else {
        // 'terbaru' - reverse order (newest first)
        filtered.reverse();
    }

    loadItems('browse-items-container', filtered);
}

// Submit new listing
function submitListing(event) {
    event.preventDefault();

    // Get form values
    const name = document.getElementById('item-name').value;
    const category = document.getElementById('item-category').value;
    const price = parseInt(document.getElementById('item-price').value);
    const condition = document.getElementById('item-condition').value;
    const location = document.getElementById('item-location').value;
    const description = document.getElementById('item-description').value;
    const contact = document.getElementById('item-contact').value;
    const image = document.getElementById('item-image').value || 'https://via.placeholder.com/400x300?text=No+Image';

    // Create new item
    const newItem = {
        id: Date.now(), // Simple ID generation
        name,
        category,
        price,
        condition,
        location,
        description,
        contact,
        image
    };

    // Add to user listings
    userListings.push(newItem);
    productsDatabase.push(newItem);

    // Save to localStorage
    localStorage.setItem('userListings', JSON.stringify(userListings));

    // Show success message
    alert('🎉 Iklan berhasil diposting!\n\nBarang Anda sekarang sudah tampil di marketplace. Semoga cepat laku!');

    // Reset form
    document.getElementById('sell-form').reset();

    // Reload items
    loadItems('items-container');
    loadItems('browse-items-container');

    // Switch to browse section to see the new item
    showSection('browse');
}

// Visitor counter functions
function incrementCounter() {
    visitorCount++;
    localStorage.setItem('visitorCount', visitorCount);
    updateCounterDisplay();

    // Add animation effect
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

// Change color function (for interactive elements)
function changeColor(element) {
    const colors = ['#667eea', '#764ba2', '#48bb78', '#f5576c', '#f093fb'];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    element.style.color = randomColor;
}
