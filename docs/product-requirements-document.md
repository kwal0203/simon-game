## Mini-PRD

## Objective

Deploy a web version of the Simon Game. The primary goal for this project is to practice the software engineering process end-to-end producing a working cloud deployment of the game that people can play.

## Target audience

The target user group is small and consists of myself (as QA engineer/engineer), up to 5 friends and family and intermittent use by hiring managers inspecting my software artifacts for interviews.

## User flow

1. User will navigate to a public URL (i.e. [www.simongame.com](http://www.simongame.com), given availability)
2. User presented with landing page containing images and ‘start game’ button
3. User clicks start game button and game begins
4. The game lights light up in a random sequence and play an associated sound for each one
5. The user clicks the buttons in the order they believe the game played them
6. If the user gets the sequence correct, the game moves to the next round and the sequence lengthens
7. If the user gets the sequence incorrect, the leaderboard is shown along with the users rank and the game ends.

## Core requirements (in scope)

The absolute minimum set of features and technical requirements needed to make the project function. If an item on this list is not completed, the project cannot be launched.

Frontend:

* Game logic: Basic game userflow (start game, mouse clicks sequences, next level, game end)
* Leaderboard UI: displays the top 100 unique user scores and highlights user rank. If user rank is outside the top 100, append an extra highlighted row at the bottom with the users score entry.

API:

* POST endpoint for score submission to leaderboard (idempotent)
* GET endpoint for leaderboard retrieval
* Python/FastAPI

Identity & idempotency:

* State management (idempotency key, player\_id cookie)

Database:

* ScoreEntry datatype:
  * score
  * score\_id
  * idempotency\_key
  * player\_id
  * created\_at
* Postgresql

## Out of scope

Frontend:

* Login/logout workflow UI
* User profile UI

Authentication:

* Social media login

Backend:

* Workers and job queues

## Success metrics

* The game is reachable at a public URL
* At least five players can play at the same time
* Leaderboard and rank are displayed on the UI at the end of a game
* Game logic \+ ‘lights’ and sound follow the physical Simon Game pattern
* Leaderboard score submission is idempotent

## Milestones

1. MVP: Gameplay, leaderboard retrieval and score submission
2. Production: CI/CD pipeline, testing, logs, monitoring
3. Hardening: Caching, CDN, rate-limiting, game-days
