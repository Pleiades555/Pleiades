<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Customer Information
    $fullName = $_POST['fullName'];
    $phoneNumber = $_POST['phoneNumber'];
    $email = $_POST['email'];
    $carMake = $_POST['carMake'];
    $regoVin = $_POST['regoVin'];
    $dateOfInquiry = $_POST['dateOfInquiry'];
    $contactMethod = $_POST['contactMethod'];

    // Parts Inquiry Details (handling multiple parts)
    $partsCount = count($_POST['part1']);
    $partsDetails = '';
    for ($i = 0; $i < $partsCount; $i++) {
        $partName = $_POST['part1'][$i];
        $partNumber = isset($_POST['partNumber1'][$i]) ? $_POST['partNumber1'][$i] : '';
        $quantity = $_POST['quantity1'][$i];
        $notes = isset($_POST['notes1'][$i]) ? $_POST['notes1'][$i] : '';

        $partsDetails .= "
        <h3>Part " . ($i + 1) . " Details</h3>
        <p><strong>Part Name/Description:</strong> $partName</p>
        <p><strong>Part Number:</strong> $partNumber</p>
        <p><strong>Quantity:</strong> $quantity</p>
        <p><strong>Additional Notes:</strong> $notes</p>";
    }

    // Email Details
    $to = "awhite@brisbanecityjlr.com.au";  // Replace with the email address where the notification will be sent
    $subject = "New Automotive Parts Inquiry";
    $message = "
    <html>
    <head>
        <title>New Automotive Parts Inquiry</title>
    </head>
    <body>
        <h3>Customer Information</h3>
        <p><strong>Full Name:</strong> $fullName</p>
        <p><strong>Phone Number:</strong> $phoneNumber</p>
        <p><strong>Email Address:</strong> $email</p>
        <p><strong>Car Make:</strong> $carMake</p>
        <p><strong>Queensland Registration Number / VIN:</strong> $regoVin</p>
        <p><strong>Date of Inquiry:</strong> $dateOfInquiry</p>
        <p><strong>Preferred Contact Method:</strong> $contactMethod</p>
        $partsDetails
    </body>
    </html>
    ";

    // Headers
    $headers = "MIME-Version: 1.0" . "\r\n";
    $headers .= "Content-Type: text/html; charset=UTF-8" . "\r\n";
    $headers .= "From: $email" . "\r\n";

    // Send email
    if (mail($to, $subject, $message, $headers)) {
        echo "Thank you for your inquiry! We will get back to you shortly.";
    } else {
        echo "Sorry, there was an issue submitting your inquiry. Please try again later.";
    }
}
?>
