// Age validation
document.getElementById('birthday').addEventListener('change', function () {
    const birthDate = new Date(this.value);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }

    const ageMessage = document.getElementById('ageMessage');
    if (age < 18) {
        ageMessage.textContent = 'User should be 18';
        ageMessage.style.color = 'red'; // Red color for error message
    } else {
        ageMessage.textContent = ''; // Clear the message if age is valid
    }
});

// Profile photo upload
function previewProfilePhoto(event) {
    const file = event.target.files[0];
    if (file) {
        // Check file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            alert('File size too large. Please choose an image under 5MB.');
            event.target.value = ''; // Clear the input
            return;
        }

        // Check file type
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file.');
            event.target.value = ''; // Clear the input
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            // Create an image element to compress
            const img = new Image();
            img.onload = function() {
                // Create canvas for compression
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');

                // Calculate new dimensions (max 800px width/height)
                let width = img.width;
                let height = img.height;
                const maxSize = 800;

                if (width > height && width > maxSize) {
                    height *= maxSize / width;
                    width = maxSize;
                } else if (height > maxSize) {
                    width *= maxSize / height;
                    height = maxSize;
                }

                canvas.width = width;
                canvas.height = height;

                // Draw and compress
                ctx.drawImage(img, 0, 0, width, height);
                
                // Get compressed image as JPEG with 0.8 quality
                const compressedDataUrl = canvas.toDataURL('image/jpeg', 0.8);
                
                // Update preview
                const preview = document.getElementById('profilePhotoPreview');
                preview.src = compressedDataUrl;
                preview.style.display = 'block';
                document.querySelector('.profile-pic span').style.display = 'none';

                // Update completed profile photo
                document.getElementById('completedProfilePhoto').src = compressedDataUrl;
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// Language management
let languages = [];

function addLanguage() {
    const input = document.getElementById('languageInput');
    const lang = input.value.trim();

    if (lang && !languages.includes(lang)) {
        languages.push(lang);
        input.value = '';
        updateTags('languageTags', languages);
    }
}

function updateTags(containerId, items) {
    const container = document.getElementById(containerId);
    container.innerHTML = items.map(item => `
        <div class="${containerId.replace('Tags', '-tag')}">
            ${item} <span onclick="removeLanguage('${item}')">×</span>
        </div>
    `).join('');
}

// Remove language
function removeLanguage(lang) {
    languages = languages.filter(l => l !== lang);
    updateTags('languageTags', languages);
}

// Destination options
const destinations = {
    domestic: ["Delhi", "Mumbai", "Goa", "Jaipur", "Manali", "Kerala", "Kolkata", "Varanasi"],
    international: ["Paris", "New York", "London", "Dubai", "Tokyo", "Sydney", "Singapore", "Bali"]
};

// Update destination dropdown
function updateDestinations() {
    const tripTypeSelect = document.getElementById("tripType");
    const destinationSelect = document.getElementById("destination");

    // Reset the dropdown
    destinationSelect.innerHTML = '<option value="">Select a destination</option>';

    if (tripTypeSelect.value) {
        destinations[tripTypeSelect.value].forEach(destination => {
            let option = document.createElement('option');
            option.value = destination;
            option.textContent = destination;
            destinationSelect.appendChild(option);
        });
        destinationSelect.disabled = false;
    } else {
        destinationSelect.disabled = true;
    }
}

// Form validation
function validateForm() {
    const requiredFields = {
        'name': document.getElementById('name'),
        'nationality': document.getElementById('nationality'),
        'birthday': document.getElementById('birthday'),
        'tripType': document.getElementById('tripType'),
        'destination': document.getElementById('destination')
    };

    let isValid = true;
    
    // Clear previous error messages
    document.querySelectorAll('.error-message').forEach(el => el.remove());

    // Check each required field
    for (let [fieldName, field] of Object.entries(requiredFields)) {
        if (!field.value.trim()) {
            isValid = false;
            field.style.borderColor = 'red';
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.color = 'red';
            errorDiv.style.fontSize = '12px';
            errorDiv.textContent = `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required`;
            field.parentElement.appendChild(errorDiv);
        } else {
            field.style.borderColor = '';
        }
    }

    // Check radio buttons (preference)
    const preference = document.querySelector('input[name="preference"]:checked');
    if (!preference) {
        isValid = false;
        const preferenceGroup = document.querySelector('.preference-group');
        if (!preferenceGroup.querySelector('.error-message')) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.color = 'red';
            errorDiv.style.fontSize = '12px';
            errorDiv.textContent = 'Please select a travel preference';
            preferenceGroup.appendChild(errorDiv);
        }
    }

    // Check if at least one language is added
    if (languages.length === 0) {
        isValid = false;
        const languageInput = document.getElementById('languageInput');
        languageInput.style.borderColor = 'red';
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = 'red';
        errorDiv.style.fontSize = '12px';
        errorDiv.textContent = 'Please add at least one language';
        languageInput.parentElement.appendChild(errorDiv);
    }

    return isValid;
}

// Save profile and navigate
function showCompletedProfile() {
    console.log('showCompletedProfile called'); // Debug log

    if (!validateForm()) {
        console.log('Form validation failed'); // Debug log
        return false;
    }

    console.log('Form validation passed'); // Debug log

    // Get profile photo
    const profilePhoto = document.getElementById('profilePhotoPreview').src;
    const photoToSend = profilePhoto.startsWith('data:image') ? profilePhoto : '';

    // Calculate age from birthday
    const birthday = document.getElementById('birthday').value;
    console.log('Birthday:', birthday); // Debug log
    
    const today = new Date();
    const birthDate = new Date(birthday);
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    console.log('Calculated age:', age); // Debug log

    const profileData = {
        name: document.getElementById('name').value.trim(),
        nationality: document.getElementById('nationality').value.trim(),
        birthday: birthday,
        age: age,
        preference: document.querySelector('input[name="preference"]:checked').value,
        sex: document.querySelector('input[name="preference"]:checked').value,
        tripType: document.getElementById('tripType').value,
        destination: document.getElementById('destination').value,
        languages: languages,
        profilePhoto: photoToSend
    };

    console.log('Sending profile data:', profileData); // Debug log

    // Show loading state
    const nextButton = document.getElementById('submitProfile');
    const originalText = nextButton.textContent;
    nextButton.textContent = 'Saving...';
    nextButton.disabled = true;

    // First, try to save the profile
    fetch('/profile', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(profileData),
    })
    .then(response => {
        console.log('Response status:', response.status); // Debug log
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then((data) => {
        console.log('Response data:', data); // Debug log
        if (data.status === 'success') {
            // Update completed profile details
            document.getElementById('completedName').textContent = profileData.name;
            document.getElementById('completedNationality').textContent = profileData.nationality;
            document.getElementById('completedBirthday').textContent = profileData.birthday;
            document.getElementById('completedPreference').textContent = profileData.preference;
            document.getElementById('completedDestination').textContent = profileData.destination;
            document.getElementById('completedLanguages').textContent = languages.join(', ');

            // Show completed profile section
            document.getElementById('mainForm').style.display = 'none';
            document.getElementById('completedProfile').style.display = 'block';
            document.getElementById('completedProfile').style.animation = 'slideIn 0.3s ease';
        } else {
            throw new Error(data.message || 'Failed to save profile');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Failed to save profile: ' + error.message);
    })
    .finally(() => {
        // Reset button state
        nextButton.textContent = originalText;
        nextButton.disabled = false;
    });

    return false; // Prevent form submission
}

// Add event listeners when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded'); // Debug log
    
    // Initialize the destinations
    updateDestinations();
    
    // Add form submit handler
    const nextButton = document.getElementById('submitProfile');
    console.log('Next button found:', nextButton); // Debug log
    
    if (nextButton) {
        nextButton.onclick = function(e) {
            console.log('Next button clicked'); // Debug log
            e.preventDefault();
            e.stopPropagation();
            console.log('Calling showCompletedProfile'); // Debug log
            showCompletedProfile();
        };
    } else {
        console.log('Next button not found in DOM'); // Debug log
    }
    
    // Add back button handler
    const backButton = document.getElementById('backButton');
    if (backButton) {
        backButton.addEventListener('click', function() {
            document.getElementById('completedProfile').style.display = 'none';
            document.getElementById('mainForm').style.display = 'block';
        });
    }
});

// Event listeners for dropdowns
document.getElementById("tripType").addEventListener("change", updateDestinations);