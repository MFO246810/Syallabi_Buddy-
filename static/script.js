document.getElementById('Calendar_options').addEventListener('change', function() {
    var selectedValue = this.value;
    if (selectedValue) {
        document.getElementById(selectedValue + '_button').style.display = 'block';
    }
});
function startProcessing() {
    // Show the processing message
    document.getElementById('processing').style.display = 'block';

    // Fetch data from the Flask server
    fetch('/submit')
        .then(response => response.json())
        .then(data => {
            // Hide the processing message
            document.getElementById('processing').style.display = 'none';
            
            // Update the dynamic text with the server response
            document.getElementById('processing').innerText = data.message;
        })
        .catch(error => {
            document.getElementById('processing').style.display = 'none';
          
            console.error('Error:', error);
        });
}
