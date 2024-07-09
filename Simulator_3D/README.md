# 3D Drone Simulation

This project is a 3D drone simulation game using Pygame. The game includes map navigation, drone movement, and sensor visualization. The drone can move autonomously, switch between different sensor configurations, and return home upon request.

## Features

- **Drone Movement**: Navigate the drone using arrow keys.
- **Sensor Configurations**: Switch between different sensor configurations using a button.
- **Autonomous Movement**: The drone can move autonomously and avoid obstacles.
- **Return Home**: The drone can return to its starting point when requested.
- **Multi-layer Maps**: The simulation includes different layers representing different floors.
- **Risk Calculation**: Sensors detect walls and other obstacles, and the drone takes action to avoid them.

## Prerequisites

- Python 3.x
- Pygame library

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/3d-drone-simulation.git
    cd 3d-drone-simulation
    ```

2. Install the Pygame library:

    ```sh
    pip install pygame
    ```

3. Ensure you have the necessary image files (`drone_pic.png` and `warning.png`) in the project directory.

## Usage

Run the simulation:

# Drone Simulation Game

## Controls

- **Arrow Keys**: Rotate the drone.
- **Spacebar**: Toggle drone movement.
- **Mouse Click**:
  - Click on "Switch Sensors" button to change the sensor configuration.
  - Click on "AI" button to enable autonomous movement.
  - Click on "Return Home" button to make the drone return to its starting point.

## Code Structure

- **drone_simulation.py**: The main script containing all the classes and logic for the game.
- **README.md**: This file.

## Classes

- **Drone**
  - Manages drone's attributes and functions like movement, drawing, and angle calculations.
- **Map**
  - Handles map configurations and loading.
- **Sensor**
  - Manages sensor configurations and drawing sensors on the screen.
- **Button**
  - Handles button creation and drawing.
- **Game**
  - Manages the game loop, event handling, and interactions between all components.

## Map Details

The maps are represented as 2D arrays within the Game class:

- **APARTMENT1_WALLS**: Walls of the first apartment.
- **APARTMENT2_WALLS**: Walls of the second apartment.
- **APARTMENT1_FLOOR**: Floor of the first apartment.
- **APARTMENT2_FLOOR**: Floor of the second apartment.
- **CEILING2_MAP**: Ceiling of the second apartment.

## Example

To run the game, simply execute the drone_simulation.py script:

```sh
python drone_simulation.py

