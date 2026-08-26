# FitLog

FitLog is a full-stack fitness tracking application that combines nutrition and workout tracking into one place.

The goal of FitLog is to make it easy for users to track their daily calories and macronutrients while also logging workouts, exercises, sets, reps, and fitness progress.

## Project Goals

FitLog will combine nutrition tracking and workout tracking so users do not need separate applications to manage their fitness journey.

The application will focus on three main areas:

- Nutrition tracking
- Workout tracking
- Progress tracking

## Version 1 — MVP

The first version of FitLog will focus on the core features needed for a functional fitness tracker.

### User Accounts

Users will be able to:

- Create an account
- Log in and log out
- Manage their profile
- Set personal fitness goals

### Nutrition Tracking

Users will be able to:

- Set a daily calorie goal
- Set protein, carbohydrate, and fat goals
- Log foods
- Organize foods into meals
- View daily calories and macronutrients
- View progress toward daily nutrition goals

### Workout Tracking

Users will be able to:

- Create workouts
- Add exercises to workouts
- Record sets
- Record weight
- Record repetitions
- View previous workout performance
- View workout history

### Progress Tracking

Users will be able to:

- Record body weight
- View body-weight history
- Track strength progress
- View personal records

### Dashboard

The FitLog dashboard will combine nutrition and workout information into one view.

Users will be able to quickly see:

- Calories consumed
- Remaining calories
- Protein, carbohydrates, and fat
- Today's workout
- Recent workout performance
- Current body weight
- Recent progress

## Technology Stack

### Frontend

- HTML
- CSS
- JavaScript
- Fetch API

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database

- PostgreSQL

### Development Tools

- Git
- GitHub
- pytest

## Project Structure

```text
FitLog/
│
├── README.md
├── .gitignore
│
├── frontend/
│   ├── index.html
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
└── backend/
```

As FitLog grows, additional files and folders will be added to keep different parts of the application organized.

## Application Architecture

FitLog will use a simple frontend, backend, and database architecture.

```text
HTML + CSS + JavaScript
       Frontend
           │
           │ Fetch API
           ▼
    Python + FastAPI
        Backend
           │
           │ SQLAlchemy
           ▼
      PostgreSQL
        Database
```

### Frontend

pages.
The frontend is responsible for everything the user sees and interacts with.

HTML will create the structure of the 
CSS will control the appearance and layout.

JavaScript will handle user interactions, calculations, and communication with the backend.

The JavaScript Fetch API will be used to send requests to the FitLog backend.

### Backend

The backend will be built with Python and FastAPI.

The backend will be responsible for:

- Processing API requests
- User authentication
- Nutrition logic
- Workout logic
- Progress tracking
- Data validation
- Communicating with the database

### Database

PostgreSQL will store the application's permanent data.

This will eventually include:

- Users
- User profiles
- Nutrition goals
- Foods
- Meals
- Exercises
- Workouts
- Workout sets
- Body-weight entries
- Personal records

## How the Parts Work Together

When a user performs an action in FitLog, the frontend will send a request to the Python backend.

For example:

```text
User clicks "View Workouts"
          │
          ▼
JavaScript
          │
        fetch()
          │
          ▼
FastAPI
          │
          ▼
PostgreSQL
          │
     Workout data
          │
          ▼
FastAPI
          │
        JSON
          │
          ▼
JavaScript
          │
          ▼
Workout displayed on screen
```

The frontend will not communicate directly with the database. FastAPI will act as the connection between the frontend and PostgreSQL.

## Future Features

The following features may be added after the first version of FitLog is working:

- Food database API integration
- Barcode scanning
- Saved meals and recipes
- Workout templates
- Larger exercise library
- Estimated one-rep max calculations
- Advanced progress charts
- Nutrition and training analytics
- Exercise recommendations
- Goal-based calorie recommendations
- Apple Health integration
- Mobile application
- Social features
- AI-powered fitness insights

A frontend framework such as React could also be introduced later if the frontend becomes large enough to benefit from one.

## Development Approach

FitLog will be developed gradually, focusing on understanding each part of the application rather than adding every feature at once.

The initial development order will focus on:

1. Project setup
2. Basic frontend
3. Basic FastAPI backend
4. Frontend-to-backend communication
5. Database integration
6. User accounts
7. Workout tracking
8. Nutrition tracking
9. Progress tracking
10. Dashboard
11. Testing and improvements

## Development Status

FitLog is currently in the initial development stage.

The first goal is to establish the project structure and create a working connection between the HTML/JavaScript frontend and Python/FastAPI backend.

## Author

FitLog is a personal full-stack software development project created to gain practical experience building a complete application using Python, JavaScript, APIs, databases, Git, and GitHub.
