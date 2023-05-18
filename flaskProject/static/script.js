function toggleFavorite() {
  var button = document.getElementById("favorite-button");
  if (button.innerHTML.includes("★")) {
    button.innerHTML = "☆ Preferiti";
  } else {
    button.innerHTML = "★ Preferiti";
  }
}
// Iterate through each summary
var summaries = document.querySelectorAll('.summary');

// Iterate through each summary
summaries.forEach(function(summary) {
    var text = summary.textContent.trim();

    // Check if the summary exceeds 300 characters
    if (text.length > 300) {
        var truncatedText = text.slice(0, 300).trim();
        var lastSpaceIndex = truncatedText.lastIndexOf(' ');

        // Check if the last space index is valid
        if (lastSpaceIndex !== -1) {
            truncatedText = truncatedText.slice(0, lastSpaceIndex);
        }

        // Add ellipsis to the truncated text
        truncatedText += '...';

        // Create a new text node with the truncated text
        var newText = document.createTextNode(truncatedText);

        // Clear the original summary text
        summary.textContent = '';

        // Append the truncated text node to the summary
        summary.appendChild(newText);

        // Create "Show More" button
        var showMoreBtn = document.createElement('button');
        showMoreBtn.textContent = 'Show More';
        showMoreBtn.classList.add('btn', 'btn-link', 'show-more-btn');

        // Toggle summary expansion on button click
        showMoreBtn.addEventListener('click', function() {
            summary.textContent = text;
        });

        // Append "Show More" button to the card body
        summary.parentElement.appendChild(showMoreBtn);
    }
});
