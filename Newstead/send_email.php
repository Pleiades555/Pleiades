<?php

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get form data
    $fullName = htmlspecialchars(trim($_POST['fullName']));
    $phoneNumber = htmlspecialchars(trim($_POST['phoneNumber']));
    $email = htmlspecialchars(trim($_POST['email']));
    $carMake = htmlspecialchars(trim($_POST['carMake']));
    $regoVin = htmlspecialchars(trim($_POST['regoVin']));
    $dateOfInquiry = htmlspecialchars(trim($_POST['dateOfInquiry']));
    $contactMethod = htmlspecialchars(trim($_POST['contactMethod']));

    // Parts details (handling multiple parts)
    $partsNames = isset($_POST['part1']) ? $_POST['part1'] : [];
    $partNumbers = isset($_POST['partNumber1']) ? $_POST['partNumber1'] : [];
    $quantities = isset($_POST['quantity1']) ? $_POST['quantity1'] : [];
    $notes = isset($_POST['notes1']) ? $_POST['notes1'] : [];

    // Email details
    $to = "awhite@brisbanecityjlr.com.au"; // Replace with your actual email address
    $subject = "Newstead Parts Inquiry from $fullName";

    // Construct email body
    $emailBody = "
    <h2>Newstead Parts Inquiry</h2>
    <p><strong>Full Name:</strong> $fullName</p>
    <p><strong>Phone Number:</strong> $phoneNumber</p>
    <p><strong>Email Address:</strong> $email</p>
    <p><strong>Car Make:</strong> $carMake</p>
    <p><strong>Queensland Registration Number / VIN:</strong> $regoVin</p>
    <p><strong>Date of Inquiry:</strong> $dateOfInquiry</p>
    <p><strong>Preferred Contact Method:</strong> $contactMethod</p>
    
    <h3>Parts Inquiry Details</h3>";

    for ($i = 0; $i < count($partsNames); $i++) {
        $partName = isset($partsNames[$i]) ? htmlspecialchars(trim($partsNames[$i])) : '';
        $partNumber = isset($partNumbers[$i]) ? htmlspecialchars(trim($partNumbers[$i])) : '';
        $quantity = isset($quantities[$i]) ? htmlspecialchars(trim($quantities[$i])) : '';
        $note = isset($notes[$i]) ? htmlspecialchars(trim($notes[$i])) : '';

        $emailBody .= "
        <h4>Part " . ($i + 1) . "</h4>
        <p><strong>Part Name/Description:</strong> $partName</p>
        <p><strong>Part Number:</strong> $partNumber</p>
        <p><strong>Quantity:</strong> $quantity</p>
        <p><strong>Additional Notes:</strong> $note</p>";
    }

    // Email headers
    $headers = "MIME-Version: 1.0" . "\r\n";
    $headers .= "Content-Type: text/html; charset=UTF-8" . "\r\n";
    $headers .= "From: $email" . "\r\n";
    $headers .= "Reply-To: $email" . "\r\n";

    // Send email
    if (mail($to, $subject, $emailBody, $headers)) {
        echo "<p>Thank you for your inquiry. We will get back to you shortly.</p>";
    } else {
        echo "<p>There was an error processing your request. Please try again later.</p>";
    }
} else {
    echo "<p>No data received. Please submit the form.
