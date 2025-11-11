
<img width="1366" height="725" alt="Screenshot (270)" src="https://github.com/user-attachments/assets/487e7b5e-2252-427a-adc9-b2af8d70acf9" />

This project is a basic healthcare website built using Django, where the main focus is on creating the UI, setting up pages, and designing the flow of the application. The project currently does not include backend processing for uploading documents, but the structure and pages are prepared for future backend integration.

Below is the simple explanation of how the website works:

--> Overall Flow of the Website

The website is designed to help users navigate through healthcare-related pages easily. Even without backend logic, the project shows how a healthcare platform will function once fully built.

--> Home Page

Acts as the main entry point for users.

Contains navigation links such as Home, Services, Contact, Upload Documents, etc.

Gives a professional healthcare-themed UI.

--> Navigation Through Pages

The website includes different pages (templates) such as:

Home

About

Services

Contact

Upload Document (frontend only)

Users can move between these pages using links or buttons. Django handles this using URL routing and templates.

--> Upload Document Page (Frontend Only)

This page displays a form where the user can select a PDF.

Since backend is not implemented, the file is not saved or processed.

The page structure is ready so backend logic can be added later.

This shows how the final document upload feature will look when backend is completed.

--> Templates & Static Files

All pages use Django templates (HTML files) to display content.

CSS and images are placed in the static folder.

Django loads these static files to style and design the website.

--> URL Routing

Each button or link on the website points to a URL.
Example:

/ → Home Page

/about/ → About Page

/upload/ → Upload Documents Page

Django uses urls.py to connect each URL to a specific page.

--> Clean UI & Smooth Navigation

The main working of the project is to provide:

A user-friendly interface

Easy navigation

Clear structure of a healthcare system

Prepared templates for future backend features

--> What the Website Currently Demonstrates

Django project setup

Template rendering

Static file handling

Page navigation

UI for uploading documents (without backend)

Beginner-friendly structure for adding backend later

--> Ready for Future Backend Integration

Although backend isn’t added, the project is prepared for:

Saving uploaded files to MEDIA folder

Storing file metadata in MySQL

Creating patient profiles

Managing appointments
