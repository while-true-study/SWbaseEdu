CREATE DATABASE IF NOT EXISTS smart_farm
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE smart_farm;

CREATE TABLE IF NOT EXISTS parm_data (
    id INT NOT NULL AUTO_INCREMENT,
    input_time DATETIME NOT NULL,
    sensor_name VARCHAR(30) NOT NULL,
    temperature INT NOT NULL,
    illuminance INT NOT NULL,
    humidity INT NOT NULL,
    PRIMARY KEY (id)
);
