# ProjetDjango

## Overview
This project is a Cloud Drive platform developed using Django, providing users with the ability to upload, manage, and download files while tracking storage usage and providing account insights. Inspired by services like Google Drive and OneDrive, this platform includes features such as user authentication, file and folder navigation, space usage statistics, and more.

## Features

Sign Up and Login: Users can create an account with a username, email, and password, and log in securely.
Password Management: Ensure security through hashed storage.
Session Management: Automatic login on successful sign-in and logout upon user request.
File Upload: Users can upload files with a maximum size of 40 MB, stored in their personal folders.
Folder Creation: Organize files by creating folders.
File Navigation: Navigate and manage files and folders in an intuitive web interface.
File Download: Users can easily download files they have uploaded.
File Size Limit: Restriction of 40 MB per file upload to avoid overload.
File Format Distribution: Displays statistics on the types of files stored by format (image, video, document, etc.).

## Installation
### To run this project locally, follow the steps below:

#### prerequisities 
Python 3.x installed on your machine.
Django (latest version) installed via pip.
#### steps to install and run
Download the Project
Set up a Virtual Environment (Optional but Recommended)
Start the Development Server
Access the site by opening your web browser and go to http://127.0.0.1:8000/ to view the site.


## site overview
When you visit the site for the first time, you will be redirected to the **Login** page (`/login`). From there, you can either create a new account or log in if you already have one.

Once logged in or after creating an account, you will be directed to the **List Documents** page, where you can view all the documents and files associated with your account.

### Key Features:

- **Uploading Files & Creating Folders**:
  - To upload a file or create a new folder, simply go to the **Upload** section in the navigation bar and click the corresponding button (either for file upload or folder creation).
  
- **Managing Files**:
  - To rename, delete, move, or download a document, click the three vertical dots next to the document's name and choose the desired action from the dropdown menu.
  - To move a document, a new page will appear where you can select the target folder for the move.
  
- **Managing Folders**:
  - Similarly, for deleting a folder, click the three vertical dots next to the folder's name and select the action you want to take.
  

- **Logging Out**:
  - To log out, click the **Logout** button in the navigation bar.

- **Dark Mode**:
  - For a more comfortable viewing experience, you can enable **Dark Mode** by toggling the option in the top-right corner of the page.

This user-friendly platform ensures seamless navigation through your files, with intuitive options to manage documents and folders directly from the interface.