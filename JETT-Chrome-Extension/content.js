// content.js

// Create a new button element
const button = document.createElement('button');

// Set the button text
button.textContent = 'Go to Example Website';

// Style the button (optional, you can customize it)
button.style.position = 'fixed'; // Position it fixed on the page
button.style.bottom = '20px';    // Place it at the bottom of the screen
button.style.right = '20px';     // Place it towards the right side
button.style.padding = '10px 20px'; // Add padding to the button
button.style.backgroundColor = '#4CAF50'; // Green background
button.style.color = 'white'; // White text color
button.style.border = 'none'; // No border
button.style.borderRadius = '5px'; // Rounded corners
button.style.fontSize = '16px'; // Larger font size
button.style.cursor = 'pointer'; // Show a pointer cursor on hover

// Add an event listener for the button click
button.addEventListener('click', () => {
  // Redirect the user to the specified URL
  window.location.href = 'https://www.google.com'; // Change the URL as needed
});

// Append the button to the body of the page
document.body.appendChild(button);
