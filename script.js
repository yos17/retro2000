// Early 2000s JavaScript

// Show an alert when the page loads
window.onload = function() {
    setTimeout(function() {
        alert("Welcome to my homepage! Thanks for visiting!");
    }, 1000);
    
    // Add event listener to visitor counter
    var counterElement = document.querySelector('.visitor-count');
    if (counterElement) {
        counterElement.addEventListener('click', incrementCounter);
    }
    
    // Add event listeners to all clickable text elements
    var clickableElements = document.querySelectorAll('[onclick="changeColor(this)"]');
    clickableElements.forEach(function(element) {
        element.addEventListener('click', function() {
            changeColor(this);
        });
    });
    
    // Add event listener to guestbook link
    var guestbookLink = document.querySelector('a[onclick="return openGuestbook()"]');
    if (guestbookLink) {
        guestbookLink.addEventListener('click', function(e) {
            e.preventDefault();
            openGuestbook();
        });
    }
};

// Function to change text color when clicked
function changeColor(element) {
    var colors = ['#FF00FF', '#00FFFF', '#FFFF00', '#FF0000', '#00FF00'];
    var randomColor = colors[Math.floor(Math.random() * colors.length)];
    element.style.color = randomColor;
}

// Function for the guestbook link
function openGuestbook() {
    alert("Sorry, the guestbook is currently under construction!");
    return false;
}

// Function to increment visitor counter when clicked
function incrementCounter() {
    var counterElement = document.querySelector('.visitor-count');
    var currentCount = parseInt(counterElement.innerText);
    currentCount++;
    
    // Format the number with leading zeros
    var formattedCount = currentCount.toString().padStart(5, '0');
    
    // Add animation effect
    counterElement.style.transform = 'scale(1.2)';
    counterElement.style.color = '#FFFF00';
    
    setTimeout(function() {
        counterElement.innerText = formattedCount;
        
        setTimeout(function() {
            counterElement.style.transform = 'scale(1)';
            counterElement.style.color = '#FF0000';
        }, 300);
    }, 200);
}

// Function to show the current date in status bar (typical of early 2000s sites)
function showDate() {
    var today = new Date();
    var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    var dateString = today.toLocaleDateString('en-US', options);
    window.status = "Today is " + dateString + " - Thanks for visiting!";
    return true;
}

// Function to simulate a "secret" message (popular in early websites)
function showSecret() {
    var secretMessage = document.createElement('div');
    secretMessage.className = 'secret-message';
    secretMessage.innerHTML = 'You found the secret message! Congratulations!';
    secretMessage.style.position = 'absolute';
    secretMessage.style.top = '50%';
    secretMessage.style.left = '50%';
    secretMessage.style.transform = 'translate(-50%, -50%)';
    secretMessage.style.backgroundColor = '#000000';
    secretMessage.style.border = '3px solid #FF00FF';
    secretMessage.style.padding = '20px';
    secretMessage.style.zIndex = '999';
    secretMessage.style.color = '#00FFFF';
    secretMessage.style.fontWeight = 'bold';
    
    document.body.appendChild(secretMessage);
    
    setTimeout(function() {
        document.body.removeChild(secretMessage);
    }, 3000);
} 