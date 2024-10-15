import pandas as pd
import numpy as np
import os

# Function to simulate bot scroll data
def generate_bot_data(bot_id, pattern_type, num_rows=30):
    data = {
        'timestamp': np.arange(0, num_rows),
        'position': [],
        'speed': []
    }

    if pattern_type == "constant_speed":
        # Bot with constant speed
        for i in range(num_rows):
            data['position'].append(i * 50)
            data['speed'].append(50)
    
    elif pattern_type == "accelerating":
        # Bot with accelerating speed
        position = 0
        speed = 10
        for i in range(num_rows):
            data['position'].append(position)
            data['speed'].append(speed)
            position += speed
            speed += 2  # Accelerating speed
    
    elif pattern_type == "decelerating":
        # Bot with decelerating speed
        position = 0
        speed = 100
        for i in range(num_rows):
            data['position'].append(position)
            data['speed'].append(speed)
            position += speed
            speed = max(5, speed - 3)  # Decelerating speed
    
    elif pattern_type == "random_jumps":
        # Bot with random jumps
        position = 0
        for i in range(num_rows):
            jump = np.random.randint(20, 100)
            data['position'].append(position)
            data['speed'].append(jump)
            position += jump
    
    elif pattern_type == "pauses":
        # Bot with pauses between scrolls
        position = 0
        speed = 50
        for i in range(num_rows):
            if i % 5 == 0:
                speed = 0  # Pause every 5 steps
            else:
                speed = 50
            data['position'].append(position)
            data['speed'].append(speed)
            position += speed

    # Save as CSV
    df = pd.DataFrame(data)
    file_path = f'/mnt/data/bot_{bot_id}_{pattern_type}.csv'
    df.to_csv(file_path, index=False)
    return file_path

# Generate CSVs for 5 different bot patterns
bot_patterns = ['constant_speed', 'accelerating', 'decelerating', 'random_jumps', 'pauses']
generated_files = [generate_bot_data(i+1, pattern) for i, pattern in enumerate(bot_patterns)]
generated_files
