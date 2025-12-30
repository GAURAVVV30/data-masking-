🛡️ Data Masking Tool
A lightweight Flask-based web application that accepts sensitive user information (Email, Phone Number, and IP Address), masks the data for privacy, and stores both original and masked versions in a MongoDB database.
🚀 Features

    Real-time Masking: Instantly obscures sensitive data patterns.
    Robust Validation: Uses Regex and ipaddress libraries to ensure data integrity.
    Persistence: Stores data records in MongoDB for audit or retrieval.
    Responsive UI: Clean, modern, and mobile-friendly single-page interface.

🏗️ Architecture

    Backend: Python Flask
    Database: MongoDB
    Frontend: HTML5, CSS3, JavaScript (Fetch API)
    Security: Flask-CORS for Cross-Origin Resource Sharing.

📖 Usage

    Open the browser and navigate to the application URL.
    Enter a valid Email, Phone Number (10 digits), and IP Address.
    Click Mask Data.
    View the result in the "Masked Data" section.

Data Masking Logic
Field	Masking Rule	Example Output
Email	Keeps first letter and domain	j****@example.com
Phone	Keeps first 3 digits and adds dashes	123-***-****
IP Address	Masks the last octet	192.168.1.***
