# Syllabi Buddy

Syllabi Buddy is a web application designed to help students navigate and manage their school syllabi more efficiently. By analyzing uploaded syllabi, Syllaby Buddy provides summaries, extracts key information, and integrates important deadlines into users' calendars, making academic planning easier and more organized.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Usage](#usage)
- [API Integration](#api-integration)
- [Contributing](#contributing)

## Overview

Syllaby Buddy aims to simplify academic management by:
- Providing concise summaries of school syllabi.
- Highlighting key dates, assignments, and exam schedules.
- Integrating important events directly into the user’s calendar of choice.

The project is built using Flask as the backend and integrates with calendar APIs to offer a seamless user experience.

## Features

- **Syllabus Analysis**: Automatically extracts key information like exam dates, assignment deadlines, and office hours from uploaded syllabi.
- **Calendar Integration**: Connects with popular calendar services (e.g., Google Calendar) to add important events and reminders.
- **User-Friendly Interface**: Simple and intuitive interface for uploading syllabi and viewing processed information.
- **Automated Summarization**: Generates a concise summary for each syllabus, helping students quickly understand their course requirements.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: Google Calendar API

## Usage

1. Access the application via `http://127.0.0.1:5000`.
2. Upload your syllabus in a supported format (e.g., PDF or DOCX).
3. View the summarized information and sync important events with your calendar.

## API Integration

Syllaby Buddy uses the Google Calendar API for adding events. To set up API integration:

1. Obtain your API credentials from the Google Cloud Console.
2. Create a `.env` file with your `CLIENT_ID`, `CLIENT_SECRET`, and other relevant details.
3. Follow the OAuth authentication flow when prompted to grant the application access to your calendar.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch
3. Make your changes and commit them
4. Push your changes
5. Open a pull request.

