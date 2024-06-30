
# Autonomous Drone 2D Simulator

## Project Overview

In this project, we delve into the world of control and management of autonomous drones. The project is divided into two main parts:

1. **Platform Search and Sensor Modeling**: 
   - Find a platform that allows three-dimensional (or two-dimensional) modeling of a structure as the drone's sensors sense the environment.
   - Define an interface that allows the calculation of all six distances given the location and orientation of the drone.

2. **Basic Control System for a Drone**:
   - Develop a basic control system for a drone to allow it to fly over as much terrain as possible.
   - Ensure the drone returns to the take-off point when the battery reaches 50%.

### Background
- Before starting, please read the [following article](https://docs.google.com/document/d/1eo34T_M7jfduRZm_oevy94YY2LkGLzRT/edit#heading=h.pbpc1ivctwps).

Autonomous drones are increasingly becoming an integral part of various industries due to their ability to perform tasks without human intervention. These drones are used in fields such as agriculture for crop monitoring, delivery services for transporting goods, surveillance for security purposes, and environmental monitoring for data collection in hard-to-reach areas. The development of autonomous drones involves complex algorithms and precise sensor integration to ensure they can navigate and perform tasks efficiently in dynamic environments.

This project focuses on simulating the behavior of an autonomous drone in a 2D environment. It draws inspiration from a comprehensive study detailed in this article, authored by three undergraduate students. The article discusses the modeling of a Tello drone equipped with additional sensors and a mission computer. The sensors provide critical data for the drone's navigation and task execution, enabling it to operate autonomously both in simulation and real-world conditions. The following videos describe the drone's autonomous flight in simulation and in real conditions:

## Getting Started

### Prerequisites

- Python 3.x
- `pygame` library

Install the required libraries using pip:
```bash
pip install pygame
```

### Project Structure

### Explanation of the Simplified Project Structure Dependencies

![אבד](https://github.com/roni5604/Model_2D_drone_simulator/assets/98646866/2217ec9d-87f0-4f50-823f-f54da5107187)

The diagram illustrates the key dependencies between the main components of the Autonomous Drone Simulator project. Each node represents a crucial file in the project, and the arrows indicate the dependencies between them.

- **SimulationWindow.py**: This is the main simulation window and user interface. It orchestrates the overall simulation, integrating various components.
  - **Depends on**:
    - **AutoAlgo1.py**: The main algorithm for autonomous drone control. It contains the logic for navigating the drone autonomously.
    - **Drone.py**: This file represents the drone's functionalities, including its sensors and movement capabilities.
    - **CPU.py**: Manages the timing and execution of different functions, ensuring that the simulation runs smoothly.
- **AutoAlgo1.py**:
  - **Depends on**:
    - **CPU.py**: Utilized for managing the timing and execution of the drone's control algorithms.
    - **Drone.py**: Interacts with the drone's functionalities to execute control commands.
    - **Lidar.py**: Simulates the Lidar sensors on the drone, providing distance measurements crucial for navigation and obstacle avoidance.

This simplified diagram highlights the essential interactions and dependencies necessary for the drone's autonomous control and simulation environment, providing a clear view of the project's core structure.

### Running the Simulation

1. Ensure the `Maps` directory contains the map images (`p12.png`, `p13.png`, `p14.png`, `p15.png`).
2. Run the `SimulationWindow.py` to start the simulation:
```bash
python SimulationWindow.py
```

## Features

- **Autonomous Navigation**: The drone navigates the environment using its sensors.
- **Collision Detection**: The drone detects obstacles using Lidar sensors.
- **Graph Visualization**: Visualizes the drone's path and explored areas.
- **Real-time Control**: Allows user input to control the drone's speed, direction, and mode.

## User Interface

- **Start/Pause**: Toggles the simulation.
- **Speed Up/Down**: Adjusts the drone's speed.
- **Spin**: Rotates the drone by a specified angle.
- **Toggle Map**: Toggles the real map view.
- **Toggle AI**: Toggles the autonomous control.
- **Return Home**: Commands the drone to return to the starting point.
- **Open Graph**: Visualizes the path taken by the drone.
- **Snake Driver**: Toggles the snake driver movement mode.
- **Keep Right Driver**: Toggles the keep right driver movement mode.

## Drone Specifications

- **Sensors**:
  - 4 Distance Meters (right, left, forward, backward)
  - Speed Sensor (Optical Flow)
  - Orientation Sensor (IMU)
  - Barometer
  - Battery Sensor

- **Capabilities**:
  - Forward Angle (Pitch): ±10 degrees, 100 degrees/second, 1 m/s², max speed 3 m/s
  - Side Angle (Roll): ±10 degrees, 100 degrees/second, 1 m/s², max speed 3 m/s
  - Angular Velocity (Yaw): 100+ degrees/second
  - Battery Status: 8 minutes maximum flight time (480 seconds)
  - 10Hz sensor measurements: [d0-d4, yaw, Vx, Vy, Z, baro, bat, pitch, roll, accX, accY, accZ]

### Instructions

1. **Part One**:
   - Search for a platform that allows 3D or 2D modeling of a structure based on the drone's sensor data.
   - Define an interface to calculate the distances given the drone's location and orientation.

2. **Part Two**:
   - Develop a basic control system to allow the drone to explore the terrain and return to the take-off point at 50% battery.

### Sensors Characteristics

- **Distance Meter**: ±2% error, detection range 0-3 meters
- Each pixel on the map represents 2.5 cm

## Explanation of Main Classes

### AutoAlgo1

`AutoAlgo1` is the main class that controls the autonomous behavior of the drone.

- **Attributes**:
  - `map_size`: Size of the map.
  - `map`: 2D array representing the state of each pixel on the map.
  - `drone`: Instance of the `Drone` class.
  - `points`: List of points representing the drone's path.
  - `m_graph`: Instance of the `Graph` class.
  - `ai_cpu`: Instance of the `CPU` class managing the AI updates.
  - Various flags and parameters to manage the drone's behavior.

### CPU

`CPU` manages the timing and execution of various functions.

- **Attributes**:
  - `hz`: Frequency of execution.
  - `functions_list`: List of functions to be executed.
  - `is_play`: Flag indicating whether the CPU is running.
  - `elapsed_milli`: Elapsed time in milliseconds.
  - `thread`: Thread running the CPU loop.

### Drone

`Drone` represents the drone and its functionalities.

- **Attributes**:
  - `real_map`: The map the drone is navigating.
  - `start_point`, `point_from_start`, `sensor_optical_flow`: Points representing various positions of the drone.
  - `lidars`: List of Lidar sensors.
  - `speed`, `rotation`, `gyro_rotation`: Movement parameters.
  - `cpu`: Instance of the `CPU` class managing the drone updates.
  - `drone_img_path`, `mImage`: Path and image of the drone.

### SimulationWindow

`SimulationWindow` is the main simulation window and user interface.

- **Attributes**:
  - `screen`, `clock`: Pygame screen and clock.
  - `running`, `toogleStop`: Flags for managing the simulation state.
  - `info_label`, `info_label2_rect`: Information labels.
  - `buttons`: List of UI buttons.
  - `algo1`: Instance of the `AutoAlgo1` class.

- **Methods of SimulationWindow.py**:

Initializes the simulation window, setting up the main interface components and preparing the environment for the simulation to run.
```
def initialize(self):
    # Initialize Pygame
    pygame.init()
    # Set up the screen
    self.screen = pygame.display.set_mode((self.width, self.height))
    pygame.display.set_caption('Drone Simulator')
    # Set up the clock
    self.clock = pygame.time.Clock()
    # Initialize additional components like buttons and labels
    self.setup_buttons()
```
toggle_cpu(): Toggles the CPU state, starting or stopping the CPU timer based on its current state.
```
def toggle_cpu(self):
    if self.cpu.is_running():
        self.cpu.stop()
    else:
        self.cpu.start()
```
speed_up(): Increases the speed of the drone.
```
def speed_up(self):
    self.drone.increase_speed()
```
speed_down(): Decreases the speed of the drone.
```
def speed_down(self):
    self.drone.decrease_speed()
```
spin_by(degrees): Rotates the drone by a specified number of degrees.
```
def spin_by(self, degrees):
    self.drone.rotate(degrees)
```
Additional Button Actions
toggle_real_map(): Toggles the display of the real map view in the simulation.
```
def

 toggle_real_map(self):
    self.show_real_map = not self.show_real_map
```
toggle_ai(): Toggles the autonomous control of the drone.
```
def toggle_ai(self):
    self.auto_algo.toggle_autonomous_mode()
```
return_home_func(): Commands the drone to return to its starting point.
```
def return_home_func(self):
    self.drone.return_to_home()
```
open_graph(): Visualizes the path taken by the drone by displaying the exploration graph.
```
def open_graph(self):
    self.graph.display()
```
toggle_snakeDriver(): Toggles the snake driver movement mode for the drone, which changes how the drone navigates.
```
def toggle_snakeDriver(self):
    self.drone.toggle_snake_mode()
```
toggle_keep_right_driver(): Toggles the keep right driver movement mode for the drone, which changes how the drone navigates.
```
def toggle_keep_right_driver(self):
    self.drone.toggle_keep_right_mode()
```
update_info(delta_time): Updates the information labels displayed on the screen, such as drone status and sensor data.
```
def update_info(self, delta_time):
    self.info_label.update(delta_time)
```
main(): The main loop for running the simulation. Handles events, updates the state of the simulation, and renders the components on the screen.
```
def main(self):
    self.initialize()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle other events like button presses
        self.update_info(self.clock.get_time())
        self.screen.fill((255, 255, 255))  # Clear screen with white background
        self.auto_algo.update(self.clock.get_time())  # Update the algorithm
        self.drone.update(self.clock.get_time())  # Update the drone
        self.graph.update(self.clock.get_time())  # Update the graph
        pygame.display.flip()  # Refresh the display
        self.clock.tick(60)  # Maintain 60 FPS
    pygame.quit()
```
Each of these methods plays a crucial role in the functionality and user interaction within the simulation window, ensuring a seamless and interactive experience.

## Additional Information

### Explanation of Key Methods: toggle_snakeDriver() vs. toggle_ai()

The `SimulationWindow.py` file contains various methods that manage the drone's behavior and user interaction within the simulation. Two important methods among these are `toggle_snakeDriver()` and `toggle_ai()`. While both methods modify the drone's mode of operation, they serve distinct purposes and function differently.

#### toggle_snakeDriver()

The `toggle_snakeDriver()` method is used to switch the drone's movement mode to or from "snake driver" mode. In this mode, the drone moves in a serpentine pattern, which can be particularly useful for systematic area coverage, such as in search and rescue operations or agricultural field monitoring.

**Functionality:**
- When activated, the drone's movement pattern changes to a back-and-forth or serpentine motion.
- This mode ensures that the drone covers the entire area in a systematic way, making it ideal for tasks that require comprehensive area scanning.
- Toggling this mode off returns the drone to its default movement behavior.

**Code Example:**
```python
def toggle_snakeDriver(self):
    self.drone.toggle_snake_mode()
```
**Detailed Explanation:**
- **toggle_snake_mode()**: A method in the `Drone` class that switches the drone's movement pattern to a snake-like motion. This is beneficial for thorough area coverage.

#### toggle_ai()

The `toggle_ai()` method, on the other hand, toggles the autonomous control mode of the drone. In this mode, the drone uses its onboard algorithms and sensor data to navigate the environment independently, making decisions in real-time to avoid obstacles and complete its mission.

**Functionality:**
- Activates or deactivates the drone's autonomous navigation and control algorithms.
- When enabled, the drone utilizes its sensors (like Lidar, IMU) and the main algorithm in `AutoAlgo1.py` to navigate and perform tasks without human intervention.
- Toggling this mode off places the drone back under manual control or into a different predefined mode.

**Code Example:**
```python
def toggle_ai(self):
    self.auto_algo.toggle_autonomous_mode()
```
**Detailed Explanation:**
- **toggle_autonomous_mode()**: A method in the `AutoAlgo1` class that activates or deactivates the autonomous control logic. This mode allows the drone to operate independently, making real-time decisions based on sensor inputs and pre-defined algorithms.

#### toggle_keep_right_driver()

The `toggle_keep_right_driver()` method is used to switch the drone's movement mode to or from "keep right driver" mode. In this mode, the drone will aim to keep to the right side and only change its course when it encounters a risky area.

**Functionality:**
- When activated, the drone attempts to keep to the right side while navigating.
- This mode ensures that the drone maintains a rightward path unless it encounters a risky area, at which point it maneuvers to avoid the risk.
- Toggling this mode off returns the drone to its default movement behavior.

**Code Example:**
```python
def toggle_keep_right_driver(self):
    self.drone.toggle_keep_right_mode()
```
**Detailed Explanation:**
- **toggle_keep_right_mode()**: A method in the `Drone` class that switches the drone's movement pattern to a rightward bias. This is beneficial for certain navigational strategies where keeping to one side is preferable.

### 8-Minute Flight Time

The drone in our project is designed to have a maximum flight time of 8 minutes (480 seconds). This feature is crucial for ensuring the drone returns to the take-off point when the battery reaches 50%, ensuring it does not remain airborne without enough power to return safely. In this project, we implement battery monitoring and ensure the drone initiates a return to the take-off point when the battery reaches 50%.

Use of Files in the Project

Several files are utilized in this project to implement the simulation and autonomous behavior of the drone:

#### CPU.py

- **Purpose**: Manages the timing and execution of various functions in the simulation.
- **Explanation**: This file defines functions such as play, stop, and resume, allowing control over the simulation's execution. It also includes a timing mechanism to ensure functions run at defined intervals based on the set frequency (Hz).

#### Tools.py

- **Purpose**: Provides utility functions for geometric and statistical calculations.
- **Explanation**: This file includes functions like get_point_by_distance to calculate a new point based on an existing point, angle, and distance, and noise_between to generate random noise within a specified range.

#### Map.py

- **Purpose**: Represents the map the drone operates within.
- **Explanation**: This file converts a map image into a boolean array and manages collisions on the map. The drone uses this information to navigate and avoid obstacles.

#### Graph.py

- **Purpose**: Represents the graph of nodes and edges created during the drone's flight.
- **Explanation**: This file includes functions to add vertices and edges to the graph and draw the graph on the screen to display the drone's path.

### Adding 8-Minute Flight Time

```python
class Drone:
    def __init__(self, real_map, start_point, battery_life=480):
        self.real_map = real_map
        self.start_point = start_point
        self.battery_life = battery_life  # Maximum flight time in seconds
        self.battery = battery_life  # Current battery status
        # continue with other initializations...

    def update_battery(self, elapsed_time):
        self.battery -= elapsed_time
        if self.battery <= self.battery_life / 2:
            self.return_to_home()

    def return_to_home(self):
        # Logic for returning to the take-off point
        pass

    def fly(self, delta_time):
        self.update_battery(delta_time)
        # additional flight logic...
```
In this section, the code in Drone.py manages the battery status and ensures the drone returns to the take-off point when the battery reaches 50%. We use the update_battery function to update the battery status in each simulation cycle.

### Summary

- **toggle_snakeDriver()**: This method changes the drone's movement to a snake-like pattern for systematic area coverage. It is particularly useful for tasks requiring thorough scanning of a designated area.
- **toggle_ai()**: This method switches the drone to autonomous mode, enabling it to navigate and complete tasks using onboard algorithms and sensor data. It allows the drone to operate independently, making real-time decisions.
- **toggle_keep_right_driver()**: This method changes the drone's movement to keep right. It ensures the drone maintains a rightward path unless it encounters a risky area, at which point it maneuvers to avoid the risk.

By understanding the distinct purposes and functionalities of these methods, users can better control the drone's behavior to suit various operational needs within the simulation.

### References

- [Link to Article](https://docs.google.com/document/d/1eo34T_M7jfduRZm_oevy94YY2LkGLzRT/edit#heading=h.pbpc1ivctwps)
- [Link to Base Project](https://github.com/vection/DroneSimulator)

