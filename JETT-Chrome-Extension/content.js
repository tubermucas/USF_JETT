const button = document.getElementById('fetchdata');
const container = document.getElementById('container');
button.addEventListener('click', () => {
    const url = 'https://lib.usf.edu/services/study-room-reservations/'; 
    window.open(url, '_blank'); 
});