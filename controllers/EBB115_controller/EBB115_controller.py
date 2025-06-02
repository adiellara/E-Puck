from controller import Robot, Motor, DistanceSensor, Camera, LED

# Configuración del tiempo
TIME_STEP = 64
MAX_SPEED = 6.28
DARK_THRESHOLD = 3500  # Cuanto más bajo, más oscuro

# Inicializar el robot
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Inicializar cámara
camera = robot.getDevice('camera')
camera.enable(timestep)

# Inicializar motores
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

# Inicializar sensores de luz
light_sensor_names = ['ls0', 'ls1', 'ls2', 'ls3', 'ls4', 'ls5', 'ls6', 'ls7']
light_sensors = [robot.getDevice(name) for name in light_sensor_names]
for sensor in light_sensors:
    sensor.enable(timestep)

# Inicializar sensores de distancia
prox_sensor_names = ["ps0", "ps1", "ps2", "ps3", "ps4", "ps5", "ps6", "ps7"]
prox_sensors = {name: robot.getDevice(name) for name in prox_sensor_names}
for sensor in prox_sensors.values():
    sensor.enable(TIME_STEP)

# Inicializar LEDs
led_names = ["led0", "led1", "led2", "led3", "led4", "led5", "led6", "led7"]
leds = {name: robot.getDevice(name) for name in led_names}

# Función para controlar LEDs
def set_leds(leds_to_activate):
    for name in led_names:
        leds[name].set(1 if name in leds_to_activate else 0)

# Bucle principal
while robot.step(TIME_STEP) != -1:
    # Leer valores de sensores de distancia
    left_wall = prox_sensors["ps5"].getValue() > 80
    left_corner = prox_sensors["ps6"].getValue() > 80
    front_wall = prox_sensors["ps7"].getValue() > 80
    right_obstacle = prox_sensors["ps2"].getValue() > 80  # Sensor a la derecha

    # Leer sensores de luz laterales (ls2 y ls5)
    front_left = light_sensors[5].getValue()
    front_right = light_sensors[2].getValue()

    print(f"Luz izq: {front_left:.2f}, Luz der: {front_right:.2f}")

    if front_left < DARK_THRESHOLD or front_right < DARK_THRESHOLD:
        print("⚠ Zona iluminada detectada → meta alcanzada")
        left_motor.setVelocity(0)
        right_motor.setVelocity(0)
        set_leds(["led0", "led7"])  # LEDs frontales encendidos
    else:
        left_speed = MAX_SPEED
        right_speed = MAX_SPEED

        if right_obstacle:
            print("Obstáculo a la derecha, girar a la izquierda")
            set_leds(["led4", "led5", "led6"])  # LEDs de giro a la izquierda
            left_speed = MAX_SPEED / 8
            right_speed = MAX_SPEED

            # Continuar girando a la izquierda hasta que no haya obstáculo a la derecha
            while right_obstacle:
                left_motor.setVelocity(left_speed)
                right_motor.setVelocity(right_speed)
                right_obstacle = prox_sensors["ps2"].getValue() > 80  # Re-evaluar el obstáculo
        elif front_wall:
            print("Girar a la derecha en su lugar")
            set_leds(["led1", "led2", "led3"])  # LEDs de giro a la derecha
            left_speed = MAX_SPEED
            right_speed = -MAX_SPEED
        elif left_wall:
            print("Avanzar recto")
            set_leds(["led0", "led7"])  # LEDs frontales encendidos
        else:
            print("Girar a la izquierda")
            set_leds(["led4", "led5", "led6"])  # LEDs de giro a la izquierda
            left_speed = MAX_SPEED / 8
            right_speed = MAX_SPEED

        if left_corner:
            print("Demasiado cerca, girar a la derecha")
            set_leds(["led1", "led2", "led3"])  # LEDs de giro a la derecha
            left_speed = MAX_SPEED
            right_speed = MAX_SPEED / 8

        # Establecer velocidades de los motores
        left_motor.setVelocity(left_speed)
        right_motor.setVelocity(right_speed)

